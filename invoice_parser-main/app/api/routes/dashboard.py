"""
Dashboard Routes

Handles user dashboard functionality including invoice history and statistics.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, Query, status

from app.services.database_service import DatabaseService
from app.services.auth_service import AuthService
from app.models.database import UserModel
from app.api.routes.auth import get_current_user
from app.api.dependencies import get_database_service, get_auth_service

router = APIRouter(tags=["dashboard"])

# Configure logging
logger = logging.getLogger(__name__)


@router.get("/dashboard/invoices")
async def get_user_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: UserModel = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Get current user's invoices with pagination.
    """
    try:
        # CRITICAL DEBUG: Log the current user info for dashboard
        logger.error(f"🚨 CRITICAL DEBUG - Dashboard get_user_invoices called")
        logger.error(f"🚨 CRITICAL DEBUG - current_user.id: {current_user.id}")
        logger.error(f"🚨 CRITICAL DEBUG - current_user.email: {current_user.email}")
        
        result = db_service.get_user_invoices(
            user_id=str(current_user.id),
            page=page,
            limit=limit
        )
        
        logger.info(f"Retrieved {len(result['invoices'])} invoices for user {current_user.email}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting invoices for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve invoices"
        )


@router.get("/dashboard/stats")
async def get_user_statistics(
    current_user: UserModel = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current user's processing statistics.
    """
    try:
        stats = auth_service.get_user_stats(str(current_user.id))
        
        logger.info(f"Retrieved stats for user {current_user.email}")
        return {
            "user": {
                "name": current_user.name,
                "email": current_user.email,
                "id": str(current_user.id),
                "is_active": current_user.is_active
            },
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting stats for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )


@router.delete("/dashboard/invoices/{invoice_id}")
async def delete_user_invoice(
    invoice_id: str,
    current_user: UserModel = Depends(get_current_user),
    db_service: DatabaseService = Depends(get_database_service)
):
    """
    Delete a specific invoice for the current user.
    """
    try:
        result = db_service.delete_user_invoice(
            user_id=str(current_user.id),
            invoice_id=invoice_id
        )
        
        if result["success"]:
            logger.info(f"Invoice {invoice_id} deleted by user {current_user.email}")
            return result
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting invoice {invoice_id} for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete invoice"
        )


@router.get("/dashboard/profile")
async def get_user_profile(
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get detailed user profile information.
    """
    try:
        return {
            "id": str(current_user.id),
            "name": current_user.name,
            "email": current_user.email,
            
            "is_active": current_user.is_active,
            "created_at": current_user.created_at.isoformat(),
            "updated_at": current_user.updated_at.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting profile for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )
