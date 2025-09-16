"""
Advanced Search Service

Provides comprehensive search, filtering, and faceted search capabilities
for invoices and related data with performance optimization.
"""
import logging
from datetime import datetime, date
from typing import Dict, List, Optional, Any, Tuple
from decimal import Decimal
from enum import Enum

from sqlalchemy import func, and_, or_, text, desc, asc
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.dialects.postgresql import to_tsvector, to_tsquery

from app.core.database import get_db_session
from app.core.logging_config import performance_monitor
from app.core.validation import sanitize_search_query
from app.models.database import InvoiceModel, CompanyModel, UserModel, LineItemModel

logger = logging.getLogger(__name__)


class SearchSortOrder(str, Enum):
    """Search result sorting options."""
    RELEVANCE = "relevance"
    DATE_DESC = "date_desc"
    DATE_ASC = "date_asc"
    AMOUNT_DESC = "amount_desc"
    AMOUNT_ASC = "amount_asc"
    INVOICE_NUMBER = "invoice_number"
    VENDOR_NAME = "vendor_name"
    CUSTOMER_NAME = "customer_name"


class SearchScope(str, Enum):
    """Search scope options."""
    ALL = "all"
    INVOICE_NUMBER = "invoice_number"
    VENDOR = "vendor"
    CUSTOMER = "customer"
    DESCRIPTION = "description"
    RAW_TEXT = "raw_text"


class SearchFilter:
    """Represents a search filter with type and value."""
    
    def __init__(self, field: str, operator: str, value: Any, data_type: str = "string"):
        self.field = field
        self.operator = operator
        self.value = value
        self.data_type = data_type
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "operator": self.operator,
            "value": self.value,
            "data_type": self.data_type
        }


class SearchResult:
    """Represents a search result with metadata."""
    
    def __init__(self, item: Dict[str, Any], score: float = 0.0, highlights: List[str] = None):
        self.item = item
        self.score = score
        self.highlights = highlights or []
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "item": self.item,
            "score": self.score,
            "highlights": self.highlights
        }


class AdvancedSearchService:
    """Advanced search service with full-text search and filtering."""
    
    def __init__(self):
        """Initialize search service."""
        pass
    
    @performance_monitor("search", "advanced_search")
    def search_invoices(
        self,
        user_id: str,
        query: str = None,
        filters: List[SearchFilter] = None,
        scope: SearchScope = SearchScope.ALL,
        sort_by: SearchSortOrder = SearchSortOrder.RELEVANCE,
        page: int = 1,
        limit: int = 20,
        include_facets: bool = False
    ) -> Dict[str, Any]:
        """
        Perform advanced search with full-text search, filtering, and faceting.
        
        Args:
            user_id: User ID for scoping results
            query: Search query string
            filters: List of filters to apply
            scope: Search scope (all fields or specific field)
            sort_by: Sort order for results
            page: Page number for pagination
            limit: Number of results per page
            include_facets: Whether to include facet counts
            
        Returns:
            Dictionary with search results, pagination, and facets
        """
        try:
            with get_db_session() as session:
                # Build base query
                base_query = self._build_base_query(session, user_id)
                
                # Apply text search
                if query:
                    base_query = self._apply_text_search(base_query, query, scope)
                
                # Apply filters
                if filters:
                    base_query = self._apply_filters(base_query, filters)
                
                # Get total count before pagination
                total_count = base_query.count()
                
                # Apply sorting
                base_query = self._apply_sorting(base_query, sort_by, query)
                
                # Apply pagination
                offset = (page - 1) * limit
                results = base_query.offset(offset).limit(limit).all()
                
                # Convert to search results
                search_results = self._convert_to_search_results(results, query)
                
                # Get facets if requested
                facets = {}
                if include_facets:
                    facets = self._get_facets(session, user_id, filters)
                
                return {
                    "success": True,
                    "results": [result.to_dict() for result in search_results],
                    "pagination": {
                        "page": page,
                        "limit": limit,
                        "total": total_count,
                        "pages": (total_count + limit - 1) // limit,
                        "has_next": page * limit < total_count,
                        "has_prev": page > 1
                    },
                    "facets": facets,
                    "search_info": {
                        "query": query,
                        "scope": scope.value,
                        "sort_by": sort_by.value,
                        "filters_applied": len(filters) if filters else 0
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in advanced search: {e}")
            return {
                "success": False,
                "error": str(e),
                "results": [],
                "pagination": {"page": page, "limit": limit, "total": 0, "pages": 0},
                "facets": {}
            }
    
    def _build_base_query(self, session: Session, user_id: str):
        """Build base query with eager loading."""
        return session.query(InvoiceModel).options(
            joinedload(InvoiceModel.vendor),
            joinedload(InvoiceModel.customer),
            selectinload(InvoiceModel.line_items)
        ).filter(InvoiceModel.user_id == user_id)
    
    def _apply_text_search(self, query, search_text: str, scope: SearchScope):
        """Apply full-text search based on scope."""
        # Sanitize search text
        clean_search = sanitize_search_query(search_text)
        if not clean_search:
            return query
        
        # PostgreSQL full-text search
        search_terms = clean_search.split()
        ts_query = " & ".join(search_terms)
        
        if scope == SearchScope.ALL:
            # Search across all text fields
            return query.filter(
                or_(
                    InvoiceModel.invoice_number.ilike(f"%{clean_search}%"),
                    InvoiceModel.raw_text.op("@@")(func.to_tsquery("english", ts_query)),
                    InvoiceModel.vendor.has(CompanyModel.company_name.ilike(f"%{clean_search}%")),
                    InvoiceModel.customer.has(CompanyModel.company_name.ilike(f"%{clean_search}%"))
                )
            )
        elif scope == SearchScope.INVOICE_NUMBER:
            return query.filter(InvoiceModel.invoice_number.ilike(f"%{clean_search}%"))
        elif scope == SearchScope.VENDOR:
            return query.filter(InvoiceModel.vendor.has(CompanyModel.company_name.ilike(f"%{clean_search}%")))
        elif scope == SearchScope.CUSTOMER:
            return query.filter(InvoiceModel.customer.has(CompanyModel.company_name.ilike(f"%{clean_search}%")))
        elif scope == SearchScope.RAW_TEXT:
            return query.filter(InvoiceModel.raw_text.op("@@")(func.to_tsquery("english", ts_query)))
        else:
            return query
    
    def _apply_filters(self, query, filters: List[SearchFilter]):
        """Apply filters to the query."""
        for filter_obj in filters:
            query = self._apply_single_filter(query, filter_obj)
        return query
    
    def _apply_single_filter(self, query, filter_obj: SearchFilter):
        """Apply a single filter to the query."""
        field = filter_obj.field
        operator = filter_obj.operator
        value = filter_obj.value
        
        if field == "amount":
            column = InvoiceModel.net_amount
            if operator == "gte":
                return query.filter(column >= Decimal(str(value)))
            elif operator == "lte":
                return query.filter(column <= Decimal(str(value)))
            elif operator == "eq":
                return query.filter(column == Decimal(str(value)))
            elif operator == "between":
                if isinstance(value, list) and len(value) == 2:
                    return query.filter(column.between(Decimal(str(value[0])), Decimal(str(value[1]))))
        
        elif field == "date":
            column = InvoiceModel.invoice_date
            if operator == "gte":
                return query.filter(column >= value)
            elif operator == "lte":
                return query.filter(column <= value)
            elif operator == "eq":
                return query.filter(column == value)
            elif operator == "between":
                if isinstance(value, list) and len(value) == 2:
                    return query.filter(column.between(value[0], value[1]))
        
        elif field == "created_at":
            column = InvoiceModel.created_at
            if operator == "gte":
                return query.filter(column >= value)
            elif operator == "lte":
                return query.filter(column <= value)
            elif operator == "between":
                if isinstance(value, list) and len(value) == 2:
                    return query.filter(column.between(value[0], value[1]))
        
        elif field == "currency":
            if operator == "eq":
                return query.filter(InvoiceModel.currency == value)
            elif operator == "in":
                if isinstance(value, list):
                    return query.filter(InvoiceModel.currency.in_(value))
        
        elif field == "confidence":
            column = InvoiceModel.extraction_confidence
            if operator == "gte":
                return query.filter(column >= float(value))
            elif operator == "lte":
                return query.filter(column <= float(value))
        
        elif field == "vendor_id":
            if operator == "eq":
                return query.filter(InvoiceModel.vendor_id == value)
            elif operator == "in":
                if isinstance(value, list):
                    return query.filter(InvoiceModel.vendor_id.in_(value))
        
        elif field == "customer_id":
            if operator == "eq":
                return query.filter(InvoiceModel.customer_id == value)
            elif operator == "in":
                if isinstance(value, list):
                    return query.filter(InvoiceModel.customer_id.in_(value))
        
        return query
    
    def _apply_sorting(self, query, sort_by: SearchSortOrder, search_text: str = None):
        """Apply sorting to the query."""
        if sort_by == SearchSortOrder.DATE_DESC:
            return query.order_by(desc(InvoiceModel.created_at))
        elif sort_by == SearchSortOrder.DATE_ASC:
            return query.order_by(asc(InvoiceModel.created_at))
        elif sort_by == SearchSortOrder.AMOUNT_DESC:
            return query.order_by(desc(InvoiceModel.net_amount))
        elif sort_by == SearchSortOrder.AMOUNT_ASC:
            return query.order_by(asc(InvoiceModel.net_amount))
        elif sort_by == SearchSortOrder.INVOICE_NUMBER:
            return query.order_by(asc(InvoiceModel.invoice_number))
        elif sort_by == SearchSortOrder.VENDOR_NAME:
            return query.join(CompanyModel, InvoiceModel.vendor_id == CompanyModel.id, isouter=True)\
                        .order_by(asc(CompanyModel.company_name))
        elif sort_by == SearchSortOrder.CUSTOMER_NAME:
            return query.join(CompanyModel, InvoiceModel.customer_id == CompanyModel.id, isouter=True)\
                        .order_by(asc(CompanyModel.company_name))
        elif sort_by == SearchSortOrder.RELEVANCE and search_text:
            # PostgreSQL relevance ranking
            clean_search = sanitize_search_query(search_text)
            if clean_search:
                search_terms = clean_search.split()
                ts_query = " & ".join(search_terms)
                return query.order_by(desc(func.ts_rank(
                    func.to_tsvector("english", InvoiceModel.raw_text),
                    func.to_tsquery("english", ts_query)
                )))
        
        # Default sorting
        return query.order_by(desc(InvoiceModel.created_at))
    
    def _convert_to_search_results(self, invoices: List[InvoiceModel], search_text: str = None) -> List[SearchResult]:
        """Convert invoice models to search results."""
        results = []
        
        for invoice in invoices:
            # Convert invoice to dict
            invoice_dict = {
                "id": str(invoice.id),
                "invoice_number": invoice.invoice_number,
                "invoice_date": invoice.invoice_date.isoformat() if invoice.invoice_date else None,
                "net_amount": float(invoice.net_amount) if invoice.net_amount else None,
                "currency": invoice.currency,
                "vendor_name": invoice.vendor.company_name if invoice.vendor else None,
                "customer_name": invoice.customer.company_name if invoice.customer else None,
                "extraction_confidence": invoice.extraction_confidence,
                "original_file_id": invoice.original_file_id,
                "original_filename": invoice.original_filename,
                "created_at": invoice.created_at.isoformat(),
                "line_items_count": len(invoice.line_items) if invoice.line_items else 0
            }
            
            # Generate highlights if search text provided
            highlights = []
            if search_text:
                highlights = self._generate_highlights(invoice, search_text)
            
            # Calculate relevance score (simplified)
            score = self._calculate_relevance_score(invoice, search_text)
            
            results.append(SearchResult(invoice_dict, score, highlights))
        
        return results
    
    def _generate_highlights(self, invoice: InvoiceModel, search_text: str) -> List[str]:
        """Generate search result highlights."""
        highlights = []
        clean_search = sanitize_search_query(search_text).lower()
        
        if not clean_search:
            return highlights
        
        search_terms = clean_search.split()
        
        # Check invoice number
        if invoice.invoice_number and any(term in invoice.invoice_number.lower() for term in search_terms):
            highlights.append(f"Invoice: {invoice.invoice_number}")
        
        # Check vendor name
        if invoice.vendor and invoice.vendor.company_name:
            if any(term in invoice.vendor.company_name.lower() for term in search_terms):
                highlights.append(f"Vendor: {invoice.vendor.company_name}")
        
        # Check customer name
        if invoice.customer and invoice.customer.company_name:
            if any(term in invoice.customer.company_name.lower() for term in search_terms):
                highlights.append(f"Customer: {invoice.customer.company_name}")
        
        # Check raw text (first 100 chars containing search term)
        if invoice.raw_text:
            for term in search_terms:
                if term in invoice.raw_text.lower():
                    # Find context around the term
                    text_lower = invoice.raw_text.lower()
                    index = text_lower.find(term)
                    if index != -1:
                        start = max(0, index - 50)
                        end = min(len(invoice.raw_text), index + 50)
                        context = invoice.raw_text[start:end]
                        if start > 0:
                            context = "..." + context
                        if end < len(invoice.raw_text):
                            context = context + "..."
                        highlights.append(f"Text: {context}")
                        break
        
        return highlights[:3]  # Limit to 3 highlights
    
    def _calculate_relevance_score(self, invoice: InvoiceModel, search_text: str = None) -> float:
        """Calculate relevance score for search result."""
        if not search_text:
            return 0.0
        
        score = 0.0
        clean_search = sanitize_search_query(search_text).lower()
        search_terms = clean_search.split()
        
        # Invoice number match (highest weight)
        if invoice.invoice_number:
            for term in search_terms:
                if term in invoice.invoice_number.lower():
                    score += 10.0
        
        # Exact company name match
        if invoice.vendor and invoice.vendor.company_name:
            for term in search_terms:
                if term in invoice.vendor.company_name.lower():
                    score += 5.0
        
        if invoice.customer and invoice.customer.company_name:
            for term in search_terms:
                if term in invoice.customer.company_name.lower():
                    score += 5.0
        
        # Raw text match (lower weight)
        if invoice.raw_text:
            text_lower = invoice.raw_text.lower()
            for term in search_terms:
                count = text_lower.count(term)
                score += count * 1.0
        
        return score
    
    def _get_facets(self, session: Session, user_id: str, existing_filters: List[SearchFilter] = None) -> Dict[str, Any]:
        """Get facet counts for search refinement."""
        facets = {}
        
        # Base query for facets
        base_query = session.query(InvoiceModel).filter(InvoiceModel.user_id == user_id)
        
        # Apply existing filters (excluding the facet we're calculating)
        if existing_filters:
            for filter_obj in existing_filters:
                base_query = self._apply_single_filter(base_query, filter_obj)
        
        # Currency facet
        currency_facet = base_query.with_entities(
            InvoiceModel.currency,
            func.count(InvoiceModel.id).label('count')
        ).group_by(InvoiceModel.currency).all()
        
        facets["currency"] = [
            {"value": row.currency, "count": row.count}
            for row in currency_facet if row.currency
        ]
        
        # Amount range facet
        amount_ranges = [
            ("0-100", 0, 100),
            ("100-500", 100, 500),
            ("500-1000", 500, 1000),
            ("1000-5000", 1000, 5000),
            ("5000+", 5000, None)
        ]
        
        amount_facet = []
        for label, min_amount, max_amount in amount_ranges:
            if max_amount:
                count = base_query.filter(
                    InvoiceModel.net_amount >= min_amount,
                    InvoiceModel.net_amount < max_amount
                ).count()
            else:
                count = base_query.filter(InvoiceModel.net_amount >= min_amount).count()
            
            amount_facet.append({"value": label, "count": count})
        
        facets["amount_range"] = amount_facet
        
        # Date range facet (last 30, 90, 180, 365 days)
        from datetime import timedelta
        now = datetime.utcnow()
        date_ranges = [
            ("last_30_days", now - timedelta(days=30)),
            ("last_90_days", now - timedelta(days=90)),
            ("last_180_days", now - timedelta(days=180)),
            ("last_year", now - timedelta(days=365))
        ]
        
        date_facet = []
        for label, since_date in date_ranges:
            count = base_query.filter(InvoiceModel.created_at >= since_date).count()
            date_facet.append({"value": label, "count": count})
        
        facets["date_range"] = date_facet
        
        # Top vendors facet
        vendor_facet = base_query.join(
            CompanyModel, InvoiceModel.vendor_id == CompanyModel.id
        ).with_entities(
            CompanyModel.company_name,
            func.count(InvoiceModel.id).label('count')
        ).group_by(CompanyModel.company_name).order_by(
            func.count(InvoiceModel.id).desc()
        ).limit(10).all()
        
        facets["vendors"] = [
            {"value": row.company_name, "count": row.count}
            for row in vendor_facet
        ]
        
        return facets
    
    @performance_monitor("search", "suggestions")
    def get_search_suggestions(self, user_id: str, query: str, limit: int = 10) -> List[str]:
        """Get search suggestions based on query."""
        try:
            if not query or len(query) < 2:
                return []
            
            clean_query = sanitize_search_query(query).lower()
            suggestions = []
            
            with get_db_session() as session:
                # Invoice number suggestions
                invoice_numbers = session.query(InvoiceModel.invoice_number).filter(
                    InvoiceModel.user_id == user_id,
                    InvoiceModel.invoice_number.ilike(f"{clean_query}%")
                ).limit(5).all()
                
                suggestions.extend([inv.invoice_number for inv in invoice_numbers if inv.invoice_number])
                
                # Company name suggestions
                companies = session.query(CompanyModel.company_name).join(
                    InvoiceModel, or_(
                        InvoiceModel.vendor_id == CompanyModel.id,
                        InvoiceModel.customer_id == CompanyModel.id
                    )
                ).filter(
                    InvoiceModel.user_id == user_id,
                    CompanyModel.company_name.ilike(f"{clean_query}%")
                ).distinct().limit(5).all()
                
                suggestions.extend([comp.company_name for comp in companies if comp.company_name])
            
            return list(set(suggestions))[:limit]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []


# Export search service
__all__ = ["AdvancedSearchService", "SearchFilter", "SearchResult", "SearchSortOrder", "SearchScope"]
