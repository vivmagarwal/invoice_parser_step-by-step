"""
SQLAlchemy Database Models

These models define the database schema and relationships
for persistent storage of invoice data.
"""
from sqlalchemy import Column, String, Text, DECIMAL, Integer, DateTime, ForeignKey, Enum, Index, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

Base = declarative_base()


class UserModel(Base):
    """Users table - stores user authentication and profile information."""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)  # Full name of the user
    email = Column(String(320), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    invoices = relationship("InvoiceModel", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"


class AddressType(enum.Enum):
    """Enumeration for address types."""
    billing = "billing"
    shipping = "shipping"


class ExtractionConfidence(enum.Enum):
    """Enumeration for AI extraction confidence levels."""
    low = "low"
    medium = "medium"
    high = "high"


class CompanyModel(Base):
    """Companies table - stores both vendors and customers."""
    __tablename__ = "companies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_name = Column(String(500), nullable=False)  # Increased for long company names
    gstin = Column(String(15), nullable=True)  # GST Identification Number
    phone = Column(String(100), nullable=True)  # Increased for multiple phone numbers
    email = Column(String(320), nullable=True)  # Standard email max length
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    addresses = relationship("AddressModel", back_populates="company", cascade="all, delete-orphan")
    vendor_invoices = relationship("InvoiceModel", foreign_keys="InvoiceModel.vendor_id", back_populates="vendor")
    customer_invoices = relationship("InvoiceModel", foreign_keys="InvoiceModel.customer_id", back_populates="customer")
    
    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.company_name}', gstin='{self.gstin}')>"


class AddressModel(Base):
    """Addresses table - linked to companies."""
    __tablename__ = "addresses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)
    street = Column(String(500), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    country = Column(String(100), nullable=True)
    pincode = Column(String(10), nullable=True)
    address_type = Column(Enum(AddressType), default=AddressType.billing)
    
    # Relationships
    company = relationship("CompanyModel", back_populates="addresses")
    
    def __repr__(self):
        return f"<Address(id={self.id}, company_id={self.company_id}, type={self.address_type})>"


class InvoiceModel(Base):
    """Main invoices table."""
    __tablename__ = "invoices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_number = Column(String(100), unique=True, nullable=True)
    invoice_date = Column(String(20), nullable=True)  # Store as string to match Pydantic model
    due_date = Column(String(20), nullable=True)
    currency = Column(String(10), default="INR")
    gross_amount = Column(DECIMAL(15, 2), nullable=True)
    net_amount = Column(DECIMAL(15, 2), nullable=True)
    amount_in_words = Column(Text, nullable=True)
    qr_code_data = Column(Text, nullable=True)
    extraction_confidence = Column(Enum(ExtractionConfidence), default=ExtractionConfidence.medium)
    raw_text = Column(Text, nullable=True)
    
    # File references
    original_file_id = Column(String(255), nullable=True)  # Reference to uploaded file
    original_filename = Column(String(255), nullable=True)  # Original filename
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    vendor = relationship("CompanyModel", foreign_keys=[vendor_id], back_populates="vendor_invoices")
    customer = relationship("CompanyModel", foreign_keys=[customer_id], back_populates="customer_invoices")
    user = relationship("UserModel", back_populates="invoices")
    line_items = relationship("LineItemModel", back_populates="invoice", cascade="all, delete-orphan")
    tax_calculation = relationship("TaxCalculationModel", back_populates="invoice", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', amount={self.net_amount})>"


class LineItemModel(Base):
    """Invoice line items table."""
    __tablename__ = "line_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False)
    serial_number = Column(Integer, nullable=True)
    description = Column(Text, nullable=False)
    hsn_code = Column(String(50), nullable=True)  # Harmonized System of Nomenclature - increased for longer codes
    quantity = Column(DECIMAL(10, 3), nullable=True)
    unit = Column(String(50), nullable=True)  # Increased for longer unit descriptions
    rate = Column(DECIMAL(15, 2), nullable=True)
    amount = Column(DECIMAL(15, 2), nullable=True)
    
    # Relationships
    invoice = relationship("InvoiceModel", back_populates="line_items")
    
    def __repr__(self):
        return f"<LineItem(id={self.id}, invoice_id={self.invoice_id}, description='{self.description[:30]}...')>"


class TaxCalculationModel(Base):
    """Tax calculations table - one-to-one with invoices."""
    __tablename__ = "tax_calculations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("invoices.id"), nullable=False, unique=True)
    taxable_amount = Column(DECIMAL(15, 2), nullable=True)
    cgst_rate = Column(DECIMAL(5, 2), nullable=True)  # Central GST rate
    cgst_amount = Column(DECIMAL(15, 2), nullable=True)
    sgst_rate = Column(DECIMAL(5, 2), nullable=True)  # State GST rate
    sgst_amount = Column(DECIMAL(15, 2), nullable=True)
    igst_rate = Column(DECIMAL(5, 2), nullable=True)  # Integrated GST rate
    igst_amount = Column(DECIMAL(15, 2), nullable=True)
    total_tax = Column(DECIMAL(15, 2), nullable=True)
    
    # Relationships
    invoice = relationship("InvoiceModel", back_populates="tax_calculation")
    
    def __repr__(self):
        return f"<TaxCalculation(id={self.id}, invoice_id={self.invoice_id}, total_tax={self.total_tax})>"


# Performance Indexes - Enhanced for common query patterns

# Single column indexes (existing)
Index('idx_invoices_number', InvoiceModel.invoice_number)
Index('idx_invoices_date', InvoiceModel.invoice_date)
Index('idx_invoices_user', InvoiceModel.user_id)
Index('idx_companies_gstin', CompanyModel.gstin)
Index('idx_line_items_invoice', LineItemModel.invoice_id)
Index('idx_addresses_company', AddressModel.company_id)
Index('idx_users_email', UserModel.email)

# Composite indexes for common query patterns
Index('idx_invoices_user_date', InvoiceModel.user_id, InvoiceModel.created_at.desc())
Index('idx_invoices_user_number', InvoiceModel.user_id, InvoiceModel.invoice_number)
Index('idx_invoices_user_amount', InvoiceModel.user_id, InvoiceModel.net_amount)
Index('idx_companies_gstin_name', CompanyModel.gstin, CompanyModel.company_name)
Index('idx_invoices_vendor_date', InvoiceModel.vendor_id, InvoiceModel.created_at.desc())
Index('idx_invoices_customer_date', InvoiceModel.customer_id, InvoiceModel.created_at.desc())
Index('idx_invoices_file_user', InvoiceModel.original_file_id, InvoiceModel.user_id)

# Partial indexes for specific conditions
Index('idx_invoices_active_files', InvoiceModel.user_id, InvoiceModel.original_file_id, 
      postgresql_where=InvoiceModel.original_file_id.isnot(None))
Index('idx_invoices_with_amounts', InvoiceModel.user_id, InvoiceModel.net_amount,
      postgresql_where=InvoiceModel.net_amount.isnot(None))

# Full-text search indexes for text fields (PostgreSQL specific)
Index('idx_invoices_text_search', InvoiceModel.raw_text, postgresql_using='gin',
      postgresql_ops={'raw_text': 'gin_trgm_ops'})
Index('idx_companies_name_search', CompanyModel.company_name, postgresql_using='gin',
      postgresql_ops={'company_name': 'gin_trgm_ops'})
