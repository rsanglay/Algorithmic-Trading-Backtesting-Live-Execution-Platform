"""
Production-grade database configuration and session management
"""
from sqlalchemy import create_engine, MetaData, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool, NullPool
import redis
from redis.connection import ConnectionPool
from contextlib import contextmanager

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# SQLAlchemy setup with production-grade connection pooling
if "sqlite" in settings.DATABASE_URL:
    # SQLite for development/testing
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    # PostgreSQL with connection pooling for production
    engine = create_engine(
        settings.DATABASE_URL,
        poolclass=QueuePool,
        pool_size=20,  # Number of connections to maintain
        max_overflow=10,  # Additional connections beyond pool_size
        pool_pre_ping=True,  # Verify connections before using
        pool_recycle=3600,  # Recycle connections after 1 hour
        echo=settings.DEBUG,
        connect_args={
            "connect_timeout": 10,
            "application_name": "trading_platform"
        }
    )

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

# Redis connection pool for production
redis_pool = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=50,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True
)

redis_client = redis.Redis(connection_pool=redis_pool)


# Database event listeners for monitoring
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Set SQLite pragmas for better performance"""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.close()


@event.listens_for(engine, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Log connection checkout"""
    if settings.DEBUG:
        logger.debug("Database connection checked out")


def get_db():
    """Database dependency with proper error handling"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Context manager for database sessions"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        logger.error(f"Database transaction error: {str(e)}", exc_info=True)
        db.rollback()
        raise
    finally:
        db.close()


def get_redis():
    """Redis dependency with connection pooling"""
    return redis_client


async def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}", exc_info=True)
        raise


def check_db_connection() -> bool:
    """Check database connection health"""
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False


def check_redis_connection() -> bool:
    """Check Redis connection health"""
    try:
        redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis connection check failed: {str(e)}")
        return False
