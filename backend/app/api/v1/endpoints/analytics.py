"""
Analytics and performance endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.core.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.risk_service import RiskService

router = APIRouter()


@router.get("/performance/{strategy_id}")
async def get_strategy_performance(
    strategy_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get performance analytics for a strategy"""
    service = AnalyticsService(db)
    return await service.get_strategy_performance(strategy_id, start_date, end_date)


@router.get("/risk-metrics/{strategy_id}")
async def get_risk_metrics(
    strategy_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get risk metrics for a strategy"""
    service = RiskService(db)
    return await service.get_risk_metrics(strategy_id, start_date, end_date)


@router.get("/portfolio-analytics")
async def get_portfolio_analytics(
    strategy_ids: List[UUID] = Query(..., description="List of strategy IDs"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get portfolio-level analytics"""
    service = AnalyticsService(db)
    return await service.get_portfolio_analytics(strategy_ids, start_date, end_date)


@router.get("/correlation-matrix")
async def get_correlation_matrix(
    symbols: List[str] = Query(..., description="List of symbols"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    db: Session = Depends(get_db)
):
    """Get correlation matrix for symbols"""
    service = AnalyticsService(db)
    return await service.get_correlation_matrix(symbols, start_date, end_date)


@router.get("/volatility-analysis")
async def get_volatility_analysis(
    symbol: str = Query(..., description="Trading symbol"),
    start_date: datetime = Query(..., description="Start date"),
    end_date: datetime = Query(..., description="End date"),
    window: int = Query(30, description="Rolling window for volatility calculation"),
    db: Session = Depends(get_db)
):
    """Get volatility analysis for a symbol"""
    service = AnalyticsService(db)
    return await service.get_volatility_analysis(symbol, start_date, end_date, window)


@router.get("/drawdown-analysis/{strategy_id}")
async def get_drawdown_analysis(
    strategy_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get drawdown analysis for a strategy"""
    service = AnalyticsService(db)
    return await service.get_drawdown_analysis(strategy_id, start_date, end_date)


@router.get("/sharpe-ratio/{strategy_id}")
async def get_sharpe_ratio(
    strategy_id: UUID,
    risk_free_rate: float = Query(0.02, description="Risk-free rate"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Calculate Sharpe ratio for a strategy"""
    service = AnalyticsService(db)
    return await service.get_sharpe_ratio(strategy_id, risk_free_rate, start_date, end_date)


@router.get("/var-calculation")
async def calculate_var(
    strategy_id: UUID,
    confidence_level: float = Query(0.95, description="Confidence level (0-1)"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Calculate Value at Risk (VaR) for a strategy"""
    service = RiskService(db)
    return await service.calculate_var(strategy_id, confidence_level, start_date, end_date)


@router.get("/stress-test/{strategy_id}")
async def stress_test(
    strategy_id: UUID,
    scenarios: List[str] = Query(..., description="List of stress test scenarios"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Perform stress testing on a strategy"""
    service = RiskService(db)
    return await service.stress_test(strategy_id, scenarios, start_date, end_date)


@router.get("/monte-carlo-simulation")
async def monte_carlo_simulation(
    strategy_id: UUID,
    num_simulations: int = Query(1000, description="Number of Monte Carlo simulations"),
    time_horizon: int = Query(252, description="Time horizon in days"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Run Monte Carlo simulation for a strategy"""
    service = AnalyticsService(db)
    return await service.monte_carlo_simulation(
        strategy_id, num_simulations, time_horizon, start_date, end_date
    )
