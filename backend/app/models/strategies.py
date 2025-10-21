"""
Trading strategy models
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Strategy(Base):
    """Trading strategy model"""
    __tablename__ = "strategies"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    strategy_type = Column(String(50), nullable=False)  # momentum, mean_reversion, etc.
    code = Column(Text, nullable=False)  # Strategy implementation code
    parameters = Column(JSON)  # Strategy parameters
    is_active = Column(Boolean, default=False)
    is_live = Column(Boolean, default=False)
    created_by = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    backtests = relationship("Backtest", back_populates="strategy")
    positions = relationship("Position", back_populates="strategy")
    orders = relationship("Order", back_populates="strategy")


class Backtest(Base):
    """Backtest results model"""
    __tablename__ = "backtests"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    name = Column(String(200), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    initial_capital = Column(Float, nullable=False)
    final_capital = Column(Float)
    
    # Performance metrics
    total_return = Column(Float)
    annualized_return = Column(Float)
    sharpe_ratio = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    profit_factor = Column(Float)
    
    # Additional metrics
    metrics = Column(JSON)  # Store additional performance metrics
    trades = Column(JSON)  # Store trade history
    
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    strategy = relationship("Strategy", back_populates="backtests")


class Position(Base):
    """Trading position model"""
    __tablename__ = "positions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    quantity = Column(Float, nullable=False)
    entry_price = Column(Float, nullable=False)
    current_price = Column(Float)
    unrealized_pnl = Column(Float)
    realized_pnl = Column(Float, default=0.0)
    is_open = Column(Boolean, default=True)
    opened_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True))
    
    # Relationships
    strategy = relationship("Strategy", back_populates="positions")


class Order(Base):
    """Trading order model"""
    __tablename__ = "orders"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    strategy_id = Column(UUID(as_uuid=True), ForeignKey("strategies.id"), nullable=False)
    symbol = Column(String(20), nullable=False)
    order_type = Column(String(20), nullable=False)  # market, limit, stop
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Float, nullable=False)
    price = Column(Float)
    status = Column(String(20), default="pending")  # pending, filled, cancelled, rejected
    filled_quantity = Column(Float, default=0.0)
    filled_price = Column(Float)
    commission = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    filled_at = Column(DateTime(timezone=True))
    
    # Relationships
    strategy = relationship("Strategy", back_populates="orders")
