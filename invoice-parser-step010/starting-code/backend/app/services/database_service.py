"""
Database Service

Handles all database operations for invoice data persistence,
including CRUD operations and business logic for data storage.
"""
import logging
from typing import Optional, Any
import os
from pathlib import Path
import uuid
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import func, and_, or_

from app.core.database import get_db_session
from app.models.database import (
    InvoiceModel, CompanyModel, AddressModel, 
    LineItemModel, TaxCalculationModel, AddressType, ExtractionConfidence
)
from app.models.schemas import InvoiceDataSchema

# Configure logging
logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations."""
    
    def generate_default_invoice_number(self) -> str:
        """Generate a default invoice number in format ip-{uuid}."""
        return f"ip-{str(uuid.uuid4())[:8]}"
    
    def check_duplicate_invoice(self, invoice_number: str, user_id: str = None) -> bool:
        """Check if invoice number already exists in database for this user."""
        if not invoice_number:
            return False
        
        try:
            with get_db_session() as session:
                query = session.query(InvoiceModel).filter(
                    InvoiceModel.invoice_number == invoice_number
                )
                
                # If user_id provided, scope to that user only
                if user_id:
                    query = query.filter(InvoiceModel.user_id == user_id)
                    logger.error(f"🚨 CRITICAL DEBUG - Checking duplicate for user {user_id}, invoice {invoice_number}")
                else:
                    logger.error(f"🚨 WARNING - Checking duplicate globally for invoice {invoice_number}")
                
                existing = query.first()
                is_duplicate = existing is not None
                logger.error(f"🚨 CRITICAL DEBUG - Duplicate check result: {is_duplicate}")
                return is_duplicate
        except Exception as e:
            logger.error(f"Error checking duplicate invoice: {e}")
            return False
    
    def get_or_create_company(self, session, company_info: Any) -> Optional[CompanyModel]:
        """Get existing company or create new one."""
        if not company_info:
            return None
        
        # Handle case where company_name might be missing or empty
        company_name = getattr(company_info, 'company_name', None)
        if not company_name or company_name.strip() == "":
            return None
        
        try:
            # Try to find existing company by GSTIN or name
            query = session.query(CompanyModel)
            
            if hasattr(company_info, 'gstin') and company_info.gstin:
                existing = query.filter(CompanyModel.gstin == company_info.gstin).first()
                if existing:
                    return existing
            
            # If no GSTIN match, try by company name
            existing = query.filter(CompanyModel.company_name == company_name).first()
            if existing:
                return existing
            
            # Create new company
            logger.info(f"Creating new company: {company_name}")
            company = CompanyModel(
                company_name=company_name,
                gstin=getattr(company_info, 'gstin', None),
                phone=getattr(company_info, 'phone', None),
                email=getattr(company_info, 'email', None)
            )
            session.add(company)
            session.flush()  # Get the ID without committing
            logger.info(f"Successfully created company with ID: {company.id}")
            
            # Add address if provided
            if hasattr(company_info, 'address') and company_info.address:
                address = AddressModel(
                    company_id=company.id,
                    street=getattr(company_info.address, 'street', None),
                    city=getattr(company_info.address, 'city', None),
                    state=getattr(company_info.address, 'state', None),
                    country=getattr(company_info.address, 'country', None),
                    pincode=getattr(company_info.address, 'pincode', None),
                    address_type=AddressType.billing
                )
                session.add(address)
            
            logger.info(f"Created new company: {company_name}")
            return company
            
        except Exception as e:
            logger.error(f"Error creating/getting company: {e}")
            raise
    
    def save_invoice_to_db(self, invoice_data: InvoiceDataSchema, user_id: str) -> dict[str, Any]:
        """
        Save complete invoice data to database.
        
        Args:
            invoice_data: Validated invoice data schema
            
        Returns:
            Dictionary with success status and details
        """
        try:
            # CRITICAL DEBUG: Log the user_id being used
            logger.error(f"🚨 CRITICAL DEBUG - save_invoice_to_db called with user_id: {user_id}")
            logger.error(f"🚨 CRITICAL DEBUG - Invoice number: {invoice_data.invoice_number}")
            
            # Generate invoice number if missing for duplicate check
            invoice_number = invoice_data.invoice_number or self.generate_default_invoice_number()
            
            # Check for duplicate (scoped to current user)
            if self.check_duplicate_invoice(invoice_number, user_id):
                return {
                    "success": False,
                    "duplicate": True,
                    "message": f"Invoice {invoice_number} already exists in database",
                    "error": "Duplicate invoice number"
                }
            
            with get_db_session() as session:
                # Get or create vendor company
                logger.info(f"Processing vendor information: {invoice_data.vendor_information}")
                vendor = self.get_or_create_company(session, invoice_data.vendor_information)
                logger.info(f"Vendor result: {vendor.company_name if vendor else 'None'}")
                
                # Get or create customer company
                logger.info(f"Processing customer information: {invoice_data.customer_information}")
                customer = self.get_or_create_company(session, invoice_data.customer_information)
                logger.info(f"Customer result: {customer.company_name if customer else 'None'}")
                
                # Create invoice record (invoice_number already generated above)
                logger.error(f"🚨 CRITICAL DEBUG - Creating invoice with user_id: {user_id}")
                logger.error(f"🚨 CRITICAL DEBUG - Invoice number being saved: {invoice_number}")
                
                invoice = InvoiceModel(
                    invoice_number=invoice_number,
                    invoice_date=invoice_data.invoice_date,
                    due_date=invoice_data.due_date,
                    currency=invoice_data.currency,
                    gross_amount=invoice_data.gross_amount,
                    net_amount=invoice_data.net_amount,
                    amount_in_words=invoice_data.amount_in_words,
                    qr_code_data=invoice_data.qr_code_data,
                    extraction_confidence=ExtractionConfidence(invoice_data.extraction_confidence or "medium"),
                    raw_text=invoice_data.raw_text,
                    original_file_id=invoice_data.original_file_id,
                    original_filename=invoice_data.original_filename,
                    vendor_id=vendor.id if vendor else None,
                    customer_id=customer.id if customer else None,
                    user_id=user_id
                )
                session.add(invoice)
                session.flush()  # Get invoice ID
                
                # Create line items
                for item_data in invoice_data.line_items:
                    line_item = LineItemModel(
                        invoice_id=invoice.id,
                        serial_number=item_data.serial_number,
                        description=item_data.description,
                        hsn_code=item_data.hsn_code,
                        quantity=item_data.quantity,
                        unit=item_data.unit,
                        rate=item_data.rate,
                        amount=item_data.amount
                    )
                    session.add(line_item)
                
                # Create tax calculation if provided
                if invoice_data.tax_calculations:
                    tax_calc = TaxCalculationModel(
                        invoice_id=invoice.id,
                        taxable_amount=invoice_data.tax_calculations.taxable_amount,
                        cgst_rate=invoice_data.tax_calculations.cgst_rate,
                        cgst_amount=invoice_data.tax_calculations.cgst_amount,
                        sgst_rate=invoice_data.tax_calculations.sgst_rate,
                        sgst_amount=invoice_data.tax_calculations.sgst_amount,
                        igst_rate=invoice_data.tax_calculations.igst_rate,
                        igst_amount=invoice_data.tax_calculations.igst_amount,
                        total_tax=invoice_data.tax_calculations.total_tax
                    )
                    session.add(tax_calc)
                
                # Commit all changes
                session.commit()
                
                logger.info(f"Successfully saved invoice {invoice_data.invoice_number} with ID {invoice.id}")
                
                return {
                    "success": True,
                    "message": "Invoice saved successfully",
                    "invoice_id": str(invoice.id),
                    "duplicate": False
                }
                
        except IntegrityError as e:
            logger.error(f"Database integrity error: {e}")
            return {
                "success": False,
                "error": "Database constraint violation - possible duplicate",
                "message": "Failed to save invoice due to data constraints"
            }
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            return {
                "success": False,
                "error": f"Database error: {str(e)}",
                "message": "Failed to save invoice due to database error"
            }
        except Exception as e:
            logger.error(f"Unexpected error saving invoice: {e}")
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "message": "Failed to save invoice due to unexpected error"
            }
    
    def get_invoice_by_id(self, invoice_id: str) -> Optional[dict[str, Any]]:
        """Retrieve invoice by ID."""
        try:
            with get_db_session() as session:
                invoice = session.query(InvoiceModel).filter(InvoiceModel.id == invoice_id).first()
                if invoice:
                    return {
                        "id": str(invoice.id),
                        "invoice_number": invoice.invoice_number,
                        "invoice_date": invoice.invoice_date,
                        "net_amount": float(invoice.net_amount) if invoice.net_amount else None,
                        "total_amount": float(invoice.net_amount) if invoice.net_amount else None,
                        "created_at": invoice.created_at.isoformat()
                    }
                return None
        except Exception as e:
            logger.error(f"Error retrieving invoice {invoice_id}: {e}")
            return None
    
    def get_invoice_stats(self) -> dict[str, Any]:
        """Get basic statistics about stored invoices."""
        try:
            with get_db_session() as session:
                invoice_count = session.query(InvoiceModel).count()
                company_count = session.query(CompanyModel).count()
                
                return {
                    "total_invoices": invoice_count,
                    "total_companies": company_count,
                    "status": "healthy"
                }
        except Exception as e:
            logger.error(f"Error getting invoice stats: {e}")
            return {
                "total_invoices": 0,
                "total_companies": 0,
                "status": "error",
                "error": str(e)
            }
    
    def get_user_invoices(self, user_id: str, page: int = 1, limit: int = 10) -> dict[str, Any]:
        """Get invoices for a specific user with pagination and optimized loading."""
        try:
            # CRITICAL DEBUG: Log the user_id being queried
            logger.error(f"🚨 CRITICAL DEBUG - get_user_invoices called with user_id: {user_id}")
            
            with get_db_session() as session:
                # Calculate offset
                offset = (page - 1) * limit
                
                # Optimized count query using index
                total = session.query(func.count(InvoiceModel.id)).filter(
                    InvoiceModel.user_id == user_id
                ).scalar()
                
                # Get paginated invoices with eager loading of related data
                invoices = session.query(InvoiceModel).options(
                    joinedload(InvoiceModel.vendor),
                    joinedload(InvoiceModel.customer),
                    selectinload(InvoiceModel.line_items),
                    joinedload(InvoiceModel.tax_calculation)
                ).filter(
                    InvoiceModel.user_id == user_id
                ).order_by(InvoiceModel.created_at.desc()).offset(offset).limit(limit).all()
                
                # CRITICAL DEBUG: Log what invoices were found
                logger.error(f"🚨 CRITICAL DEBUG - Found {len(invoices)} invoices for user {user_id}")
                if invoices:
                    invoice_numbers = [inv.invoice_number for inv in invoices]
                    logger.error(f"🚨 CRITICAL DEBUG - Invoice numbers: {invoice_numbers}")
                
                # Convert to dict format
                invoice_list = []
                for invoice in invoices:
                    invoice_list.append({
                        "id": str(invoice.id),
                        "invoice_number": invoice.invoice_number,
                        "invoice_date": invoice.invoice_date,
                        "net_amount": float(invoice.net_amount) if invoice.net_amount else None,
                        "total_amount": float(invoice.net_amount) if invoice.net_amount else None,
                        "currency": invoice.currency,
                        "extraction_confidence": invoice.extraction_confidence,
                        "original_file_id": invoice.original_file_id,
                        "original_filename": invoice.original_filename,
                        "created_at": invoice.created_at.isoformat(),
                        "vendor_name": invoice.vendor.company_name if invoice.vendor else "Unknown Vendor",
                        "customer_name": invoice.customer.company_name if invoice.customer else "Unknown Customer",
                        "line_items_count": len(invoice.line_items) if invoice.line_items else 0,
                        "has_tax_calculation": invoice.tax_calculation is not None
                    })
                
                return {
                    "invoices": invoice_list,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit
                    }
                }
                
        except Exception as e:
            logger.error(f"Error getting user invoices for {user_id}: {e}")
            return {
                "invoices": [],
                "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0}
            }
    
    def delete_user_invoice(self, user_id: str, invoice_id: str) -> dict[str, Any]:
        """Delete a specific invoice for a user and clean up associated files."""
        try:
            with get_db_session() as session:
                invoice = session.query(InvoiceModel).filter(
                    InvoiceModel.id == invoice_id,
                    InvoiceModel.user_id == user_id
                ).first()
                
                if not invoice:
                    return {
                        "success": False,
                        "message": "Invoice not found or access denied"
                    }
                
                # Store file information for cleanup before deleting
                file_id = invoice.original_file_id
                
                # Delete invoice from database (cascade will handle related records)
                session.delete(invoice)
                session.commit()
                
                # Clean up associated file if it exists
                if file_id:
                    try:
                        file_path = Path("uploads") / file_id
                        if file_path.exists():
                            os.remove(file_path)
                            logger.info(f"Deleted file: {file_path}")
                    except Exception as file_error:
                        logger.warning(f"Failed to delete file {file_id}: {file_error}")
                        # Don't fail the whole operation if file cleanup fails
                
                logger.info(f"Deleted invoice {invoice_id} for user {user_id}")
                
                return {
                    "success": True,
                    "message": "Invoice deleted successfully"
                }
                
        except Exception as e:
            logger.error(f"Error deleting invoice {invoice_id} for user {user_id}: {e}")
            return {
                "success": False,
                "message": "Failed to delete invoice",
                "error": str(e)
            }
    
    def search_invoices(
        self, 
        user_id: str, 
        query: str = None, 
        date_from: str = None, 
        date_to: str = None,
        min_amount: float = None,
        max_amount: float = None,
        page: int = 1, 
        limit: int = 10
    ) -> dict[str, Any]:
        """Advanced search for user invoices with filters."""
        try:
            with get_db_session() as session:
                offset = (page - 1) * limit
                
                # Build base query
                base_query = session.query(InvoiceModel).filter(
                    InvoiceModel.user_id == user_id
                )
                
                # Apply filters
                if query:
                    # Search in invoice number, company names, and raw text
                    search_filter = or_(
                        InvoiceModel.invoice_number.ilike(f"%{query}%"),
                        InvoiceModel.raw_text.ilike(f"%{query}%")
                    )
                    
                    # Join with companies for name search
                    base_query = base_query.outerjoin(
                        CompanyModel, 
                        or_(
                            InvoiceModel.vendor_id == CompanyModel.id,
                            InvoiceModel.customer_id == CompanyModel.id
                        )
                    ).filter(
                        or_(
                            search_filter,
                            CompanyModel.company_name.ilike(f"%{query}%")
                        )
                    )
                
                if date_from:
                    base_query = base_query.filter(InvoiceModel.invoice_date >= date_from)
                
                if date_to:
                    base_query = base_query.filter(InvoiceModel.invoice_date <= date_to)
                
                if min_amount is not None:
                    base_query = base_query.filter(InvoiceModel.net_amount >= min_amount)
                
                if max_amount is not None:
                    base_query = base_query.filter(InvoiceModel.net_amount <= max_amount)
                
                # Get total count
                total = base_query.count()
                
                # Get results with eager loading
                invoices = base_query.options(
                    joinedload(InvoiceModel.vendor),
                    joinedload(InvoiceModel.customer)
                ).order_by(
                    InvoiceModel.created_at.desc()
                ).offset(offset).limit(limit).all()
                
                # Convert to dict format
                invoice_list = []
                for invoice in invoices:
                    invoice_list.append({
                        "id": str(invoice.id),
                        "invoice_number": invoice.invoice_number,
                        "invoice_date": invoice.invoice_date,
                        "net_amount": float(invoice.net_amount) if invoice.net_amount else None,
                        "total_amount": float(invoice.net_amount) if invoice.net_amount else None,
                        "currency": invoice.currency,
                        "vendor_name": invoice.vendor.company_name if invoice.vendor else None,
                        "customer_name": invoice.customer.company_name if invoice.customer else None,
                        "extraction_confidence": invoice.extraction_confidence,
                        "original_file_id": invoice.original_file_id,
                        "created_at": invoice.created_at.isoformat()
                    })
                
                return {
                    "invoices": invoice_list,
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total,
                        "pages": (total + limit - 1) // limit
                    },
                    "filters": {
                        "query": query,
                        "date_from": date_from,
                        "date_to": date_to,
                        "min_amount": min_amount,
                        "max_amount": max_amount
                    }
                }
                
        except Exception as e:
            logger.error(f"Error searching invoices for user {user_id}: {e}")
            return {
                "invoices": [],
                "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0},
                "filters": {}
            }
    
    def _serialize_date(self, date_value) -> Optional[str]:
        """Safely serialize date values to ISO format string."""
        if not date_value:
            return None
        
        # If it's already a string, return as-is (assuming it's in valid format)
        if isinstance(date_value, str):
            return date_value
        
        # If it's a datetime object, convert to ISO format
        if isinstance(date_value, datetime):
            return date_value.isoformat()
        
        return None

    def get_complete_invoice_details(self, invoice_id: str, user_id: str) -> Optional[dict]:
        """Get complete invoice details with all relationships."""
        try:
            with get_db_session() as session:
                invoice = session.query(InvoiceModel).options(
                    joinedload(InvoiceModel.vendor).joinedload(CompanyModel.addresses),
                    joinedload(InvoiceModel.customer).joinedload(CompanyModel.addresses),
                    selectinload(InvoiceModel.line_items),
                    joinedload(InvoiceModel.tax_calculation)
                ).filter(
                    InvoiceModel.id == invoice_id,
                    InvoiceModel.user_id == user_id
                ).first()
                
                if not invoice:
                    return None
                
                # Convert to dict with all relationships
                return {
                    "id": str(invoice.id),
                    "invoice_number": invoice.invoice_number,
                    "invoice_date": self._serialize_date(invoice.invoice_date),
                    "due_date": self._serialize_date(invoice.due_date),
                    "currency": invoice.currency,
                    "gross_amount": float(invoice.gross_amount) if invoice.gross_amount else None,
                    "net_amount": float(invoice.net_amount) if invoice.net_amount else None,
                    "total_amount": float(invoice.net_amount) if invoice.net_amount else None,  # For frontend compatibility
                    "amount_in_words": invoice.amount_in_words,
                    "qr_code_data": invoice.qr_code_data,
                    "extraction_confidence": invoice.extraction_confidence.value if invoice.extraction_confidence else "medium",
                    "raw_text": invoice.raw_text,
                    "original_file_id": invoice.original_file_id,
                    "original_filename": invoice.original_filename,
                    "created_at": invoice.created_at.isoformat(),
                    "updated_at": invoice.updated_at.isoformat(),
                    
                    # Vendor information
                    "vendor": {
                        "id": str(invoice.vendor.id) if invoice.vendor else None,
                        "company_name": invoice.vendor.company_name if invoice.vendor else None,
                        "gstin": invoice.vendor.gstin if invoice.vendor else None,
                        "phone": invoice.vendor.phone if invoice.vendor else None,
                        "email": invoice.vendor.email if invoice.vendor else None,
                        "addresses": [
                            {
                                "street": addr.street,
                                "city": addr.city,
                                "state": addr.state,
                                "country": addr.country,
                                "pincode": addr.pincode,
                                "type": addr.address_type.value if addr.address_type else "billing"
                            } for addr in (invoice.vendor.addresses if invoice.vendor else [])
                        ]
                    } if invoice.vendor else None,
                    
                    # Customer information
                    "customer": {
                        "id": str(invoice.customer.id) if invoice.customer else None,
                        "company_name": invoice.customer.company_name if invoice.customer else None,
                        "gstin": invoice.customer.gstin if invoice.customer else None,
                        "phone": invoice.customer.phone if invoice.customer else None,
                        "email": invoice.customer.email if invoice.customer else None,
                        "addresses": [
                            {
                                "street": addr.street,
                                "city": addr.city,
                                "state": addr.state,
                                "country": addr.country,
                                "pincode": addr.pincode,
                                "type": addr.address_type.value if addr.address_type else "billing"
                            } for addr in (invoice.customer.addresses if invoice.customer else [])
                        ]
                    } if invoice.customer else None,
                    
                    # Line items
                    "line_items": [
                        {
                            "id": str(item.id),
                            "serial_number": item.serial_number,
                            "description": item.description,
                            "hsn_code": item.hsn_code,
                            "quantity": float(item.quantity) if item.quantity else None,
                            "unit": item.unit,
                            "rate": float(item.rate) if item.rate else None,
                            "amount": float(item.amount) if item.amount else None
                        } for item in invoice.line_items
                    ],
                    
                    # Tax calculations
                    "tax_calculation": {
                        "taxable_amount": float(invoice.tax_calculation.taxable_amount) if invoice.tax_calculation and invoice.tax_calculation.taxable_amount else None,
                        "cgst_rate": float(invoice.tax_calculation.cgst_rate) if invoice.tax_calculation and invoice.tax_calculation.cgst_rate else None,
                        "cgst_amount": float(invoice.tax_calculation.cgst_amount) if invoice.tax_calculation and invoice.tax_calculation.cgst_amount else None,
                        "sgst_rate": float(invoice.tax_calculation.sgst_rate) if invoice.tax_calculation and invoice.tax_calculation.sgst_rate else None,
                        "sgst_amount": float(invoice.tax_calculation.sgst_amount) if invoice.tax_calculation and invoice.tax_calculation.sgst_amount else None,
                        "igst_rate": float(invoice.tax_calculation.igst_rate) if invoice.tax_calculation and invoice.tax_calculation.igst_rate else None,
                        "igst_amount": float(invoice.tax_calculation.igst_amount) if invoice.tax_calculation and invoice.tax_calculation.igst_amount else None,
                        "total_tax": float(invoice.tax_calculation.total_tax) if invoice.tax_calculation and invoice.tax_calculation.total_tax else None
                    } if invoice.tax_calculation else None
                }
                
        except Exception as e:
            logger.error(f"Error getting complete invoice details: {e}")
            return None
