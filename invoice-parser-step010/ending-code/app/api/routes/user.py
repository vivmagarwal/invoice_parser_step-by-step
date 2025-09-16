"""
User Context Routes

Provides user-specific context information for intelligent routing.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.database_service import DatabaseService
from app.models.database import UserModel
from app.api.routes.auth import get_current_user
from app.api.dependencies import get_database_service

router = APIRouter(tags=["user"])

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/user/invoice-count")
async def get_user_invoice_count(
    current_user: UserModel = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Get user's invoice count for contextual routing.
    
    Returns:
        - count: Number of invoices processed by user
        - has_invoices: Boolean indicating if user has any invoices
        - recommended_view: Suggested view based on user experience
    """
    try:
        # Get user's invoice count
        result = db_service.get_user_invoices(str(current_user.id), page=1, limit=1)
        invoice_count = result["pagination"]["total"]
        
        # Determine recommended view
        if invoice_count == 0:
            recommended_view = "processing"
        else:
            recommended_view = "dashboard"
        
        logger.info(f"User {current_user.email} has {invoice_count} invoices, recommending {recommended_view}")
        
        return {
            "count": invoice_count,
            "has_invoices": invoice_count > 0,
            "recommended_view": recommended_view,
            "user_id": str(current_user.id),
            "username": current_user.email
        }
        
    except Exception as e:
        logger.error(f"Error getting invoice count for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user invoice count"
        )


@router.get("/user/status")
async def get_user_status(
    current_user: UserModel = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Get comprehensive user status for UI decisions.
    
    Returns:
        - is_new_user: True if user has no invoices
        - recommended_view: View to show user
        - user_info: Basic user information
        - quick_stats: Summary statistics
    """
    try:
        # Get user's invoice count and recent activity
        invoices_result = db_service.get_user_invoices(str(current_user.id), page=1, limit=5)
        invoice_count = invoices_result["pagination"]["total"]
        recent_invoices = invoices_result["invoices"]
        
        # Determine user status
        is_new_user = invoice_count == 0
        recommended_view = "processing" if is_new_user else "dashboard"
        
        # Get user creation date for "member since"
        member_since = current_user.created_at.isoformat()
        
        response_data = {
            "is_new_user": is_new_user,
            "recommended_view": recommended_view,
            "user_info": {
                "id": str(current_user.id),
                "username": current_user.email,
                "full_name": current_user.full_name,
                "member_since": member_since
            },
            "quick_stats": {
                "total_invoices": invoice_count,
                "recent_invoices_count": len(recent_invoices),
                "has_recent_activity": len(recent_invoices) > 0
            },
            "recent_invoices": recent_invoices[:3] if recent_invoices else []  # Show last 3 for quick access
        }
        
        logger.info(f"User status for {current_user.email}: new_user={is_new_user}, view={recommended_view}")
        return response_data
        
    except Exception as e:
        logger.error(f"Error getting user status for {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user status"
        )
