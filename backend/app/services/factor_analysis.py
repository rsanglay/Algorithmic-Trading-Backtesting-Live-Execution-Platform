"""
Factor analysis library with Fama-French factors and custom factors
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from app.core.logging import get_logger

logger = get_logger(__name__)


@dataclass
class FactorExposure:
    """Factor exposure for a portfolio"""
    market: float
    smb: float  # Small Minus Big
    hml: float  # High Minus Low
    rmw: float  # Robust Minus Weak (profitability)
    cma: float  # Conservative Minus Aggressive (investment)


@dataclass
class FactorReturns:
    """Factor returns over time"""
    market: pd.Series
    smb: pd.Series
    hml: pd.Series
    rmw: Optional[pd.Series] = None
    cma: Optional[pd.Series] = None


class FactorLibrary:
    """Library for calculating and analyzing factors"""
    
    @staticmethod
    def calculate_momentum(prices: pd.Series, period: int = 252) -> pd.Series:
        """
        Calculate momentum factor (12-month return)
        
        Args:
            prices: Price series
            period: Lookback period in days
        """
        return prices.pct_change(period)
    
    @staticmethod
    def calculate_value_pe(price: pd.Series, earnings: pd.Series) -> pd.Series:
        """Calculate P/E ratio (inverse value factor)"""
        return price / earnings
    
    @staticmethod
    def calculate_value_pb(price: pd.Series, book_value: pd.Series) -> pd.Series:
        """Calculate P/B ratio (inverse value factor)"""
        return price / book_value
    
    @staticmethod
    def calculate_quality_roe(net_income: pd.Series, equity: pd.Series) -> pd.Series:
        """Calculate ROE (Return on Equity)"""
        return net_income / equity
    
    @staticmethod
    def calculate_quality_profit_margin(revenue: pd.Series, net_income: pd.Series) -> pd.Series:
        """Calculate profit margin"""
        return net_income / revenue
    
    @staticmethod
    def calculate_volatility(returns: pd.Series, window: int = 60) -> pd.Series:
        """Calculate rolling volatility"""
        return returns.rolling(window=window).std() * np.sqrt(252)
    
    @staticmethod
    def calculate_liquidity_amihud(prices: pd.Series, volumes: pd.Series) -> pd.Series:
        """Calculate Amihud illiquidity measure"""
        returns = prices.pct_change()
        dollar_volume = prices * volumes
        return abs(returns) / dollar_volume
    
    @staticmethod
    def fama_french_3_factor_model(
        portfolio_returns: pd.Series,
        market_returns: pd.Series,
        smb_returns: pd.Series,
        hml_returns: pd.Series
    ) -> Dict:
        """
        Run Fama-French 3-factor model regression
        
        Args:
            portfolio_returns: Portfolio returns
            market_returns: Market returns (e.g., S&P 500)
            smb_returns: Small Minus Big factor returns
            hml_returns: High Minus Low factor returns
        """
        # Align indices
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_returns,
            'market': market_returns,
            'smb': smb_returns,
            'hml': hml_returns
        }).dropna()
        
        if len(aligned_data) < 30:
            return {
                'alpha': 0,
                'market_beta': 0,
                'smb_beta': 0,
                'hml_beta': 0,
                'r_squared': 0,
                'p_values': {}
            }
        
        # Multiple linear regression
        X = aligned_data[['market', 'smb', 'hml']]
        y = aligned_data['portfolio']
        
        # Add intercept
        X = np.column_stack([np.ones(len(X)), X])
        
        # OLS regression
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        
        # Calculate R-squared
        y_pred = X @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'alpha': beta[0],
            'market_beta': beta[1],
            'smb_beta': beta[2],
            'hml_beta': beta[3],
            'r_squared': r_squared,
            'factor_exposures': FactorExposure(
                market=beta[1],
                smb=beta[2],
                hml=beta[3],
                rmw=0,
                cma=0
            )
        }
    
    @staticmethod
    def fama_french_5_factor_model(
        portfolio_returns: pd.Series,
        market_returns: pd.Series,
        smb_returns: pd.Series,
        hml_returns: pd.Series,
        rmw_returns: pd.Series,
        cma_returns: pd.Series
    ) -> Dict:
        """
        Run Fama-French 5-factor model regression
        """
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_returns,
            'market': market_returns,
            'smb': smb_returns,
            'hml': hml_returns,
            'rmw': rmw_returns,
            'cma': cma_returns
        }).dropna()
        
        if len(aligned_data) < 30:
            return {
                'alpha': 0,
                'market_beta': 0,
                'smb_beta': 0,
                'hml_beta': 0,
                'rmw_beta': 0,
                'cma_beta': 0,
                'r_squared': 0
            }
        
        X = aligned_data[['market', 'smb', 'hml', 'rmw', 'cma']]
        y = aligned_data['portfolio']
        X = np.column_stack([np.ones(len(X)), X])
        
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        
        y_pred = X @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
        
        return {
            'alpha': beta[0],
            'market_beta': beta[1],
            'smb_beta': beta[2],
            'hml_beta': beta[3],
            'rmw_beta': beta[4],
            'cma_beta': beta[5],
            'r_squared': r_squared,
            'factor_exposures': FactorExposure(
                market=beta[1],
                smb=beta[2],
                hml=beta[3],
                rmw=beta[4],
                cma=beta[5]
            )
        }
    
    @staticmethod
    def calculate_factor_correlation_matrix(factor_returns: FactorReturns) -> pd.DataFrame:
        """Calculate correlation matrix between factors"""
        factors = {
            'Market': factor_returns.market,
            'SMB': factor_returns.smb,
            'HML': factor_returns.hml
        }
        
        if factor_returns.rmw is not None:
            factors['RMW'] = factor_returns.rmw
        if factor_returns.cma is not None:
            factors['CMA'] = factor_returns.cma
        
        df = pd.DataFrame(factors)
        return df.corr()
    
    @staticmethod
    def factor_attribution(
        portfolio_returns: pd.Series,
        factor_returns: FactorReturns,
        factor_exposures: FactorExposure
    ) -> Dict:
        """
        Attribute portfolio returns to factors
        
        Args:
            portfolio_returns: Portfolio returns
            factor_returns: Factor return series
            factor_exposures: Factor exposures (betas)
        """
        # Align data
        aligned = pd.DataFrame({
            'portfolio': portfolio_returns,
            'market': factor_returns.market,
            'smb': factor_returns.smb,
            'hml': factor_returns.hml
        }).dropna()
        
        # Calculate factor contributions
        market_contribution = factor_exposures.market * aligned['market']
        smb_contribution = factor_exposures.smb * aligned['smb']
        hml_contribution = factor_exposures.hml * aligned['hml']
        
        # Alpha (residual)
        explained_returns = market_contribution + smb_contribution + hml_contribution
        alpha = aligned['portfolio'] - explained_returns
        
        return {
            'total_return': aligned['portfolio'].sum(),
            'market_contribution': market_contribution.sum(),
            'smb_contribution': smb_contribution.sum(),
            'hml_contribution': hml_contribution.sum(),
            'alpha_contribution': alpha.sum(),
            'factor_explanatory_power': explained_returns.var() / aligned['portfolio'].var() if aligned['portfolio'].var() > 0 else 0
        }


class FactorAnalysisService:
    """Service wrapper around factor analytics utilities."""

    def __init__(self) -> None:
        pass

    async def calculate_fama_french_factors(
        self,
        market_returns: List[float],
        small_cap_returns: List[float],
        high_value_returns: List[float],
        risk_free_rate: List[float],
    ) -> Dict[str, Any]:
        min_len = min(len(market_returns), len(small_cap_returns), len(high_value_returns), len(risk_free_rate))
        if min_len == 0:
            return {"factors": {}, "averages": {}}

        market_series = pd.Series(market_returns[:min_len])
        smb_series = pd.Series(small_cap_returns[:min_len])
        hml_series = pd.Series(high_value_returns[:min_len])
        rf_series = pd.Series(risk_free_rate[:min_len])

        factors = {
            "Mkt-Rf": market_series.tolist(),
            "SMB": smb_series.tolist(),
            "HML": hml_series.tolist(),
            "Rf": rf_series.tolist(),
        }

        averages = {
            "avg_mkt_rf": market_series.mean(),
            "avg_smb": smb_series.mean(),
            "avg_hml": hml_series.mean(),
            "avg_rf": rf_series.mean(),
        }

        return {"factors": factors, "averages": averages}

    async def get_factor_exposure(
        self,
        portfolio_returns: List[float],
        factors: Dict[str, List[float]],
    ) -> Dict[str, Any]:
        if not portfolio_returns or not factors:
            return {"error": "Portfolio returns and factors cannot be empty."}

        min_len = min([len(portfolio_returns)] + [len(vals) for vals in factors.values()])
        if min_len < 30:
            return {"error": "Need at least 30 observations for regression."}

        aligned = pd.DataFrame({"portfolio": portfolio_returns[:min_len]})
        for name, values in factors.items():
            aligned[name] = values[:min_len]

        aligned = aligned.dropna()
        if len(aligned) < 30:
            return {"error": "Insufficient overlapping data for regression."}

        y = aligned["portfolio"].values
        X = aligned[[name for name in factors.keys()]].values
        X = np.column_stack([np.ones(len(X)), X])

        beta, residuals, rank, s = np.linalg.lstsq(X, y, rcond=None)

        y_pred = X @ beta
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        factor_exposures = {"alpha": beta[0]}
        for idx, factor_name in enumerate(factors.keys(), start=1):
            factor_exposures[f"beta_{factor_name}"] = beta[idx]

        return {
            "portfolio_returns": aligned["portfolio"].tolist(),
            "factors_used": list(factors.keys()),
            "factor_exposures": factor_exposures,
            "r_squared": r_squared,
        }

