"""
Pydantic schemas for ML models
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


class MLModelBase(BaseModel):
    """Base ML model schema"""
    name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type")
    purpose: str = Field(..., description="Model purpose")
    version: str = Field(..., description="Model version")
    features: Optional[List[str]] = Field(default_factory=list, description="Input features")
    target: Optional[str] = Field(None, description="Target variable")
    hyperparameters: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Model hyperparameters")


class MLModelCreate(MLModelBase):
    """Schema for creating an ML model"""
    pass


class MLModelUpdate(BaseModel):
    """Schema for updating an ML model"""
    name: Optional[str] = None
    description: Optional[str] = None
    hyperparameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class MLModel(MLModelBase):
    """Schema for ML model response"""
    id: UUID
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    model_path: Optional[str] = None
    scaler_path: Optional[str] = None
    feature_importance: Optional[Dict[str, float]] = None
    training_start_date: Optional[datetime] = None
    training_end_date: Optional[datetime] = None
    training_samples: Optional[int] = None
    validation_samples: Optional[int] = None
    is_active: bool = False
    is_training: bool = False
    status: str = "draft"
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PredictionBase(BaseModel):
    """Base prediction schema"""
    symbol: str = Field(..., description="Trading symbol")
    timestamp: datetime = Field(..., description="Prediction timestamp")
    features: Dict[str, Any] = Field(..., description="Input features")


class PredictionCreate(PredictionBase):
    """Schema for creating a prediction"""
    pass


class Prediction(PredictionBase):
    """Schema for prediction response"""
    id: UUID
    model_id: UUID
    prediction_value: float
    confidence: Optional[float] = None
    actual_value: Optional[float] = None
    error: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModelPerformance(BaseModel):
    """Schema for model performance tracking"""
    id: UUID
    model_id: UUID
    date: datetime
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    mse: Optional[float] = None
    mae: Optional[float] = None
    feature_drift: Optional[float] = None
    prediction_drift: Optional[float] = None
    missing_values: Optional[float] = None
    outlier_ratio: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class ModelTrainingRequest(BaseModel):
    """Schema for model training request"""
    model_id: UUID
    training_data: Optional[Dict[str, Any]] = None
    validation_split: float = Field(default=0.2, description="Validation split ratio")
    test_split: float = Field(default=0.1, description="Test split ratio")


class ModelPredictionRequest(BaseModel):
    """Schema for model prediction request"""
    model_id: UUID
    features: Dict[str, Any] = Field(..., description="Input features for prediction")
    symbol: str = Field(..., description="Trading symbol")
    timestamp: datetime = Field(default_factory=datetime.now, description="Prediction timestamp")


class ModelEvaluationRequest(BaseModel):
    """Schema for model evaluation request"""
    model_id: UUID
    test_data: Optional[Dict[str, Any]] = None
    metrics: List[str] = Field(default_factory=lambda: ["accuracy", "precision", "recall", "f1_score"], description="Metrics to calculate")


class FeatureImportanceRequest(BaseModel):
    """Schema for feature importance request"""
    model_id: UUID
    method: str = Field(default="permutation", description="Feature importance method")
    n_repeats: int = Field(default=10, description="Number of repeats for permutation importance")
