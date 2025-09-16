"""
Authentication Service

Handles user authentication, registration, and session management.
"""
import logging
from typing import Optional
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.security import hash_password, verify_password, create_access_token, verify_token
from app.models.database import UserModel
from app.models.schemas import (
    UserCreateSchema, UserSchema, UserLoginSchema, 
    TokenSchema, UserInDBSchema
)

# Configure logging
logger = logging.getLogger(__name__)


class AuthService:
    """Service for user authentication and management."""
    
    def create_user(self, user_data: UserCreateSchema) -> UserSchema:
        """
        Create a new user account.
        
        Args:
            user_data: User registration data
            
        Returns:
            Created user information
            
        Raises:
            ValueError: If username or email already exists
        """
        try:
            with get_db_session() as session:
                # Check if email already exists
                existing_user = session.query(UserModel).filter(
                    UserModel.email == user_data.email
                ).first()
                
                if existing_user:
                    raise ValueError("Email already exists")
                
                # Create new user
                hashed_password = hash_password(user_data.password)
                
                new_user = UserModel(
                    name=user_data.name,
                    email=user_data.email,
                    hashed_password=hashed_password,
                    is_active=True
                )
                
                session.add(new_user)
                session.flush()  # Get the ID
                
                # Access attributes while in session context
                user_id = str(new_user.id)
                name = new_user.name
                email = new_user.email
                is_active = new_user.is_active
                
                logger.info(f"Created new user: {user_data.email}")
                
                return UserSchema(
                    id=user_id,
                    name=name,
                    email=email,
                    is_active=is_active
                )
                
        except IntegrityError as e:
            logger.error(f"Database integrity error creating user: {e}")
            raise ValueError("Username or email already exists")
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise
    
    def authenticate_user(self, email: str, password: str) -> Optional[UserModel]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            User model if authentication successful, None otherwise
        """
        try:
            with get_db_session() as session:
                # Find user by email
                user = session.query(UserModel).filter(
                    UserModel.email == email
                ).first()
                
                if not user:
                    logger.warning(f"Authentication failed: user not found - {email}")
                    return None
                
                if not user.is_active:
                    logger.warning(f"Authentication failed: user inactive - {email}")
                    return None
                
                if not verify_password(password, user.hashed_password):
                    logger.warning(f"Authentication failed: invalid password - {email}")
                    return None
                
                logger.info(f"User authenticated successfully: {email}")
                return user
                
        except Exception as e:
            logger.error(f"Error authenticating user {email}: {e}")
            return None
    
    def login_user(self, login_data: UserLoginSchema) -> TokenSchema:
        """
        Login user and return access token.
        
        Args:
            login_data: Login credentials
            
        Returns:
            Token with user information
            
        Raises:
            ValueError: If authentication fails
        """
        # Authenticate and get user data within session context
        with get_db_session() as session:
            # Find user by email
            user = session.query(UserModel).filter(
                UserModel.email == login_data.email
            ).first()
            
            if not user:
                raise ValueError("Invalid email or password")
            
            if not user.is_active:
                raise ValueError("Invalid email or password")
            
            if not verify_password(login_data.password, user.hashed_password):
                raise ValueError("Invalid email or password")
            
            # Access user attributes while in session context
            user_id = str(user.id)
            name = user.name
            email = user.email
            is_active = user.is_active
            
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user_id, "email": email}
        )
        
        user_schema = UserSchema(
            id=user_id,
            name=name,
            email=email,
            is_active=is_active
        )
        
        return TokenSchema(
            access_token=access_token,
            token_type="bearer",
            user=user_schema
        )
    
    def get_current_user(self, token: str) -> Optional[UserModel]:
        """
        Get current user from JWT token.
        
        Args:
            token: JWT access token
            
        Returns:
            User model if token is valid, None otherwise
        """
        try:
            payload = verify_token(token)
            if not payload:
                return None
            
            user_id: str = payload.get("sub")
            if not user_id:
                return None
            
            with get_db_session() as session:
                user = session.query(UserModel).filter(UserModel.id == user_id).first()
                
                if not user or not user.is_active:
                    return None
                
                # Ensure the user object is detached from session but still accessible
                session.expunge(user)
                return user
                
        except Exception as e:
            logger.error(f"Error getting current user from token: {e}")
            return None
    
    def get_user_by_id(self, user_id: str) -> Optional[UserSchema]:
        """
        Get user information by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User schema if found, None otherwise
        """
        try:
            with get_db_session() as session:
                user = session.query(UserModel).filter(UserModel.id == user_id).first()
                
                if not user:
                    return None
                
                return UserSchema(
                    id=str(user.id),
                    name=user.name,
                    email=user.email,
                    is_active=user.is_active
                )
                
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    def get_user_stats(self, user_id: str) -> dict:
        """
        Get user statistics.
        
        Args:
            user_id: User UUID
            
        Returns:
            Dictionary with user statistics
        """
        try:
            with get_db_session() as session:
                from app.models.database import InvoiceModel
                
                # Get invoice count for user
                invoice_count = session.query(InvoiceModel).filter(
                    InvoiceModel.user_id == user_id
                ).count()
                
                # Get recent activity (last 30 days)
                thirty_days_ago = datetime.utcnow() - timedelta(days=30)
                recent_count = session.query(InvoiceModel).filter(
                    InvoiceModel.user_id == user_id,
                    InvoiceModel.created_at >= thirty_days_ago
                ).count()
                
                # Calculate total amount processed
                from sqlalchemy import func
                total_amount = session.query(func.sum(InvoiceModel.net_amount)).filter(
                    InvoiceModel.user_id == user_id,
                    InvoiceModel.net_amount.isnot(None)
                ).scalar() or 0
                
                # Calculate storage used (count of files)
                files_count = session.query(InvoiceModel).filter(
                    InvoiceModel.user_id == user_id,
                    InvoiceModel.original_file_id.isnot(None)
                ).count()
                
                return {
                    "total_invoices": invoice_count,
                    "recent_invoices": recent_count,
                    "success_rate": 100.0 if invoice_count > 0 else 0.0,
                    "total_amount": float(total_amount),
                    "storage_used": files_count,
                    "storage_limit": 1000,  # Default limit
                    "account_created": True
                }
                
        except Exception as e:
            logger.error(f"Error getting user stats for {user_id}: {e}")
            return {
                "total_invoices": 0,
                "recent_invoices": 0,
                "success_rate": 0.0,
                "total_amount": 0.0,
                "storage_used": 0,
                "storage_limit": 1000,
                "account_created": False
            }
