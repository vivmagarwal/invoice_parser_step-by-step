from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.invoice import Invoice, InvoiceStatus
from app.schemas.invoice import InvoiceCreate, InvoiceUpdate


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