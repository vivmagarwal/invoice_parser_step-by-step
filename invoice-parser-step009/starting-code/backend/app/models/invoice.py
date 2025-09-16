from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class InvoiceStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)

    # File information
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    mime_type = Column(String, nullable=False)

    # Processing status
    status = Column(Enum(InvoiceStatus), default=InvoiceStatus.UPLOADED, nullable=False)
    error_message = Column(Text, nullable=True)

    # Extracted data (will be populated after AI processing)
    invoice_number = Column(String, nullable=True)
    invoice_date = Column(DateTime, nullable=True)
    vendor_name = Column(String, nullable=True)
    total_amount = Column(Float, nullable=True)
    extracted_data = Column(Text, nullable=True)  # JSON string of all extracted data

    # Ownership
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="invoices")