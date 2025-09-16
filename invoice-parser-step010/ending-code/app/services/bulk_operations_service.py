"""
Bulk Operations Service

Provides batch processing capabilities for invoice operations including
bulk upload, processing, deletion, and data manipulation with progress tracking.
"""
import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, AsyncGenerator
from enum import Enum
from dataclasses import dataclass, asdict
import json

from app.core.database import get_db_session
from app.core.logging_config import performance_monitor
from app.core.websocket_manager import websocket_manager, NotificationType, NotificationPriority
from app.services.invoice_service import InvoiceService
from app.services.database_service import DatabaseService
from app.models.database import InvoiceModel, UserModel
from app.models.schemas import InvoiceDataSchema

logger = logging.getLogger(__name__)


class BulkOperationType(str, Enum):
    """Types of bulk operations."""
    UPLOAD_PROCESS = "upload_process"
    DELETE = "delete"
    UPDATE = "update"
    EXPORT = "export"
    REPROCESS = "reprocess"
    ARCHIVE = "archive"
    VALIDATE = "validate"


class BulkOperationStatus(str, Enum):
    """Bulk operation status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


@dataclass
class BulkOperationItem:
    """Represents a single item in a bulk operation."""
    id: str
    status: str
    data: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    processed_at: Optional[datetime] = None


@dataclass
class BulkOperationProgress:
    """Tracks progress of a bulk operation."""
    total: int
    processed: int
    successful: int
    failed: int
    percentage: float
    current_item: Optional[str] = None
    estimated_remaining_time: Optional[float] = None


@dataclass
class BulkOperation:
    """Represents a bulk operation."""
    id: str
    user_id: str
    operation_type: BulkOperationType
    status: BulkOperationStatus
    items: List[BulkOperationItem]
    progress: BulkOperationProgress
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    error: Optional[str] = None


class BulkOperationsService:
    """Service for handling bulk operations with progress tracking."""
    
    def __init__(self):
        """Initialize bulk operations service."""
        self.invoice_service = InvoiceService()
        self.db_service = DatabaseService()
        self.active_operations: Dict[str, BulkOperation] = {}
        self.operation_tasks: Dict[str, asyncio.Task] = {}
    
    async def create_bulk_upload_operation(
        self,
        user_id: str,
        files_data: List[Dict[str, Any]],
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create a bulk upload and processing operation.
        
        Args:
            user_id: User ID
            files_data: List of file data dictionaries with 'data', 'content_type', 'filename'
            metadata: Additional metadata for the operation
            
        Returns:
            Operation ID
        """
        operation_id = str(uuid.uuid4())
        
        # Create operation items
        items = []
        for i, file_data in enumerate(files_data):
            item = BulkOperationItem(
                id=str(uuid.uuid4()),
                status="pending",
                data={
                    "index": i,
                    "filename": file_data.get("filename", f"file_{i}"),
                    "content_type": file_data.get("content_type"),
                    "size": len(file_data.get("data", b""))
                }
            )
            items.append(item)
        
        # Create operation
        operation = BulkOperation(
            id=operation_id,
            user_id=user_id,
            operation_type=BulkOperationType.UPLOAD_PROCESS,
            status=BulkOperationStatus.PENDING,
            items=items,
            progress=BulkOperationProgress(
                total=len(items),
                processed=0,
                successful=0,
                failed=0,
                percentage=0.0
            ),
            created_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Store operation
        self.active_operations[operation_id] = operation
        
        # Store files data separately (not in the operation object for memory efficiency)
        operation.metadata["files_data"] = files_data
        
        logger.info(f"Created bulk upload operation {operation_id} for user {user_id} with {len(files_data)} files")
        
        return operation_id
    
    async def create_bulk_delete_operation(
        self,
        user_id: str,
        invoice_ids: List[str],
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create a bulk delete operation.
        
        Args:
            user_id: User ID
            invoice_ids: List of invoice IDs to delete
            metadata: Additional metadata
            
        Returns:
            Operation ID
        """
        operation_id = str(uuid.uuid4())
        
        # Create operation items
        items = []
        for invoice_id in invoice_ids:
            item = BulkOperationItem(
                id=str(uuid.uuid4()),
                status="pending",
                data={"invoice_id": invoice_id}
            )
            items.append(item)
        
        # Create operation
        operation = BulkOperation(
            id=operation_id,
            user_id=user_id,
            operation_type=BulkOperationType.DELETE,
            status=BulkOperationStatus.PENDING,
            items=items,
            progress=BulkOperationProgress(
                total=len(items),
                processed=0,
                successful=0,
                failed=0,
                percentage=0.0
            ),
            created_at=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        # Store operation
        self.active_operations[operation_id] = operation
        
        logger.info(f"Created bulk delete operation {operation_id} for user {user_id} with {len(invoice_ids)} invoices")
        
        return operation_id
    
    async def start_operation(self, operation_id: str) -> bool:
        """
        Start executing a bulk operation.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            True if started successfully
        """
        if operation_id not in self.active_operations:
            logger.error(f"Operation {operation_id} not found")
            return False
        
        operation = self.active_operations[operation_id]
        
        if operation.status != BulkOperationStatus.PENDING:
            logger.warning(f"Operation {operation_id} is not in pending status")
            return False
        
        # Update operation status
        operation.status = BulkOperationStatus.RUNNING
        operation.started_at = datetime.utcnow()
        
        # Start background task
        if operation.operation_type == BulkOperationType.UPLOAD_PROCESS:
            task = asyncio.create_task(self._execute_bulk_upload(operation))
        elif operation.operation_type == BulkOperationType.DELETE:
            task = asyncio.create_task(self._execute_bulk_delete(operation))
        else:
            logger.error(f"Unsupported operation type: {operation.operation_type}")
            operation.status = BulkOperationStatus.FAILED
            operation.error = "Unsupported operation type"
            return False
        
        self.operation_tasks[operation_id] = task
        
        # Notify start
        await websocket_manager.send_notification(
            NotificationType.BULK_OPERATION,
            f"Bulk operation started: {operation.operation_type.value}",
            user_id=operation.user_id,
            priority=NotificationPriority.NORMAL,
            data={
                "operation_id": operation_id,
                "operation_type": operation.operation_type.value,
                "total_items": operation.progress.total,
                "status": "started"
            }
        )
        
        logger.info(f"Started bulk operation {operation_id}")
        return True
    
    async def _execute_bulk_upload(self, operation: BulkOperation):
        """Execute bulk upload operation."""
        try:
            files_data = operation.metadata.get("files_data", [])
            start_time = datetime.utcnow()
            
            for i, (item, file_data) in enumerate(zip(operation.items, files_data)):
                try:
                    # Update current item
                    operation.progress.current_item = item.data["filename"]
                    
                    # Notify progress
                    await self._notify_progress(operation)
                    
                    # Process file
                    item.status = "processing"
                    
                    # Extract file data
                    file_bytes = file_data.get("data", b"")
                    content_type = file_data.get("content_type", "")
                    filename = file_data.get("filename", f"file_{i}")
                    
                    # Process invoice
                    result = await self.invoice_service.process_invoice(
                        file_data=file_bytes,
                        content_type=content_type,
                        filename=filename,
                        user_id=operation.user_id
                    )
                    
                    if result.success:
                        # Save to database if processing succeeded
                        if result.data:
                            save_result = self.invoice_service.save_invoice(
                                result.data, 
                                operation.user_id
                            )
                            
                            if save_result.success:
                                item.status = "completed"
                                item.result = {
                                    "invoice_id": save_result.invoice_id,
                                    "confidence": result.confidence,
                                    "processing_time": result.processing_time
                                }
                                operation.progress.successful += 1
                            else:
                                item.status = "failed"
                                item.error = save_result.error
                                operation.progress.failed += 1
                        else:
                            item.status = "failed"
                            item.error = "No data extracted from invoice"
                            operation.progress.failed += 1
                    else:
                        item.status = "failed"
                        item.error = result.error
                        operation.progress.failed += 1
                    
                    item.processed_at = datetime.utcnow()
                    operation.progress.processed += 1
                    operation.progress.percentage = (operation.progress.processed / operation.progress.total) * 100
                    
                    # Calculate estimated remaining time
                    elapsed = (datetime.utcnow() - start_time).total_seconds()
                    if operation.progress.processed > 0:
                        avg_time_per_item = elapsed / operation.progress.processed
                        remaining_items = operation.progress.total - operation.progress.processed
                        operation.progress.estimated_remaining_time = avg_time_per_item * remaining_items
                    
                    # Small delay to prevent overwhelming the system
                    await asyncio.sleep(0.1)
                    
                except Exception as e:
                    logger.error(f"Error processing item {item.id}: {e}")
                    item.status = "failed"
                    item.error = str(e)
                    item.processed_at = datetime.utcnow()
                    operation.progress.processed += 1
                    operation.progress.failed += 1
                    operation.progress.percentage = (operation.progress.processed / operation.progress.total) * 100
            
            # Operation completed
            operation.status = BulkOperationStatus.COMPLETED if operation.progress.failed == 0 else BulkOperationStatus.PARTIAL
            operation.completed_at = datetime.utcnow()
            
            # Final notification
            await websocket_manager.send_notification(
                NotificationType.BULK_OPERATION,
                f"Bulk upload completed: {operation.progress.successful} successful, {operation.progress.failed} failed",
                user_id=operation.user_id,
                priority=NotificationPriority.HIGH,
                data={
                    "operation_id": operation.id,
                    "status": "completed",
                    "successful": operation.progress.successful,
                    "failed": operation.progress.failed,
                    "total": operation.progress.total
                }
            )
            
            logger.info(f"Bulk upload operation {operation.id} completed: {operation.progress.successful}/{operation.progress.total} successful")
            
        except Exception as e:
            logger.error(f"Error in bulk upload operation {operation.id}: {e}")
            operation.status = BulkOperationStatus.FAILED
            operation.error = str(e)
            operation.completed_at = datetime.utcnow()
            
            await websocket_manager.send_notification(
                NotificationType.BULK_OPERATION,
                f"Bulk upload failed: {str(e)}",
                user_id=operation.user_id,
                priority=NotificationPriority.HIGH,
                data={
                    "operation_id": operation.id,
                    "status": "failed",
                    "error": str(e)
                }
            )
        
        finally:
            # Clean up files data from memory
            if "files_data" in operation.metadata:
                del operation.metadata["files_data"]
            
            # Remove task reference
            if operation.id in self.operation_tasks:
                del self.operation_tasks[operation.id]
    
    async def _execute_bulk_delete(self, operation: BulkOperation):
        """Execute bulk delete operation."""
        try:
            start_time = datetime.utcnow()
            
            for item in operation.items:
                try:
                    # Update current item
                    invoice_id = item.data["invoice_id"]
                    operation.progress.current_item = f"Invoice {invoice_id}"
                    
                    # Notify progress
                    await self._notify_progress(operation)
                    
                    # Delete invoice
                    item.status = "processing"
                    
                    delete_result = self.db_service.delete_invoice(invoice_id, operation.user_id)
                    
                    if delete_result["success"]:
                        item.status = "completed"
                        item.result = {"deleted": True}
                        operation.progress.successful += 1
                    else:
                        item.status = "failed"
                        item.error = delete_result.get("error", "Unknown error")
                        operation.progress.failed += 1
                    
                    item.processed_at = datetime.utcnow()
                    operation.progress.processed += 1
                    operation.progress.percentage = (operation.progress.processed / operation.progress.total) * 100
                    
                    # Calculate estimated remaining time
                    elapsed = (datetime.utcnow() - start_time).total_seconds()
                    if operation.progress.processed > 0:
                        avg_time_per_item = elapsed / operation.progress.processed
                        remaining_items = operation.progress.total - operation.progress.processed
                        operation.progress.estimated_remaining_time = avg_time_per_item * remaining_items
                    
                    # Small delay
                    await asyncio.sleep(0.05)
                    
                except Exception as e:
                    logger.error(f"Error deleting item {item.id}: {e}")
                    item.status = "failed"
                    item.error = str(e)
                    item.processed_at = datetime.utcnow()
                    operation.progress.processed += 1
                    operation.progress.failed += 1
                    operation.progress.percentage = (operation.progress.processed / operation.progress.total) * 100
            
            # Operation completed
            operation.status = BulkOperationStatus.COMPLETED if operation.progress.failed == 0 else BulkOperationStatus.PARTIAL
            operation.completed_at = datetime.utcnow()
            
            # Final notification
            await websocket_manager.send_notification(
                NotificationType.BULK_OPERATION,
                f"Bulk delete completed: {operation.progress.successful} successful, {operation.progress.failed} failed",
                user_id=operation.user_id,
                priority=NotificationPriority.HIGH,
                data={
                    "operation_id": operation.id,
                    "status": "completed",
                    "successful": operation.progress.successful,
                    "failed": operation.progress.failed,
                    "total": operation.progress.total
                }
            )
            
            logger.info(f"Bulk delete operation {operation.id} completed: {operation.progress.successful}/{operation.progress.total} successful")
            
        except Exception as e:
            logger.error(f"Error in bulk delete operation {operation.id}: {e}")
            operation.status = BulkOperationStatus.FAILED
            operation.error = str(e)
            operation.completed_at = datetime.utcnow()
            
            await websocket_manager.send_notification(
                NotificationType.BULK_OPERATION,
                f"Bulk delete failed: {str(e)}",
                user_id=operation.user_id,
                priority=NotificationPriority.HIGH,
                data={
                    "operation_id": operation.id,
                    "status": "failed",
                    "error": str(e)
                }
            )
        
        finally:
            # Remove task reference
            if operation.id in self.operation_tasks:
                del self.operation_tasks[operation.id]
    
    async def _notify_progress(self, operation: BulkOperation):
        """Send progress notification for operation."""
        await websocket_manager.send_notification(
            NotificationType.BULK_OPERATION,
            f"Processing {operation.progress.current_item}",
            user_id=operation.user_id,
            priority=NotificationPriority.LOW,
            data={
                "operation_id": operation.id,
                "progress": asdict(operation.progress),
                "status": "progress"
            }
        )
    
    def get_operation(self, operation_id: str) -> Optional[Dict[str, Any]]:
        """Get operation status and details."""
        if operation_id not in self.active_operations:
            return None
        
        operation = self.active_operations[operation_id]
        return {
            "id": operation.id,
            "user_id": operation.user_id,
            "operation_type": operation.operation_type.value,
            "status": operation.status.value,
            "progress": asdict(operation.progress),
            "created_at": operation.created_at.isoformat(),
            "started_at": operation.started_at.isoformat() if operation.started_at else None,
            "completed_at": operation.completed_at.isoformat() if operation.completed_at else None,
            "error": operation.error,
            "items_summary": {
                "total": len(operation.items),
                "pending": len([i for i in operation.items if i.status == "pending"]),
                "processing": len([i for i in operation.items if i.status == "processing"]),
                "completed": len([i for i in operation.items if i.status == "completed"]),
                "failed": len([i for i in operation.items if i.status == "failed"])
            }
        }
    
    def get_operation_items(self, operation_id: str, limit: int = 100, offset: int = 0) -> Optional[List[Dict[str, Any]]]:
        """Get operation items with pagination."""
        if operation_id not in self.active_operations:
            return None
        
        operation = self.active_operations[operation_id]
        items = operation.items[offset:offset + limit]
        
        return [
            {
                "id": item.id,
                "status": item.status,
                "data": item.data,
                "result": item.result,
                "error": item.error,
                "processed_at": item.processed_at.isoformat() if item.processed_at else None
            }
            for item in items
        ]
    
    async def cancel_operation(self, operation_id: str) -> bool:
        """Cancel a running operation."""
        if operation_id not in self.active_operations:
            return False
        
        operation = self.active_operations[operation_id]
        
        if operation.status != BulkOperationStatus.RUNNING:
            return False
        
        # Cancel the task
        if operation_id in self.operation_tasks:
            task = self.operation_tasks[operation_id]
            task.cancel()
            del self.operation_tasks[operation_id]
        
        # Update operation status
        operation.status = BulkOperationStatus.CANCELLED
        operation.completed_at = datetime.utcnow()
        
        # Notify cancellation
        await websocket_manager.send_notification(
            NotificationType.BULK_OPERATION,
            "Bulk operation cancelled",
            user_id=operation.user_id,
            priority=NotificationPriority.NORMAL,
            data={
                "operation_id": operation_id,
                "status": "cancelled"
            }
        )
        
        logger.info(f"Cancelled bulk operation {operation_id}")
        return True
    
    def cleanup_completed_operations(self, max_age_hours: int = 24):
        """Clean up old completed operations."""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for operation_id, operation in self.active_operations.items():
            if (operation.status in [BulkOperationStatus.COMPLETED, BulkOperationStatus.FAILED, BulkOperationStatus.CANCELLED] and
                operation.completed_at and operation.completed_at.timestamp() < cutoff_time):
                to_remove.append(operation_id)
        
        for operation_id in to_remove:
            del self.active_operations[operation_id]
            logger.info(f"Cleaned up old operation {operation_id}")
        
        return len(to_remove)
    
    def get_user_operations(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get operations for a specific user."""
        user_operations = []
        
        for operation in self.active_operations.values():
            if operation.user_id == user_id:
                user_operations.append({
                    "id": operation.id,
                    "operation_type": operation.operation_type.value,
                    "status": operation.status.value,
                    "progress": asdict(operation.progress),
                    "created_at": operation.created_at.isoformat(),
                    "completed_at": operation.completed_at.isoformat() if operation.completed_at else None
                })
        
        # Sort by creation date (newest first)
        user_operations.sort(key=lambda x: x["created_at"], reverse=True)
        
        return user_operations[:limit]


# Export bulk operations components
__all__ = [
    "BulkOperationsService",
    "BulkOperationType",
    "BulkOperationStatus",
    "BulkOperation",
    "BulkOperationItem",
    "BulkOperationProgress"
]
