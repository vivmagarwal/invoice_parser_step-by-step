from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class InvoiceStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class InvoiceBase(BaseModel):
    filename: str
    original_filename: str
    file_size: int
    mime_type: str


class InvoiceCreate(InvoiceBase):
    file_path: str
    user_id: int


class InvoiceUpdate(BaseModel):
    status: Optional[InvoiceStatus] = None
    error_message: Optional[str] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[datetime] = None
    vendor_name: Optional[str] = None
    total_amount: Optional[float] = None
    extracted_data: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    id: int
    status: InvoiceStatus
    error_message: Optional[str]
    invoice_number: Optional[str]
    invoice_date: Optional[datetime]
    vendor_name: Optional[str]
    total_amount: Optional[float]
    extracted_data: Optional[str]
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InvoiceList(BaseModel):
    invoices: list[InvoiceResponse]
    total: int