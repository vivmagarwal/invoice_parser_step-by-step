from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
import json
from datetime import datetime

from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate
from app.services.ai_service import ai_service


class InvoiceService:
    """Service for managing invoices."""

    @staticmethod
    async def create_invoice(
        db: AsyncSession,
        invoice_data: InvoiceCreate
    ) -> Invoice:
        """Create a new invoice record."""
        invoice = Invoice(**invoice_data.model_dump())
        db.add(invoice)
        await db.commit()
        await db.refresh(invoice)
        return invoice

    @staticmethod
    async def get_invoice(
        db: AsyncSession,
        invoice_id: int,
        user_id: Optional[int] = None
    ) -> Optional[Invoice]:
        """Get a single invoice by ID."""
        query = select(Invoice).where(Invoice.id == invoice_id)
        if user_id:
            query = query.where(Invoice.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_invoices(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Invoice]:
        """Get all invoices for a user."""
        query = (
            select(Invoice)
            .where(Invoice.user_id == user_id)
            .order_by(Invoice.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update_invoice(
        db: AsyncSession,
        invoice_id: int,
        update_data: InvoiceUpdate,
        user_id: Optional[int] = None
    ) -> Optional[Invoice]:
        """Update an invoice."""
        invoice = await InvoiceService.get_invoice(db, invoice_id, user_id)
        if not invoice:
            return None

        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(invoice, field, value)

        await db.commit()
        await db.refresh(invoice)
        return invoice

    @staticmethod
    async def delete_invoice(
        db: AsyncSession,
        invoice_id: int,
        user_id: Optional[int] = None
    ) -> bool:
        """Delete an invoice."""
        invoice = await InvoiceService.get_invoice(db, invoice_id, user_id)
        if not invoice:
            return False

        await db.delete(invoice)
        await db.commit()
        return True

    @staticmethod
    async def count_user_invoices(
        db: AsyncSession,
        user_id: int
    ) -> int:
        """Count total invoices for a user."""
        query = select(Invoice).where(Invoice.user_id == user_id)
        result = await db.execute(query)
        return len(result.scalars().all())

    @staticmethod
    async def process_invoice(
        db: AsyncSession,
        invoice_id: int,
        user_id: int
    ) -> Invoice:
        """Process an invoice with AI to extract data."""
        # Get the invoice
        invoice = await InvoiceService.get_invoice(db, invoice_id, user_id)
        if not invoice:
            raise HTTPException(status_code=404, detail="Invoice not found")

        if invoice.status != InvoiceStatus.pending:
            raise HTTPException(
                status_code=400,
                detail=f"Invoice is already {invoice.status}"
            )

        try:
            # Update status to processing
            invoice.status = InvoiceStatus.processing
            await db.commit()

            # Extract data using AI
            invoice_data = await ai_service.extract_invoice_data(
                invoice.file_path,
                invoice.file_type
            )

            # Store extracted data
            invoice.extracted_data = invoice_data.model_dump_json()
            invoice.status = InvoiceStatus.completed
            invoice.processed_at = datetime.utcnow()

            # Extract key fields for quick access
            extracted = invoice_data.model_dump()
            invoice.vendor_name = extracted.get("vendor_name")
            invoice.total_amount = extracted.get("total_amount")
            invoice.invoice_date = extracted.get("invoice_date")
            invoice.currency = extracted.get("currency", "USD")

            await db.commit()
            await db.refresh(invoice)
            return invoice

        except Exception as e:
            # Update status to failed
            invoice.status = InvoiceStatus.failed
            invoice.error_message = str(e)
            await db.commit()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process invoice: {str(e)}"
            )