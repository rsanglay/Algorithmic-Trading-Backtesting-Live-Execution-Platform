"""
Risk management service
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import pandas as pd
import numpy as np
from scipy import stats

from app.models.strategies import Strategy, Backtest, Position, Order
from app.models.market_data import MarketData


class RiskService:
    """Service for risk management and analysis"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_risk_metrics(self, strategy_id: UUID, start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Get comprehensive risk metrics for a strategy"""
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
            return {"error": "No backtests found"}
        
        # Calculate risk metrics
        returns = [bt.total_return for bt in backtests if bt.total_return is not None]
        sharpe_ratios = [bt.sharpe_ratio for bt in backtests if bt.sharpe_ratio is not None]
        max_drawdowns = [bt.max_drawdown for bt in backtests if bt.max_drawdown is not None]
        
        risk_metrics = {
            "strategy_id": strategy_id,
            "strategy_name": strategy.name,
            "total_backtests": len(backtests),
            "return_metrics": {
                "mean_return": np.mean(returns) if returns else 0,
                "std_return": np.std(returns) if returns else 0,
                "skewness": stats.skew(returns) if len(returns) > 2 else 0,
                "kurtosis": stats.kurtosis(returns) if len(returns) > 2 else 0,
                "min_return": np.min(returns) if returns else 0,
                "max_return": np.max(returns) if returns else 0
            },
            "risk_metrics": {
                "average_sharpe_ratio": np.mean(sharpe_ratios) if sharpe_ratios else 0,
                "average_max_drawdown": np.mean(max_drawdowns) if max_drawdowns else 0,
                "worst_drawdown": np.min(max_drawdowns) if max_drawdowns else 0,
                "volatility": np.std(returns) if returns else 0,
                "downside_deviation": self._calculate_downside_deviation(returns),
                "sortino_ratio": self._calculate_sortino_ratio(returns),
                "calmar_ratio": self._calculate_calmar_ratio(returns, max_drawdowns)
            },
            "risk_percentiles": {
                "var_95": np.percentile(returns, 5) if returns else 0,
                "var_99": np.percentile(returns, 1) if returns else 0,
                "cvar_95": np.mean([r for r in returns if r <= np.percentile(returns, 5)]) if returns else 0,
                "cvar_99": np.mean([r for r in returns if r <= np.percentile(returns, 1)]) if returns else 0
            }
        }
        
        return risk_metrics
    
    def _calculate_downside_deviation(self, returns: List[float]) -> float:
        """Calculate downside deviation"""
        if not returns:
            return 0
        
        negative_returns = [r for r in returns if r < 0]
        if not negative_returns:
            return 0
        
        return np.std(negative_returns)
    
    def _calculate_sortino_ratio(self, returns: List[float], risk_free_rate: float = 0.02) -> float:
        """Calculate Sortino ratio"""
        if not returns:
            return 0
        
        excess_returns = [r - risk_free_rate for r in returns]
        downside_deviation = self._calculate_downside_deviation(returns)
        
        if downside_deviation == 0:
            return 0
        
        return np.mean(excess_returns) / downside_deviation
    
    def _calculate_calmar_ratio(self, returns: List[float], max_drawdowns: List[float]) -> float:
        """Calculate Calmar ratio"""
        if not returns or not max_drawdowns:
            return 0
        
        annualized_return = np.mean(returns) * 252  # Assuming daily returns
        max_drawdown = np.min(max_drawdowns)
        
        if max_drawdown == 0:
            return 0
        
        return annualized_return / abs(max_drawdown)
    
    async def calculate_var(self, strategy_id: UUID, confidence_level: float = 0.95,
                          start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate Value at Risk (VaR) for a strategy"""
        # Get backtests
        query = self.db.query(Backtest).filter(Backtest.strategy_id == strategy_id)
        if start_date:
            query = query.filter(Backtest.start_date >= start_date)
        if end_date:
            query = query.filter(Backtest.end_date <= end_date)
        
        backtests = query.all()
        
        if not backtests:
            return {"error": "No backtests found"}
        
        # Get returns
        returns = [bt.total_return for bt in backtests if bt.total_return is not None]
        
        if not returns:
            return {"error": "No returns data available"}
        
        # Calculate VaR using historical simulation
        var_percentile = (1 - confidence_level) * 100
        var_value = np.percentile(returns, var_percentile)
        
        # Calculate Conditional VaR (Expected Shortfall)
        var_threshold = var_value
        tail_returns = [r for r in returns if r <= var_threshold]
        cvar_value = np.mean(tail_returns) if tail_returns else var_value
        
        # Calculate parametric VaR (assuming normal distribution)
        mean_return = np.mean(returns)
        std_return = np.std(returns)
        z_score = stats.norm.ppf(1 - confidence_level)
        parametric_var = mean_return + z_score * std_return
        
        var_results = {
            "strategy_id": strategy_id,
            "confidence_level": confidence_level,
            "historical_var": var_value,
            "conditional_var": cvar_value,
            "parametric_var": parametric_var,
            "total_observations": len(returns),
            "var_interpretation": f"With {confidence_level*100}% confidence, losses should not exceed {var_value:.4f}",
            "risk_level": "high" if var_value < -0.1 else "medium" if var_value < -0.05 else "low"
        }
        
        return var_results
    
    async def stress_test(self, strategy_id: UUID, scenarios: List[str],
                         start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Perform stress testing on a strategy"""
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
            return {"error": "No backtests found"}
        
        # Get returns
        returns = [bt.total_return for bt in backtests if bt.total_return is not None]
        
        if not returns:
            return {"error": "No returns data available"}
        
        # Perform stress tests for each scenario
        stress_results = {}
        
        for scenario in scenarios:
            if scenario == "market_crash":
                # Simulate 2008-style market crash (-50% return)
                stressed_returns = [r - 0.5 for r in returns]
                stress_results[scenario] = {
                    "scenario": "Market Crash (-50%)",
                    "original_mean_return": np.mean(returns),
                    "stressed_mean_return": np.mean(stressed_returns),
                    "impact": np.mean(stressed_returns) - np.mean(returns),
                    "survival_rate": len([r for r in stressed_returns if r > 0]) / len(stressed_returns)
                }
            
            elif scenario == "high_volatility":
                # Simulate high volatility (2x standard deviation)
                stressed_returns = [r * 2 for r in returns]
                stress_results[scenario] = {
                    "scenario": "High Volatility (2x)",
                    "original_volatility": np.std(returns),
                    "stressed_volatility": np.std(stressed_returns),
                    "impact": np.std(stressed_returns) - np.std(returns),
                    "sharpe_impact": (np.mean(returns) / np.std(stressed_returns)) - (np.mean(returns) / np.std(returns))
                }
            
            elif scenario == "interest_rate_shock":
                # Simulate interest rate shock (-2% impact)
                stressed_returns = [r - 0.02 for r in returns]
                stress_results[scenario] = {
                    "scenario": "Interest Rate Shock (-2%)",
                    "original_mean_return": np.mean(returns),
                    "stressed_mean_return": np.mean(stressed_returns),
                    "impact": np.mean(stressed_returns) - np.mean(returns),
                    "survival_rate": len([r for r in stressed_returns if r > 0]) / len(stressed_returns)
                }
        
        return {
            "strategy_id": strategy_id,
            "strategy_name": strategy.name,
            "total_scenarios": len(scenarios),
            "stress_results": stress_results,
            "overall_assessment": self._assess_stress_test_results(stress_results)
        }
    
    def _assess_stress_test_results(self, stress_results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall stress test results"""
        if not stress_results:
            return {"assessment": "No stress test results available"}
        
        # Calculate overall resilience score
        resilience_scores = []
        for scenario, results in stress_results.items():
            if "survival_rate" in results:
                resilience_scores.append(results["survival_rate"])
            elif "sharpe_impact" in results:
                # Convert Sharpe impact to resilience score
                resilience_scores.append(max(0, 1 + results["sharpe_impact"]))
        
        overall_resilience = np.mean(resilience_scores) if resilience_scores else 0
        
        return {
            "overall_resilience": overall_resilience,
            "risk_level": "high" if overall_resilience < 0.3 else "medium" if overall_resilience < 0.7 else "low",
            "recommendation": self._get_risk_recommendation(overall_resilience)
        }
    
    def _get_risk_recommendation(self, resilience_score: float) -> str:
        """Get risk management recommendation based on resilience score"""
        if resilience_score < 0.3:
            return "High risk detected. Consider reducing position sizes, adding hedging strategies, or improving risk controls."
        elif resilience_score < 0.7:
            return "Medium risk level. Monitor closely and consider additional risk management measures."
        else:
            return "Low risk level. Strategy appears resilient to stress scenarios."
    
    async def get_portfolio_risk(self, strategy_ids: List[UUID], start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Calculate portfolio-level risk metrics"""
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
        
        # Calculate portfolio risk metrics
        all_returns = [bt.total_return for bt in backtests if bt.total_return is not None]
        
        if not all_returns:
            return {"error": "No returns data available"}
        
        portfolio_risk = {
            "total_strategies": len(strategies),
            "total_backtests": len(backtests),
            "portfolio_metrics": {
                "mean_return": np.mean(all_returns),
                "std_return": np.std(all_returns),
                "skewness": stats.skew(all_returns),
                "kurtosis": stats.kurtosis(all_returns),
                "var_95": np.percentile(all_returns, 5),
                "var_99": np.percentile(all_returns, 1),
                "max_drawdown": np.min(all_returns),
                "sharpe_ratio": np.mean(all_returns) / np.std(all_returns) if np.std(all_returns) > 0 else 0
            },
            "diversification_benefits": {
                "correlation_analysis": "Available with multiple strategies",
                "concentration_risk": "Monitor individual strategy weights",
                "diversification_ratio": self._calculate_diversification_ratio(all_returns)
            }
        }
        
        return portfolio_risk
    
    def _calculate_diversification_ratio(self, returns: List[float]) -> float:
        """Calculate diversification ratio"""
        if not returns or len(returns) < 2:
            return 1.0
        
        # Simplified diversification ratio
        # In practice, this would consider correlations between strategies
        return 1.0  # Placeholder for now
