"""
Analytics service for performance and risk analysis
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import pandas as pd
import numpy as np
from scipy import stats

from app.models.strategies import Strategy, Backtest, Position, Order
from app.models.market_data import MarketData


class AnalyticsService:
    """Service for analytics and performance calculations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_strategy_performance(self, strategy_id: UUID, start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get performance analytics for a strategy"""
        # Get strategy
        strategy = self.db.query(Strategy).filter(Strategy.id == strategy_id).first()
        if not strategy:
            return {"error": "Strategy not found"}
        
        # Get backtests
        query = self.db.query(Backtest).filter(Backtest.strategy_id == strategy_id)
        if start_date:
            query = query.filter(Backtest.start_date >= start_date)
        if end_date:
            query = query.filter(Backtest.end_date <= end_date)
        
        backtests = query.all()
        
        if not backtests:
            return {"error": "No backtests found for strategy"}
        
        # Calculate aggregate performance metrics
        total_returns = [bt.total_return for bt in backtests if bt.total_return is not None]
        sharpe_ratios = [bt.sharpe_ratio for bt in backtests if bt.sharpe_ratio is not None]
        max_drawdowns = [bt.max_drawdown for bt in backtests if bt.max_drawdown is not None]
        
        performance = {
            "strategy_id": strategy_id,
            "strategy_name": strategy.name,
            "total_backtests": len(backtests),
            "average_return": np.mean(total_returns) if total_returns else 0,
            "median_return": np.median(total_returns) if total_returns else 0,
            "best_return": np.max(total_returns) if total_returns else 0,
            "worst_return": np.min(total_returns) if total_returns else 0,
            "average_sharpe": np.mean(sharpe_ratios) if sharpe_ratios else 0,
            "average_drawdown": np.mean(max_drawdowns) if max_drawdowns else 0,
            "win_rate": len([r for r in total_returns if r > 0]) / len(total_returns) if total_returns else 0,
            "volatility": np.std(total_returns) if total_returns else 0
        }
        
        return performance
    
    async def get_portfolio_analytics(self, strategy_ids: List[UUID], start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get portfolio-level analytics"""
        # Get all strategies
        strategies = self.db.query(Strategy).filter(Strategy.id.in_(strategy_ids)).all()
        
        if not strategies:
            return {"error": "No strategies found"}
        
        # Get backtests for all strategies
        query = self.db.query(Backtest).filter(Backtest.strategy_id.in_(strategy_ids))
        if start_date:
            query = query.filter(Backtest.start_date >= start_date)
        if end_date:
            query = query.filter(Backtest.end_date <= end_date)
        
        backtests = query.all()
        
        if not backtests:
            return {"error": "No backtests found"}
        
        # Calculate portfolio metrics
        total_returns = [bt.total_return for bt in backtests if bt.total_return is not None]
        initial_capitals = [bt.initial_capital for bt in backtests if bt.initial_capital is not None]
        final_capitals = [bt.final_capital for bt in backtests if bt.final_capital is not None]
        
        portfolio_analytics = {
            "total_strategies": len(strategies),
            "total_backtests": len(backtests),
            "total_initial_capital": sum(initial_capitals) if initial_capitals else 0,
            "total_final_capital": sum(final_capitals) if final_capitals else 0,
            "portfolio_return": (sum(final_capitals) - sum(initial_capitals)) / sum(initial_capitals) if initial_capitals else 0,
            "average_strategy_return": np.mean(total_returns) if total_returns else 0,
            "best_strategy_return": np.max(total_returns) if total_returns else 0,
            "worst_strategy_return": np.min(total_returns) if total_returns else 0,
            "portfolio_volatility": np.std(total_returns) if total_returns else 0
        }
        
        return portfolio_analytics
    
    async def get_correlation_matrix(self, symbols: List[str], start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get correlation matrix for symbols"""
        # Get market data for all symbols
        market_data = self.db.query(MarketData).filter(
            and_(
                MarketData.symbol.in_(symbols),
                MarketData.timestamp >= start_date,
                MarketData.timestamp <= end_date
            )
        ).order_by(MarketData.timestamp).all()
        
        if not market_data:
            return {"error": "No market data found for the specified symbols and date range"}
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'symbol': row.symbol,
            'timestamp': row.timestamp,
            'close': row.close_price
        } for row in market_data])
        
        # Pivot to get close prices for each symbol
        price_df = df.pivot(index='timestamp', columns='symbol', values='close')
        
        # Calculate returns
        returns_df = price_df.pct_change().dropna()
        
        # Calculate correlation matrix
        correlation_matrix = returns_df.corr()
        
        return {
            "symbols": symbols,
            "correlation_matrix": correlation_matrix.to_dict(),
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "data_points": len(returns_df)
        }
    
    async def get_volatility_analysis(self, symbol: str, start_date: datetime, end_date: datetime,
                                     window: int = 30) -> Dict[str, Any]:
        """Get volatility analysis for a symbol"""
        # Get market data
        market_data = self.db.query(MarketData).filter(
            and_(
                MarketData.symbol == symbol,
                MarketData.timestamp >= start_date,
                MarketData.timestamp <= end_date
            )
        ).order_by(MarketData.timestamp).all()
        
        if not market_data:
            return {"error": "No market data found"}
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': row.timestamp,
            'close': row.close_price
        } for row in market_data])
        
        df.set_index('timestamp', inplace=True)
        
        # Calculate returns
        returns = df['close'].pct_change().dropna()
        
        # Calculate rolling volatility
        rolling_volatility = returns.rolling(window=window).std() * np.sqrt(252)
        
        # Calculate GARCH-like volatility (simplified)
        volatility_analysis = {
            "symbol": symbol,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "total_volatility": returns.std() * np.sqrt(252),
            "average_rolling_volatility": rolling_volatility.mean(),
            "max_rolling_volatility": rolling_volatility.max(),
            "min_rolling_volatility": rolling_volatility.min(),
            "volatility_trend": "increasing" if rolling_volatility.iloc[-1] > rolling_volatility.iloc[0] else "decreasing",
            "volatility_percentiles": {
                "25th": rolling_volatility.quantile(0.25),
                "50th": rolling_volatility.quantile(0.5),
                "75th": rolling_volatility.quantile(0.75),
                "95th": rolling_volatility.quantile(0.95)
            }
        }
        
        return volatility_analysis
    
    async def get_drawdown_analysis(self, strategy_id: UUID, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get drawdown analysis for a strategy"""
        # Get backtests
        query = self.db.query(Backtest).filter(Backtest.strategy_id == strategy_id)
        if start_date:
            query = query.filter(Backtest.start_date >= start_date)
        if end_date:
            query = query.filter(Backtest.end_date <= end_date)
        
        backtests = query.all()
        
        if not backtests:
            return {"error": "No backtests found"}
        
        # Calculate drawdown metrics
        max_drawdowns = [bt.max_drawdown for bt in backtests if bt.max_drawdown is not None]
        
        drawdown_analysis = {
            "strategy_id": strategy_id,
            "total_backtests": len(backtests),
            "average_max_drawdown": np.mean(max_drawdowns) if max_drawdowns else 0,
            "worst_drawdown": np.min(max_drawdowns) if max_drawdowns else 0,
            "best_drawdown": np.max(max_drawdowns) if max_drawdowns else 0,
            "drawdown_volatility": np.std(max_drawdowns) if max_drawdowns else 0,
            "drawdown_percentiles": {
                "25th": np.percentile(max_drawdowns, 25) if max_drawdowns else 0,
                "50th": np.percentile(max_drawdowns, 50) if max_drawdowns else 0,
                "75th": np.percentile(max_drawdowns, 75) if max_drawdowns else 0,
                "95th": np.percentile(max_drawdowns, 95) if max_drawdowns else 0
            }
        }
        
        return drawdown_analysis
    
    async def get_sharpe_ratio(self, strategy_id: UUID, risk_free_rate: float = 0.02,
                             start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate Sharpe ratio for a strategy"""
        # Get backtests
        query = self.db.query(Backtest).filter(Backtest.strategy_id == strategy_id)
        if start_date:
            query = query.filter(Backtest.start_date >= start_date)
        if end_date:
            query = query.filter(Backtest.end_date <= end_date)
        
        backtests = query.all()
        
        if not backtests:
            return {"error": "No backtests found"}
        
        # Calculate Sharpe ratios
        sharpe_ratios = [bt.sharpe_ratio for bt in backtests if bt.sharpe_ratio is not None]
        total_returns = [bt.total_return for bt in backtests if bt.total_return is not None]
        
        sharpe_analysis = {
            "strategy_id": strategy_id,
            "risk_free_rate": risk_free_rate,
            "average_sharpe_ratio": np.mean(sharpe_ratios) if sharpe_ratios else 0,
            "best_sharpe_ratio": np.max(sharpe_ratios) if sharpe_ratios else 0,
            "worst_sharpe_ratio": np.min(sharpe_ratios) if sharpe_ratios else 0,
            "sharpe_volatility": np.std(sharpe_ratios) if sharpe_ratios else 0,
            "total_backtests": len(backtests),
            "sharpe_percentiles": {
                "25th": np.percentile(sharpe_ratios, 25) if sharpe_ratios else 0,
                "50th": np.percentile(sharpe_ratios, 50) if sharpe_ratios else 0,
                "75th": np.percentile(sharpe_ratios, 75) if sharpe_ratios else 0,
                "95th": np.percentile(sharpe_ratios, 95) if sharpe_ratios else 0
            }
        }
        
        return sharpe_analysis
    
    async def monte_carlo_simulation(self, strategy_id: UUID, num_simulations: int = 1000,
                                   time_horizon: int = 252, start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Run Monte Carlo simulation for a strategy"""
        # Get backtests to estimate return distribution
        query = self.db.query(Backtest).filter(Backtest.strategy_id == strategy_id)
        if start_date:
            query = query.filter(Backtest.start_date >= start_date)
        if end_date:
            query = query.filter(Backtest.end_date <= end_date)
        
        backtests = query.all()
        
        if not backtests:
            return {"error": "No backtests found"}
        
        # Get return distribution
        returns = [bt.total_return for bt in backtests if bt.total_return is not None]
        
        if not returns:
            return {"error": "No returns data available"}
        
        # Estimate distribution parameters
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        
        # Run Monte Carlo simulation
        simulated_returns = np.random.normal(mean_return, std_return, (num_simulations, time_horizon))
        cumulative_returns = np.cumprod(1 + simulated_returns, axis=1)
        
        # Calculate statistics
        final_values = cumulative_returns[:, -1]
        
        monte_carlo_results = {
            "strategy_id": strategy_id,
            "num_simulations": num_simulations,
            "time_horizon": time_horizon,
            "simulation_results": {
                "mean_final_value": np.mean(final_values),
                "median_final_value": np.median(final_values),
                "std_final_value": np.std(final_values),
                "min_final_value": np.min(final_values),
                "max_final_value": np.max(final_values),
                "percentiles": {
                    "5th": np.percentile(final_values, 5),
                    "25th": np.percentile(final_values, 25),
                    "75th": np.percentile(final_values, 75),
                    "95th": np.percentile(final_values, 95)
                }
            },
            "risk_metrics": {
                "probability_of_loss": len(final_values[final_values < 1]) / len(final_values),
                "expected_shortfall": np.mean(final_values[final_values < np.percentile(final_values, 5)])
            }
        }
        
        return monte_carlo_results
