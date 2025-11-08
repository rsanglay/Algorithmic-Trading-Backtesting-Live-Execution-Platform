"""
Comprehensive risk metrics calculation service
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class RiskMetrics:
    """Comprehensive risk metrics"""
    var_95: float
    var_99: float
    cvar_95: float
    cvar_99: float
    max_drawdown: float
    max_drawdown_duration: int
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    volatility: float
    beta: float
    alpha: float
    tracking_error: float
    information_ratio: float
    skewness: float
    kurtosis: float
    tail_ratio: float


class RiskMetricsService:
    """Service for calculating comprehensive risk metrics"""
    
    @staticmethod
    def calculate_var(
        returns: pd.Series,
        confidence_level: float = 0.95,
        method: str = "historical"
    ) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            returns: Return series
            confidence_level: Confidence level (0.95 for 95% VaR)
            method: Method ('historical', 'parametric', 'monte_carlo')
        """
        if method == "historical":
            percentile = (1 - confidence_level) * 100
            return np.percentile(returns, percentile)
        elif method == "parametric":
            mean = returns.mean()
            std = returns.std()
            # Use numpy for normal distribution approximation
            # For 95% VaR, z-score ≈ 1.645
            # For 99% VaR, z-score ≈ 2.326
            z_scores = {0.95: 1.645, 0.99: 2.326, 0.90: 1.282}
            z_score = z_scores.get(confidence_level, 1.645)
            return mean + z_score * std
        else:
            # Monte Carlo (simplified)
            return np.percentile(returns, (1 - confidence_level) * 100)
    
    @staticmethod
    def calculate_cvar(
        returns: pd.Series,
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Conditional Value at Risk (CVaR) / Expected Shortfall
        
        Args:
            returns: Return series
            confidence_level: Confidence level
        """
        var = RiskMetricsService.calculate_var(returns, confidence_level)
        tail_returns = returns[returns <= var]
        return tail_returns.mean() if len(tail_returns) > 0 else var
    
    @staticmethod
    def calculate_max_drawdown(equity_curve: pd.Series) -> Tuple[float, int]:
        """
        Calculate maximum drawdown and duration
        
        Args:
            equity_curve: Portfolio value over time
        """
        cumulative = equity_curve / equity_curve.iloc[0]
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        
        max_dd = abs(drawdown.min())
        
        # Calculate duration
        is_drawdown = drawdown < 0
        if is_drawdown.any():
            drawdown_periods = is_drawdown.groupby((~is_drawdown).cumsum()).sum()
            max_dd_duration = int(drawdown_periods.max())
        else:
            max_dd_duration = 0
        
        return max_dd, max_dd_duration
    
    @staticmethod
    def calculate_sharpe_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252
    ) -> float:
        """Calculate Sharpe ratio"""
        excess_returns = returns - (risk_free_rate / periods_per_year)
        annualized_return = excess_returns.mean() * periods_per_year
        annualized_vol = returns.std() * np.sqrt(periods_per_year)
        
        return annualized_return / annualized_vol if annualized_vol > 0 else 0
    
    @staticmethod
    def calculate_sortino_ratio(
        returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252
    ) -> float:
        """Calculate Sortino ratio (downside deviation)"""
        excess_returns = returns - (risk_free_rate / periods_per_year)
        annualized_return = excess_returns.mean() * periods_per_year
        
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(periods_per_year) if len(downside_returns) > 0 else 0
        
        return annualized_return / downside_std if downside_std > 0 else 0
    
    @staticmethod
    def calculate_calmar_ratio(
        returns: pd.Series,
        equity_curve: pd.Series,
        periods_per_year: int = 252
    ) -> float:
        """Calculate Calmar ratio (return / max drawdown)"""
        annualized_return = returns.mean() * periods_per_year
        max_dd, _ = RiskMetricsService.calculate_max_drawdown(equity_curve)
        
        return annualized_return / max_dd if max_dd > 0 else 0
    
    @staticmethod
    def calculate_beta(
        portfolio_returns: pd.Series,
        market_returns: pd.Series
    ) -> float:
        """Calculate beta (market sensitivity)"""
        aligned = pd.DataFrame({
            'portfolio': portfolio_returns,
            'market': market_returns
        }).dropna()
        
        if len(aligned) < 2:
            return 0
        
        covariance = aligned['portfolio'].cov(aligned['market'])
        market_variance = aligned['market'].var()
        
        return covariance / market_variance if market_variance > 0 else 0
    
    @staticmethod
    def calculate_alpha(
        portfolio_returns: pd.Series,
        market_returns: pd.Series,
        risk_free_rate: float = 0.0,
        periods_per_year: int = 252
    ) -> float:
        """Calculate alpha (excess return)"""
        beta = RiskMetricsService.calculate_beta(portfolio_returns, market_returns)
        
        portfolio_annual = portfolio_returns.mean() * periods_per_year
        market_annual = market_returns.mean() * periods_per_year
        rf_annual = risk_free_rate
        
        return portfolio_annual - (rf_annual + beta * (market_annual - rf_annual))
    
    @staticmethod
    def calculate_tracking_error(
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """Calculate tracking error"""
        aligned = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned) < 2:
            return 0
        
        active_returns = aligned['portfolio'] - aligned['benchmark']
        return active_returns.std() * np.sqrt(252)
    
    @staticmethod
    def calculate_information_ratio(
        portfolio_returns: pd.Series,
        benchmark_returns: pd.Series
    ) -> float:
        """Calculate information ratio"""
        aligned = pd.DataFrame({
            'portfolio': portfolio_returns,
            'benchmark': benchmark_returns
        }).dropna()
        
        if len(aligned) < 2:
            return 0
        
        active_returns = aligned['portfolio'] - aligned['benchmark']
        tracking_error = active_returns.std() * np.sqrt(252)
        active_return = active_returns.mean() * 252
        
        return active_return / tracking_error if tracking_error > 0 else 0
    
    @staticmethod
    def calculate_tail_ratio(returns: pd.Series) -> float:
        """Calculate tail ratio (95th percentile / 5th percentile)"""
        percentile_95 = np.percentile(returns, 95)
        percentile_5 = np.percentile(returns, 5)
        
        return abs(percentile_95 / percentile_5) if percentile_5 != 0 else 0
    
    @staticmethod
    def calculate_comprehensive_risk_metrics(
        returns: pd.Series,
        equity_curve: pd.Series,
        market_returns: Optional[pd.Series] = None,
        benchmark_returns: Optional[pd.Series] = None,
        risk_free_rate: float = 0.0
    ) -> RiskMetrics:
        """Calculate all risk metrics"""
        var_95 = RiskMetricsService.calculate_var(returns, 0.95)
        var_99 = RiskMetricsService.calculate_var(returns, 0.99)
        cvar_95 = RiskMetricsService.calculate_cvar(returns, 0.95)
        cvar_99 = RiskMetricsService.calculate_cvar(returns, 0.99)
        
        max_dd, max_dd_duration = RiskMetricsService.calculate_max_drawdown(equity_curve)
        
        sharpe = RiskMetricsService.calculate_sharpe_ratio(returns, risk_free_rate)
        sortino = RiskMetricsService.calculate_sortino_ratio(returns, risk_free_rate)
        calmar = RiskMetricsService.calculate_calmar_ratio(returns, equity_curve)
        
        volatility = returns.std() * np.sqrt(252)
        
        beta = RiskMetricsService.calculate_beta(returns, market_returns) if market_returns is not None else 0
        alpha = RiskMetricsService.calculate_alpha(returns, market_returns, risk_free_rate) if market_returns is not None else 0
        
        tracking_error = RiskMetricsService.calculate_tracking_error(returns, benchmark_returns) if benchmark_returns is not None else 0
        information_ratio = RiskMetricsService.calculate_information_ratio(returns, benchmark_returns) if benchmark_returns is not None else 0
        
        skewness = returns.skew()
        kurtosis = returns.kurtosis()
        tail_ratio = RiskMetricsService.calculate_tail_ratio(returns)
        
        return RiskMetrics(
            var_95=var_95,
            var_99=var_99,
            cvar_95=cvar_95,
            cvar_99=cvar_99,
            max_drawdown=max_dd,
            max_drawdown_duration=max_dd_duration,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            calmar_ratio=calmar,
            volatility=volatility,
            beta=beta,
            alpha=alpha,
            tracking_error=tracking_error,
            information_ratio=information_ratio,
            skewness=skewness,
            kurtosis=kurtosis,
            tail_ratio=tail_ratio
        )

