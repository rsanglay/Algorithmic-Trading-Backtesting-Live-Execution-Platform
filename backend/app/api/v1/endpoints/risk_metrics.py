"""
Risk metrics API endpoints
"""
from dataclasses import asdict
from datetime import datetime
from typing import Optional, List
from uuid import UUID

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.schemas.user import UserPreferencesUpdate
from app.services.analytics_data_service import AnalyticsDataService
from app.services.risk_metrics import RiskMetricsService
from app.services.user_service import UserService

router = APIRouter(prefix="/risk", tags=["risk"])

STRESS_SCENARIOS = {
    "crisis_2008": {"shock": -0.38, "vol_multiplier": 2.5},
    "covid_2020": {"shock": -0.32, "vol_multiplier": 2.0},
    "flash_crash": {"shock": -0.09, "vol_multiplier": 3.0},
    "dotcom_bubble": {"shock": -0.49, "vol_multiplier": 1.8},
}


async def _persist_preferences(db: Session, user_id: str, key: str, payload: dict) -> None:
    user_service = UserService(db)
    preferences = UserPreferencesUpdate(dashboard_preferences={key: payload})
    await user_service.update_user_preferences(UUID(user_id), preferences)


@router.get("/var/{strategy_id}")
async def get_var(
    strategy_id: UUID,
    confidence_level: float = Query(0.95, ge=0.5, le=0.995, description="Confidence level"),
    method: str = Query("historical", description="VaR method (historical, parametric, monte_carlo)"),
    period: str = Query("1y", description="Historical period to fetch"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate Value at Risk for a strategy."""

    analytics_service = AnalyticsDataService(db)
    try:
        context = await analytics_service.get_strategy_context(strategy_id)
        price_df = await analytics_service.load_price_history(context.symbol, period=period, interval=interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    returns = analytics_service.to_returns(price_df)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Not enough returns to calculate VaR")

    var_value = RiskMetricsService.calculate_var(returns, confidence_level=confidence_level, method=method)

    payload = {
        "strategy_id": str(strategy_id),
        "symbol": context.symbol,
        "confidence_level": confidence_level,
        "method": method,
        "var": var_value,
    }

    await _persist_preferences(db, current_user["id"], "risk_var", payload)

    return payload


@router.get("/cvar/{strategy_id}")
async def get_cvar(
    strategy_id: UUID,
    confidence_level: float = Query(0.95, ge=0.5, le=0.995),
    period: str = Query("1y", description="Historical period to fetch"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate Conditional VaR (Expected Shortfall)."""

    analytics_service = AnalyticsDataService(db)
    try:
        context = await analytics_service.get_strategy_context(strategy_id)
        price_df = await analytics_service.load_price_history(context.symbol, period=period, interval=interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    returns = analytics_service.to_returns(price_df)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Not enough returns to calculate CVaR")

    cvar_value = RiskMetricsService.calculate_cvar(returns, confidence_level=confidence_level)

    payload = {
        "strategy_id": str(strategy_id),
        "symbol": context.symbol,
        "confidence_level": confidence_level,
        "cvar": cvar_value,
    }

    await _persist_preferences(db, current_user["id"], "risk_cvar", payload)

    return payload


@router.get("/metrics/{strategy_id}")
async def get_comprehensive_risk_metrics(
    strategy_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    period: str = Query("2y", description="Fallback historical period when dates are not provided"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive risk metrics for a strategy."""

    analytics_service = AnalyticsDataService(db)
    try:
        context = await analytics_service.get_strategy_context(strategy_id)
        price_df = await analytics_service.load_price_history(
            context.symbol,
            period=period,
            interval=interval,
            start_date=start_date,
            end_date=end_date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    returns = analytics_service.to_returns(price_df)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Insufficient data to calculate risk metrics")

    equity_curve = analytics_service.equity_curve_from_returns(returns)
    metrics = RiskMetricsService.calculate_comprehensive_risk_metrics(returns, equity_curve)

    payload = {
        "strategy_id": str(strategy_id),
        "symbol": context.symbol,
        "metrics": asdict(metrics),
    }

    await _persist_preferences(db, current_user["id"], "risk_metrics", payload)

    return payload


@router.get("/stress-test/{strategy_id}")
async def run_stress_test(
    strategy_id: UUID,
    scenario: str = Query(..., description="Stress scenario (crisis_2008, covid_2020, flash_crash, dotcom_bubble)"),
    allocation: float = Query(1.0, ge=0.0, le=1.0, description="Fraction of capital allocated to the strategy"),
    period: str = Query("1y", description="Historical period for baseline volatility"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run stress test on a strategy."""

    if scenario not in STRESS_SCENARIOS:
        raise HTTPException(status_code=400, detail=f"Unknown scenario '{scenario}'")

    analytics_service = AnalyticsDataService(db)
    try:
        context = await analytics_service.get_strategy_context(strategy_id)
        price_df = await analytics_service.load_price_history(context.symbol, period=period)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    returns = analytics_service.to_returns(price_df)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Insufficient data for stress test")

    scenario_conf = STRESS_SCENARIOS[scenario]
    recent_vol = returns.std() * np.sqrt(252)
    shocked_vol = recent_vol * scenario_conf["vol_multiplier"]
    pnl_impact = allocation * scenario_conf["shock"]

    payload = {
        "strategy_id": str(strategy_id),
        "symbol": context.symbol,
        "scenario": scenario,
        "pnl_impact": pnl_impact,
        "baseline_vol": recent_vol,
        "shocked_vol": shocked_vol,
    }

    await _persist_preferences(db, current_user["id"], "stress_test", payload)

    return payload


@router.get("/correlation/{strategy_id}")
async def get_correlation_risk(
    strategy_id: UUID,
    symbols: Optional[List[str]] = Query(None, description="Additional symbols to include in the correlation analysis"),
    period: str = Query("1y", description="Historical period"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get correlation risk analysis."""

    analytics_service = AnalyticsDataService(db)
    try:
        context = await analytics_service.get_strategy_context(strategy_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    symbols_to_fetch = [context.symbol]
    if symbols:
        symbols_to_fetch.extend(symbols)
    symbols_to_fetch = list(dict.fromkeys(symbols_to_fetch))

    price_frames = {}
    for symbol in symbols_to_fetch:
        try:
            price_frames[symbol] = await analytics_service.load_price_history(symbol, period=period, interval=interval)
        except ValueError:
            continue

    if len(price_frames) < 2:
        raise HTTPException(status_code=400, detail="Not enough symbols with price data to compute correlation")

    returns_df = []
    for symbol, df in price_frames.items():
        series = analytics_service.to_returns(df)
        if not series.empty:
            returns_df.append(series.rename(symbol))

    if len(returns_df) < 2:
        raise HTTPException(status_code=400, detail="Insufficient return series to compute correlation")

    joined = pd.concat(returns_df, axis=1).dropna()
    correlation_matrix = joined.corr().round(4).to_dict()

    payload = {
        "strategy_id": str(strategy_id),
        "symbols": list(correlation_matrix.keys()),
        "correlation_matrix": correlation_matrix,
    }

    await _persist_preferences(db, current_user["id"], "correlation_risk", payload)

    return payload

