"""
Production-grade authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT token security
security = HTTPBearer()
REFRESH_TOKEN_SUBJECT = "refresh"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a refresh token with a longer expiry."""
    payload = data.copy()
    payload["scope"] = REFRESH_TOKEN_SUBJECT
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expire, "iat": datetime.utcnow()})
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None


def decode_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    payload = decode_access_token(token)
    if not payload:
        return None
    if payload.get("scope") != REFRESH_TOKEN_SUBJECT:
        logger.warning("Invalid refresh token scope")
        return None
    return payload


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get the current authenticated user"""
    token = credentials.credentials

    payload = decode_access_token(token)
    if payload is None:
        raise UnauthorizedError("Invalid authentication credentials")

    if payload.get("scope") == REFRESH_TOKEN_SUBJECT:
        raise UnauthorizedError("Refresh token cannot be used for access")

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise UnauthorizedError("Invalid authentication credentials")

    # Fetch user from database
    from app.services.user_service import UserService
    user_service = UserService(db)
    db_user = await user_service.get_user(user_id)

    if not db_user:
        raise UnauthorizedError("User not found")

    if not db_user.is_active:
        raise UnauthorizedError("User account is inactive")

    user = {
        "id": str(db_user.id),
        "email": db_user.email,
        "username": db_user.username,
        "full_name": db_user.full_name,
        "roles": ["user"] + (["admin"] if db_user.is_superuser else []),
        "dashboard_preferences": db_user.dashboard_preferences or {},
        "trading_preferences": db_user.trading_preferences or {}
    }

    return user


async def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the current active user"""
    # In a real application, check if user is active
    # if not current_user.get("is_active"):
    #     raise ForbiddenError("User account is inactive")

    return current_user


def require_role(required_role: str):
    """Decorator to require a specific role"""
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        user_roles = current_user.get("roles", [])
        if required_role not in user_roles:
            raise ForbiddenError(f"Required role: {required_role}")
        return current_user

    return role_checker


def require_any_role(*required_roles: str):
    """Decorator to require any of the specified roles"""
    async def role_checker(
        current_user: Dict[str, Any] = Depends(get_current_active_user)
    ) -> Dict[str, Any]:
        user_roles = current_user.get("roles", [])
        if not any(role in user_roles for role in required_roles):
            raise ForbiddenError(f"Required one of roles: {', '.join(required_roles)}")
        return current_user

    return role_checker


class RateLimiter:
    """Rate limiter for API endpoints"""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_counts: Dict[str, Dict[str, Any]] = {}

    async def __call__(self, request):
        """Check rate limit for a request"""
        client_ip = request.client.host if request.client else "unknown"
        current_time = datetime.utcnow()

        # Clean old entries
        self.request_counts = {
            ip: data
            for ip, data in self.request_counts.items()
            if (current_time - data["timestamp"]).total_seconds() < 60
        }

        # Check rate limit
        if client_ip in self.request_counts:
            count_data = self.request_counts[client_ip]
            if count_data["count"] >= self.requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for {client_ip}",
                    extra={"client_ip": client_ip, "path": request.url.path}
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                    headers={"Retry-After": "60"}
                )
            count_data["count"] += 1
        else:
            self.request_counts[client_ip] = {
                "count": 1,
                "timestamp": current_time
            }

        return True
