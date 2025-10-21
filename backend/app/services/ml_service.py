"""
Machine learning service for model management and predictions
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

from app.models.ml_models import MLModel, Prediction, ModelPerformance
from app.schemas.ml_models import MLModelCreate, MLModelUpdate, PredictionCreate
from app.core.config import settings


class MLService:
    """Service for machine learning model management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.models_dir = os.path.join(settings.DATA_STORAGE_PATH, "models")
        os.makedirs(self.models_dir, exist_ok=True)
    
    async def create_model(self, model_data: MLModelCreate) -> MLModel:
        """Create a new ML model"""
        model = MLModel(
            name=model_data.name,
            model_type=model_data.model_type,
            purpose=model_data.purpose,
            version=model_data.version,
            features=model_data.features,
            target=model_data.target,
            hyperparameters=model_data.hyperparameters
        )
        
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model
    
    async def get_models(self, skip: int = 0, limit: int = 100, model_type: Optional[str] = None,
                       purpose: Optional[str] = None, is_active: Optional[bool] = None) -> List[MLModel]:
        """Get ML models with filters"""
        query = self.db.query(MLModel)
        
        if model_type:
            query = query.filter(MLModel.model_type == model_type)
        if purpose:
            query = query.filter(MLModel.purpose == purpose)
        if is_active is not None:
            query = query.filter(MLModel.is_active == is_active)
        
        return query.offset(skip).limit(limit).all()
    
    async def get_model(self, model_id: UUID) -> Optional[MLModel]:
        """Get a specific ML model"""
        return self.db.query(MLModel).filter(MLModel.id == model_id).first()
    
    async def update_model(self, model_id: UUID, model_update: MLModelUpdate) -> Optional[MLModel]:
        """Update an ML model"""
        model = await self.get_model(model_id)
        if not model:
            return None
        
        update_data = model_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        
        self.db.commit()
        self.db.refresh(model)
        return model
    
    async def delete_model(self, model_id: UUID) -> bool:
        """Delete an ML model"""
        model = await self.get_model(model_id)
        if not model:
            return False
        
        # Delete model files if they exist
        if model.model_path and os.path.exists(model.model_path):
            os.remove(model.model_path)
        if model.scaler_path and os.path.exists(model.scaler_path):
            os.remove(model.scaler_path)
        
        self.db.delete(model)
        self.db.commit()
        return True
    
    async def train_model(self, model_id: UUID, training_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Train an ML model"""
        model = await self.get_model(model_id)
        if not model:
            return {"error": "Model not found"}
        
        try:
            # Update status to training
            model.is_training = True
            model.status = "training"
            self.db.commit()
            
            # This is a simplified training process
            # In a real implementation, you would:
            # 1. Fetch training data from database
            # 2. Preprocess the data
            # 3. Train the model based on model_type
            # 4. Save the model and scaler
            
            # For demonstration, we'll create a simple model
            if model.model_type == "random_forest":
                ml_model = RandomForestRegressor(
                    n_estimators=model.hyperparameters.get('n_estimators', 100),
                    max_depth=model.hyperparameters.get('max_depth', 10),
                    random_state=42
                )
            else:
                # Default to RandomForest for now
                ml_model = RandomForestRegressor(random_state=42)
            
            # Generate dummy training data for demonstration
            X = np.random.randn(1000, len(model.features) if model.features else 10)
            y = np.random.randn(1000)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Train model
            ml_model.fit(X_train_scaled, y_train)
            
            # Make predictions
            y_pred = ml_model.predict(X_test_scaled)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            # Save model and scaler
            model_path = os.path.join(self.models_dir, f"{model_id}.joblib")
            scaler_path = os.path.join(self.models_dir, f"{model_id}_scaler.joblib")
            
            joblib.dump(ml_model, model_path)
            joblib.dump(scaler, scaler_path)
            
            # Update model with results
            model.model_path = model_path
            model.scaler_path = scaler_path
            model.mse = mse
            model.mae = mae
            model.accuracy = r2  # Using R² as accuracy metric for regression
            model.training_start_date = datetime.now()
            model.training_end_date = datetime.now()
            model.training_samples = len(X_train)
            model.validation_samples = len(X_test)
            model.is_training = False
            model.status = "ready"
            
            self.db.commit()
            
            return {
                "message": "Model training completed",
                "metrics": {
                    "mse": mse,
                    "mae": mae,
                    "r2": r2
                }
            }
            
        except Exception as e:
            model.is_training = False
            model.status = "failed"
            self.db.commit()
            return {"error": f"Training failed: {str(e)}"}
    
    async def make_prediction(self, model_id: UUID, prediction_data: PredictionCreate) -> Prediction:
        """Make a prediction using an ML model"""
        model = await self.get_model(model_id)
        if not model or not model.is_active:
            raise ValueError("Model not found or not active")
        
        # Load model and scaler
        if not model.model_path or not os.path.exists(model.model_path):
            raise ValueError("Model not trained or model file not found")
        
        ml_model = joblib.load(model.model_path)
        scaler = joblib.load(model.scaler_path)
        
        # Prepare features
        features = np.array([prediction_data.features[f] for f in model.features]).reshape(1, -1)
        features_scaled = scaler.transform(features)
        
        # Make prediction
        prediction_value = ml_model.predict(features_scaled)[0]
        confidence = 0.8  # Simplified confidence calculation
        
        # Create prediction record
        prediction = Prediction(
            model_id=model_id,
            symbol=prediction_data.symbol,
            timestamp=prediction_data.timestamp,
            prediction_value=prediction_value,
            confidence=confidence,
            features=prediction_data.features
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        return prediction
    
    async def get_model_predictions(self, model_id: UUID, symbol: Optional[str] = None,
                                  start_date: Optional[datetime] = None, end_date: Optional[datetime] = None,
                                  skip: int = 0, limit: int = 100) -> List[Prediction]:
        """Get predictions for a model"""
        query = self.db.query(Prediction).filter(Prediction.model_id == model_id)
        
        if symbol:
            query = query.filter(Prediction.symbol == symbol)
        if start_date:
            query = query.filter(Prediction.timestamp >= start_date)
        if end_date:
            query = query.filter(Prediction.timestamp <= end_date)
        
        return query.order_by(desc(Prediction.timestamp)).offset(skip).limit(limit).all()
    
    async def get_model_performance(self, model_id: UUID, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> List[ModelPerformance]:
        """Get model performance metrics"""
        query = self.db.query(ModelPerformance).filter(ModelPerformance.model_id == model_id)
        
        if start_date:
            query = query.filter(ModelPerformance.date >= start_date)
        if end_date:
            query = query.filter(ModelPerformance.date <= end_date)
        
        return query.order_by(desc(ModelPerformance.date)).all()
    
    async def activate_model(self, model_id: UUID) -> bool:
        """Activate an ML model"""
        model = await self.get_model(model_id)
        if not model or model.status != "ready":
            return False
        
        model.is_active = True
        self.db.commit()
        return True
    
    async def deactivate_model(self, model_id: UUID) -> bool:
        """Deactivate an ML model"""
        model = await self.get_model(model_id)
        if not model:
            return False
        
        model.is_active = False
        self.db.commit()
        return True
    
    async def retrain_model(self, model_id: UUID) -> Dict[str, Any]:
        """Retrain an ML model with new data"""
        # This would typically:
        # 1. Fetch new training data
        # 2. Retrain the model
        # 3. Validate performance
        # 4. Update model if performance is better
        
        return await self.train_model(model_id)
    
    async def detect_model_drift(self, model_id: UUID) -> Dict[str, Any]:
        """Detect model drift"""
        # This would implement drift detection algorithms
        # For now, return a placeholder
        return {
            "model_id": model_id,
            "drift_detected": False,
            "drift_score": 0.1,
            "recommendation": "Model is performing well"
        }
