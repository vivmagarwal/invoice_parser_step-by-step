"""
Authentication Routes

Handles user registration, login, logout, and profile management.
"""
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import AuthService
from app.models.schemas import (
    UserCreateSchema, UserLoginSchema, TokenSchema, UserSchema
)
from app.api.dependencies import get_auth_service

router = APIRouter(tags=["authentication"])
security = HTTPBearer()

# Configure logging
logger = logging.getLogger(__name__)


@router.post("/auth/register", response_model=TokenSchema)
async def register_user(
    user_data: UserCreateSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user account.
    
    Creates a new user and returns an access token for immediate login.
    """
    try:
        # Create user
        user = auth_service.create_user(user_data)
        
        # Auto-login after registration
        login_data = UserLoginSchema(
            email=user_data.email,
            password=user_data.password
        )
        token_response = auth_service.login_user(login_data)
        
        logger.info(f"User registered and logged in: {user.email}")
        return token_response
        
    except ValueError as e:
        logger.warning(f"Registration failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed due to server error"
        )


@router.post("/auth/login", response_model=TokenSchema)
async def login_user(
    login_data: UserLoginSchema,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return access token.
    """
    try:
        token_response = auth_service.login_user(login_data)
        logger.info(f"User logged in: {login_data.email}")
        return token_response
        
    except ValueError as e:
        logger.warning(f"Login failed for {login_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        logger.error(f"Login error for {login_data.email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed due to server error"
        )


@router.get("/auth/me", response_model=UserSchema)
async def get_current_user_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current user's profile information.
    """
    try:
        user = auth_service.get_current_user(credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return UserSchema(
            id=str(user.id),
            name=user.name,
            email=user.email,
            
            is_active=user.is_active,
            
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user profile"
        )


@router.post("/auth/logout")
async def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user (client-side token removal).
    
    Note: Since we're using stateless JWT tokens, actual logout happens
    on the client side by removing the token from storage.
    """
    try:
        # Verify token is valid
        user = auth_service.get_current_user(credentials.credentials)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        logger.info(f"User logged out: {user.email}")
        
        return {
            "message": "Logged out successfully",
            "detail": "Please remove the token from client storage"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


# Dependency for getting current authenticated user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Dependency to get current authenticated user.
    
    Use this in other routes that require authentication.
    """
    user = auth_service.get_current_user(credentials.credentials)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user
