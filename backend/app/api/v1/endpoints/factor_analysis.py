"""
Factor analysis API endpoints
"""
from typing import Dict, Any, List, Optional
from uuid import UUID

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_active_user
from app.core.database import get_db
from app.schemas.user import UserPreferencesUpdate
from app.services.analytics_data_service import AnalyticsDataService
from app.services.factor_analysis import FactorAnalysisService
from app.services.user_service import UserService

router = APIRouter(prefix="/factors", tags=["factors"])

FACTOR_PROXIES = {
    "market": "SPY",
    "small_cap": "IWM",
    "large_cap": "SPY",
    "value": "IWD",
    "growth": "IWF",
    "quality": "QUAL",
    "momentum": "MTUM",
    "low_vol": "USMV",
}

RISK_FREE_DAILY = 0.0001  # Approx. 2.5% annualised


async def _persist_preferences(db: Session, user_id: str, key: str, payload: dict) -> None:
    user_service = UserService(db)
    preferences = UserPreferencesUpdate(dashboard_preferences={key: payload})
    await user_service.update_user_preferences(UUID(user_id), preferences)


async def _load_proxy_returns(
    analytics_service: AnalyticsDataService,
    symbols: List[str],
    period: str,
    interval: str,
) -> Dict[str, pd.Series]:
    returns: Dict[str, pd.Series] = {}
    for symbol in symbols:
        try:
            df = await analytics_service.load_price_history(symbol, period=period, interval=interval)
            series = analytics_service.to_returns(df)
            if not series.empty:
                returns[symbol] = series
        except ValueError:
            continue
    if not returns:
        raise ValueError("Unable to load price data for factor proxies")
    return returns


def _align_series(series_dict: Dict[str, pd.Series]) -> pd.DataFrame:
    df = pd.concat(series_dict.values(), axis=1, join="inner")
    df.columns = list(series_dict.keys())
    return df.dropna()


async def _compute_fama_french_3(
    analytics_service: AnalyticsDataService,
    period: str,
    interval: str,
) -> Dict[str, List[float]]:
    symbols = [
        FACTOR_PROXIES["market"],
        FACTOR_PROXIES["small_cap"],
        FACTOR_PROXIES["large_cap"],
        FACTOR_PROXIES["value"],
        FACTOR_PROXIES["growth"],
    ]
    symbol_returns = await _load_proxy_returns(analytics_service, symbols, period, interval)

    df = _align_series(symbol_returns)
    if df.empty or df.shape[0] < 30:
        raise ValueError("Not enough overlapping data to compute factors")

    market = df[FACTOR_PROXIES["market"]]
    small = df[FACTOR_PROXIES["small_cap"]]
    large = df[FACTOR_PROXIES["large_cap"]]
    value = df[FACTOR_PROXIES["value"]]
    growth = df[FACTOR_PROXIES["growth"]]

    market_rf = (market - RISK_FREE_DAILY).tolist()
    smb = (small - large).tolist()
    hml = (value - growth).tolist()
    rf = [RISK_FREE_DAILY] * len(market_rf)

    return {
        "market_rf": market_rf,
        "smb": smb,
        "hml": hml,
        "risk_free": rf,
    }


async def _compute_fama_french_5(
    analytics_service: AnalyticsDataService,
    period: str,
    interval: str,
) -> Dict[str, List[float]]:
    ff3 = await _compute_fama_french_3(analytics_service, period, interval)

    symbols = [
        FACTOR_PROXIES["quality"],
        FACTOR_PROXIES["market"],
        FACTOR_PROXIES["low_vol"],
        FACTOR_PROXIES["momentum"],
    ]
    symbol_returns = await _load_proxy_returns(analytics_service, symbols, period, interval)
    df = _align_series(symbol_returns)

    quality = df[FACTOR_PROXIES["quality"]]
    low_vol = df[FACTOR_PROXIES["low_vol"]]
    momentum = df[FACTOR_PROXIES["momentum"]]
    market = df[FACTOR_PROXIES["market"]]

    rmw = (quality - market).tolist()
    cma = (low_vol - momentum).tolist()

    ff3.update({"rmw": rmw, "cma": cma})
    return ff3


async def _get_portfolio_returns(
    analytics_service: AnalyticsDataService,
    portfolio_symbol: str,
    period: str,
    interval: str,
) -> pd.Series:
    df = await analytics_service.load_price_history(portfolio_symbol, period=period, interval=interval)
    series = analytics_service.to_returns(df)
    if series.empty:
        raise ValueError(f"No returns available for portfolio symbol {portfolio_symbol}")
    return series


@router.get("/fama-french-3")
async def get_fama_french_3_factor_model(
    portfolio_id: str = Query(..., description="Portfolio identifier or symbol"),
    period: str = Query("2y", description="Historical period to fetch"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run Fama-French 3-factor model analysis."""

    analytics_service = AnalyticsDataService(db)
    service = FactorAnalysisService()

    try:
        ff_data = await _compute_fama_french_3(analytics_service, period, interval)
        portfolio_returns = await _get_portfolio_returns(analytics_service, portfolio_id, period, interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results = await service.calculate_fama_french_factors(
        market_returns=ff_data["market_rf"],
        small_cap_returns=ff_data["smb"],
        high_value_returns=ff_data["hml"],
        risk_free_rate=ff_data["risk_free"],
    )

    factors = {
        "Mkt-Rf": ff_data["market_rf"],
        "SMB": ff_data["smb"],
        "HML": ff_data["hml"],
    }
    exposure = await service.get_factor_exposure(portfolio_returns.tolist(), factors)

    payload = {
        "portfolio_id": portfolio_id,
        "period": period,
        "interval": interval,
        "factors": results,
        "exposure": exposure,
    }

    await _persist_preferences(db, current_user["id"], "factor_ff3", payload)

    return payload


@router.get("/fama-french-5")
async def get_fama_french_5_factor_model(
    portfolio_id: str = Query(..., description="Portfolio identifier or symbol"),
    period: str = Query("3y", description="Historical period to fetch"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Run Fama-French 5-factor model analysis."""

    analytics_service = AnalyticsDataService(db)
    service = FactorAnalysisService()

    try:
        ff_data = await _compute_fama_french_5(analytics_service, period, interval)
        portfolio_returns = await _get_portfolio_returns(analytics_service, portfolio_id, period, interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    ff5_payload = await service.calculate_fama_french_factors(
        market_returns=ff_data["market_rf"],
        small_cap_returns=ff_data["smb"],
        high_value_returns=ff_data["hml"],
        risk_free_rate=ff_data["risk_free"],
    )

    ff5_payload["factors"].update({
        "RMW": ff_data.get("rmw", []),
        "CMA": ff_data.get("cma", []),
    })

    factors = {
        "Mkt-Rf": ff_data["market_rf"],
        "SMB": ff_data["smb"],
        "HML": ff_data["hml"],
        "RMW": ff_data.get("rmw", []),
        "CMA": ff_data.get("cma", []),
    }
    exposure = await service.get_factor_exposure(portfolio_returns.tolist(), factors)

    payload = {
        "portfolio_id": portfolio_id,
        "period": period,
        "interval": interval,
        "factors": ff5_payload,
        "exposure": exposure,
    }

    await _persist_preferences(db, current_user["id"], "factor_ff5", payload)

    return payload


@router.get("/exposure")
async def get_factor_exposure(
    portfolio_id: str = Query(..., description="Portfolio identifier or symbol"),
    period: str = Query("2y", description="Historical period"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get factor exposures for a portfolio."""

    analytics_service = AnalyticsDataService(db)
    service = FactorAnalysisService()

    try:
        ff_data = await _compute_fama_french_5(analytics_service, period, interval)
        portfolio_returns = await _get_portfolio_returns(analytics_service, portfolio_id, period, interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    factors = {
        "Mkt-Rf": ff_data["market_rf"],
        "SMB": ff_data["smb"],
        "HML": ff_data["hml"],
        "RMW": ff_data.get("rmw", []),
        "CMA": ff_data.get("cma", []),
    }

    exposure = await service.get_factor_exposure(portfolio_returns.tolist(), factors)

    payload = {
        "portfolio_id": portfolio_id,
        "period": period,
        "interval": interval,
        "factor_exposures": exposure,
    }

    await _persist_preferences(db, current_user["id"], "factor_exposure", payload)

    return payload


@router.get("/attribution")
async def get_factor_attribution(
    portfolio_id: str = Query(..., description="Portfolio identifier or symbol"),
    period: str = Query("2y", description="Historical period"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get factor attribution analysis."""

    analytics_service = AnalyticsDataService(db)
    service = FactorAnalysisService()

    try:
        exposure_payload = await get_factor_exposure(
            portfolio_id=portfolio_id,
            period=period,
            interval=interval,
            current_user=current_user,
            db=db,
        )
    except HTTPException as exc:
        raise exc

    exposures = exposure_payload["factor_exposures"].get("factor_exposures", {})
    factors_used = exposure_payload["factor_exposures"].get("factors_used", [])

    # Compute contribution using average factor return multiplied by beta
    average_contributions = {}
    for factor_name in exposures:
        if factor_name == "alpha":
            continue
        beta = exposures[factor_name]
        average_contributions[factor_name] = beta  # placeholder linear contribution

    attribution = {
        "portfolio_id": portfolio_id,
        "period": period,
        "interval": interval,
        "factor_contributions": average_contributions,
        "factors_used": factors_used,
    }

    await _persist_preferences(db, current_user["id"], "factor_attribution", attribution)

    return attribution


@router.get("/correlation")
async def get_factor_correlation(
    period: str = Query("3y", description="Historical period"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get factor correlation matrix."""

    analytics_service = AnalyticsDataService(db)

    try:
        symbol_returns = await _load_proxy_returns(
            analytics_service,
            list(FACTOR_PROXIES.values()),
            period,
            interval,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    df = _align_series(symbol_returns)
    correlation_matrix = df.corr().round(4).to_dict()

    payload = {
        "period": period,
        "interval": interval,
        "symbols": list(symbol_returns.keys()),
        "correlation_matrix": correlation_matrix,
    }

    await _persist_preferences(db, current_user["id"], "factor_correlation", payload)

    return payload


@router.post("/custom")
async def calculate_custom_factor(
    factor_type: str,
    symbols: List[str],
    parameters: Optional[dict] = None,
    period: str = Query("1y", description="Historical period"),
    interval: str = Query("1d", description="Data interval"),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Calculate custom factor."""

    analytics_service = AnalyticsDataService(db)

    if not symbols:
        raise HTTPException(status_code=400, detail="At least one symbol is required")

    try:
        symbol_returns = await _load_proxy_returns(analytics_service, symbols, period, interval)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    df = _align_series(symbol_returns)

    if factor_type == "momentum":
        factor_series = df.mean(axis=1).rolling(window=parameters.get("lookback", 63)).mean()
    elif factor_type == "value":
        factor_series = df.mean(axis=1)
    elif factor_type == "volatility":
        factor_series = df.mean(axis=1).rolling(window=parameters.get("window", 21)).std()
    else:
        factor_series = df.mean(axis=1)

    factor_values = factor_series.dropna().tolist()

    payload = {
        "factor_type": factor_type,
        "symbols": symbols,
        "parameters": parameters or {},
        "values": factor_values,
    }

    await _persist_preferences(db, current_user["id"], "factor_custom", payload)

    return payload

