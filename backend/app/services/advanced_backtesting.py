"""
Advanced backtesting framework with walk-forward analysis and Monte Carlo simulation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from app.core.logging import get_logger

logger = get_logger(__name__)


class TransactionCostModel(Enum):
    """Transaction cost models"""
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    SLIPPAGE = "slippage"
    MARKET_IMPACT = "market_impact"


@dataclass
class BacktestConfig:
    """Configuration for backtest"""
    initial_capital: float = 100000.0
    commission: float = 0.001  # 0.1%
    slippage: float = 0.0005  # 0.05%
    transaction_cost_model: TransactionCostModel = TransactionCostModel.PERCENTAGE
    benchmark_symbol: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@dataclass
class BacktestMetrics:
    """Comprehensive backtest performance metrics"""
    total_return: float
    annualized_return: float
    volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_factor: float
    total_trades: int
    avg_trade_return: float
    var_95: float
    cvar_95: float
    skewness: float
    kurtosis: float


class AdvancedBacktestEngine:
    """Advanced backtesting engine with walk-forward and Monte Carlo capabilities"""
    
    def __init__(self, config: BacktestConfig):
        self.config = config
        self.portfolio_value = []
        self.returns = []
        self.trades = []
        self.equity_curve = None
    
    def run_backtest(
        self,
        signals: pd.DataFrame,
        prices: pd.DataFrame,
        strategy_func: callable
    ) -> Dict:
        """
        Run a standard backtest
        
        Args:
            signals: DataFrame with trading signals (buy/sell/hold)
            prices: DataFrame with OHLCV data
            strategy_func: Strategy function to generate signals
        """
        portfolio_value = self.config.initial_capital
        position = 0
        equity_curve = [portfolio_value]
        
        for i in range(1, len(prices)):
            # Get signal for current bar
            signal = strategy_func(prices.iloc[:i+1])
            current_price = prices.iloc[i]['close']
            
            # Execute trades
            if signal == 'buy' and position == 0:
                # Calculate position size
                shares = self._calculate_position_size(portfolio_value, current_price)
                cost = shares * current_price * (1 + self.config.commission)
                
                if cost <= portfolio_value:
                    position = shares
                    portfolio_value -= cost
                    self.trades.append({
                        'date': prices.index[i],
                        'action': 'buy',
                        'price': current_price,
                        'shares': shares,
                        'cost': cost
                    })
            
            elif signal == 'sell' and position > 0:
                revenue = position * current_price * (1 - self.config.commission)
                portfolio_value += revenue
                
                self.trades.append({
                    'date': prices.index[i],
                    'action': 'sell',
                    'price': current_price,
                    'shares': position,
                    'revenue': revenue
                })
                position = 0
            
            # Update portfolio value
            if position > 0:
                current_value = position * current_price
                portfolio_value_with_position = portfolio_value + current_value
            else:
                portfolio_value_with_position = portfolio_value
            
            equity_curve.append(portfolio_value_with_position)
        
        self.equity_curve = pd.Series(equity_curve, index=prices.index)
        self.portfolio_value = equity_curve
        self.returns = self.equity_curve.pct_change().dropna()
        
        return self._calculate_metrics()
    
    def walk_forward_analysis(
        self,
        prices: pd.DataFrame,
        strategy_func: callable,
        train_period: int = 252,  # 1 year
        test_period: int = 63,    # 3 months
        step: int = 21            # 1 month steps
    ) -> Dict:
        """
        Walk-forward analysis to prevent overfitting
        
        Args:
            prices: DataFrame with OHLCV data
            strategy_func: Strategy function
            train_period: Training window size (days)
            test_period: Testing window size (days)
            step: Step size for rolling window (days)
        """
        results = []
        
        for start_idx in range(0, len(prices) - train_period - test_period, step):
            train_end = start_idx + train_period
            test_end = train_end + test_period
            
            train_data = prices.iloc[start_idx:train_end]
            test_data = prices.iloc[train_end:test_end]
            
            # Optimize on training data (placeholder - would optimize parameters)
            # For now, just run strategy on test data
            
            # Run backtest on test data
            test_config = BacktestConfig(
                initial_capital=self.config.initial_capital,
                commission=self.config.commission,
                slippage=self.config.slippage
            )
            test_engine = AdvancedBacktestEngine(test_config)
            
            signals = pd.DataFrame(index=test_data.index)
            metrics = test_engine.run_backtest(signals, test_data, strategy_func)
            
            results.append({
                'train_start': train_data.index[0],
                'train_end': train_data.index[-1],
                'test_start': test_data.index[0],
                'test_end': test_data.index[-1],
                'metrics': metrics
            })
        
        return {
            'walk_forward_results': results,
            'summary': self._summarize_walk_forward(results)
        }
    
    def monte_carlo_simulation(
        self,
        returns: pd.Series,
        n_simulations: int = 10000,
        n_periods: int = 252,
        confidence_level: float = 0.95
    ) -> Dict:
        """
        Monte Carlo simulation for risk analysis
        
        Args:
            returns: Historical returns series
            n_simulations: Number of simulation paths
            n_periods: Number of periods to simulate
            confidence_level: Confidence level for VaR/CVaR
        """
        mu = returns.mean()
        sigma = returns.std()
        
        simulated_paths = []
        final_values = []
        
        for _ in range(n_simulations):
            # Generate random returns
            random_returns = np.random.normal(mu, sigma, n_periods)
            # Calculate cumulative path
            path = self.config.initial_capital * (1 + random_returns).cumprod()
            simulated_paths.append(path)
            final_values.append(path[-1])
        
        simulated_paths = np.array(simulated_paths)
        final_values = np.array(final_values)
        
        # Calculate statistics
        var_percentile = (1 - confidence_level) * 100
        var = np.percentile(final_values, var_percentile)
        cvar = final_values[final_values <= var].mean()
        
        return {
            'simulated_paths': simulated_paths,
            'final_values': final_values,
            'mean_final_value': final_values.mean(),
            'std_final_value': final_values.std(),
            'var': var,
            'cvar': cvar,
            'confidence_level': confidence_level,
            'percentile_5': np.percentile(final_values, 5),
            'percentile_95': np.percentile(final_values, 95)
        }
    
    def _calculate_position_size(self, capital: float, price: float) -> float:
        """Calculate position size (simplified - 100% of capital)"""
        return capital / price
    
    def _calculate_metrics(self) -> BacktestMetrics:
        """Calculate comprehensive performance metrics"""
        if len(self.returns) == 0:
            return BacktestMetrics(
                total_return=0, annualized_return=0, volatility=0,
                sharpe_ratio=0, sortino_ratio=0, calmar_ratio=0,
                max_drawdown=0, max_drawdown_duration=0, win_rate=0,
                profit_factor=0, total_trades=0, avg_trade_return=0,
                var_95=0, cvar_95=0, skewness=0, kurtosis=0
            )
        
        total_return = (self.equity_curve[-1] / self.equity_curve[0] - 1)
        annualized_return = (1 + total_return) ** (252 / len(self.returns)) - 1
        volatility = self.returns.std() * np.sqrt(252)
        
        # Sharpe Ratio (assuming risk-free rate = 0)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Sortino Ratio (downside deviation)
        downside_returns = self.returns[self.returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = annualized_return / downside_std if downside_std > 0 else 0
        
        # Max Drawdown
        cumulative = (1 + self.returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = abs(drawdown.min())
        
        # Max Drawdown Duration
        is_drawdown = drawdown < 0
        drawdown_periods = is_drawdown.groupby((~is_drawdown).cumsum()).sum()
        max_drawdown_duration = drawdown_periods.max() if len(drawdown_periods) > 0 else 0
        
        # Calmar Ratio
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        # Trade statistics
        if len(self.trades) >= 2:
            trade_returns = []
            for i in range(1, len(self.trades), 2):
                if i < len(self.trades):
                    buy_trade = self.trades[i-1]
                    sell_trade = self.trades[i]
                    if buy_trade['action'] == 'buy' and sell_trade['action'] == 'sell':
                        trade_return = (sell_trade['price'] - buy_trade['price']) / buy_trade['price']
                        trade_returns.append(trade_return)
            
            if trade_returns:
                winning_trades = [r for r in trade_returns if r > 0]
                losing_trades = [r for r in trade_returns if r < 0]
                win_rate = len(winning_trades) / len(trade_returns)
                
                avg_win = np.mean(winning_trades) if winning_trades else 0
                avg_loss = abs(np.mean(losing_trades)) if losing_trades else 1
                profit_factor = (avg_win * len(winning_trades)) / (avg_loss * len(losing_trades)) if avg_loss > 0 else 0
                avg_trade_return = np.mean(trade_returns)
            else:
                win_rate = 0
                profit_factor = 0
                avg_trade_return = 0
        else:
            win_rate = 0
            profit_factor = 0
            avg_trade_return = 0
        
        # VaR and CVaR (95% confidence)
        var_95 = np.percentile(self.returns, 5) * self.config.initial_capital
        cvar_95 = self.returns[self.returns <= np.percentile(self.returns, 5)].mean() * self.config.initial_capital
        
        # Skewness and Kurtosis
        skewness = self.returns.skew()
        kurtosis = self.returns.kurtosis()
        
        return BacktestMetrics(
            total_return=total_return,
            annualized_return=annualized_return,
            volatility=volatility,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            calmar_ratio=calmar_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_duration=int(max_drawdown_duration),
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=len(self.trades) // 2,
            avg_trade_return=avg_trade_return,
            var_95=var_95,
            cvar_95=cvar_95,
            skewness=skewness,
            kurtosis=kurtosis
        )
    
    def _summarize_walk_forward(self, results: List[Dict]) -> Dict:
        """Summarize walk-forward analysis results"""
        if not results:
            return {}
        
        returns = [r['metrics'].annualized_return for r in results]
        sharpe_ratios = [r['metrics'].sharpe_ratio for r in results]
        max_drawdowns = [r['metrics'].max_drawdown for r in results]
        
        return {
            'avg_return': np.mean(returns),
            'std_return': np.std(returns),
            'avg_sharpe': np.mean(sharpe_ratios),
            'avg_max_drawdown': np.mean(max_drawdowns),
            'consistency': len([r for r in returns if r > 0]) / len(returns)
        }

