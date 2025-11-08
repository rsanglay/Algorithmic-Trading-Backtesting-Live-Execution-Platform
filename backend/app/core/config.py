"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List, Optional, Union
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Algorithmic Trading Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/trading_platform"
    REDIS_URL: str = "redis://localhost:6379"
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: Union[str, List[str]] = "http://localhost:3000,http://localhost:8000"
    
    @field_validator('ALLOWED_HOSTS', mode='before')
    @classmethod
    def parse_allowed_hosts(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(',')]
        return v
    
    # External APIs
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    IEX_CLOUD_API_KEY: Optional[str] = None
    POLYGON_API_KEY: Optional[str] = None
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Data Storage
    DATA_STORAGE_PATH: str = "./data"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Trading
    DEFAULT_CASH: float = 100000.0
    COMMISSION: float = 0.001  # 0.1%
    SLIPPAGE: float = 0.0005  # 0.05%
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
