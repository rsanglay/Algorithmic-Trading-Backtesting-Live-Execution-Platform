"""
Advanced backtesting API endpoints
"""
from dataclasses import asdict
from uuid import UUID

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.schemas.user import UserPreferencesUpdate
from app.services.advanced_backtesting import AdvancedBacktestEngine, BacktestConfig, TransactionCostModel
from app.services.analytics_data_service import AnalyticsDataService
from app.services.user_service import UserService

router = APIRouter(prefix="/advanced-backtesting", tags=["advanced-backtesting"])


async def _persist_dashboard_preference(
    db: Session,
    user_id: str,
    key: str,
    payload: dict,
) -> None:
    """Persist the latest analysis snapshot into user dashboard preferences."""

    user_service = UserService(db)
    preferences = UserPreferencesUpdate(
        dashboard_preferences={key: payload}
    )
    await user_service.update_user_preferences(UUID(user_id), preferences)


@router.post("/walk-forward")
async def run_walk_forward_analysis(
    strategy_id: UUID,
    train_period: int = Query(252, description="Training period in days"),
    test_period: int = Query(63, description="Testing period in days"),
    step: int = Query(21, description="Step size in days"),
    period: str = Query("2y", description="Historical period to fetch from Yahoo Finance"),
    interval: str = Query("1d", description="Data interval for historical prices"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run walk-forward analysis for a strategy."""

    analytics_service = AnalyticsDataService(db)

    try:
        context = await analytics_service.get_strategy_context(strategy_id)
        price_df = await analytics_service.load_price_history(
            context.symbol,
            period=period,
            interval=interval,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if len(price_df) < train_period + test_period + step:
        raise HTTPException(
            status_code=400,
            detail="Not enough price history to perform walk-forward analysis."
        )

    strategy_func = analytics_service.get_strategy_function(context.strategy.strategy_type)

    config = BacktestConfig(initial_capital=100_000.0)
    engine = AdvancedBacktestEngine(config)

    results = engine.walk_forward_analysis(
        prices=price_df,
        strategy_func=lambda data: strategy_func(data),
        train_period=train_period,
        test_period=test_period,
        step=step,
    )

    await _persist_dashboard_preference(
        db,
        current_user["id"],
        "walk_forwardAnalysis",
        {
            "strategy_id": str(strategy_id),
            "symbol": context.symbol,
            "train_period": train_period,
            "test_period": test_period,
            "step": step,
            "summary": results.get("summary"),
        },
    )

    return results


@router.post("/monte-carlo")
async def run_monte_carlo_simulation(
    strategy_id: UUID,
    n_simulations: int = Query(1000, description="Number of simulations"),
    n_periods: int = Query(252, description="Number of periods"),
    confidence_level: float = Query(0.95, description="Confidence level"),
    period: str = Query("2y", description="Historical period to fetch from Yahoo Finance"),
    interval: str = Query("1d", description="Data interval for historical prices"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run Monte Carlo simulation for risk analysis."""

    analytics_service = AnalyticsDataService(db)

    try:
        context = await analytics_service.get_strategy_context(strategy_id)
        price_df = await analytics_service.load_price_history(
            context.symbol,
            period=period,
            interval=interval,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    returns = analytics_service.to_returns(price_df)
    if returns.empty:
        raise HTTPException(status_code=400, detail="Insufficient data to compute returns.")

    config = BacktestConfig(initial_capital=100_000.0)
    engine = AdvancedBacktestEngine(config)

    results = engine.monte_carlo_simulation(
        returns,
        num_simulations=n_simulations,
        num_steps=n_periods,
        confidence_level=confidence_level,
    )

    summary_payload = {
        "strategy_id": str(strategy_id),
        "symbol": context.symbol,
        "n_simulations": n_simulations,
        "n_periods": n_periods,
        "confidence_level": confidence_level,
        "mean_final_value": results.get("mean_final_value"),
        "var": results.get("var"),
        "cvar": results.get("cvar"),
    }
    await _persist_dashboard_preference(
        db,
        current_user["id"],
        "monte_carlo",
        summary_payload,
    )

    # Convert numpy arrays to lists for JSON serialisation
    serialized = results.copy()
    sim_paths = serialized.get("simulated_paths")
    final_values = serialized.get("final_values")

    if isinstance(sim_paths, np.ndarray):
        serialized["simulated_paths"] = sim_paths.tolist()
    elif hasattr(sim_paths, "tolist"):
        serialized["simulated_paths"] = sim_paths.tolist()

    if isinstance(final_values, np.ndarray):
        serialized["final_values"] = final_values.tolist()
    elif hasattr(final_values, "tolist"):
        serialized["final_values"] = final_values.tolist()

    return serialized


@router.get("/metrics/{backtest_id}")
async def get_advanced_metrics(
    backtest_id: UUID,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive backtest metrics from a completed backtest record."""
    from app.services.backtest_service import BacktestService

    service = BacktestService(db)
    backtest = await service.get_backtest(backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")

    if backtest.status != "completed" or not backtest.metrics:
        raise HTTPException(status_code=400, detail="Backtest has no metrics available yet")

    metrics = backtest.metrics or {}
    payload = {
        "backtest_id": str(backtest_id),
        "strategy_id": str(backtest.strategy_id),
        "metrics": metrics,
    }

    await _persist_dashboard_preference(
        db,
        current_user["id"],
        "backtest_metrics",
        payload,
    )

    return {
        "backtest": {
            "id": str(backtest.id),
            "strategy_id": str(backtest.strategy_id),
            "name": backtest.name,
            "start_date": backtest.start_date,
            "end_date": backtest.end_date,
            "initial_capital": backtest.initial_capital,
            "final_capital": backtest.final_capital,
            "status": backtest.status,
        },
        "metrics": metrics,
        "trades": backtest.trades,
    }

