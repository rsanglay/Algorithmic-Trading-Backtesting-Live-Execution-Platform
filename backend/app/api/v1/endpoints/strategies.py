"""
Strategy management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.strategies import Strategy, Backtest, Position, Order
from app.schemas.strategies import (
    StrategyCreate, StrategyUpdate, Strategy as StrategySchema,
    BacktestCreate, Backtest as BacktestSchema,
    PositionCreate, Position as PositionSchema,
    OrderCreate, Order as OrderSchema
)
from app.services.strategy_service import StrategyService
from app.services.backtest_service import BacktestService

router = APIRouter()


@router.post("/", response_model=StrategySchema)
async def create_strategy(
    strategy: StrategyCreate,
    db: Session = Depends(get_db)
):
    """Create a new trading strategy"""
    service = StrategyService(db)
    return await service.create_strategy(strategy)


@router.get("/", response_model=List[StrategySchema])
async def get_strategies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all strategies"""
    service = StrategyService(db)
    return await service.get_strategies(skip=skip, limit=limit)


@router.get("/{strategy_id}", response_model=StrategySchema)
async def get_strategy(
    strategy_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific strategy"""
    service = StrategyService(db)
    strategy = await service.get_strategy(strategy_id)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.put("/{strategy_id}", response_model=StrategySchema)
async def update_strategy(
    strategy_id: UUID,
    strategy_update: StrategyUpdate,
    db: Session = Depends(get_db)
):
    """Update a strategy"""
    service = StrategyService(db)
    strategy = await service.update_strategy(strategy_id, strategy_update)
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return strategy


@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: UUID,
    db: Session = Depends(get_db)
):
    """Delete a strategy"""
    service = StrategyService(db)
    success = await service.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy deleted successfully"}


@router.post("/{strategy_id}/activate")
async def activate_strategy(
    strategy_id: UUID,
    db: Session = Depends(get_db)
):
    """Activate a strategy for live trading"""
    service = StrategyService(db)
    success = await service.activate_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy activated"}


@router.post("/{strategy_id}/deactivate")
async def deactivate_strategy(
    strategy_id: UUID,
    db: Session = Depends(get_db)
):
    """Deactivate a strategy"""
    service = StrategyService(db)
    success = await service.deactivate_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Strategy not found")
    return {"message": "Strategy deactivated"}


# Backtest endpoints
@router.post("/{strategy_id}/backtests", response_model=BacktestSchema)
async def create_backtest(
    strategy_id: UUID,
    backtest: BacktestCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create and run a backtest"""
    service = BacktestService(db)
    backtest_result = await service.create_backtest(strategy_id, backtest)
    
    # Run backtest in background
    background_tasks.add_task(service.run_backtest, backtest_result.id)
    
    return backtest_result


@router.get("/{strategy_id}/backtests", response_model=List[BacktestSchema])
async def get_strategy_backtests(
    strategy_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get backtests for a strategy"""
    service = BacktestService(db)
    return await service.get_strategy_backtests(strategy_id, skip=skip, limit=limit)


@router.get("/backtests/{backtest_id}", response_model=BacktestSchema)
async def get_backtest(
    backtest_id: UUID,
    db: Session = Depends(get_db)
):
    """Get a specific backtest"""
    service = BacktestService(db)
    backtest = await service.get_backtest(backtest_id)
    if not backtest:
        raise HTTPException(status_code=404, detail="Backtest not found")
    return backtest


# Position endpoints
@router.get("/{strategy_id}/positions", response_model=List[PositionSchema])
async def get_strategy_positions(
    strategy_id: UUID,
    db: Session = Depends(get_db)
):
    """Get positions for a strategy"""
    service = StrategyService(db)
    return await service.get_strategy_positions(strategy_id)


# Order endpoints
@router.get("/{strategy_id}/orders", response_model=List[OrderSchema])
async def get_strategy_orders(
    strategy_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get orders for a strategy"""
    service = StrategyService(db)
    return await service.get_strategy_orders(strategy_id, skip=skip, limit=limit)
