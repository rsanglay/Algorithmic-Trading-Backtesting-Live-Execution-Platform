"""
Backtesting service for trading strategies
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from app.models.strategies import Strategy, Backtest
from app.models.market_data import MarketData
from app.schemas.strategies import BacktestCreate


class BacktestService:
    """Service for running backtests"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_backtest(self, strategy_id: UUID, backtest_data: BacktestCreate) -> Backtest:
        """Create a new backtest"""
        backtest = Backtest(
            strategy_id=strategy_id,
            name=backtest_data.name,
            start_date=backtest_data.start_date,
            end_date=backtest_data.end_date,
            initial_capital=backtest_data.initial_capital
        )
        
        self.db.add(backtest)
        self.db.commit()
        self.db.refresh(backtest)
        return backtest
    
    async def get_backtest(self, backtest_id: UUID) -> Optional[Backtest]:
        """Get a specific backtest"""
        return self.db.query(Backtest).filter(Backtest.id == backtest_id).first()
    
    async def get_strategy_backtests(self, strategy_id: UUID, skip: int = 0, limit: int = 100) -> List[Backtest]:
        """Get backtests for a strategy"""
        return self.db.query(Backtest).filter(
            Backtest.strategy_id == strategy_id
        ).offset(skip).limit(limit).all()
    
    async def run_backtest(self, backtest_id: UUID) -> Dict[str, Any]:
        """Run a backtest simulation"""
        backtest = await self.get_backtest(backtest_id)
        if not backtest:
            return {"error": "Backtest not found"}
        
        try:
            # Update status to running
            backtest.status = "running"
            self.db.commit()
            
            # Get market data for the backtest period
            market_data = self.db.query(MarketData).filter(
                and_(
                    MarketData.timestamp >= backtest.start_date,
                    MarketData.timestamp <= backtest.end_date
                )
            ).order_by(MarketData.timestamp).all()
            
            if not market_data:
                backtest.status = "failed"
                self.db.commit()
                return {"error": "No market data available for the specified period"}
            
            # Convert to DataFrame for easier processing
            df = pd.DataFrame([{
                'timestamp': row.timestamp,
                'open': row.open_price,
                'high': row.high_price,
                'low': row.low_price,
                'close': row.close_price,
                'volume': row.volume
            } for row in market_data])
            
            # Run the backtest simulation
            results = await self._simulate_backtest(backtest, df)
            
            # Update backtest with results
            backtest.final_capital = results['final_capital']
            backtest.total_return = results['total_return']
            backtest.annualized_return = results['annualized_return']
            backtest.sharpe_ratio = results['sharpe_ratio']
            backtest.max_drawdown = results['max_drawdown']
            backtest.win_rate = results['win_rate']
            backtest.profit_factor = results['profit_factor']
            backtest.metrics = results['metrics']
            backtest.trades = results['trades']
            backtest.status = "completed"
            backtest.completed_at = datetime.now()
            
            self.db.commit()
            
            return {"message": "Backtest completed successfully", "results": results}
            
        except Exception as e:
            backtest.status = "failed"
            self.db.commit()
            return {"error": f"Backtest failed: {str(e)}"}
    
    async def _simulate_backtest(self, backtest: Backtest, df: pd.DataFrame) -> Dict[str, Any]:
        """Simulate the backtest with market data"""
        # Initialize portfolio
        cash = backtest.initial_capital
        positions = {}
        trades = []
        portfolio_values = []
        
        # Simple buy and hold strategy for demonstration
        # In a real implementation, this would execute the strategy code
        for _, row in df.iterrows():
            # Calculate portfolio value
            portfolio_value = cash + sum(positions.get(symbol, 0) * row['close'] for symbol in positions)
            portfolio_values.append({
                'timestamp': row['timestamp'],
                'value': portfolio_value
            })
            
            # Simple strategy: buy on first day, sell on last day
            if row['timestamp'] == df.iloc[0]['timestamp']:
                # Buy signal
                shares_to_buy = cash * 0.95 / row['close']  # Use 95% of cash
                cash -= shares_to_buy * row['close']
                positions['SPY'] = shares_to_buy
                trades.append({
                    'timestamp': row['timestamp'],
                    'action': 'buy',
                    'symbol': 'SPY',
                    'quantity': shares_to_buy,
                    'price': row['close']
                })
            elif row['timestamp'] == df.iloc[-1]['timestamp']:
                # Sell signal
                if 'SPY' in positions:
                    cash += positions['SPY'] * row['close']
                    trades.append({
                        'timestamp': row['timestamp'],
                        'action': 'sell',
                        'symbol': 'SPY',
                        'quantity': positions['SPY'],
                        'price': row['close']
                    })
                    positions = {}
        
        # Calculate final portfolio value
        final_value = cash + sum(positions.get(symbol, 0) * df.iloc[-1]['close'] for symbol in positions)
        
        # Calculate performance metrics
        returns = pd.Series([pv['value'] for pv in portfolio_values]).pct_change().dropna()
        
        total_return = (final_value - backtest.initial_capital) / backtest.initial_capital
        annualized_return = (1 + total_return) ** (252 / len(df)) - 1
        sharpe_ratio = returns.mean() / returns.std() * np.sqrt(252) if returns.std() > 0 else 0
        
        # Calculate maximum drawdown
        cumulative_returns = (1 + returns).cumprod()
        running_max = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # Calculate win rate and profit factor
        trade_returns = []
        for i in range(0, len(trades), 2):
            if i + 1 < len(trades):
                buy_trade = trades[i]
                sell_trade = trades[i + 1]
                trade_return = (sell_trade['price'] - buy_trade['price']) / buy_trade['price']
                trade_returns.append(trade_return)
        
        win_rate = len([r for r in trade_returns if r > 0]) / len(trade_returns) if trade_returns else 0
        
        gross_profit = sum([r for r in trade_returns if r > 0])
        gross_loss = abs(sum([r for r in trade_returns if r < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        return {
            'final_capital': final_value,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'profit_factor': profit_factor,
            'metrics': {
                'total_trades': len(trades),
                'avg_trade_return': np.mean(trade_returns) if trade_returns else 0,
                'volatility': returns.std() * np.sqrt(252)
            },
            'trades': trades
        }
