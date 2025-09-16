"""
Pydantic Models (API Schemas)

These models define the structure for API request/response data
and provide automatic validation and serialization.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class LineItemSchema(BaseModel):
    """Schema for invoice line items."""
    serial_number: Optional[int] = None
    description: str
    hsn_code: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    rate: Optional[float] = None
    amount: Optional[float] = None


class AddressSchema(BaseModel):
    """Schema for company addresses."""
    street: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    pincode: Optional[str] = None


class CompanyInfoSchema(BaseModel):
    """Schema for company information (vendors/customers)."""
    company_name: str
    gstin: Optional[str] = None
    address: Optional[AddressSchema] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class TaxCalculationSchema(BaseModel):
    """Schema for tax calculations."""
    taxable_amount: Optional[float] = None
    cgst_rate: Optional[float] = None
    cgst_amount: Optional[float] = None
    sgst_rate: Optional[float] = None
    sgst_amount: Optional[float] = None
    igst_rate: Optional[float] = None
    igst_amount: Optional[float] = None
    total_tax: Optional[float] = None


class InvoiceDataSchema(BaseModel):
    """Schema for complete invoice data."""
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    due_date: Optional[str] = None
    currency: str = "INR"
    vendor_information: Optional[CompanyInfoSchema] = None
    customer_information: Optional[CompanyInfoSchema] = None
    line_items: list[LineItemSchema] = []
    tax_calculations: Optional[TaxCalculationSchema] = None
    gross_amount: Optional[float] = None
    net_amount: Optional[float] = None
    amount_in_words: Optional[str] = None
    qr_code_data: Optional[str] = None
    extraction_confidence: Optional[str] = "medium"
    raw_text: Optional[str] = None
    
    # File references (for enhanced file management)
    original_file_id: Optional[str] = None
    original_filename: Optional[str] = None


class ParseResponseSchema(BaseModel):
    """Schema for invoice parsing API response."""
    success: bool
    data: Optional[InvoiceDataSchema] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None


class SaveResponseSchema(BaseModel):
    """Schema for database save API response."""
    success: bool
    message: str
    invoice_id: Optional[str] = None
    duplicate: Optional[bool] = False
    error: Optional[str] = None


# Authentication Schemas

class UserCreateSchema(BaseModel):
    """Schema for user registration."""
    name: str  # Full name of the user
    email: str  # Using str instead of EmailStr for simplicity
    password: str


class UserSchema(BaseModel):
    """Schema for user information (response)."""
    id: str
    name: str  # Full name of the user
    email: str
    is_active: bool


class UserLoginSchema(BaseModel):
    """Schema for user login."""
    email: str
    password: str


class TokenSchema(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserSchema


class UserInDBSchema(BaseModel):
    """Schema for user data from database."""
    id: str
    name: str  # Changed from username to match UserModel
    email: str
    hashed_password: str
    is_active: bool
    created_at: str


# Export schemas for easy importing
__all__ = [
    "LineItemSchema",
    "AddressSchema", 
    "CompanyInfoSchema",
    "TaxCalculationSchema",
    "InvoiceDataSchema",
    "ParseResponseSchema",
    "SaveResponseSchema",
    # Authentication schemas
    "UserCreateSchema",
    "UserSchema",
    "UserLoginSchema",
    "TokenSchema",
    "UserInDBSchema",
    # Backward compatibility aliases
    "LineItem",
    "Address",
    "CompanyInfo", 
    "TaxCalculation",
    "InvoiceData",
    "ParseResponse",
    "SaveResponse"
]

# Backward compatibility aliases (for gradual migration)
LineItem = LineItemSchema
Address = AddressSchema
CompanyInfo = CompanyInfoSchema
TaxCalculation = TaxCalculationSchema
InvoiceData = InvoiceDataSchema
ParseResponse = ParseResponseSchema
SaveResponse = SaveResponseSchema
