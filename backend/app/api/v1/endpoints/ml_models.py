"""
Machine learning model endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.core.database import get_db
from app.models.ml_models import MLModel, Prediction, ModelPerformance
from app.schemas.ml_models import (
    MLModelCreate, MLModelUpdate, MLModel as MLModelSchema,
    PredictionCreate, Prediction as PredictionSchema,
    ModelPerformance as ModelPerformanceSchema
)
from app.services.ml_service import MLService

router = APIRouter()


@router.post("/", response_model=MLModelSchema)
async def create_model(
    model: MLModelCreate,
    db: Session = Depends(get_db)
):
    """Create a new ML model"""
    service = MLService(db)
    return await service.create_model(model)


@router.get("/", response_model=List[MLModelSchema])
async def get_models(
    skip: int = 0,
    limit: int = 100,
    model_type: Optional[str] = None,
    purpose: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get ML models"""
    service = MLService(db)
    return await service.get_models(
        skip=skip, limit=limit, model_type=model_type,
        purpose=purpose, is_active=is_active
    )


@router.get("/{model_id}", response_model=MLModelSchema)
async def get_model(
    model_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific ML model"""
    service = MLService(db)
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.put("/{model_id}", response_model=MLModelSchema)
async def update_model(
    model_id: UUID,
    model_update: MLModelUpdate,
    db: Session = Depends(get_db)
):
    """Update an ML model"""
    service = MLService(db)
    model = await service.update_model(model_id, model_update)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.delete("/{model_id}")
async def delete_model(
    model_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete an ML model"""
    service = MLService(db)
    success = await service.delete_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model deleted successfully"}


@router.post("/{model_id}/train", response_model=dict)
async def train_model(
    model_id: UUID,
    background_tasks: BackgroundTasks,
    training_data: Optional[dict] = None,
    db: Session = Depends(get_db)
):
    """Train an ML model"""
    service = MLService(db)
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Start training in background
    background_tasks.add_task(service.train_model, model_id, training_data)
    
    return {"message": "Model training started", "model_id": model_id}


@router.post("/{model_id}/predict", response_model=PredictionSchema)
async def make_prediction(
    model_id: UUID,
    prediction_data: PredictionCreate,
    db: Session = Depends(get_db)
):
    """Make a prediction using an ML model"""
    service = MLService(db)
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    if not model.is_active:
        raise HTTPException(status_code=400, detail="Model is not active")
    
    prediction = await service.make_prediction(model_id, prediction_data)
    return prediction


@router.get("/{model_id}/predictions", response_model=List[PredictionSchema])
async def get_model_predictions(
    model_id: UUID,
    symbol: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get predictions for a model"""
    service = MLService(db)
    return await service.get_model_predictions(
        model_id, symbol=symbol, start_date=start_date,
        end_date=end_date, skip=skip, limit=limit
    )


@router.get("/{model_id}/performance", response_model=List[ModelPerformanceSchema])
async def get_model_performance(
    model_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get model performance metrics"""
    service = MLService(db)
    return await service.get_model_performance(
        model_id, start_date=start_date, end_date=end_date
    )


@router.post("/{model_id}/activate")
async def activate_model(
    model_id: UUID,
    db: Session = Depends(get_db)
):
    """Activate an ML model"""
    service = MLService(db)
    success = await service.activate_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model activated"}


@router.post("/{model_id}/deactivate")
async def deactivate_model(
    model_id: UUID,
    db: Session = Depends(get_db)
):
    """Deactivate an ML model"""
    service = MLService(db)
    success = await service.deactivate_model(model_id)
    if not success:
        raise HTTPException(status_code=404, detail="Model not found")
    return {"message": "Model deactivated"}


@router.post("/{model_id}/retrain")
async def retrain_model(
    model_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Retrain an ML model with new data"""
    service = MLService(db)
    model = await service.get_model(model_id)
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Start retraining in background
    background_tasks.add_task(service.retrain_model, model_id)
    
    return {"message": "Model retraining started", "model_id": model_id}
