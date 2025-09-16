"""
Advanced Analytics Service

Provides comprehensive analytics, reporting, and business intelligence
for invoice processing and management.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from decimal import Decimal

from sqlalchemy import func, and_, or_, extract, text
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.logging_config import performance_monitor
from app.models.database import InvoiceModel, CompanyModel, UserModel, LineItemModel, TaxCalculationModel

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Advanced analytics and reporting service."""
    
    def __init__(self):
        """Initialize analytics service."""
        pass
    
    @performance_monitor("analytics", "dashboard_metrics")
    def get_dashboard_analytics(self, user_id: str, date_range: int = 30) -> Dict[str, Any]:
        """Get comprehensive dashboard analytics."""
        try:
            with get_db_session() as session:
                end_date = datetime.utcnow()
                start_date = end_date - timedelta(days=date_range)
                
                # Base query for user's invoices
                base_query = session.query(InvoiceModel).filter(
                    InvoiceModel.user_id == user_id,
                    InvoiceModel.created_at >= start_date
                )
                
                analytics = {
                    "summary": self._get_summary_metrics(session, user_id, start_date, end_date),
                    "trends": self._get_trend_analysis(session, user_id, start_date, end_date),
                    "categories": self._get_category_analysis(session, user_id, start_date, end_date),
                    "vendors": self._get_vendor_analysis(session, user_id, start_date, end_date),
                    "processing": self._get_processing_analytics(session, user_id, start_date, end_date),
                    "time_analysis": self._get_time_based_analysis(session, user_id, start_date, end_date),
                    "financial": self._get_financial_insights(session, user_id, start_date, end_date)
                }
                
                return {
                    "success": True,
                    "data": analytics,
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                        "days": date_range
                    }
                }
                
        except Exception as e:
            logger.error(f"Error generating dashboard analytics for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def _get_summary_metrics(self, session: Session, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get summary metrics for the dashboard."""
        # Total invoices and amounts
        total_invoices = session.query(func.count(InvoiceModel.id)).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).scalar() or 0
        
        total_amount = session.query(func.sum(InvoiceModel.net_amount)).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date,
            InvoiceModel.net_amount.isnot(None)
        ).scalar() or Decimal('0')
        
        # Average processing confidence
        avg_confidence = session.query(func.avg(InvoiceModel.extraction_confidence)).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date,
            InvoiceModel.extraction_confidence.isnot(None)
        ).scalar() or 0
        
        # Unique vendors and customers
        unique_vendors = session.query(func.count(func.distinct(InvoiceModel.vendor_id))).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date,
            InvoiceModel.vendor_id.isnot(None)
        ).scalar() or 0
        
        unique_customers = session.query(func.count(func.distinct(InvoiceModel.customer_id))).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date,
            InvoiceModel.customer_id.isnot(None)
        ).scalar() or 0
        
        # Previous period comparison
        prev_start = start_date - (end_date - start_date)
        prev_invoices = session.query(func.count(InvoiceModel.id)).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= prev_start,
            InvoiceModel.created_at < start_date
        ).scalar() or 0
        
        prev_amount = session.query(func.sum(InvoiceModel.net_amount)).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= prev_start,
            InvoiceModel.created_at < start_date,
            InvoiceModel.net_amount.isnot(None)
        ).scalar() or Decimal('0')
        
        return {
            "total_invoices": total_invoices,
            "total_amount": float(total_amount),
            "average_amount": float(total_amount / total_invoices) if total_invoices > 0 else 0,
            "average_confidence": round(float(avg_confidence), 2) if avg_confidence else 0,
            "unique_vendors": unique_vendors,
            "unique_customers": unique_customers,
            "growth": {
                "invoices_change": ((total_invoices - prev_invoices) / prev_invoices * 100) if prev_invoices > 0 else 0,
                "amount_change": ((float(total_amount) - float(prev_amount)) / float(prev_amount) * 100) if prev_amount > 0 else 0
            }
        }
    
    def _get_trend_analysis(self, session: Session, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get trend analysis over time."""
        # Daily invoice counts and amounts
        daily_data = session.query(
            func.date(InvoiceModel.created_at).label('date'),
            func.count(InvoiceModel.id).label('count'),
            func.sum(InvoiceModel.net_amount).label('amount')
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).group_by(
            func.date(InvoiceModel.created_at)
        ).order_by('date').all()
        
        # Weekly aggregation
        weekly_data = session.query(
            extract('week', InvoiceModel.created_at).label('week'),
            extract('year', InvoiceModel.created_at).label('year'),
            func.count(InvoiceModel.id).label('count'),
            func.sum(InvoiceModel.net_amount).label('amount')
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).group_by(
            extract('week', InvoiceModel.created_at),
            extract('year', InvoiceModel.created_at)
        ).order_by('year', 'week').all()
        
        return {
            "daily": [
                {
                    "date": row.date.isoformat(),
                    "count": row.count,
                    "amount": float(row.amount or 0)
                }
                for row in daily_data
            ],
            "weekly": [
                {
                    "week": f"{row.year}-W{row.week:02d}",
                    "count": row.count,
                    "amount": float(row.amount or 0)
                }
                for row in weekly_data
            ]
        }
    
    def _get_category_analysis(self, session: Session, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get category-based analysis."""
        # Amount ranges
        amount_ranges = [
            ("0-100", 0, 100),
            ("100-500", 100, 500),
            ("500-1000", 500, 1000),
            ("1000-5000", 1000, 5000),
            ("5000+", 5000, float('inf'))
        ]
        
        range_data = []
        for label, min_amount, max_amount in amount_ranges:
            if max_amount == float('inf'):
                count = session.query(func.count(InvoiceModel.id)).filter(
                    InvoiceModel.user_id == user_id,
                    InvoiceModel.created_at >= start_date,
                    InvoiceModel.net_amount >= min_amount
                ).scalar() or 0
            else:
                count = session.query(func.count(InvoiceModel.id)).filter(
                    InvoiceModel.user_id == user_id,
                    InvoiceModel.created_at >= start_date,
                    InvoiceModel.net_amount >= min_amount,
                    InvoiceModel.net_amount < max_amount
                ).scalar() or 0
            
            range_data.append({
                "range": label,
                "count": count,
                "percentage": 0  # Will be calculated after getting total
            })
        
        # Calculate percentages
        total_invoices = sum(item["count"] for item in range_data)
        if total_invoices > 0:
            for item in range_data:
                item["percentage"] = round((item["count"] / total_invoices) * 100, 1)
        
        return {
            "amount_ranges": range_data,
            "currency_distribution": self._get_currency_distribution(session, user_id, start_date)
        }
    
    def _get_currency_distribution(self, session: Session, user_id: str, start_date: datetime) -> List[Dict[str, Any]]:
        """Get currency distribution."""
        currency_data = session.query(
            InvoiceModel.currency,
            func.count(InvoiceModel.id).label('count'),
            func.sum(InvoiceModel.net_amount).label('total_amount')
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date,
            InvoiceModel.currency.isnot(None)
        ).group_by(
            InvoiceModel.currency
        ).order_by(func.count(InvoiceModel.id).desc()).all()
        
        return [
            {
                "currency": row.currency,
                "count": row.count,
                "total_amount": float(row.total_amount or 0)
            }
            for row in currency_data
        ]
    
    def _get_vendor_analysis(self, session: Session, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get vendor analysis."""
        # Top vendors by transaction count
        top_vendors = session.query(
            CompanyModel.company_name,
            func.count(InvoiceModel.id).label('transaction_count'),
            func.sum(InvoiceModel.net_amount).label('total_amount'),
            func.avg(InvoiceModel.net_amount).label('avg_amount')
        ).join(
            InvoiceModel, InvoiceModel.vendor_id == CompanyModel.id
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).group_by(
            CompanyModel.id, CompanyModel.company_name
        ).order_by(
            func.count(InvoiceModel.id).desc()
        ).limit(10).all()
        
        # Top customers by amount
        top_customers = session.query(
            CompanyModel.company_name,
            func.count(InvoiceModel.id).label('transaction_count'),
            func.sum(InvoiceModel.net_amount).label('total_amount'),
            func.avg(InvoiceModel.net_amount).label('avg_amount')
        ).join(
            InvoiceModel, InvoiceModel.customer_id == CompanyModel.id
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).group_by(
            CompanyModel.id, CompanyModel.company_name
        ).order_by(
            func.sum(InvoiceModel.net_amount).desc()
        ).limit(10).all()
        
        return {
            "top_vendors": [
                {
                    "name": row.company_name,
                    "transaction_count": row.transaction_count,
                    "total_amount": float(row.total_amount or 0),
                    "average_amount": float(row.avg_amount or 0)
                }
                for row in top_vendors
            ],
            "top_customers": [
                {
                    "name": row.company_name,
                    "transaction_count": row.transaction_count,
                    "total_amount": float(row.total_amount or 0),
                    "average_amount": float(row.avg_amount or 0)
                }
                for row in top_customers
            ]
        }
    
    def _get_processing_analytics(self, session: Session, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get processing performance analytics."""
        # Confidence score distribution
        confidence_ranges = [
            ("Low (0-60%)", 0, 0.6),
            ("Medium (60-80%)", 0.6, 0.8),
            ("High (80-95%)", 0.8, 0.95),
            ("Excellent (95%+)", 0.95, 1.0)
        ]
        
        confidence_data = []
        for label, min_conf, max_conf in confidence_ranges:
            count = session.query(func.count(InvoiceModel.id)).filter(
                InvoiceModel.user_id == user_id,
                InvoiceModel.created_at >= start_date,
                InvoiceModel.extraction_confidence >= min_conf,
                InvoiceModel.extraction_confidence < max_conf if max_conf < 1.0 else InvoiceModel.extraction_confidence <= max_conf
            ).scalar() or 0
            
            confidence_data.append({
                "range": label,
                "count": count
            })
        
        # Average processing time (if tracked)
        # This would require additional tracking in the processing pipeline
        
        return {
            "confidence_distribution": confidence_data,
            "total_processed": sum(item["count"] for item in confidence_data)
        }
    
    def _get_time_based_analysis(self, session: Session, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get time-based processing patterns."""
        # Hour of day analysis
        hourly_data = session.query(
            extract('hour', InvoiceModel.created_at).label('hour'),
            func.count(InvoiceModel.id).label('count')
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).group_by(
            extract('hour', InvoiceModel.created_at)
        ).order_by('hour').all()
        
        # Day of week analysis
        dow_data = session.query(
            extract('dow', InvoiceModel.created_at).label('dow'),
            func.count(InvoiceModel.id).label('count')
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).group_by(
            extract('dow', InvoiceModel.created_at)
        ).order_by('dow').all()
        
        # Map day of week numbers to names
        dow_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        
        return {
            "hourly_pattern": [
                {
                    "hour": int(row.hour),
                    "count": row.count
                }
                for row in hourly_data
            ],
            "weekly_pattern": [
                {
                    "day": dow_names[int(row.dow)],
                    "day_number": int(row.dow),
                    "count": row.count
                }
                for row in dow_data
            ]
        }
    
    def _get_financial_insights(self, session: Session, user_id: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get financial insights and patterns."""
        # Tax analysis
        tax_data = session.query(
            func.sum(TaxCalculationModel.total_tax).label('total_tax'),
            func.avg(TaxCalculationModel.total_tax).label('avg_tax'),
            func.count(TaxCalculationModel.id).label('tax_invoices')
        ).join(
            InvoiceModel, TaxCalculationModel.invoice_id == InvoiceModel.id
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).first()
        
        # Monthly financial summary
        monthly_data = session.query(
            extract('year', InvoiceModel.created_at).label('year'),
            extract('month', InvoiceModel.created_at).label('month'),
            func.count(InvoiceModel.id).label('count'),
            func.sum(InvoiceModel.net_amount).label('total_amount'),
            func.avg(InvoiceModel.net_amount).label('avg_amount')
        ).filter(
            InvoiceModel.user_id == user_id,
            InvoiceModel.created_at >= start_date
        ).group_by(
            extract('year', InvoiceModel.created_at),
            extract('month', InvoiceModel.created_at)
        ).order_by('year', 'month').all()
        
        return {
            "tax_summary": {
                "total_tax": float(tax_data.total_tax or 0),
                "average_tax": float(tax_data.avg_tax or 0),
                "invoices_with_tax": tax_data.tax_invoices or 0
            },
            "monthly_summary": [
                {
                    "period": f"{int(row.year)}-{int(row.month):02d}",
                    "count": row.count,
                    "total_amount": float(row.total_amount or 0),
                    "average_amount": float(row.avg_amount or 0)
                }
                for row in monthly_data
            ]
        }
    
    @performance_monitor("analytics", "export_data")
    def export_analytics_data(self, user_id: str, format_type: str = "json", date_range: int = 30) -> Dict[str, Any]:
        """Export analytics data in various formats."""
        try:
            analytics_data = self.get_dashboard_analytics(user_id, date_range)
            
            if not analytics_data["success"]:
                return analytics_data
            
            if format_type.lower() == "csv":
                # Convert to CSV format
                return self._convert_to_csv(analytics_data["data"])
            elif format_type.lower() == "pdf":
                # Generate PDF report
                return self._generate_pdf_report(analytics_data["data"])
            else:
                # Return JSON format
                return analytics_data
                
        except Exception as e:
            logger.error(f"Error exporting analytics data for user {user_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _convert_to_csv(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert analytics data to CSV format."""
        # This would implement CSV conversion logic
        return {
            "success": True,
            "format": "csv",
            "data": "CSV conversion not implemented yet"
        }
    
    def _generate_pdf_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PDF analytics report."""
        # This would implement PDF generation logic
        return {
            "success": True,
            "format": "pdf",
            "data": "PDF generation not implemented yet"
        }


# Export analytics service
__all__ = ["AnalyticsService"]
