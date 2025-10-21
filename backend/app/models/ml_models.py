"""
Machine learning models for trading
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class MLModel(Base):
    """Machine learning model registry"""
    __tablename__ = "ml_models"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    model_type = Column(String(50), nullable=False)  # lstm, transformer, ensemble, etc.
    purpose = Column(String(100), nullable=False)  # price_prediction, volatility_forecast, etc.
    version = Column(String(20), nullable=False)
    
    # Model metadata
    features = Column(JSON)  # List of input features
    target = Column(String(100))  # Target variable
    hyperparameters = Column(JSON)  # Model hyperparameters
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    mse = Column(Float)
    mae = Column(Float)
    
    # Model artifacts
    model_path = Column(String(500))  # Path to saved model
    scaler_path = Column(String(500))  # Path to feature scaler
    feature_importance = Column(JSON)  # Feature importance scores
    
    # Training info
    training_start_date = Column(DateTime(timezone=True))
    training_end_date = Column(DateTime(timezone=True))
    training_samples = Column(Integer)
    validation_samples = Column(Integer)
    
    # Status
    is_active = Column(Boolean, default=False)
    is_training = Column(Boolean, default=False)
    status = Column(String(20), default="draft")  # draft, training, ready, failed
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Prediction(Base):
    """Model predictions table"""
    __tablename__ = "predictions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), nullable=False)
    symbol = Column(String(20), nullable=False)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Prediction data
    prediction_value = Column(Float, nullable=False)
    confidence = Column(Float)  # Prediction confidence score
    actual_value = Column(Float)  # Actual value for validation
    error = Column(Float)  # Prediction error
    
    # Input features used for prediction
    features = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelPerformance(Base):
    """Model performance tracking"""
    __tablename__ = "model_performance"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    
    # Performance metrics
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    mse = Column(Float)
    mae = Column(Float)
    
    # Drift detection
    feature_drift = Column(Float)  # Feature drift score
    prediction_drift = Column(Float)  # Prediction drift score
    
    # Data quality
    missing_values = Column(Float)  # Percentage of missing values
    outlier_ratio = Column(Float)  # Percentage of outliers
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
