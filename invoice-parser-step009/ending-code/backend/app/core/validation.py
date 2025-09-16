"""
Enhanced Input Validation and Sanitization

Provides comprehensive input validation, sanitization, and security checks
to prevent injection attacks and ensure data integrity.
"""
import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from email_validator import validate_email, EmailNotValidError
from pydantic import BaseModel, field_validator, Field
import bleach

from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Input sanitization utilities."""
    
    # Allowed HTML tags for rich text (if needed)
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
    ALLOWED_ATTRIBUTES = {}
    
    @classmethod
    def sanitize_html(cls, text: str, strip_tags: bool = True) -> str:
        """Sanitize HTML content."""
        if not text:
            return ""
        
        if strip_tags:
            # Remove all HTML tags
            return bleach.clean(text, tags=[], attributes={}, strip=True)
        else:
            # Allow only safe HTML tags
            return bleach.clean(text, tags=cls.ALLOWED_TAGS, attributes=cls.ALLOWED_ATTRIBUTES)
    
    @classmethod
    def sanitize_sql(cls, text: str) -> str:
        """Basic SQL injection prevention."""
        if not text:
            return ""
        
        # Remove common SQL injection patterns
        dangerous_patterns = [
            r"[';\"\\]",  # Quotes and backslashes
            r"--",        # SQL comments
            r"/\*.*?\*/", # Block comments
            r"\b(DROP|DELETE|INSERT|UPDATE|CREATE|ALTER|EXEC|EXECUTE|UNION|SELECT)\b",
        ]
        
        cleaned = text
        for pattern in dangerous_patterns:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        
        return cleaned.strip()
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for safe storage."""
        if not filename:
            return "unnamed_file"
        
        # Remove path separators and dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Limit length
        if len(sanitized) > 255:
            name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
            sanitized = name[:250] + ('.' + ext if ext else '')
        
        return sanitized or "unnamed_file"
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: int = None) -> str:
        """General text sanitization."""
        if not text:
            return ""
        
        # HTML decode and strip tags
        sanitized = html.unescape(text)
        sanitized = cls.sanitize_html(sanitized, strip_tags=True)
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Apply length limit
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rstrip()
        
        return sanitized


class InputValidator:
    """Input validation utilities."""
    
    @staticmethod
    def validate_email_address(email: str) -> str:
        """Validate and normalize email address."""
        if not email:
            raise ValidationException("Email address is required")
        
        try:
            # Use email-validator library for comprehensive validation
            valid = validate_email(email)
            return valid.email
        except EmailNotValidError as e:
            raise ValidationException(f"Invalid email address: {str(e)}")
    
    @staticmethod
    def validate_password(password: str) -> str:
        """Validate password strength."""
        if not password:
            raise ValidationException("Password is required")
        
        if len(password) < 8:
            raise ValidationException("Password must be at least 8 characters long")
        
        if len(password) > 128:
            raise ValidationException("Password must be less than 128 characters")
        
        # Check for required character types
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        missing = []
        if not has_upper:
            missing.append("uppercase letter")
        if not has_lower:
            missing.append("lowercase letter")
        if not has_digit:
            missing.append("digit")
        if not has_special:
            missing.append("special character")
        
        if missing:
            raise ValidationException(f"Password must contain at least one: {', '.join(missing)}")
        
        return password
    
    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """Validate and normalize phone number."""
        if not phone:
            return ""
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Basic length validation
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValidationException("Phone number must be between 10 and 15 digits")
        
        return digits_only
    
    @staticmethod
    def validate_gstin(gstin: str) -> str:
        """Validate Indian GSTIN format."""
        if not gstin:
            return ""
        
        gstin = gstin.upper().strip()
        
        # GSTIN format: 2 digits (state) + 10 chars (PAN) + 1 char (entity) + 1 char (Z) + 1 check digit
        gstin_pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}[Z]{1}[0-9A-Z]{1}$'
        
        if not re.match(gstin_pattern, gstin):
            raise ValidationException("Invalid GSTIN format")
        
        return gstin
    
    @staticmethod
    def validate_amount(amount: Union[str, int, float, Decimal]) -> Decimal:
        """Validate and normalize monetary amount."""
        if amount is None:
            return Decimal('0')
        
        try:
            decimal_amount = Decimal(str(amount))
            
            # Check for reasonable bounds
            if decimal_amount < 0:
                raise ValidationException("Amount cannot be negative")
            
            if decimal_amount > Decimal('999999999.99'):
                raise ValidationException("Amount is too large")
            
            # Round to 2 decimal places
            return decimal_amount.quantize(Decimal('0.01'))
            
        except (InvalidOperation, ValueError):
            raise ValidationException("Invalid amount format")
    
    @staticmethod
    def validate_date_string(date_str: str, format_str: str = "%Y-%m-%d") -> date:
        """Validate and parse date string."""
        if not date_str:
            raise ValidationException("Date is required")
        
        try:
            parsed_date = datetime.strptime(date_str, format_str).date()
            
            # Reasonable date bounds
            if parsed_date < date(1900, 1, 1):
                raise ValidationException("Date is too old")
            
            if parsed_date > date(2100, 12, 31):
                raise ValidationException("Date is too far in the future")
            
            return parsed_date
            
        except ValueError:
            raise ValidationException(f"Invalid date format. Expected format: {format_str}")
    
    @staticmethod
    def validate_file_type(filename: str, allowed_types: List[str]) -> str:
        """Validate file type based on extension."""
        if not filename:
            raise ValidationException("Filename is required")
        
        # Get file extension
        if '.' not in filename:
            raise ValidationException("File must have an extension")
        
        extension = filename.lower().split('.')[-1]
        
        if extension not in [t.lower() for t in allowed_types]:
            raise ValidationException(f"File type '{extension}' not allowed. Allowed types: {', '.join(allowed_types)}")
        
        return extension
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> int:
        """Validate file size."""
        max_bytes = max_size_mb * 1024 * 1024
        
        if file_size <= 0:
            raise ValidationException("File is empty")
        
        if file_size > max_bytes:
            raise ValidationException(f"File size ({file_size / 1024 / 1024:.1f}MB) exceeds maximum allowed size ({max_size_mb}MB)")
        
        return file_size


class SecureValidator(BaseModel):
    """Base model with enhanced validation and sanitization."""
    
    model_config = {
        # Validate all fields, even when not required
        "validate_default": True,
        # Allow population by field name or alias
        "populate_by_name": True,
        # Use enum values
        "use_enum_values": True
    }
    
    @field_validator('*', mode='before')
    @classmethod
    def sanitize_strings(cls, v):
        """Sanitize string inputs."""
        if isinstance(v, str):
            return InputSanitizer.sanitize_text(v, max_length=10000)
        return v


class UserRegistrationValidator(SecureValidator):
    """Validator for user registration data."""
    
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        """Validate user name."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        
        # Remove extra whitespace and limit length
        sanitized = InputSanitizer.sanitize_text(v, max_length=100)
        
        # Check for reasonable content
        if len(sanitized) < 2:
            raise ValueError("Name must be at least 2 characters")
        
        return sanitized
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email address."""
        return InputValidator.validate_email_address(v)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password."""
        return InputValidator.validate_password(v)


class InvoiceDataValidator(SecureValidator):
    """Validator for invoice data."""
    
    invoice_number: Optional[str] = Field(None, max_length=100)
    invoice_date: Optional[str] = None
    vendor_name: Optional[str] = Field(None, max_length=200)
    customer_name: Optional[str] = Field(None, max_length=200)
    net_amount: Optional[Union[str, float, Decimal]] = None
    currency: Optional[str] = Field("INR", max_length=3)
    
    @field_validator('invoice_number')
    @classmethod
    def validate_invoice_number(cls, v):
        """Validate invoice number."""
        if not v:
            return None
        
        sanitized = InputSanitizer.sanitize_text(v, max_length=100)
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        return sanitized
    
    @field_validator('invoice_date')
    @classmethod
    def validate_invoice_date(cls, v):
        """Validate invoice date."""
        if not v:
            return None
        
        # Try multiple date formats
        formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"]
        
        for fmt in formats:
            try:
                return InputValidator.validate_date_string(v, fmt).isoformat()
            except ValidationException:
                continue
        
        raise ValueError("Invalid date format")
    
    @field_validator('vendor_name', 'customer_name')
    @classmethod
    def validate_company_name(cls, v):
        """Validate company names."""
        if not v:
            return None
        
        sanitized = InputSanitizer.sanitize_text(v, max_length=200)
        
        # Additional validation for company names
        if sanitized and len(sanitized) < 2:
            raise ValueError("Company name must be at least 2 characters")
        
        return sanitized
    
    @field_validator('net_amount')
    @classmethod
    def validate_amount(cls, v):
        """Validate monetary amount."""
        if v is None:
            return None
        
        try:
            return float(InputValidator.validate_amount(v))
        except ValidationException as e:
            raise ValueError(str(e))
    
    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        """Validate currency code."""
        if not v:
            return "INR"
        
        # List of common currency codes
        valid_currencies = ['INR', 'USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD']
        
        currency = v.upper().strip()
        
        if currency not in valid_currencies:
            raise ValueError(f"Invalid currency code. Supported: {', '.join(valid_currencies)}")
        
        return currency


# Utility functions for common validations
def validate_and_sanitize_dict(data: Dict[str, Any], validator_class: type) -> Dict[str, Any]:
    """Validate and sanitize dictionary data using a validator class."""
    try:
        validator_instance = validator_class(**data)
        return validator_instance.dict(exclude_unset=True)
    except Exception as e:
        logger.error(f"Validation error: {e}")
        raise ValidationException(f"Validation failed: {str(e)}")


def sanitize_search_query(query: str) -> str:
    """Sanitize search query to prevent injection attacks."""
    if not query:
        return ""
    
    # Basic sanitization
    sanitized = InputSanitizer.sanitize_text(query, max_length=500)
    
    # Remove SQL injection patterns
    sanitized = InputSanitizer.sanitize_sql(sanitized)
    
    # Remove excessive special characters
    sanitized = re.sub(r'[^\w\s\-_.,()]', '', sanitized)
    
    return sanitized.strip()


# Install email-validator if not present
try:
    import email_validator
except ImportError:
    logger.warning("email-validator not installed. Email validation will be basic.")
    
    def validate_email(email: str):
        """Basic email validation fallback."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise EmailNotValidError("Invalid email format")
        return type('ValidatedEmail', (), {'email': email.lower().strip()})()


# Export validation components
__all__ = [
    "InputSanitizer",
    "InputValidator", 
    "SecureValidator",
    "UserRegistrationValidator",
    "InvoiceDataValidator",
    "validate_and_sanitize_dict",
    "sanitize_search_query",
    "ValidationException"
]
