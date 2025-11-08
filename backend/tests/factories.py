import uuid
import factory
from factory import LazyFunction
from factory.fuzzy import FuzzyDecimal

from app.models.user import User
from app.models.strategies import Strategy
from app.models.strategies import Backtest


class BaseFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory with default SQLAlchemy configuration."""

    class Meta:
        abstract = True
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "flush"


class UserFactory(BaseFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    id = LazyFunction(uuid.uuid4)
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    username = factory.Sequence(lambda n: f"testuser{n}")
    full_name = factory.Sequence(lambda n: f"Test User {n}")
    hashed_password = "testpasswordhash"
    is_active = True
    is_verified = False
    is_superuser = False
    dashboard_preferences = factory.Dict({
        "layout": "default",
        "widgets": ["metrics", "performance_chart"],
        "default_timeframe": "1M"
    })
    trading_preferences = factory.Dict({
        "default_exchange": "US",
        "default_currency": "USD"
    })


class StrategyFactory(BaseFactory):
    """Factory for creating test strategies."""

    class Meta:
        model = Strategy

    id = LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Strategy {n}")
    description = factory.Faker("sentence")
    strategy_type = factory.Iterator([
        "momentum",
        "mean_reversion",
        "pairs_trading",
        "stat_arbitrage"
    ])
    code = """
from typing import Dict

def execute(data: Dict[str, float]) -> str:
    if data['close'] > data['sma_20']:
        return 'buy'
    if data['close'] < data['sma_20']:
        return 'sell'
    return 'hold'
"""
    parameters = factory.Dict({"lookback": 20, "threshold": 0.05})
    is_active = False
    is_live = False
    created_by = factory.Sequence(lambda n: f"user{n}")


class BacktestFactory(BaseFactory):
    """Factory for creating test backtests."""

    class Meta:
        model = Backtest

    id = LazyFunction(uuid.uuid4)
    strategy_id = LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"Backtest {n}")
    start_date = factory.Faker("date_time_this_year")
    end_date = factory.Faker("date_time_this_year")
    initial_capital = FuzzyDecimal(10000.0, 50000.0)
    total_return = FuzzyDecimal(-0.2, 0.5)
    annualized_return = FuzzyDecimal(-0.1, 0.3)
    sharpe_ratio = FuzzyDecimal(-1.0, 3.0)
    max_drawdown = FuzzyDecimal(0.0, 0.3)
    win_rate = FuzzyDecimal(0.3, 0.8)
    profit_factor = FuzzyDecimal(0.5, 2.5)
    status = "completed"
