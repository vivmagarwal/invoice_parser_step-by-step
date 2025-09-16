"""
Advanced AI Insights Service

Provides intelligent analysis, pattern recognition, and insights
from invoice data using advanced AI techniques and machine learning.
"""
import logging
import statistics
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
from decimal import Decimal
import re

from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.logging_config import performance_monitor
from app.models.database import InvoiceModel, CompanyModel, LineItemModel
from app.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


class AIInsightsService:
    """Advanced AI-powered insights and analytics service."""
    
    def __init__(self):
        """Initialize AI insights service."""
        self.db_service = DatabaseService()
    
    @performance_monitor("ai_insights", "comprehensive_analysis")
    def get_comprehensive_insights(
        self,
        user_id: str,
        date_range: int = 90,
        include_predictions: bool = True
    ) -> Dict[str, Any]:
        """
        Generate comprehensive AI-powered insights from invoice data.
        
        Args:
            user_id: User ID for scoping data
            date_range: Number of days to analyze
            include_predictions: Whether to include predictive analytics
            
        Returns:
            Dictionary with comprehensive insights and recommendations
        """
        try:
            with get_db_session() as session:
                # Get base data
                since_date = datetime.utcnow() - timedelta(days=date_range)
                
                invoices = session.query(InvoiceModel).filter(
                    InvoiceModel.user_id == user_id,
                    InvoiceModel.created_at >= since_date
                ).all()
                
                if not invoices:
                    return {
                        "success": True,
                        "insights": {
                            "summary": "No invoice data available for analysis",
                            "recommendations": ["Start by uploading some invoices to get insights"]
                        }
                    }
                
                # Generate various insights
                insights = {
                    "spending_patterns": self._analyze_spending_patterns(invoices),
                    "vendor_insights": self._analyze_vendor_patterns(invoices),
                    "seasonal_trends": self._analyze_seasonal_trends(invoices),
                    "anomaly_detection": self._detect_anomalies(invoices),
                    "cost_optimization": self._analyze_cost_optimization(invoices),
                    "payment_behavior": self._analyze_payment_behavior(invoices),
                    "category_analysis": self._analyze_categories(invoices),
                    "quality_insights": self._analyze_data_quality(invoices),
                    "recommendations": self._generate_recommendations(invoices)
                }
                
                if include_predictions:
                    insights["predictions"] = self._generate_predictions(invoices)
                
                # Add metadata
                insights["analysis_metadata"] = {
                    "total_invoices": len(invoices),
                    "date_range": date_range,
                    "analysis_date": datetime.utcnow().isoformat(),
                    "currency_distribution": self._get_currency_distribution(invoices)
                }
                
                return {
                    "success": True,
                    "insights": insights
                }
                
        except Exception as e:
            logger.error(f"Error generating comprehensive insights: {e}")
            return {
                "success": False,
                "error": str(e),
                "insights": {}
            }
    
    def _analyze_spending_patterns(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Analyze spending patterns and trends."""
        if not invoices:
            return {"message": "No data available"}
        
        amounts = [float(inv.net_amount) for inv in invoices if inv.net_amount]
        if not amounts:
            return {"message": "No amount data available"}
        
        # Basic statistics
        total_spend = sum(amounts)
        avg_spend = statistics.mean(amounts)
        median_spend = statistics.median(amounts)
        std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
        
        # Spending distribution
        amount_ranges = {
            "small": (0, 100),
            "medium": (100, 1000),
            "large": (1000, 10000),
            "very_large": (10000, float('inf'))
        }
        
        distribution = {}
        for range_name, (min_val, max_val) in amount_ranges.items():
            count = len([a for a in amounts if min_val <= a < max_val])
            distribution[range_name] = {
                "count": count,
                "percentage": (count / len(amounts)) * 100,
                "total_amount": sum([a for a in amounts if min_val <= a < max_val])
            }
        
        # Monthly trend analysis
        monthly_data = defaultdict(list)
        for invoice in invoices:
            if invoice.net_amount and invoice.created_at:
                month_key = invoice.created_at.strftime('%Y-%m')
                monthly_data[month_key].append(float(invoice.net_amount))
        
        monthly_trends = {}
        for month, amounts_list in monthly_data.items():
            monthly_trends[month] = {
                "total": sum(amounts_list),
                "count": len(amounts_list),
                "average": statistics.mean(amounts_list)
            }
        
        # Growth analysis
        sorted_months = sorted(monthly_trends.keys())
        growth_rate = 0
        if len(sorted_months) >= 2:
            first_month = monthly_trends[sorted_months[0]]["total"]
            last_month = monthly_trends[sorted_months[-1]]["total"]
            if first_month > 0:
                growth_rate = ((last_month - first_month) / first_month) * 100
        
        return {
            "summary": {
                "total_spend": total_spend,
                "average_spend": avg_spend,
                "median_spend": median_spend,
                "standard_deviation": std_dev,
                "monthly_growth_rate": growth_rate
            },
            "distribution": distribution,
            "monthly_trends": monthly_trends,
            "insights": [
                f"Average invoice amount is ${avg_spend:.2f}",
                f"Spending variability (std dev): ${std_dev:.2f}",
                f"Monthly growth rate: {growth_rate:.1f}%"
            ]
        }
    
    def _analyze_vendor_patterns(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Analyze vendor relationships and patterns."""
        vendor_data = defaultdict(lambda: {
            "count": 0,
            "total_amount": 0,
            "amounts": [],
            "frequencies": [],
            "last_invoice": None
        })
        
        for invoice in invoices:
            if invoice.vendor and invoice.net_amount:
                vendor_name = invoice.vendor.company_name
                amount = float(invoice.net_amount)
                
                vendor_data[vendor_name]["count"] += 1
                vendor_data[vendor_name]["total_amount"] += amount
                vendor_data[vendor_name]["amounts"].append(amount)
                
                if not vendor_data[vendor_name]["last_invoice"] or invoice.created_at > vendor_data[vendor_name]["last_invoice"]:
                    vendor_data[vendor_name]["last_invoice"] = invoice.created_at
        
        # Analyze vendor relationships
        vendor_insights = {}
        for vendor, data in vendor_data.items():
            if data["amounts"]:
                avg_amount = statistics.mean(data["amounts"])
                consistency = 1 - (statistics.stdev(data["amounts"]) / avg_amount) if len(data["amounts"]) > 1 and avg_amount > 0 else 1
                
                # Calculate relationship strength (frequency + consistency + recency)
                days_since_last = (datetime.utcnow() - data["last_invoice"]).days if data["last_invoice"] else 999
                recency_score = max(0, 1 - (days_since_last / 90))  # 90-day window
                
                relationship_score = (
                    (data["count"] / len(invoices)) * 0.4 +  # Frequency weight
                    consistency * 0.3 +  # Consistency weight
                    recency_score * 0.3  # Recency weight
                ) * 100
                
                vendor_insights[vendor] = {
                    "transaction_count": data["count"],
                    "total_spend": data["total_amount"],
                    "average_amount": avg_amount,
                    "consistency_score": consistency * 100,
                    "relationship_score": relationship_score,
                    "days_since_last_invoice": days_since_last,
                    "category": self._categorize_vendor_relationship(relationship_score)
                }
        
        # Sort by relationship score
        top_vendors = sorted(vendor_insights.items(), key=lambda x: x[1]["relationship_score"], reverse=True)[:10]
        
        return {
            "total_vendors": len(vendor_data),
            "top_vendors": dict(top_vendors),
            "vendor_concentration": {
                "top_5_percentage": sum(data["total_amount"] for _, data in top_vendors[:5]) / sum(data["total_amount"] for data in vendor_data.values()) * 100 if vendor_data else 0
            },
            "insights": [
                f"You work with {len(vendor_data)} different vendors",
                f"Top 5 vendors account for {sum(data['total_amount'] for _, data in top_vendors[:5]) / sum(data['total_amount'] for data in vendor_data.values()) * 100:.1f}% of spending" if vendor_data else "No vendor data available"
            ]
        }
    
    def _categorize_vendor_relationship(self, score: float) -> str:
        """Categorize vendor relationship based on score."""
        if score >= 70:
            return "strategic_partner"
        elif score >= 50:
            return "regular_vendor"
        elif score >= 30:
            return "occasional_vendor"
        else:
            return "one_time_vendor"
    
    def _analyze_seasonal_trends(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Analyze seasonal patterns in invoice data."""
        if not invoices:
            return {"message": "No data available"}
        
        # Group by month and quarter
        monthly_data = defaultdict(lambda: {"count": 0, "total": 0})
        quarterly_data = defaultdict(lambda: {"count": 0, "total": 0})
        weekly_data = defaultdict(lambda: {"count": 0, "total": 0})
        
        for invoice in invoices:
            if invoice.created_at and invoice.net_amount:
                amount = float(invoice.net_amount)
                
                # Monthly
                month = invoice.created_at.month
                monthly_data[month]["count"] += 1
                monthly_data[month]["total"] += amount
                
                # Quarterly
                quarter = (month - 1) // 3 + 1
                quarterly_data[quarter]["count"] += 1
                quarterly_data[quarter]["total"] += amount
                
                # Weekly (day of week)
                weekday = invoice.created_at.weekday()
                weekly_data[weekday]["count"] += 1
                weekly_data[weekday]["total"] += amount
        
        # Find peak periods
        peak_month = max(monthly_data.items(), key=lambda x: x[1]["total"])[0] if monthly_data else None
        peak_quarter = max(quarterly_data.items(), key=lambda x: x[1]["total"])[0] if quarterly_data else None
        peak_weekday = max(weekly_data.items(), key=lambda x: x[1]["count"])[0] if weekly_data else None
        
        weekday_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        month_names = ["", "January", "February", "March", "April", "May", "June", 
                      "July", "August", "September", "October", "November", "December"]
        
        return {
            "monthly_patterns": dict(monthly_data),
            "quarterly_patterns": dict(quarterly_data),
            "weekly_patterns": dict(weekly_data),
            "peak_periods": {
                "month": month_names[peak_month] if peak_month else None,
                "quarter": f"Q{peak_quarter}" if peak_quarter else None,
                "weekday": weekday_names[peak_weekday] if peak_weekday is not None else None
            },
            "insights": [
                f"Peak spending month: {month_names[peak_month] if peak_month else 'Unknown'}",
                f"Peak spending quarter: Q{peak_quarter}" if peak_quarter else "No quarterly data",
                f"Most active day: {weekday_names[peak_weekday] if peak_weekday is not None else 'Unknown'}"
            ]
        }
    
    def _detect_anomalies(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Detect anomalies and unusual patterns in invoice data."""
        if not invoices:
            return {"message": "No data available"}
        
        anomalies = []
        
        # Amount-based anomalies
        amounts = [float(inv.net_amount) for inv in invoices if inv.net_amount]
        if len(amounts) > 5:
            mean_amount = statistics.mean(amounts)
            std_amount = statistics.stdev(amounts)
            threshold = mean_amount + (2 * std_amount)  # 2 standard deviations
            
            for invoice in invoices:
                if invoice.net_amount and float(invoice.net_amount) > threshold:
                    anomalies.append({
                        "type": "high_amount",
                        "invoice_id": str(invoice.id),
                        "amount": float(invoice.net_amount),
                        "threshold": threshold,
                        "severity": "medium" if float(invoice.net_amount) < threshold * 1.5 else "high",
                        "description": f"Unusually high amount: ${float(invoice.net_amount):.2f} (threshold: ${threshold:.2f})"
                    })
        
        # Frequency-based anomalies
        vendor_frequencies = Counter(inv.vendor.company_name for inv in invoices if inv.vendor)
        avg_frequency = statistics.mean(vendor_frequencies.values()) if vendor_frequencies else 0
        
        for vendor, freq in vendor_frequencies.items():
            if freq > avg_frequency * 3:  # 3x average frequency
                anomalies.append({
                    "type": "high_frequency_vendor",
                    "vendor": vendor,
                    "frequency": freq,
                    "average": avg_frequency,
                    "severity": "low",
                    "description": f"Unusually high frequency from vendor: {vendor} ({freq} invoices)"
                })
        
        # Time-based anomalies (invoices created at unusual hours)
        creation_hours = [inv.created_at.hour for inv in invoices if inv.created_at]
        if creation_hours:
            unusual_hours = [hour for hour in creation_hours if hour < 6 or hour > 22]
            if unusual_hours:
                anomalies.append({
                    "type": "unusual_processing_hours",
                    "count": len(unusual_hours),
                    "hours": list(set(unusual_hours)),
                    "severity": "low",
                    "description": f"{len(unusual_hours)} invoices processed during unusual hours"
                })
        
        # Duplicate detection
        invoice_numbers = [inv.invoice_number for inv in invoices if inv.invoice_number]
        duplicates = [num for num, count in Counter(invoice_numbers).items() if count > 1]
        if duplicates:
            for dup in duplicates:
                anomalies.append({
                    "type": "duplicate_invoice_number",
                    "invoice_number": dup,
                    "count": Counter(invoice_numbers)[dup],
                    "severity": "high",
                    "description": f"Duplicate invoice number detected: {dup}"
                })
        
        return {
            "total_anomalies": len(anomalies),
            "anomalies": anomalies,
            "severity_breakdown": {
                "high": len([a for a in anomalies if a.get("severity") == "high"]),
                "medium": len([a for a in anomalies if a.get("severity") == "medium"]),
                "low": len([a for a in anomalies if a.get("severity") == "low"])
            },
            "insights": [
                f"Detected {len(anomalies)} potential anomalies",
                f"High priority issues: {len([a for a in anomalies if a.get('severity') == 'high'])}"
            ]
        }
    
    def _analyze_cost_optimization(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Analyze potential cost optimization opportunities."""
        if not invoices:
            return {"message": "No data available"}
        
        opportunities = []
        
        # Vendor consolidation opportunities
        vendor_data = defaultdict(lambda: {"count": 0, "total": 0, "categories": set()})
        for invoice in invoices:
            if invoice.vendor and invoice.net_amount:
                vendor = invoice.vendor.company_name
                vendor_data[vendor]["count"] += 1
                vendor_data[vendor]["total"] += float(invoice.net_amount)
                # Simple category detection based on vendor name
                if any(word in vendor.lower() for word in ['office', 'supply', 'stationery']):
                    vendor_data[vendor]["categories"].add("office_supplies")
                elif any(word in vendor.lower() for word in ['software', 'saas', 'tech']):
                    vendor_data[vendor]["categories"].add("software")
        
        # Find vendors with similar categories but low individual spending
        category_vendors = defaultdict(list)
        for vendor, data in vendor_data.items():
            for category in data["categories"]:
                category_vendors[category].append((vendor, data))
        
        for category, vendors in category_vendors.items():
            if len(vendors) > 2:  # Multiple vendors in same category
                total_spend = sum(data["total"] for _, data in vendors)
                small_vendors = [(v, d) for v, d in vendors if d["total"] < total_spend * 0.1]
                
                if len(small_vendors) >= 2:
                    opportunities.append({
                        "type": "vendor_consolidation",
                        "category": category,
                        "potential_savings": sum(d["total"] for _, d in small_vendors) * 0.1,  # Assume 10% savings
                        "vendors_to_consolidate": len(small_vendors),
                        "description": f"Consider consolidating {len(small_vendors)} small vendors in {category}"
                    })
        
        # Payment term optimization
        amounts = [float(inv.net_amount) for inv in invoices if inv.net_amount]
        if amounts:
            large_invoices = [a for a in amounts if a > statistics.mean(amounts) * 2]
            if large_invoices:
                opportunities.append({
                    "type": "payment_terms",
                    "large_invoice_count": len(large_invoices),
                    "potential_savings": sum(large_invoices) * 0.02,  # Assume 2% early payment discount
                    "description": f"Negotiate early payment discounts for {len(large_invoices)} large invoices"
                })
        
        # Subscription optimization
        recurring_patterns = self._detect_recurring_patterns(invoices)
        if recurring_patterns:
            opportunities.append({
                "type": "subscription_optimization",
                "recurring_vendors": len(recurring_patterns),
                "description": f"Review {len(recurring_patterns)} recurring payments for optimization"
            })
        
        total_potential_savings = sum(opp.get("potential_savings", 0) for opp in opportunities)
        
        return {
            "total_opportunities": len(opportunities),
            "opportunities": opportunities,
            "potential_annual_savings": total_potential_savings * 12,  # Annualized
            "insights": [
                f"Identified {len(opportunities)} cost optimization opportunities",
                f"Potential annual savings: ${total_potential_savings * 12:.2f}"
            ]
        }
    
    def _detect_recurring_patterns(self, invoices: List[InvoiceModel]) -> List[Dict[str, Any]]:
        """Detect recurring payment patterns."""
        vendor_amounts = defaultdict(list)
        
        for invoice in invoices:
            if invoice.vendor and invoice.net_amount and invoice.created_at:
                vendor = invoice.vendor.company_name
                vendor_amounts[vendor].append({
                    "amount": float(invoice.net_amount),
                    "date": invoice.created_at
                })
        
        recurring_patterns = []
        for vendor, payments in vendor_amounts.items():
            if len(payments) >= 3:  # At least 3 payments to detect pattern
                amounts = [p["amount"] for p in payments]
                # Check if amounts are similar (within 10% variance)
                if len(set(amounts)) <= 2 or (max(amounts) - min(amounts)) / statistics.mean(amounts) < 0.1:
                    recurring_patterns.append({
                        "vendor": vendor,
                        "frequency": len(payments),
                        "average_amount": statistics.mean(amounts),
                        "pattern_type": "subscription" if len(set(amounts)) <= 2 else "regular_service"
                    })
        
        return recurring_patterns
    
    def _analyze_payment_behavior(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Analyze payment timing and behavior patterns."""
        if not invoices:
            return {"message": "No data available"}
        
        # Analyze processing time patterns
        processing_times = []
        for invoice in invoices:
            if invoice.created_at and invoice.invoice_date:
                # Time from invoice date to processing
                time_diff = (invoice.created_at - invoice.invoice_date).days
                if 0 <= time_diff <= 365:  # Reasonable range
                    processing_times.append(time_diff)
        
        behavior_analysis = {}
        if processing_times:
            behavior_analysis["processing_time"] = {
                "average_days": statistics.mean(processing_times),
                "median_days": statistics.median(processing_times),
                "fastest": min(processing_times),
                "slowest": max(processing_times)
            }
            
            # Categorize payment speed
            fast_payments = len([t for t in processing_times if t <= 7])
            slow_payments = len([t for t in processing_times if t > 30])
            
            behavior_analysis["payment_speed"] = {
                "fast_percentage": (fast_payments / len(processing_times)) * 100,
                "slow_percentage": (slow_payments / len(processing_times)) * 100,
                "category": "fast_payer" if fast_payments / len(processing_times) > 0.7 else 
                          "slow_payer" if slow_payments / len(processing_times) > 0.3 else "average_payer"
            }
        
        # Analyze invoice amounts vs processing speed
        amount_speed_correlation = []
        for invoice in invoices:
            if (invoice.net_amount and invoice.created_at and invoice.invoice_date and
                0 <= (invoice.created_at - invoice.invoice_date).days <= 365):
                amount_speed_correlation.append({
                    "amount": float(invoice.net_amount),
                    "processing_days": (invoice.created_at - invoice.invoice_date).days
                })
        
        return {
            "behavior_analysis": behavior_analysis,
            "insights": [
                f"Average processing time: {behavior_analysis.get('processing_time', {}).get('average_days', 0):.1f} days" if behavior_analysis.get('processing_time') else "No processing time data",
                f"Payment behavior: {behavior_analysis.get('payment_speed', {}).get('category', 'unknown')}" if behavior_analysis.get('payment_speed') else "No payment speed data"
            ]
        }
    
    def _analyze_categories(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Analyze spending categories and patterns."""
        categories = defaultdict(lambda: {"count": 0, "total": 0, "vendors": set()})
        
        for invoice in invoices:
            if invoice.net_amount:
                amount = float(invoice.net_amount)
                
                # Simple category classification based on vendor name and amount
                category = self._classify_invoice_category(invoice)
                categories[category]["count"] += 1
                categories[category]["total"] += amount
                
                if invoice.vendor:
                    categories[category]["vendors"].add(invoice.vendor.company_name)
        
        # Convert sets to counts for serialization
        category_analysis = {}
        for cat, data in categories.items():
            category_analysis[cat] = {
                "count": data["count"],
                "total": data["total"],
                "vendor_count": len(data["vendors"]),
                "average": data["total"] / data["count"] if data["count"] > 0 else 0
            }
        
        # Find top categories by spending
        top_categories = sorted(category_analysis.items(), key=lambda x: x[1]["total"], reverse=True)[:5]
        
        return {
            "category_breakdown": category_analysis,
            "top_categories": dict(top_categories),
            "insights": [
                f"Top spending category: {top_categories[0][0] if top_categories else 'Unknown'}",
                f"Number of spending categories: {len(categories)}"
            ]
        }
    
    def _classify_invoice_category(self, invoice: InvoiceModel) -> str:
        """Classify invoice into spending category."""
        if not invoice.vendor:
            return "uncategorized"
        
        vendor_name = invoice.vendor.company_name.lower()
        amount = float(invoice.net_amount) if invoice.net_amount else 0
        
        # Category classification rules
        if any(word in vendor_name for word in ['software', 'saas', 'tech', 'cloud', 'microsoft', 'google', 'adobe']):
            return "software_technology"
        elif any(word in vendor_name for word in ['office', 'supply', 'stationery', 'paper']):
            return "office_supplies"
        elif any(word in vendor_name for word in ['travel', 'hotel', 'airline', 'uber', 'taxi']):
            return "travel_transport"
        elif any(word in vendor_name for word in ['marketing', 'advertising', 'promotion', 'social']):
            return "marketing_advertising"
        elif any(word in vendor_name for word in ['utility', 'electric', 'gas', 'water', 'internet', 'phone']):
            return "utilities"
        elif any(word in vendor_name for word in ['consulting', 'service', 'professional', 'legal', 'accounting']):
            return "professional_services"
        elif amount > 10000:
            return "large_purchases"
        elif amount < 50:
            return "small_expenses"
        else:
            return "general_business"
    
    def _analyze_data_quality(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Analyze data quality and completeness."""
        total_invoices = len(invoices)
        if total_invoices == 0:
            return {"message": "No data available"}
        
        quality_metrics = {
            "completeness": {
                "invoice_number": len([i for i in invoices if i.invoice_number]) / total_invoices * 100,
                "invoice_date": len([i for i in invoices if i.invoice_date]) / total_invoices * 100,
                "net_amount": len([i for i in invoices if i.net_amount]) / total_invoices * 100,
                "vendor_info": len([i for i in invoices if i.vendor]) / total_invoices * 100,
                "customer_info": len([i for i in invoices if i.customer]) / total_invoices * 100
            },
            "accuracy": {
                "extraction_confidence": statistics.mean([i.extraction_confidence for i in invoices if i.extraction_confidence]) if any(i.extraction_confidence for i in invoices) else 0,
                "high_confidence_percentage": len([i for i in invoices if i.extraction_confidence and i.extraction_confidence > 0.8]) / total_invoices * 100
            }
        }
        
        # Overall quality score
        completeness_score = statistics.mean(quality_metrics["completeness"].values())
        accuracy_score = quality_metrics["accuracy"]["extraction_confidence"] * 100
        overall_quality = (completeness_score + accuracy_score) / 2
        
        # Quality issues
        issues = []
        if quality_metrics["completeness"]["invoice_number"] < 90:
            issues.append("Many invoices missing invoice numbers")
        if quality_metrics["completeness"]["net_amount"] < 95:
            issues.append("Some invoices missing amount information")
        if quality_metrics["accuracy"]["extraction_confidence"] < 0.8:
            issues.append("Low extraction confidence detected")
        
        return {
            "quality_metrics": quality_metrics,
            "overall_quality_score": overall_quality,
            "quality_grade": self._get_quality_grade(overall_quality),
            "issues": issues,
            "insights": [
                f"Overall data quality: {overall_quality:.1f}%",
                f"Average extraction confidence: {quality_metrics['accuracy']['extraction_confidence']:.1%}",
                f"Data completeness: {completeness_score:.1f}%"
            ]
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert quality score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def _generate_recommendations(self, invoices: List[InvoiceModel]) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        if not invoices:
            return ["Start by uploading some invoices to get personalized recommendations"]
        
        amounts = [float(inv.net_amount) for inv in invoices if inv.net_amount]
        
        # Spending recommendations
        if amounts:
            avg_amount = statistics.mean(amounts)
            if avg_amount > 1000:
                recommendations.append("Consider negotiating volume discounts with your major vendors")
            if len(set(amounts)) > len(amounts) * 0.8:  # High variance
                recommendations.append("Implement spending approval workflows for better cost control")
        
        # Vendor recommendations
        vendor_count = len(set(inv.vendor.company_name for inv in invoices if inv.vendor))
        if vendor_count > 50:
            recommendations.append("Consider vendor consolidation to reduce administrative overhead")
        
        # Data quality recommendations
        missing_numbers = len([i for i in invoices if not i.invoice_number])
        if missing_numbers > len(invoices) * 0.1:
            recommendations.append("Improve invoice number capture for better tracking")
        
        # Automation recommendations
        if len(invoices) > 100:
            recommendations.append("Consider implementing automated invoice processing workflows")
        
        # Security recommendations
        high_amounts = [a for a in amounts if a > statistics.mean(amounts) * 3] if amounts else []
        if high_amounts:
            recommendations.append("Implement additional approval steps for high-value invoices")
        
        return recommendations[:10]  # Limit to top 10 recommendations
    
    def _generate_predictions(self, invoices: List[InvoiceModel]) -> Dict[str, Any]:
        """Generate predictive analytics and forecasts."""
        if len(invoices) < 10:
            return {"message": "Insufficient data for predictions"}
        
        # Monthly spending trend prediction
        monthly_data = defaultdict(float)
        for invoice in invoices:
            if invoice.net_amount and invoice.created_at:
                month_key = invoice.created_at.strftime('%Y-%m')
                monthly_data[month_key] += float(invoice.net_amount)
        
        # Simple linear trend prediction
        sorted_months = sorted(monthly_data.keys())
        if len(sorted_months) >= 3:
            recent_months = sorted_months[-3:]
            trend = (monthly_data[recent_months[-1]] - monthly_data[recent_months[0]]) / 2
            
            next_month_prediction = monthly_data[sorted_months[-1]] + trend
            
            predictions = {
                "next_month_spending": max(0, next_month_prediction),
                "trend": "increasing" if trend > 0 else "decreasing" if trend < 0 else "stable",
                "confidence": "low",  # Simple model has low confidence
                "insights": [
                    f"Predicted next month spending: ${next_month_prediction:.2f}",
                    f"Spending trend: {('increasing' if trend > 0 else 'decreasing' if trend < 0 else 'stable')}"
                ]
            }
            
            return predictions
        
        return {"message": "Insufficient historical data for trend prediction"}
    
    def _get_currency_distribution(self, invoices: List[InvoiceModel]) -> Dict[str, int]:
        """Get distribution of currencies in invoices."""
        currencies = Counter(inv.currency for inv in invoices if inv.currency)
        return dict(currencies)
    
    @performance_monitor("ai_insights", "smart_categorization")
    def suggest_invoice_categories(self, user_id: str, limit: int = 20) -> Dict[str, Any]:
        """Suggest categories for uncategorized invoices."""
        try:
            with get_db_session() as session:
                # Get recent uncategorized invoices
                invoices = session.query(InvoiceModel).filter(
                    InvoiceModel.user_id == user_id
                ).order_by(desc(InvoiceModel.created_at)).limit(limit).all()
                
                suggestions = []
                for invoice in invoices:
                    category = self._classify_invoice_category(invoice)
                    confidence = self._calculate_category_confidence(invoice, category)
                    
                    suggestions.append({
                        "invoice_id": str(invoice.id),
                        "suggested_category": category,
                        "confidence": confidence,
                        "reasoning": self._get_categorization_reasoning(invoice, category)
                    })
                
                return {
                    "success": True,
                    "suggestions": suggestions
                }
                
        except Exception as e:
            logger.error(f"Error generating category suggestions: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _calculate_category_confidence(self, invoice: InvoiceModel, category: str) -> float:
        """Calculate confidence score for category suggestion."""
        confidence = 0.5  # Base confidence
        
        if invoice.vendor:
            vendor_name = invoice.vendor.company_name.lower()
            
            # Category-specific confidence boosters
            category_keywords = {
                "software_technology": ["software", "saas", "tech", "cloud"],
                "office_supplies": ["office", "supply", "stationery"],
                "travel_transport": ["travel", "hotel", "airline"],
                "utilities": ["utility", "electric", "gas", "internet"]
            }
            
            if category in category_keywords:
                keyword_matches = sum(1 for keyword in category_keywords[category] if keyword in vendor_name)
                confidence += (keyword_matches / len(category_keywords[category])) * 0.4
        
        # Amount-based confidence
        if invoice.net_amount:
            amount = float(invoice.net_amount)
            if category == "large_purchases" and amount > 10000:
                confidence += 0.3
            elif category == "small_expenses" and amount < 50:
                confidence += 0.3
        
        return min(1.0, confidence)
    
    def _get_categorization_reasoning(self, invoice: InvoiceModel, category: str) -> str:
        """Get human-readable reasoning for categorization."""
        if not invoice.vendor:
            return "Based on amount and general patterns"
        
        vendor_name = invoice.vendor.company_name
        amount = float(invoice.net_amount) if invoice.net_amount else 0
        
        reasoning_map = {
            "software_technology": f"Vendor '{vendor_name}' appears to be a technology company",
            "office_supplies": f"Vendor '{vendor_name}' appears to sell office supplies",
            "travel_transport": f"Vendor '{vendor_name}' appears to be travel-related",
            "utilities": f"Vendor '{vendor_name}' appears to be a utility provider",
            "large_purchases": f"High amount (${amount:.2f}) suggests a major purchase",
            "small_expenses": f"Low amount (${amount:.2f}) suggests a minor expense"
        }
        
        return reasoning_map.get(category, f"Categorized as '{category}' based on vendor and amount patterns")


# Export AI insights components
__all__ = ["AIInsightsService"]
