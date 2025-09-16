"""
Bulk Operations API Routes

Provides endpoints for bulk processing operations including
bulk upload, delete, and batch processing with real-time progress tracking.
"""
import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.api.routes.auth import get_current_user
from app.core.logging_config import performance_monitor
from app.models.database import UserModel
from app.models.api_responses import success_response, error_response
from app.services.bulk_operations_service import (
    BulkOperationsService,
    BulkOperationType,
    BulkOperationStatus
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["bulk"])


# Pydantic models
class BulkDeleteRequest(BaseModel):
    """Request model for bulk delete operation."""
    invoice_ids: List[str] = Field(..., description="List of invoice IDs to delete")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")


class BulkOperationResponse(BaseModel):
    """Response model for bulk operations."""
    operation_id: str
    message: str


def get_bulk_service() -> BulkOperationsService:
    """Dependency to get bulk operations service instance."""
    return BulkOperationsService()


@router.post("/bulk/upload")
@performance_monitor("api", "bulk_upload")
async def bulk_upload_invoices(
    files: List[UploadFile] = File(..., description="Invoice files to process"),
    auto_start: bool = Form(True, description="Automatically start processing"),
    metadata: Optional[str] = Form(None, description="JSON metadata for the operation"),
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Upload and process multiple invoice files in bulk.
    
    Features:
    - Supports multiple file formats (PNG, JPG, PDF)
    - Real-time progress tracking via WebSocket
    - Automatic or manual processing start
    - Comprehensive error handling per file
    - Metadata support for operation tracking
    
    Returns operation ID for tracking progress.
    """
    try:
        # Validate files
        if not files:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No files provided"
            )
        
        if len(files) > 100:  # Reasonable limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many files. Maximum 100 files per batch."
            )
        
        # Process metadata
        operation_metadata = {}
        if metadata:
            try:
                import json
                operation_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                logger.warning("Invalid metadata JSON provided")
        
        # Prepare files data
        files_data = []
        total_size = 0
        
        for file in files:
            # Read file data
            file_data = await file.read()
            file_size = len(file_data)
            total_size += file_size
            
            # Size validation per file (10MB limit)
            if file_size > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} is too large. Maximum size is 10MB."
                )
            
            # Content type validation
            allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'application/pdf']
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File {file.filename} has unsupported type {file.content_type}"
                )
            
            files_data.append({
                "data": file_data,
                "content_type": file.content_type,
                "filename": file.filename
            })
        
        # Total size validation (100MB limit for batch)
        if total_size > 100 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Total batch size exceeds 100MB limit"
            )
        
        # Create bulk operation
        operation_metadata.update({
            "total_files": len(files),
            "total_size": total_size,
            "file_types": list(set(f["content_type"] for f in files_data))
        })
        
        operation_id = await bulk_service.create_bulk_upload_operation(
            user_id=str(current_user.id),
            files_data=files_data,
            metadata=operation_metadata
        )
        
        # Start operation if requested
        if auto_start:
            started = await bulk_service.start_operation(operation_id)
            if not started:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to start bulk operation"
                )
        
        return success_response(
            data={
                "operation_id": operation_id,
                "total_files": len(files),
                "auto_started": auto_start,
                "estimated_time": len(files) * 10  # Rough estimate: 10 seconds per file
            },
            message=f"Bulk upload operation created with {len(files)} files" + 
                   (" and started" if auto_start else "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bulk upload operation"
        )


@router.post("/bulk/delete")
@performance_monitor("api", "bulk_delete")
async def bulk_delete_invoices(
    delete_request: BulkDeleteRequest,
    auto_start: bool = Query(True, description="Automatically start processing"),
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Delete multiple invoices in bulk.
    
    Features:
    - Batch deletion with progress tracking
    - Real-time status updates via WebSocket
    - Individual item error handling
    - Rollback protection (failed items remain)
    
    Returns operation ID for tracking progress.
    """
    try:
        if not delete_request.invoice_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No invoice IDs provided"
            )
        
        if len(delete_request.invoice_ids) > 1000:  # Reasonable limit
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many invoices. Maximum 1000 invoices per batch."
            )
        
        # Create bulk delete operation
        operation_id = await bulk_service.create_bulk_delete_operation(
            user_id=str(current_user.id),
            invoice_ids=delete_request.invoice_ids,
            metadata=delete_request.metadata
        )
        
        # Start operation if requested
        if auto_start:
            started = await bulk_service.start_operation(operation_id)
            if not started:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to start bulk delete operation"
                )
        
        return success_response(
            data={
                "operation_id": operation_id,
                "total_invoices": len(delete_request.invoice_ids),
                "auto_started": auto_start
            },
            message=f"Bulk delete operation created for {len(delete_request.invoice_ids)} invoices" +
                   (" and started" if auto_start else "")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in bulk delete: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create bulk delete operation"
        )


@router.post("/bulk/operations/{operation_id}/start")
@performance_monitor("api", "start_bulk_operation")
async def start_bulk_operation(
    operation_id: str,
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Start a pending bulk operation.
    
    Useful for operations created with auto_start=False
    or for retrying failed operations.
    """
    try:
        # Verify operation exists and belongs to user
        operation = bulk_service.get_operation(operation_id)
        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation not found"
            )
        
        if operation["user_id"] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this operation"
            )
        
        # Start operation
        started = await bulk_service.start_operation(operation_id)
        if not started:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operation cannot be started (may already be running or completed)"
            )
        
        return success_response(
            data={"operation_id": operation_id},
            message="Bulk operation started successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting bulk operation {operation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start bulk operation"
        )


@router.post("/bulk/operations/{operation_id}/cancel")
@performance_monitor("api", "cancel_bulk_operation")
async def cancel_bulk_operation(
    operation_id: str,
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Cancel a running bulk operation.
    
    Stops processing of remaining items while preserving
    results of already processed items.
    """
    try:
        # Verify operation exists and belongs to user
        operation = bulk_service.get_operation(operation_id)
        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation not found"
            )
        
        if operation["user_id"] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this operation"
            )
        
        # Cancel operation
        cancelled = await bulk_service.cancel_operation(operation_id)
        if not cancelled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Operation cannot be cancelled (may not be running)"
            )
        
        return success_response(
            data={"operation_id": operation_id},
            message="Bulk operation cancelled successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling bulk operation {operation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel bulk operation"
        )


@router.get("/bulk/operations/{operation_id}")
@performance_monitor("api", "get_bulk_operation")
async def get_bulk_operation_status(
    operation_id: str,
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Get detailed status and progress of a bulk operation.
    
    Returns:
    - Operation metadata
    - Current progress
    - Summary statistics
    - Error information if applicable
    """
    try:
        operation = bulk_service.get_operation(operation_id)
        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation not found"
            )
        
        if operation["user_id"] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this operation"
            )
        
        return success_response(
            data=operation,
            message="Operation status retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bulk operation status {operation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve operation status"
        )


@router.get("/bulk/operations/{operation_id}/items")
@performance_monitor("api", "get_bulk_operation_items")
async def get_bulk_operation_items(
    operation_id: str,
    limit: int = Query(100, ge=1, le=500, description="Number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Get detailed items from a bulk operation with pagination.
    
    Returns individual item status, results, and errors.
    Useful for debugging failed operations or viewing detailed results.
    """
    try:
        # Verify operation exists and belongs to user
        operation = bulk_service.get_operation(operation_id)
        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation not found"
            )
        
        if operation["user_id"] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this operation"
            )
        
        # Get items
        items = bulk_service.get_operation_items(operation_id, limit, offset)
        if items is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation items not found"
            )
        
        return success_response(
            data={
                "items": items,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": operation["items_summary"]["total"],
                    "returned": len(items)
                }
            },
            message=f"Retrieved {len(items)} operation items"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting bulk operation items {operation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve operation items"
        )


@router.get("/bulk/operations")
@performance_monitor("api", "get_user_bulk_operations")
async def get_user_bulk_operations(
    limit: int = Query(50, ge=1, le=100, description="Number of operations to return"),
    operation_type: Optional[BulkOperationType] = Query(None, description="Filter by operation type"),
    status: Optional[BulkOperationStatus] = Query(None, description="Filter by status"),
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Get bulk operations for the current user.
    
    Features:
    - Pagination support
    - Filtering by operation type and status
    - Sorted by creation date (newest first)
    
    Returns summary information for each operation.
    """
    try:
        operations = bulk_service.get_user_operations(str(current_user.id), limit)
        
        # Apply filters
        if operation_type:
            operations = [op for op in operations if op["operation_type"] == operation_type.value]
        
        if status:
            operations = [op for op in operations if op["status"] == status.value]
        
        return success_response(
            data={
                "operations": operations,
                "total": len(operations),
                "filters": {
                    "operation_type": operation_type.value if operation_type else None,
                    "status": status.value if status else None
                }
            },
            message=f"Retrieved {len(operations)} bulk operations"
        )
        
    except Exception as e:
        logger.error(f"Error getting user bulk operations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bulk operations"
        )


@router.delete("/bulk/operations/{operation_id}")
@performance_monitor("api", "delete_bulk_operation")
async def delete_bulk_operation_record(
    operation_id: str,
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Delete a bulk operation record.
    
    Only completed, failed, or cancelled operations can be deleted.
    This removes the operation from the active operations list.
    """
    try:
        # Verify operation exists and belongs to user
        operation = bulk_service.get_operation(operation_id)
        if not operation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operation not found"
            )
        
        if operation["user_id"] != str(current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this operation"
            )
        
        # Check if operation can be deleted
        if operation["status"] in ["pending", "running"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete pending or running operations. Cancel first."
            )
        
        # Delete operation record
        if operation_id in bulk_service.active_operations:
            del bulk_service.active_operations[operation_id]
        
        return success_response(
            data={"operation_id": operation_id},
            message="Bulk operation record deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bulk operation record {operation_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete operation record"
        )


@router.get("/bulk/stats")
@performance_monitor("api", "get_bulk_stats")
async def get_bulk_operation_stats(
    current_user: UserModel = Depends(get_current_user),
    bulk_service: BulkOperationsService = Depends(get_bulk_service)
):
    """
    Get bulk operation statistics for the current user.
    
    Returns:
    - Total operations by type and status
    - Processing statistics
    - Recent activity summary
    """
    try:
        user_operations = bulk_service.get_user_operations(str(current_user.id), 1000)
        
        # Calculate statistics
        stats = {
            "total_operations": len(user_operations),
            "by_type": {},
            "by_status": {},
            "recent_activity": user_operations[:10],  # Last 10 operations
            "processing_stats": {
                "total_items_processed": 0,
                "total_successful": 0,
                "total_failed": 0,
                "success_rate": 0.0
            }
        }
        
        # Count by type and status
        for op in user_operations:
            op_type = op["operation_type"]
            op_status = op["status"]
            
            stats["by_type"][op_type] = stats["by_type"].get(op_type, 0) + 1
            stats["by_status"][op_status] = stats["by_status"].get(op_status, 0) + 1
            
            # Accumulate processing stats
            progress = op.get("progress", {})
            stats["processing_stats"]["total_items_processed"] += progress.get("processed", 0)
            stats["processing_stats"]["total_successful"] += progress.get("successful", 0)
            stats["processing_stats"]["total_failed"] += progress.get("failed", 0)
        
        # Calculate success rate
        total_processed = stats["processing_stats"]["total_items_processed"]
        if total_processed > 0:
            stats["processing_stats"]["success_rate"] = (
                stats["processing_stats"]["total_successful"] / total_processed
            ) * 100
        
        return success_response(
            data=stats,
            message="Bulk operation statistics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting bulk operation stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve bulk operation statistics"
        )
