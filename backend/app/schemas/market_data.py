"""
Pydantic schemas for market data
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class MarketDataBase(BaseModel):
    """Base market data schema"""
    symbol: str = Field(..., description="Trading symbol")
    timestamp: datetime = Field(..., description="Data timestamp")
    open_price: float = Field(..., description="Open price")
    high_price: float = Field(..., description="High price")
    low_price: float = Field(..., description="Low price")
    close_price: float = Field(..., description="Close price")
    volume: float = Field(..., description="Volume")
    source: str = Field(..., description="Data source")


class MarketDataCreate(MarketDataBase):
    """Schema for creating market data"""
    pass


class MarketData(MarketDataBase):
    """Schema for market data response"""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class TickerInfoBase(BaseModel):
    """Base ticker info schema"""
    symbol: str = Field(..., description="Trading symbol")
    name: str = Field(..., description="Company name")
    exchange: str = Field(..., description="Exchange")
    sector: Optional[str] = Field(None, description="Sector")
    industry: Optional[str] = Field(None, description="Industry")
    market_cap: Optional[float] = Field(None, description="Market capitalization")
    currency: str = Field(default="USD", description="Currency")
    is_active: str = Field(default="true", description="Active status")


class TickerInfoCreate(TickerInfoBase):
    """Schema for creating ticker info"""
    pass


class TickerInfo(TickerInfoBase):
    """Schema for ticker info response"""
    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class NewsDataBase(BaseModel):
    """Base news data schema"""
    symbol: str = Field(..., description="Trading symbol")
    timestamp: datetime = Field(..., description="News timestamp")
    title: str = Field(..., description="News title")
    content: Optional[str] = Field(None, description="News content")
    source: str = Field(..., description="News source")
    sentiment_score: Optional[float] = Field(None, description="Sentiment score (-1 to 1)")
    sentiment_label: Optional[str] = Field(None, description="Sentiment label")
    url: Optional[str] = Field(None, description="News URL")


class NewsDataCreate(NewsDataBase):
    """Schema for creating news data"""
    pass


class NewsData(NewsDataBase):
    """Schema for news data response"""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class MarketDataRequest(BaseModel):
    """Schema for market data requests"""
    symbols: List[str] = Field(..., description="List of symbols")
    start_date: datetime = Field(..., description="Start date")
    end_date: datetime = Field(..., description="End date")
    interval: str = Field(default="1d", description="Data interval")


class TechnicalIndicators(BaseModel):
    """Schema for technical indicators"""
    symbol: str
    timestamp: datetime
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_middle: Optional[float] = None
    bollinger_lower: Optional[float] = None
    atr: Optional[float] = None
    adx: Optional[float] = None
    stochastic_k: Optional[float] = None
    stochastic_d: Optional[float] = None
