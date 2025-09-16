from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.models.invoice import Invoice
from app.schemas.invoice import InvoiceResponse, InvoiceList, InvoiceCreate
from app.services.file_service import FileService
from app.services.invoice_service import InvoiceService

router = APIRouter(prefix="/api/invoices", tags=["invoices"])


@router.post("/upload", response_model=InvoiceResponse)
async def upload_invoice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an invoice file.

    - Accepts PDF, JPG, JPEG, PNG files
    - Maximum file size: 10MB
    - File is saved to user-specific directory
    - Invoice metadata is stored in database
    """
    try:
        # Save file to disk
        file_info = await FileService.save_file(file, current_user.id)

        # Create invoice record
        invoice_data = InvoiceCreate(
            **file_info,
            user_id=current_user.id
        )
        invoice = await InvoiceService.create_invoice(db, invoice_data)

        return invoice

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload invoice: {str(e)}"
        )


@router.get("/", response_model=InvoiceList)
async def get_invoices(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all invoices for the current user."""
    invoices = await InvoiceService.get_user_invoices(
        db, current_user.id, skip, limit
    )
    total = await InvoiceService.count_user_invoices(db, current_user.id)

    return InvoiceList(invoices=invoices, total=total)


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific invoice."""
    invoice = await InvoiceService.get_invoice(
        db, invoice_id, current_user.id
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    return invoice


@router.post("/{invoice_id}/process", response_model=InvoiceResponse)
async def process_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process an invoice with AI to extract data.

    - Uses Gemini AI to analyze the invoice
    - Extracts vendor info, customer info, line items, totals
    - Updates invoice status and stores extracted data
    - Returns the processed invoice with extracted data
    """
    try:
        invoice = await InvoiceService.process_invoice(
            db, invoice_id, current_user.id
        )
        return invoice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process invoice: {str(e)}"
        )


@router.delete("/{invoice_id}")
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an invoice."""
    # Get invoice first to get file path
    invoice = await InvoiceService.get_invoice(
        db, invoice_id, current_user.id
    )

    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )

    # Delete file from disk
    FileService.delete_file(invoice.file_path)

    # Delete invoice record
    await InvoiceService.delete_invoice(db, invoice_id, current_user.id)

    return {"message": "Invoice deleted successfully"}