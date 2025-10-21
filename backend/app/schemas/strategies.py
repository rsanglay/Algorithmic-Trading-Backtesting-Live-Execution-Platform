"""
Pydantic schemas for trading strategies
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class StrategyBase(BaseModel):
    """Base strategy schema"""
    name: str = Field(..., description="Strategy name")
    description: Optional[str] = Field(None, description="Strategy description")
    strategy_type: str = Field(..., description="Strategy type")
    code: str = Field(..., description="Strategy implementation code")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Strategy parameters")


class StrategyCreate(StrategyBase):
    """Schema for creating a strategy"""
    created_by: str = Field(..., description="Creator user ID")


class StrategyUpdate(BaseModel):
    """Schema for updating a strategy"""
    name: Optional[str] = None
    description: Optional[str] = None
    code: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    is_live: Optional[bool] = None


class Strategy(StrategyBase):
    """Schema for strategy response"""
    id: UUID
    is_active: bool
    is_live: bool
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BacktestBase(BaseModel):
    """Base backtest schema"""
    name: str = Field(..., description="Backtest name")
    start_date: datetime = Field(..., description="Backtest start date")
    end_date: datetime = Field(..., description="Backtest end date")
    initial_capital: float = Field(..., description="Initial capital")


class BacktestCreate(BacktestBase):
    """Schema for creating a backtest"""
    strategy_id: UUID = Field(..., description="Strategy ID")


class Backtest(BacktestBase):
    """Schema for backtest response"""
    id: UUID
    strategy_id: UUID
    final_capital: Optional[float] = None
    total_return: Optional[float] = None
    annualized_return: Optional[float] = None
    sharpe_ratio: Optional[float] = None
    max_drawdown: Optional[float] = None
    win_rate: Optional[float] = None
    profit_factor: Optional[float] = None
    metrics: Optional[Dict[str, Any]] = None
    trades: Optional[List[Dict[str, Any]]] = None
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PositionBase(BaseModel):
    """Base position schema"""
    symbol: str = Field(..., description="Trading symbol")
    quantity: float = Field(..., description="Position quantity")
    entry_price: float = Field(..., description="Entry price")


class PositionCreate(PositionBase):
    """Schema for creating a position"""
    strategy_id: UUID = Field(..., description="Strategy ID")


class Position(PositionBase):
    """Schema for position response"""
    id: UUID
    strategy_id: UUID
    current_price: Optional[float] = None
    unrealized_pnl: Optional[float] = None
    realized_pnl: float = 0.0
    is_open: bool = True
    opened_at: datetime
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    """Base order schema"""
    symbol: str = Field(..., description="Trading symbol")
    order_type: str = Field(..., description="Order type")
    side: str = Field(..., description="Order side")
    quantity: float = Field(..., description="Order quantity")
    price: Optional[float] = Field(None, description="Order price")


class OrderCreate(OrderBase):
    """Schema for creating an order"""
    strategy_id: UUID = Field(..., description="Strategy ID")


class Order(OrderBase):
    """Schema for order response"""
    id: UUID
    strategy_id: UUID
    status: str
    filled_quantity: float = 0.0
    filled_price: Optional[float] = None
    commission: float = 0.0
    created_at: datetime
    filled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
