"""
User model with preferences for dashboard customization
"""
from sqlalchemy import Column, String, Boolean, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class User(Base):
    """User model with authentication and preferences"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200))
    
    # User status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Dashboard preferences (JSON)
    dashboard_preferences = Column(JSON, default=lambda: {
        "layout": "default",
        "widgets": ["metrics", "performance_chart", "recent_strategies", "market_overview"],
        "default_timeframe": "1M",
        "favorite_instruments": [],
        "theme": "light",
        "chart_type": "candlestick",
        "show_indicators": True,
        "indicators": ["SMA", "RSI", "MACD"]
    })
    
    # Trading preferences
    trading_preferences = Column(JSON, default=lambda: {
        "default_exchange": "US",
        "default_currency": "USD",
        "risk_tolerance": "medium",
        "notification_settings": {
            "email_alerts": True,
            "trade_notifications": True,
            "price_alerts": False
        }
    })
    
    # Relationships
    # Note: Strategy model uses created_by as String, not foreign key
    # We can add proper foreign key relationship in a future migration


# Update Strategy model to have proper foreign key
# This will be done in a migration, but we'll note it here

