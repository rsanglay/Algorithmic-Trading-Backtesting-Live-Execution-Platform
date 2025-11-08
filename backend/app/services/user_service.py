"""
User service for authentication and user management
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import uuid
import re

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserPreferencesUpdate, Token
from app.core.auth import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.core.exceptions import NotFoundError, BadRequestError
from app.core.config import settings

PASSWORD_POLICY_REGEXES = {
    "upper": re.compile(r"[A-Z]"),
    "lower": re.compile(r"[a-z]"),
    "digit": re.compile(r"\d"),
    "special": re.compile(r"[!@#$%^&*(),.?\"{}|<>]"),
}


class UserService:
    """Service for managing users"""
    
    def __init__(self, db: Session):
        self.db = db

    def _validate_password(self, password: str) -> None:
        if len(password) > settings.PASSWORD_MAX_LENGTH:
            raise BadRequestError("Password exceeds maximum supported length of 72 characters")
        if settings.PASSWORD_REQUIRE_UPPERCASE and not PASSWORD_POLICY_REGEXES["upper"].search(password):
            raise BadRequestError("Password must contain at least one uppercase letter")
        if settings.PASSWORD_REQUIRE_LOWERCASE and not PASSWORD_POLICY_REGEXES["lower"].search(password):
            raise BadRequestError("Password must contain at least one lowercase letter")
        if settings.PASSWORD_REQUIRE_NUMBER and not PASSWORD_POLICY_REGEXES["digit"].search(password):
            raise BadRequestError("Password must contain at least one number")
        if settings.PASSWORD_REQUIRE_SPECIAL and not PASSWORD_POLICY_REGEXES["special"].search(password):
            raise BadRequestError("Password must contain at least one special character")
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            or_(
                User.email == user_data.email,
                User.username == user_data.username
            )
        ).first()
        
        if existing_user:
            if existing_user.email == user_data.email:
                raise BadRequestError("Email already registered")
            else:
                raise BadRequestError("Username already taken")

        self._validate_password(user_data.password)

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_password
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        # Try to find user by username or email
        user = self.db.query(User).filter(
            or_(
                User.username == username,
                User.email == username
            )
        ).first()
        
        if not user:
            return None
        
        if not verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        return user
    
    async def get_user(self, user_id) -> Optional[User]:
        """Get a user by ID"""
        # Handle both UUID and string IDs
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                return None
        return self.db.query(User).filter(User.id == user_id).first()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        user = await self.get_user(user_id)
        if not user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(user, key, value)
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def update_user_preferences(
        self, 
        user_id: UUID, 
        preferences: UserPreferencesUpdate
    ) -> Optional[User]:
        """Update user preferences"""
        user = await self.get_user(user_id)
        if not user:
            return None
        
        if preferences.dashboard_preferences:
            if user.dashboard_preferences:
                user.dashboard_preferences.update(preferences.dashboard_preferences)
            else:
                user.dashboard_preferences = preferences.dashboard_preferences
        
        if preferences.trading_preferences:
            if user.trading_preferences:
                user.trading_preferences.update(preferences.trading_preferences)
            else:
                user.trading_preferences = preferences.trading_preferences
        
        self.db.commit()
        self.db.refresh(user)
        return user
    
    async def create_access_token_for_user(self, user: User) -> str:
        """Deprecated: use create_tokens_for_user"""
        tokens = await self.create_tokens_for_user(user)
        return tokens["access_token"]

    async def create_tokens_for_user(self, user: User) -> Dict[str, str]:
        token_payload = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "roles": ["user"] + (["admin"] if user.is_superuser else []),
        }
        access_token = create_access_token(token_payload)
        refresh_token = create_refresh_token(token_payload)
        return {"access_token": access_token, "refresh_token": refresh_token}

