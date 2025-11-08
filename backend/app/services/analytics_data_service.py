"""Utility service for loading price data and strategy context for analytics endpoints."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple, Callable
from uuid import UUID

import pandas as pd

from sqlalchemy.orm import Session

from app.models.strategies import Strategy
from app.services.market_data_service import MarketDataService


DEFAULT_SYMBOL = "SPY"
DEFAULT_PERIOD = "2y"
DEFAULT_INTERVAL = "1d"


@dataclass
class StrategyContext:
    """Container for strategy metadata used in analytics."""

    strategy: Strategy
    symbol: str
    parameters: Dict[str, Any]


class AnalyticsDataService:
    """Helper for analytics endpoints to fetch strategies and price series."""

    def __init__(self, db: Session):
        self.db = db
        self.market_service = MarketDataService(db)

    async def get_strategy_context(self, strategy_id: UUID, fallback_symbol: str = DEFAULT_SYMBOL) -> StrategyContext:
        strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            raise ValueError("Strategy not found")

        params = strategy.parameters or {}
        symbol = params.get("symbol") or params.get("ticker") or fallback_symbol

        return StrategyContext(strategy=strategy, symbol=symbol, parameters=params)

    async def load_price_history(
        self,
        symbol: str,
        period: str = DEFAULT_PERIOD,
        interval: str = DEFAULT_INTERVAL,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> pd.DataFrame:
        """Load price history either from database (if cached) or Yahoo Finance."""

        if start_date and not end_date:
            end_date = datetime.utcnow()
        if not start_date and end_date:
            start_date = end_date - timedelta(days=365)

        # Try to load from local database first if explicit dates are provided
        if start_date and end_date:
            data = await self.market_service.get_market_data(symbol, start_date, end_date)
            if data:
                df = pd.DataFrame(
                    {
                        "timestamp": [row.timestamp for row in data],
                        "open": [row.open_price for row in data],
                        "high": [row.high_price for row in data],
                        "low": [row.low_price for row in data],
                        "close": [row.close_price for row in data],
                        "volume": [row.volume for row in data],
                    }
                )
                df.set_index(pd.to_datetime(df["timestamp"]), inplace=True)
                df.drop(columns=["timestamp"], inplace=True)
                return df.sort_index()

        # Fallback to Yahoo Finance
        response = await self.market_service.fetch_yfinance_data_direct(symbol, period=period, interval=interval)
        if response.get("error"):
            raise ValueError(response["error"])

        price_rows = response.get("data", [])
        if not price_rows:
            raise ValueError(f"No price data available for symbol {symbol}")

        df = pd.DataFrame(price_rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.set_index("timestamp", inplace=True)
        df.rename(
            columns={"open": "open", "high": "high", "low": "low", "close": "close", "volume": "volume"},
            inplace=True,
        )
        df.sort_index(inplace=True)

        if start_date:
            df = df[df.index >= start_date]
        if end_date:
            df = df[df.index <= end_date]

        return df

    @staticmethod
    def to_returns(df: pd.DataFrame, column: str = "close") -> pd.Series:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
        returns = df[column].pct_change().dropna()
        return returns

    @staticmethod
    def equity_curve_from_returns(returns: pd.Series, initial_capital: float = 100_000.0) -> pd.Series:
        cumulative = (1 + returns).cumprod()
        return cumulative * initial_capital

    def get_strategy_function(self, strategy_type: str) -> Callable[[pd.DataFrame], str]:
        """Map strategy type to quantitative strategy function."""
        from app.services.quantitative_strategies import QuantitativeStrategies

        strategy_type = (strategy_type or "").lower()

        mapping: Dict[str, Callable[[pd.DataFrame], Any]] = {
            "momentum": lambda data: QuantitativeStrategies.momentum_strategy(data["close"]),
            "mean_reversion": lambda data: QuantitativeStrategies.mean_reversion_rsi(data["close"]),
            "mean_reversion_rsi": lambda data: QuantitativeStrategies.mean_reversion_rsi(data["close"]),
            "pairs_trading": lambda data: QuantitativeStrategies.moving_average_crossover(data["close"]),
            "trend_following": lambda data: QuantitativeStrategies.moving_average_crossover(data["close"]),
            "bollinger_bands": lambda data: QuantitativeStrategies.bollinger_bands_strategy(data["close"]),
            "macd": lambda data: QuantitativeStrategies.macd_strategy(data["close"]),
        }

        if strategy_type in mapping:
            return mapping[strategy_type]

        # Default to simple momentum style
        return mapping["momentum"]
