"""
Pytest configuration and fixtures
"""
from typing import Callable, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.compiler import compiles

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.models.strategies import Strategy
from tests.factories import BaseFactory, UserFactory, StrategyFactory


@compiles(UUID, "sqlite")
def compile_uuid(element, compiler, **kwargs):
    """Render PostgreSQL UUID columns as CHAR for SQLite compatibility."""
    return "CHAR(36)"


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    """Create a fresh database session for each test"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
def configure_factory_session(db_session):
    """Set SQLAlchemy session for factory_boy models."""
    BaseFactory._meta.sqlalchemy_session = db_session
    yield
    BaseFactory._meta.sqlalchemy_session = None


@pytest.fixture(scope="function")
def client(db_session) -> Generator[TestClient, None, None]:
    """Create a synchronous test client"""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session) -> AsyncClient:
    """Async HTTP client for FastAPI app."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(app=app, base_url="http://testserver", follow_redirects=True) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def create_user() -> Callable[..., User]:
    """Factory helper to create a user instance."""

    def _create_user(**kwargs) -> User:
        user = UserFactory(**kwargs)
        return user

    return _create_user


@pytest.fixture
def create_strategy(create_user) -> Callable[..., Strategy]:
    """Factory helper to create a strategy instance."""

    def _create_strategy(**kwargs) -> Strategy:
        # Ensure a creator exists
        if "created_by" not in kwargs:
            creator = create_user()
            kwargs.setdefault("created_by", creator.username)
        strategy = StrategyFactory(**kwargs)
        return strategy

    return _create_strategy


@pytest.fixture
def sample_strategy_data():
    """Sample strategy data for API payloads."""
    return {
        "name": "Test Momentum Strategy",
        "description": "A test momentum strategy",
        "strategy_type": "momentum",
        "code": """
 def execute(data):
     # Simple momentum strategy
     if data['close'] > data['sma_20']:
         return 'buy'
     elif data['close'] < data['sma_20']:
         return 'sell'
     return 'hold'
 """,
        "parameters": {"lookback": 20},
        "created_by": "test_user",
    }


@pytest.fixture
def sample_market_data():
    """Sample market data for testing"""
    return {
        "symbol": "SPY",
        "timestamp": "2024-01-01T00:00:00",
        "open_price": 100.0,
        "high_price": 101.0,
        "low_price": 99.0,
        "close_price": 100.5,
        "volume": 1000000,
        "source": "test",
    }


@pytest.fixture
def sample_backtest_data():
    """Sample backtest data for testing"""
    return {
        "name": "Test Backtest",
        "start_date": "2024-01-01T00:00:00",
        "end_date": "2024-12-31T23:59:59",
        "initial_capital": 100000.0,
    }
