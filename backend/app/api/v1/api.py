"""
Main API router for v1
"""
from fastapi import APIRouter
from app.api.v1.endpoints import (
    strategies, market_data, ml_models, analytics, auth,
    advanced_backtesting, factor_analysis, risk_metrics, strategies_templates
)

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)  # Auth routes don't need prefix
api_router.include_router(strategies.router, prefix="/strategies", tags=["strategies"])
api_router.include_router(market_data.router, prefix="/market-data", tags=["market-data"])
api_router.include_router(ml_models.router, prefix="/ml-models", tags=["ml-models"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(advanced_backtesting.router)
api_router.include_router(factor_analysis.router)
api_router.include_router(risk_metrics.router)
api_router.include_router(strategies_templates.router)
