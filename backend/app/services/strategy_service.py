"""
Strategy management service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.models.strategies import Strategy, Position, Order
from app.schemas.strategies import StrategyCreate, StrategyUpdate


class StrategyService:
    """Service for managing trading strategies"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_strategy(self, strategy_data: StrategyCreate) -> Strategy:
        """Create a new trading strategy"""
        strategy = Strategy(
            name=strategy_data.name,
            description=strategy_data.description,
            strategy_type=strategy_data.strategy_type,
            code=strategy_data.code,
            parameters=strategy_data.parameters,
            created_by=strategy_data.created_by
        )
        
        self.db.add(strategy)
        self.db.commit()
        self.db.refresh(strategy)
        return strategy
    
    async def get_strategies(self, skip: int = 0, limit: int = 100) -> List[Strategy]:
        """Get all strategies"""
        return self.db.query(Strategy).offset(skip).limit(limit).all()
    
    async def get_strategy(self, strategy_id: UUID) -> Optional[Strategy]:
        """Get a specific strategy"""
        return self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
    
    async def update_strategy(self, strategy_id: UUID, strategy_update: StrategyUpdate) -> Optional[Strategy]:
        """Update a strategy"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return None
        
        update_data = strategy_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(strategy, field, value)
        
        self.db.commit()
        self.db.refresh(strategy)
        return strategy
    
    async def delete_strategy(self, strategy_id: UUID) -> bool:
        """Delete a strategy"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return False
        
        self.db.delete(strategy)
        self.db.commit()
        return True
    
    async def activate_strategy(self, strategy_id: UUID) -> bool:
        """Activate a strategy for live trading"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return False
        
        strategy.is_active = True
        self.db.commit()
        return True
    
    async def deactivate_strategy(self, strategy_id: UUID) -> bool:
        """Deactivate a strategy"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy:
            return False
        
        strategy.is_active = False
        strategy.is_live = False
        self.db.commit()
        return True
    
    async def get_strategy_positions(self, strategy_id: UUID) -> List[Position]:
        """Get positions for a strategy"""
        return self.db.query(Position).filter(
            and_(Position.strategy_id == strategy_id, Position.is_open == True)
        ).all()
    
    async def get_strategy_orders(self, strategy_id: UUID, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders for a strategy"""
        return self.db.query(Order).filter(
            Order.strategy_id == strategy_id
        ).offset(skip).limit(limit).all()
    
    async def execute_strategy(self, strategy_id: UUID, market_data: dict) -> dict:
        """Execute a strategy with current market data"""
        strategy = await self.get_strategy(strategy_id)
        if not strategy or not strategy.is_active:
            return {"error": "Strategy not found or not active"}
        
        try:
            # This would execute the strategy code with market data
            # For now, return a placeholder
            return {
                "strategy_id": strategy_id,
                "execution_time": datetime.now(),
                "signals": [],
                "orders": []
            }
        except Exception as e:
            return {"error": f"Strategy execution failed: {str(e)}"}
