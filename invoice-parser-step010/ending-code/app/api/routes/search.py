"""
Advanced Search API Routes

Provides comprehensive search, filtering, and faceted search endpoints
for invoices and related data.
"""
import logging
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException, status, Body
from pydantic import BaseModel, Field

from app.api.routes.auth import get_current_user
from app.core.logging_config import performance_monitor
from app.models.database import UserModel
from app.models.api_responses import success_response, error_response
from app.services.search_service import (
    AdvancedSearchService, 
    SearchFilter, 
    SearchSortOrder, 
    SearchScope
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["search"])


# Pydantic models for request/response
class SearchFilterRequest(BaseModel):
    """Request model for search filters."""
    field: str = Field(..., description="Field to filter on")
    operator: str = Field(..., description="Filter operator (eq, gte, lte, in, between)")
    value: Any = Field(..., description="Filter value")
    data_type: str = Field(default="string", description="Data type (string, number, date)")


class AdvancedSearchRequest(BaseModel):
    """Request model for advanced search."""
    query: Optional[str] = Field(None, description="Search query string")
    filters: Optional[List[SearchFilterRequest]] = Field(default=[], description="Search filters")
    scope: Optional[SearchScope] = Field(default=SearchScope.ALL, description="Search scope")
    sort_by: Optional[SearchSortOrder] = Field(default=SearchSortOrder.RELEVANCE, description="Sort order")
    page: Optional[int] = Field(default=1, ge=1, description="Page number")
    limit: Optional[int] = Field(default=20, ge=1, le=100, description="Results per page")
    include_facets: Optional[bool] = Field(default=False, description="Include facet counts")


def get_search_service() -> AdvancedSearchService:
    """Dependency to get search service instance."""
    return AdvancedSearchService()


@router.get("/search")
@performance_monitor("api", "search_invoices")
async def search_invoices(
    query: Optional[str] = Query(None, description="Search query string"),
    scope: Optional[SearchScope] = Query(SearchScope.ALL, description="Search scope"),
    sort_by: Optional[SearchSortOrder] = Query(SearchSortOrder.RELEVANCE, description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    include_facets: bool = Query(False, description="Include facet counts"),
    # Filter parameters
    min_amount: Optional[float] = Query(None, description="Minimum amount filter"),
    max_amount: Optional[float] = Query(None, description="Maximum amount filter"),
    currency: Optional[str] = Query(None, description="Currency filter"),
    date_from: Optional[date] = Query(None, description="Start date filter"),
    date_to: Optional[date] = Query(None, description="End date filter"),
    vendor_id: Optional[str] = Query(None, description="Vendor ID filter"),
    customer_id: Optional[str] = Query(None, description="Customer ID filter"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence filter"),
    current_user: UserModel = Depends(get_current_user),
    search_service: AdvancedSearchService = Depends(get_search_service)
):
    """
    Search invoices with advanced filtering and faceting.
    
    Supports:
    - Full-text search across multiple fields
    - Field-specific search (invoice number, vendor, customer)
    - Amount, date, and confidence filtering
    - Multiple sorting options
    - Faceted search for refinement
    - Pagination
    
    Returns paginated search results with optional facets for search refinement.
    """
    try:
        # Build filters from query parameters
        filters = []
        
        if min_amount is not None or max_amount is not None:
            if min_amount is not None and max_amount is not None:
                filters.append(SearchFilter("amount", "between", [min_amount, max_amount], "number"))
            elif min_amount is not None:
                filters.append(SearchFilter("amount", "gte", min_amount, "number"))
            elif max_amount is not None:
                filters.append(SearchFilter("amount", "lte", max_amount, "number"))
        
        if currency:
            filters.append(SearchFilter("currency", "eq", currency, "string"))
        
        if date_from or date_to:
            if date_from and date_to:
                filters.append(SearchFilter("date", "between", [date_from, date_to], "date"))
            elif date_from:
                filters.append(SearchFilter("date", "gte", date_from, "date"))
            elif date_to:
                filters.append(SearchFilter("date", "lte", date_to, "date"))
        
        if vendor_id:
            filters.append(SearchFilter("vendor_id", "eq", vendor_id, "string"))
        
        if customer_id:
            filters.append(SearchFilter("customer_id", "eq", customer_id, "string"))
        
        if min_confidence is not None:
            filters.append(SearchFilter("confidence", "gte", min_confidence, "number"))
        
        # Perform search
        search_results = search_service.search_invoices(
            user_id=str(current_user.id),
            query=query,
            filters=filters,
            scope=scope,
            sort_by=sort_by,
            page=page,
            limit=limit,
            include_facets=include_facets
        )
        
        if search_results["success"]:
            return success_response(
                data=search_results,
                message=f"Search completed. Found {search_results['pagination']['total']} results."
            )
        else:
            return error_response(
                message="Search failed",
                error_details={"error": search_results.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed"
        )


@router.post("/search/advanced")
@performance_monitor("api", "advanced_search")
async def advanced_search(
    search_request: AdvancedSearchRequest,
    current_user: UserModel = Depends(get_current_user),
    search_service: AdvancedSearchService = Depends(get_search_service)
):
    """
    Advanced search with complex filtering via POST request.
    
    Allows for complex filter combinations and advanced search parameters
    that may be too complex for GET query parameters.
    
    Supports all search features:
    - Full-text search
    - Complex filter combinations
    - Multiple data types (string, number, date)
    - Advanced operators (in, between, etc.)
    - Faceted search
    """
    try:
        # Convert request filters to SearchFilter objects
        filters = []
        for filter_req in search_request.filters:
            filters.append(SearchFilter(
                field=filter_req.field,
                operator=filter_req.operator,
                value=filter_req.value,
                data_type=filter_req.data_type
            ))
        
        # Perform search
        search_results = search_service.search_invoices(
            user_id=str(current_user.id),
            query=search_request.query,
            filters=filters,
            scope=search_request.scope,
            sort_by=search_request.sort_by,
            page=search_request.page,
            limit=search_request.limit,
            include_facets=search_request.include_facets
        )
        
        if search_results["success"]:
            return success_response(
                data=search_results,
                message=f"Advanced search completed. Found {search_results['pagination']['total']} results."
            )
        else:
            return error_response(
                message="Advanced search failed",
                error_details={"error": search_results.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in advanced search endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Advanced search operation failed"
        )


@router.get("/search/suggestions")
@performance_monitor("api", "search_suggestions")
async def get_search_suggestions(
    query: str = Query(..., min_length=2, description="Search query for suggestions"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of suggestions"),
    current_user: UserModel = Depends(get_current_user),
    search_service: AdvancedSearchService = Depends(get_search_service)
):
    """
    Get search suggestions based on partial query.
    
    Returns relevant suggestions from:
    - Invoice numbers
    - Company names (vendors/customers)
    - Common search terms
    
    Useful for implementing search auto-complete functionality.
    """
    try:
        suggestions = search_service.get_search_suggestions(
            user_id=str(current_user.id),
            query=query,
            limit=limit
        )
        
        return success_response(
            data={
                "suggestions": suggestions,
                "query": query,
                "count": len(suggestions)
            },
            message=f"Found {len(suggestions)} search suggestions"
        )
        
    except Exception as e:
        logger.error(f"Error getting search suggestions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get search suggestions"
        )


@router.get("/search/facets")
@performance_monitor("api", "search_facets")
async def get_search_facets(
    query: Optional[str] = Query(None, description="Search query to scope facets"),
    current_user: UserModel = Depends(get_current_user),
    search_service: AdvancedSearchService = Depends(get_search_service)
):
    """
    Get search facets for filtering and refinement.
    
    Returns facet counts for:
    - Currency types
    - Amount ranges
    - Date ranges
    - Top vendors/customers
    
    Can be scoped by a search query to show relevant facets.
    """
    try:
        # Get facets by performing a search with facets enabled
        search_results = search_service.search_invoices(
            user_id=str(current_user.id),
            query=query,
            filters=[],
            page=1,
            limit=1,  # We only need facets, not results
            include_facets=True
        )
        
        if search_results["success"]:
            return success_response(
                data={
                    "facets": search_results["facets"],
                    "query": query,
                    "total_invoices": search_results["pagination"]["total"]
                },
                message="Search facets retrieved successfully"
            )
        else:
            return error_response(
                message="Failed to retrieve facets",
                error_details={"error": search_results.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error getting search facets: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve search facets"
        )


@router.get("/search/filters")
async def get_available_filters():
    """
    Get available filter fields and operators.
    
    Returns metadata about available filters including:
    - Field names and types
    - Supported operators for each field
    - Value formats and examples
    
    Useful for building dynamic search interfaces.
    """
    try:
        filter_metadata = {
            "fields": {
                "amount": {
                    "type": "number",
                    "operators": ["eq", "gte", "lte", "between"],
                    "description": "Invoice amount filtering",
                    "example": {"operator": "between", "value": [100, 1000]}
                },
                "date": {
                    "type": "date",
                    "operators": ["eq", "gte", "lte", "between"],
                    "description": "Invoice date filtering",
                    "example": {"operator": "gte", "value": "2024-01-01"}
                },
                "created_at": {
                    "type": "datetime",
                    "operators": ["gte", "lte", "between"],
                    "description": "Creation date filtering",
                    "example": {"operator": "gte", "value": "2024-01-01T00:00:00"}
                },
                "currency": {
                    "type": "string",
                    "operators": ["eq", "in"],
                    "description": "Currency code filtering",
                    "example": {"operator": "in", "value": ["USD", "EUR", "INR"]}
                },
                "confidence": {
                    "type": "number",
                    "operators": ["gte", "lte"],
                    "description": "Extraction confidence filtering",
                    "example": {"operator": "gte", "value": 0.8}
                },
                "vendor_id": {
                    "type": "string",
                    "operators": ["eq", "in"],
                    "description": "Vendor company ID filtering",
                    "example": {"operator": "eq", "value": "company-uuid"}
                },
                "customer_id": {
                    "type": "string",
                    "operators": ["eq", "in"],
                    "description": "Customer company ID filtering",
                    "example": {"operator": "eq", "value": "company-uuid"}
                }
            },
            "search_scopes": {
                "all": "Search all fields (default)",
                "invoice_number": "Search only invoice numbers",
                "vendor": "Search only vendor names",
                "customer": "Search only customer names",
                "description": "Search only line item descriptions",
                "raw_text": "Search only raw extracted text"
            },
            "sort_options": {
                "relevance": "Sort by search relevance (default for text search)",
                "date_desc": "Sort by date (newest first)",
                "date_asc": "Sort by date (oldest first)",
                "amount_desc": "Sort by amount (highest first)",
                "amount_asc": "Sort by amount (lowest first)",
                "invoice_number": "Sort by invoice number",
                "vendor_name": "Sort by vendor name",
                "customer_name": "Sort by customer name"
            }
        }
        
        return success_response(
            data=filter_metadata,
            message="Filter metadata retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error getting filter metadata: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve filter metadata"
        )
