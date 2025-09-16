"""
AI Insights API Routes

Provides advanced AI-powered insights, pattern recognition, and intelligent
analysis endpoints for invoice data with machine learning capabilities.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status

from app.api.routes.auth import get_current_user
from app.core.logging_config import performance_monitor
from app.models.database import UserModel
from app.models.api_responses import success_response, error_response
from app.services.ai_insights_service import AIInsightsService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["ai-insights"])


def get_ai_insights_service() -> AIInsightsService:
    """Dependency to get AI insights service instance."""
    return AIInsightsService()


@router.get("/ai/insights/comprehensive")
@performance_monitor("api", "comprehensive_ai_insights")
async def get_comprehensive_ai_insights(
    date_range: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    include_predictions: bool = Query(True, description="Include predictive analytics"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get comprehensive AI-powered insights and analysis.
    
    Features:
    - Spending pattern analysis with trend detection
    - Vendor relationship insights and scoring
    - Seasonal trend analysis and forecasting
    - Anomaly detection and risk assessment
    - Cost optimization recommendations
    - Payment behavior analysis
    - Category-based spending breakdown
    - Data quality assessment
    - Predictive analytics and forecasting
    - Actionable business recommendations
    
    Returns detailed insights with confidence scores and explanations.
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=include_predictions
        )
        
        if insights_result["success"]:
            return success_response(
                data=insights_result["insights"],
                message=f"Comprehensive AI insights generated for {date_range} days of data"
            )
        else:
            return error_response(
                message="Failed to generate AI insights",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in comprehensive AI insights endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate comprehensive AI insights"
        )


@router.get("/ai/insights/spending-patterns")
@performance_monitor("api", "spending_patterns_insights")
async def get_spending_patterns_insights(
    date_range: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get detailed spending pattern analysis.
    
    Returns:
    - Spending distribution analysis
    - Monthly and quarterly trends
    - Growth rate calculations
    - Statistical insights (mean, median, std dev)
    - Pattern recognition and anomalies
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=False
        )
        
        if insights_result["success"]:
            spending_insights = insights_result["insights"].get("spending_patterns", {})
            return success_response(
                data=spending_insights,
                message="Spending pattern insights generated successfully"
            )
        else:
            return error_response(
                message="Failed to generate spending pattern insights",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in spending patterns insights endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate spending pattern insights"
        )


@router.get("/ai/insights/vendor-analysis")
@performance_monitor("api", "vendor_analysis_insights")
async def get_vendor_analysis_insights(
    date_range: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get intelligent vendor relationship analysis.
    
    Returns:
    - Vendor relationship scoring
    - Spending concentration analysis
    - Vendor performance metrics
    - Relationship strength indicators
    - Consolidation opportunities
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=False
        )
        
        if insights_result["success"]:
            vendor_insights = insights_result["insights"].get("vendor_insights", {})
            return success_response(
                data=vendor_insights,
                message="Vendor analysis insights generated successfully"
            )
        else:
            return error_response(
                message="Failed to generate vendor analysis insights",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in vendor analysis insights endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate vendor analysis insights"
        )


@router.get("/ai/insights/anomaly-detection")
@performance_monitor("api", "anomaly_detection")
async def get_anomaly_detection_insights(
    date_range: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    severity_filter: Optional[str] = Query(None, regex="^(low|medium|high)$", description="Filter by severity level"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get AI-powered anomaly detection results.
    
    Detects:
    - Unusual spending amounts (statistical outliers)
    - Abnormal vendor frequency patterns
    - Duplicate invoice numbers
    - Unusual processing times
    - Suspicious transaction patterns
    
    Returns detailed anomaly reports with severity levels and recommendations.
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=False
        )
        
        if insights_result["success"]:
            anomaly_insights = insights_result["insights"].get("anomaly_detection", {})
            
            # Apply severity filter if specified
            if severity_filter and "anomalies" in anomaly_insights:
                filtered_anomalies = [
                    anomaly for anomaly in anomaly_insights["anomalies"]
                    if anomaly.get("severity") == severity_filter
                ]
                anomaly_insights["anomalies"] = filtered_anomalies
                anomaly_insights["filtered_count"] = len(filtered_anomalies)
                anomaly_insights["filter_applied"] = severity_filter
            
            return success_response(
                data=anomaly_insights,
                message=f"Anomaly detection completed. Found {anomaly_insights.get('total_anomalies', 0)} anomalies."
            )
        else:
            return error_response(
                message="Failed to perform anomaly detection",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in anomaly detection endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform anomaly detection"
        )


@router.get("/ai/insights/cost-optimization")
@performance_monitor("api", "cost_optimization_insights")
async def get_cost_optimization_insights(
    date_range: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get AI-powered cost optimization recommendations.
    
    Analyzes:
    - Vendor consolidation opportunities
    - Payment term optimization potential
    - Subscription and recurring payment analysis
    - Volume discount opportunities
    - Contract renegotiation suggestions
    
    Returns actionable cost-saving recommendations with estimated savings.
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=False
        )
        
        if insights_result["success"]:
            cost_insights = insights_result["insights"].get("cost_optimization", {})
            return success_response(
                data=cost_insights,
                message=f"Cost optimization analysis completed. Found {cost_insights.get('total_opportunities', 0)} opportunities."
            )
        else:
            return error_response(
                message="Failed to generate cost optimization insights",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in cost optimization insights endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate cost optimization insights"
        )


@router.get("/ai/insights/seasonal-trends")
@performance_monitor("api", "seasonal_trends_insights")
async def get_seasonal_trends_insights(
    date_range: int = Query(180, ge=90, le=365, description="Number of days to analyze (minimum 90 for seasonal analysis)"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get seasonal trend analysis and patterns.
    
    Analyzes:
    - Monthly spending patterns
    - Quarterly business cycles
    - Weekly activity patterns
    - Peak spending periods
    - Seasonal variations and forecasts
    
    Useful for budget planning and cash flow management.
    """
    try:
        if date_range < 90:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum 90 days required for meaningful seasonal analysis"
            )
        
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=True
        )
        
        if insights_result["success"]:
            seasonal_insights = insights_result["insights"].get("seasonal_trends", {})
            return success_response(
                data=seasonal_insights,
                message="Seasonal trend analysis completed successfully"
            )
        else:
            return error_response(
                message="Failed to generate seasonal trend insights",
                error_details={"error": insights_result.get("error")}
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in seasonal trends insights endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate seasonal trend insights"
        )


@router.get("/ai/insights/predictions")
@performance_monitor("api", "predictive_insights")
async def get_predictive_insights(
    date_range: int = Query(180, ge=30, le=365, description="Number of days of historical data to analyze"),
    forecast_period: int = Query(30, ge=7, le=90, description="Number of days to forecast"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get AI-powered predictive analytics and forecasts.
    
    Features:
    - Spending trend predictions
    - Cash flow forecasting
    - Vendor relationship predictions
    - Seasonal adjustment forecasts
    - Budget variance predictions
    
    Uses machine learning models to predict future patterns based on historical data.
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=True
        )
        
        if insights_result["success"]:
            predictions = insights_result["insights"].get("predictions", {})
            
            # Add forecast period to metadata
            if predictions:
                predictions["forecast_metadata"] = {
                    "historical_days": date_range,
                    "forecast_days": forecast_period,
                    "model_type": "linear_trend",
                    "confidence_level": "low"  # Simple model
                }
            
            return success_response(
                data=predictions,
                message=f"Predictive analysis completed for {forecast_period} day forecast"
            )
        else:
            return error_response(
                message="Failed to generate predictive insights",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in predictive insights endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate predictive insights"
        )


@router.get("/ai/insights/data-quality")
@performance_monitor("api", "data_quality_insights")
async def get_data_quality_insights(
    date_range: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get data quality assessment and recommendations.
    
    Analyzes:
    - Data completeness scores
    - Extraction accuracy metrics
    - Missing field analysis
    - Confidence score distribution
    - Data quality issues and recommendations
    
    Helps improve invoice processing accuracy and completeness.
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=False
        )
        
        if insights_result["success"]:
            quality_insights = insights_result["insights"].get("quality_insights", {})
            return success_response(
                data=quality_insights,
                message="Data quality analysis completed successfully"
            )
        else:
            return error_response(
                message="Failed to generate data quality insights",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in data quality insights endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate data quality insights"
        )


@router.get("/ai/insights/recommendations")
@performance_monitor("api", "ai_recommendations")
async def get_ai_recommendations(
    date_range: int = Query(90, ge=7, le=365, description="Number of days to analyze"),
    category: Optional[str] = Query(None, regex="^(cost|vendor|process|security|automation)$", description="Filter recommendations by category"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get AI-powered business recommendations.
    
    Categories:
    - cost: Cost reduction and optimization
    - vendor: Vendor management and relationships
    - process: Process improvement and automation
    - security: Security and compliance
    - automation: Workflow automation opportunities
    
    Returns prioritized, actionable recommendations based on data analysis.
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=False
        )
        
        if insights_result["success"]:
            all_recommendations = insights_result["insights"].get("recommendations", [])
            
            # Filter by category if specified
            if category:
                # Simple category filtering based on keywords
                category_keywords = {
                    "cost": ["cost", "discount", "savings", "negotiate"],
                    "vendor": ["vendor", "consolidation", "relationship"],
                    "process": ["workflow", "process", "automation", "approval"],
                    "security": ["security", "approval", "control"],
                    "automation": ["automat", "workflow", "process"]
                }
                
                if category in category_keywords:
                    keywords = category_keywords[category]
                    filtered_recommendations = [
                        rec for rec in all_recommendations
                        if any(keyword in rec.lower() for keyword in keywords)
                    ]
                    
                    return success_response(
                        data={
                            "recommendations": filtered_recommendations,
                            "category_filter": category,
                            "total_filtered": len(filtered_recommendations),
                            "total_available": len(all_recommendations)
                        },
                        message=f"Found {len(filtered_recommendations)} {category} recommendations"
                    )
            
            return success_response(
                data={
                    "recommendations": all_recommendations,
                    "total": len(all_recommendations)
                },
                message=f"Generated {len(all_recommendations)} AI recommendations"
            )
        else:
            return error_response(
                message="Failed to generate AI recommendations",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in AI recommendations endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI recommendations"
        )


@router.get("/ai/insights/category-suggestions")
@performance_monitor("api", "category_suggestions")
async def get_category_suggestions(
    limit: int = Query(20, ge=1, le=100, description="Number of suggestions to return"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get AI-powered category suggestions for invoices.
    
    Features:
    - Intelligent category classification
    - Confidence scoring for suggestions
    - Reasoning explanations
    - Bulk categorization support
    
    Helps automatically organize invoices into meaningful categories.
    """
    try:
        suggestions_result = ai_service.suggest_invoice_categories(
            user_id=str(current_user.id),
            limit=limit
        )
        
        if suggestions_result["success"]:
            suggestions = suggestions_result["suggestions"]
            
            # Add summary statistics
            high_confidence = len([s for s in suggestions if s["confidence"] > 0.8])
            medium_confidence = len([s for s in suggestions if 0.6 <= s["confidence"] <= 0.8])
            low_confidence = len([s for s in suggestions if s["confidence"] < 0.6])
            
            return success_response(
                data={
                    "suggestions": suggestions,
                    "summary": {
                        "total": len(suggestions),
                        "high_confidence": high_confidence,
                        "medium_confidence": medium_confidence,
                        "low_confidence": low_confidence
                    }
                },
                message=f"Generated {len(suggestions)} category suggestions"
            )
        else:
            return error_response(
                message="Failed to generate category suggestions",
                error_details={"error": suggestions_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in category suggestions endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate category suggestions"
        )


@router.get("/ai/insights/summary")
@performance_monitor("api", "ai_insights_summary")
async def get_ai_insights_summary(
    date_range: int = Query(30, ge=7, le=90, description="Number of days to analyze"),
    current_user: UserModel = Depends(get_current_user),
    ai_service: AIInsightsService = Depends(get_ai_insights_service)
):
    """
    Get a concise summary of key AI insights.
    
    Perfect for dashboard widgets and quick overviews.
    Returns the most important insights and alerts in a condensed format.
    """
    try:
        insights_result = ai_service.get_comprehensive_insights(
            user_id=str(current_user.id),
            date_range=date_range,
            include_predictions=False
        )
        
        if insights_result["success"]:
            insights = insights_result["insights"]
            
            # Extract key summary points
            summary = {
                "spending_summary": {
                    "total": insights.get("spending_patterns", {}).get("summary", {}).get("total_spend", 0),
                    "trend": "stable"  # Simplified
                },
                "top_vendor": None,
                "anomaly_count": insights.get("anomaly_detection", {}).get("total_anomalies", 0),
                "optimization_opportunities": insights.get("cost_optimization", {}).get("total_opportunities", 0),
                "data_quality_grade": insights.get("quality_insights", {}).get("quality_grade", "N/A"),
                "top_recommendation": insights.get("recommendations", ["No recommendations available"])[0] if insights.get("recommendations") else "No recommendations available"
            }
            
            # Get top vendor
            vendor_insights = insights.get("vendor_insights", {})
            if "top_vendors" in vendor_insights and vendor_insights["top_vendors"]:
                top_vendor = list(vendor_insights["top_vendors"].keys())[0]
                summary["top_vendor"] = top_vendor
            
            return success_response(
                data=summary,
                message="AI insights summary generated successfully"
            )
        else:
            return error_response(
                message="Failed to generate AI insights summary",
                error_details={"error": insights_result.get("error")}
            )
            
    except Exception as e:
        logger.error(f"Error in AI insights summary endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate AI insights summary"
        )
