"""
Quantitative strategy templates API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict

from app.core.database import get_db
from app.services.quantitative_strategies import QuantitativeStrategies
from app.core.auth import get_current_active_user

router = APIRouter(prefix="/strategy-templates", tags=["strategy-templates"])

# Strategy template definitions
STRATEGY_TEMPLATES_INFO = {
    'momentum': {
        'name': 'Momentum Strategy',
        'description': 'Buy when short-term momentum exceeds long-term momentum',
        'category': 'momentum'
    },
    'mean_reversion_rsi': {
        'name': 'Mean Reversion (RSI)',
        'description': 'RSI-based mean reversion strategy',
        'category': 'mean_reversion'
    },
    'moving_average_crossover': {
        'name': 'Moving Average Crossover',
        'description': 'Golden/death cross strategy',
        'category': 'trend_following'
    },
    'bollinger_bands': {
        'name': 'Bollinger Bands',
        'description': 'Mean reversion using Bollinger Bands',
        'category': 'mean_reversion'
    },
    'macd': {
        'name': 'MACD Strategy',
        'description': 'MACD crossover signals',
        'category': 'trend_following'
    }
}


@router.get("/")
async def get_strategy_templates(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all available strategy templates"""
    templates = []
    for key, info in STRATEGY_TEMPLATES_INFO.items():
        templates.append({
            "id": key,
            "name": info['name'],
            "description": info['description'],
            "category": info['category']
        })
    
    return {"templates": templates}


@router.get("/{template_id}")
async def get_strategy_template(
    template_id: str,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get details of a specific strategy template"""
    if template_id not in STRATEGY_TEMPLATES_INFO:
        raise HTTPException(status_code=404, detail="Strategy template not found")
    
    info = STRATEGY_TEMPLATES_INFO[template_id]
    return {
        "id": template_id,
        "name": info['name'],
        "description": info['description'],
        "category": info['category'],
        "parameters": _get_template_parameters(template_id)
    }


def _get_strategy_category(template_id: str) -> str:
    """Get strategy category"""
    categories = {
        'momentum': 'momentum',
        'mean_reversion_rsi': 'mean_reversion',
        'moving_average_crossover': 'trend_following',
        'bollinger_bands': 'mean_reversion',
        'macd': 'trend_following'
    }
    return categories.get(template_id, 'other')


def _get_template_parameters(template_id: str) -> Dict:
    """Get default parameters for template"""
    params = {
        'momentum': {
            'lookback_short': 21,
            'lookback_long': 252,
            'threshold': 0.0
        },
        'mean_reversion_rsi': {
            'period': 14,
            'oversold': 30,
            'overbought': 70
        },
        'moving_average_crossover': {
            'short_period': 50,
            'long_period': 200
        },
        'bollinger_bands': {
            'period': 20,
            'num_std': 2.0
        },
        'macd': {
            'fast_period': 12,
            'slow_period': 26,
            'signal_period': 9
        }
    }
    return params.get(template_id, {})

