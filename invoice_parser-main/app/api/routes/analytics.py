"""
Analytics API Routes

Provides advanced analytics, reporting, and business intelligence endpoints
for invoice data analysis and insights.
"""
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.api.routes.auth import get_current_user
from app.models.database import UserModel
from app.services.analytics_service import AnalyticsService
from app.models.api_responses import success_response, error_response
from app.core.logging_config import performance_monitor

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analytics"])


def get_analytics_service() -> AnalyticsService:
    """Dependency to get analytics service instance."""
    return AnalyticsService()


@router.get("/analytics/dashboard")
@performance_monitor("api", "analytics_dashboard")
async def get_dashboard_analytics(
    date_range: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get comprehensive dashboard analytics for the current user.
    
    Returns detailed analytics including:
    - Summary metrics (total invoices, amounts, growth)
    - Trend analysis (daily/weekly patterns)
    - Category breakdown (amount ranges, currencies)
    - Vendor/customer analysis
    - Processing performance metrics
    - Time-based patterns
    - Financial insights
    """
    try:
        analytics_data = analytics_service.get_dashboard_analytics(
            user_id=str(current_user.id),
            date_range=date_range
        )
        
        if analytics_data["success"]:
            return success_response(
                data=analytics_data["data"],
                message=f"Analytics retrieved for {date_range} days"
            )
        else:
            return error_response(
                message="Failed to retrieve analytics",
                error_details={"error": analytics_data.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in dashboard analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics data"
        )


@router.get("/analytics/summary")
@performance_monitor("api", "analytics_summary")
async def get_analytics_summary(
    date_range: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get summary analytics for quick dashboard overview.
    
    Returns condensed analytics including:
    - Key metrics (count, total amount, average)
    - Growth indicators
    - Top vendors/customers
    - Processing confidence
    """
    try:
        full_analytics = analytics_service.get_dashboard_analytics(
            user_id=str(current_user.id),
            date_range=date_range
        )
        
        if not full_analytics["success"]:
            return error_response(
                message="Failed to retrieve analytics summary",
                error_details={"error": full_analytics.get("error")}
            )
        
        # Extract summary data
        data = full_analytics["data"]
        summary = {
            "summary": data["summary"],
            "top_vendors": data["vendors"]["top_vendors"][:5],
            "top_customers": data["vendors"]["top_customers"][:5],
            "processing_stats": data["processing"],
            "recent_trends": data["trends"]["daily"][-7:] if data["trends"]["daily"] else []
        }
        
        return success_response(
            data=summary,
            message="Analytics summary retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in analytics summary endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analytics summary"
        )


@router.get("/analytics/trends")
@performance_monitor("api", "analytics_trends")
async def get_trend_analytics(
    date_range: int = Query(90, ge=7, le=365, description="Number of days for trend analysis"),
    granularity: str = Query("daily", regex="^(daily|weekly|monthly)$", description="Trend granularity"),
    current_user: UserModel = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get detailed trend analysis over time.
    
    Supports different granularities:
    - daily: Day-by-day trends
    - weekly: Week-by-week trends  
    - monthly: Month-by-month trends
    """
    try:
        analytics_data = analytics_service.get_dashboard_analytics(
            user_id=str(current_user.id),
            date_range=date_range
        )
        
        if not analytics_data["success"]:
            return error_response(
                message="Failed to retrieve trend analytics",
                error_details={"error": analytics_data.get("error")}
            )
        
        trends_data = analytics_data["data"]["trends"]
        
        # Return requested granularity
        if granularity == "weekly":
            trend_data = trends_data["weekly"]
        elif granularity == "monthly":
            # For monthly, we'd need to implement monthly aggregation
            trend_data = trends_data["daily"]  # Fallback to daily for now
        else:
            trend_data = trends_data["daily"]
        
        return success_response(
            data={
                "trends": trend_data,
                "granularity": granularity,
                "date_range": date_range,
                "time_analysis": analytics_data["data"]["time_analysis"]
            },
            message=f"Trend analysis retrieved for {granularity} granularity"
        )
        
    except Exception as e:
        logger.error(f"Error in trend analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve trend analytics"
        )


@router.get("/analytics/vendors")
@performance_monitor("api", "analytics_vendors")
async def get_vendor_analytics(
    date_range: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
    limit: int = Query(20, ge=5, le=100, description="Maximum number of vendors to return"),
    current_user: UserModel = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get detailed vendor and customer analytics.
    
    Returns:
    - Top vendors by transaction count and amount
    - Top customers by transaction count and amount
    - Vendor performance metrics
    - Customer relationship insights
    """
    try:
        analytics_data = analytics_service.get_dashboard_analytics(
            user_id=str(current_user.id),
            date_range=date_range
        )
        
        if not analytics_data["success"]:
            return error_response(
                message="Failed to retrieve vendor analytics",
                error_details={"error": analytics_data.get("error")}
            )
        
        vendor_data = analytics_data["data"]["vendors"]
        
        return success_response(
            data={
                "top_vendors": vendor_data["top_vendors"][:limit],
                "top_customers": vendor_data["top_customers"][:limit],
                "vendor_count": len(vendor_data["top_vendors"]),
                "customer_count": len(vendor_data["top_customers"]),
                "date_range": date_range
            },
            message="Vendor analytics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in vendor analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve vendor analytics"
        )


@router.get("/analytics/financial")
@performance_monitor("api", "analytics_financial")
async def get_financial_analytics(
    date_range: int = Query(90, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get detailed financial analytics and insights.
    
    Returns:
    - Financial summary and trends
    - Tax analysis
    - Monthly financial breakdown
    - Currency distribution
    - Amount categorization
    """
    try:
        analytics_data = analytics_service.get_dashboard_analytics(
            user_id=str(current_user.id),
            date_range=date_range
        )
        
        if not analytics_data["success"]:
            return error_response(
                message="Failed to retrieve financial analytics",
                error_details={"error": analytics_data.get("error")}
            )
        
        data = analytics_data["data"]
        financial_data = {
            "financial_insights": data["financial"],
            "category_analysis": data["categories"],
            "summary_metrics": data["summary"],
            "monthly_trends": data["financial"]["monthly_summary"]
        }
        
        return success_response(
            data=financial_data,
            message="Financial analytics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in financial analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve financial analytics"
        )


@router.get("/analytics/export")
@performance_monitor("api", "analytics_export")
async def export_analytics(
    format_type: str = Query("json", regex="^(json|csv|pdf)$", description="Export format"),
    date_range: int = Query(30, ge=1, le=365, description="Number of days to export"),
    current_user: UserModel = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Export analytics data in various formats.
    
    Supported formats:
    - json: JSON format for API consumption
    - csv: CSV format for spreadsheet analysis
    - pdf: PDF report for presentations
    """
    try:
        export_data = analytics_service.export_analytics_data(
            user_id=str(current_user.id),
            format_type=format_type,
            date_range=date_range
        )
        
        if export_data["success"]:
            return success_response(
                data=export_data,
                message=f"Analytics exported in {format_type.upper()} format"
            )
        else:
            return error_response(
                message="Failed to export analytics",
                error_details={"error": export_data.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in analytics export endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to export analytics data"
        )


@router.get("/analytics/performance")
@performance_monitor("api", "analytics_performance")
async def get_performance_analytics(
    date_range: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """
    Get processing performance analytics.
    
    Returns:
    - Extraction confidence distribution
    - Processing time analysis
    - Quality metrics
    - Error rate analysis
    """
    try:
        analytics_data = analytics_service.get_dashboard_analytics(
            user_id=str(current_user.id),
            date_range=date_range
        )
        
        if not analytics_data["success"]:
            return error_response(
                message="Failed to retrieve performance analytics",
                error_details={"error": analytics_data.get("error")}
            )
        
        performance_data = {
            "processing_analytics": analytics_data["data"]["processing"],
            "confidence_distribution": analytics_data["data"]["processing"]["confidence_distribution"],
            "summary_metrics": analytics_data["data"]["summary"],
            "quality_score": analytics_data["data"]["summary"]["average_confidence"]
        }
        
        return success_response(
            data=performance_data,
            message="Performance analytics retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Error in performance analytics endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve performance analytics"
        )
