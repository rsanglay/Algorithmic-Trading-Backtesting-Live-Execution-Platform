"""
Production-grade caching utilities
"""
from typing import Any, Optional, Callable
from functools import wraps
import json
import hashlib
from datetime import timedelta
import redis
from redis.exceptions import RedisError

from app.core.config import settings
from app.core.database import get_redis
from app.core.logging import get_logger

logger = get_logger(__name__)


class CacheManager:
    """Redis-based cache manager"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self._connect()
    
    def _connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = get_redis()
            self.redis_client.ping()
        except RedisError as e:
            logger.warning(f"Redis connection failed: {str(e)}. Caching disabled.")
            self.redis_client = None
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
        except (RedisError, json.JSONDecodeError) as e:
            logger.warning(f"Cache get error for key {key}: {str(e)}")
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache"""
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except (RedisError, TypeError) as e:
            logger.warning(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not self.redis_client:
            return False
        
        try:
            self.redis_client.delete(key)
            return True
        except RedisError as e:
            logger.warning(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.warning(f"Cache clear pattern error for {pattern}: {str(e)}")
            return 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis_client:
            return False
        
        try:
            return bool(self.redis_client.exists(key))
        except RedisError:
            return False


# Global cache manager instance
cache_manager = CacheManager()


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 3600, key_prefix: str = ""):
    """Decorator to cache function results"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key_str = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            cached_value = cache_manager.get(cache_key_str)
            if cached_value is not None:
                return cached_value
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            cache_manager.set(cache_key_str, result, ttl)
            
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    """Invalidate cache entries matching pattern"""
    cache_manager.clear_pattern(pattern)


class CacheKeys:
    """Cache key constants"""
    MARKET_DATA = "market_data"
    STRATEGY = "strategy"
    BACKTEST = "backtest"
    ML_MODEL = "ml_model"
    ANALYTICS = "analytics"
    
    @staticmethod
    def market_data(symbol: str, start_date: str, end_date: str) -> str:
        return f"{CacheKeys.MARKET_DATA}:{symbol}:{start_date}:{end_date}"
    
    @staticmethod
    def strategy(strategy_id: str) -> str:
        return f"{CacheKeys.STRATEGY}:{strategy_id}"
    
    @staticmethod
    def backtest(backtest_id: str) -> str:
        return f"{CacheKeys.BACKTEST}:{backtest_id}"
    
    @staticmethod
    def ml_model(model_id: str) -> str:
        return f"{CacheKeys.ML_MODEL}:{model_id}"
    
    @staticmethod
    def analytics(strategy_id: str, metric_type: str) -> str:
        return f"{CacheKeys.ANALYTICS}:{strategy_id}:{metric_type}"
