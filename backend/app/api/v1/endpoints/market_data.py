"""
Market data endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.core.database import get_db
from app.models.market_data import MarketData, TickerInfo, NewsData
from app.schemas.market_data import (
    MarketDataCreate, MarketData as MarketDataSchema,
    TickerInfoCreate, TickerInfo as TickerInfoSchema,
    NewsDataCreate, NewsData as NewsDataSchema,
    MarketDataRequest, TechnicalIndicators
)
from app.services.market_data_service import MarketDataService
from app.services.technical_analysis_service import TechnicalAnalysisService

router = APIRouter()


@router.get("/ohlcv", response_model=List[MarketDataSchema])
async def get_market_data(
    symbol: str = Query(..., description="Trading symbol"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    interval: str = Query("1d", description="Data interval"),
    db: Session = Depends(get_db)
):
    """Get OHLCV market data"""
    service = MarketDataService(db)
    return await service.get_market_data(symbol, start_date, end_date, interval)


@router.post("/ohlcv", response_model=MarketDataSchema)
async def create_market_data(
    market_data: MarketDataCreate,
    db: Session = Depends(get_db)
):
    """Create market data entry"""
    service = MarketDataService(db)
    return await service.create_market_data(market_data)


@router.get("/tickers", response_model=List[TickerInfoSchema])
async def get_tickers(
    skip: int = 0,
    limit: int = 100,
    exchange: Optional[str] = None,
    sector: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get ticker information"""
    service = MarketDataService(db)
    return await service.get_tickers(skip=skip, limit=limit, exchange=exchange, sector=sector)


@router.post("/tickers", response_model=TickerInfoSchema)
async def create_ticker_info(
    ticker_info: TickerInfoCreate,
    db: Session = Depends(get_db)
):
    """Create ticker information"""
    service = MarketDataService(db)
    return await service.create_ticker_info(ticker_info)


@router.get("/news", response_model=List[NewsDataSchema])
async def get_news_data(
    symbol: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    sentiment_label: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get news and sentiment data"""
    service = MarketDataService(db)
    return await service.get_news_data(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        sentiment_label=sentiment_label,
        skip=skip,
        limit=limit
    )


@router.post("/news", response_model=NewsDataSchema)
async def create_news_data(
    news_data: NewsDataCreate,
    db: Session = Depends(get_db)
):
    """Create news data entry"""
    service = MarketDataService(db)
    return await service.create_news_data(news_data)


@router.get("/technical-indicators", response_model=List[TechnicalIndicators])
async def get_technical_indicators(
    symbol: str = Query(..., description="Trading symbol"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    indicators: List[str] = Query(..., description="List of indicators to calculate"),
    db: Session = Depends(get_db)
):
    """Get technical indicators for a symbol"""
    service = TechnicalAnalysisService(db)
    return await service.calculate_indicators(symbol, start_date, end_date, indicators)


@router.post("/sync")
async def sync_market_data(
    symbols: List[str],
    start_date: datetime,
    end_date: datetime,
    source: str = "alpha_vantage",
    db: Session = Depends(get_db)
):
    """Sync market data from external sources"""
    service = MarketDataService(db)
    result = await service.sync_market_data(symbols, start_date, end_date, source)
    return {"message": f"Synced data for {len(symbols)} symbols", "details": result}


@router.get("/realtime/{symbol}")
async def get_realtime_data(
    symbol: str,
    db: Session = Depends(get_db)
):
    """Get real-time market data for a symbol"""
    service = MarketDataService(db)
    return await service.get_realtime_data(symbol)
