"""
Invoice Processing Routes

Handles invoice upload, processing, and database operations.
"""
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
from app.models.schemas import (
    InvoiceDataSchema, ParseResponseSchema, SaveResponseSchema
)
from app.models.database import UserModel
from app.api.dependencies import get_invoice_service, get_database_service
from app.api.routes.auth import get_current_user
from app.services.invoice_service import InvoiceService
from app.services.file_service import FileService
from app.services.database_service import DatabaseService

router = APIRouter(tags=["invoices"])


def get_file_service() -> FileService:
    """Dependency to get file service instance."""
    return FileService()


@router.get("/supported-formats")
async def get_supported_formats():
    """Get information about supported file formats and recommendations."""
    settings = get_settings()
    
    return {
        "supported_formats": [
            {
                "type": "JPEG/JPG",
                "mime_types": ["image/jpeg", "image/jpg"],
                "max_size": f"{settings.MAX_FILE_SIZE // (1024*1024)}MB",
                "recommended": True
            },
            {
                "type": "PNG", 
                "mime_types": ["image/png"],
                "max_size": f"{settings.MAX_FILE_SIZE // (1024*1024)}MB",
                "recommended": True
            },
            {
                "type": "WEBP",
                "mime_types": ["image/webp"], 
                "max_size": f"{settings.MAX_FILE_SIZE // (1024*1024)}MB",
                "recommended": False
            }
        ],
        "recommendations": [
            "Use high-resolution images (minimum 300 DPI)",
            "Ensure good lighting and minimal shadows",
            "Keep text clearly visible and unobstructed",
            "JPEG format provides best balance of quality and file size"
        ]
    }


@router.post("/parse-invoice", response_model=ParseResponseSchema)
async def parse_invoice(
    file: UploadFile = File(...),
    current_user: UserModel = Depends(get_current_user),
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    """
    Parse an uploaded invoice image and extract structured data.
    
    Supports: JPG, JPEG, PNG, WEBP
    Returns: Structured JSON data following Indian GST invoice standards
    """
    try:
        # Read file data
        file_data = await file.read()
        content_type = file.content_type or "application/octet-stream"
        filename = file.filename or "unknown"
        
        # Validate file
        is_valid, error_message = invoice_service.validate_file(
            file_data, content_type
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Process invoice
        result = await invoice_service.process_invoice(
            file_data, content_type, filename
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/save-invoice", response_model=SaveResponseSchema)
async def save_invoice_to_database(
    invoice_data: InvoiceDataSchema,
    current_user: UserModel = Depends(get_current_user),
    invoice_service: InvoiceService = Depends(get_invoice_service)
):
    """
    Save extracted invoice data to PostgreSQL database.
    
    Args:
        invoice_data: InvoiceDataSchema with extracted invoice information
        
    Returns:
        SaveResponseSchema with success status and invoice ID or error details
    """
    try:
        # CRITICAL DEBUG: Log the current user info
        logger.error(f"🚨 CRITICAL DEBUG - API save_invoice_to_database called")
        logger.error(f"🚨 CRITICAL DEBUG - current_user.id: {current_user.id}")
        logger.error(f"🚨 CRITICAL DEBUG - current_user.email: {current_user.email}")
        logger.error(f"🚨 CRITICAL DEBUG - Invoice number from request: {invoice_data.invoice_number}")
        
        # Save using invoice service
        result = invoice_service.save_invoice(invoice_data, str(current_user.id))
        
        # Handle specific error cases
        if not result.success and result.duplicate:
            # Return 409 for duplicates but don't raise exception
            # Client can handle this gracefully
            pass
        elif not result.success:
            # For other errors, we might want to return 500
            raise HTTPException(
                status_code=500,
                detail=result.error or "Failed to save invoice"
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/process-and-save", response_model=dict)
async def process_and_save_invoice(
    file: UploadFile = File(...),
    auto_save: bool = True,
    current_user: UserModel = Depends(get_current_user),
    invoice_service: InvoiceService = Depends(get_invoice_service),
    file_service: FileService = Depends(get_file_service)
):
    """
    Complete pipeline: save file, process invoice, and optionally save to database.
    
    This endpoint combines file saving, parsing and database saving in a single operation.
    """
    try:
        # CRITICAL DEBUG: Log the current user info for process-and-save
        logger.error(f"🚨 CRITICAL DEBUG - API process_and_save_invoice called")
        logger.error(f"🚨 CRITICAL DEBUG - current_user.id: {current_user.id}")
        logger.error(f"🚨 CRITICAL DEBUG - current_user.email: {current_user.email}")
        logger.error(f"🚨 CRITICAL DEBUG - File name: {file.filename}")
        
        # First, save the uploaded file
        file_id, file_info = await file_service.save_uploaded_file(file, str(current_user.id))
        
        # Read file data for processing
        file_data = await file.read()
        content_type = file.content_type or "application/octet-stream"
        filename = file.filename or "unknown"
        
        # Validate file
        is_valid, error_message = invoice_service.validate_file(
            file_data, content_type
        )
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Process and optionally save with file information
        parse_result, save_result = await invoice_service.process_and_save_invoice(
            file_data, content_type, filename, auto_save, str(current_user.id), 
            file_id=file_id, original_filename=filename
        )
        
        return {
            "parse_result": parse_result,
            "save_result": save_result,
            "pipeline_success": parse_result.success and (not auto_save or save_result.success)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pipeline error: {str(e)}"
        )


@router.get("/invoices/{invoice_id}")
async def get_invoice_details(
    invoice_id: str,
    current_user: UserModel = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Get complete invoice details with all relationships.
    
    Returns detailed invoice information including:
    - Basic invoice data (number, date, amounts)
    - Vendor and customer information with addresses
    - Complete line items with descriptions and amounts
    - Tax calculation breakdown
    - File attachment information
    """
    try:
        invoice = db_service.get_complete_invoice_details(
            invoice_id=invoice_id,
            user_id=str(current_user.id)
        )
        
        if not invoice:
            raise HTTPException(
                status_code=404,
                detail="Invoice not found or access denied"
            )
        
        return {
            "success": True,
            "data": invoice
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve invoice details: {str(e)}"
        )
