"""
Quantitative strategy library with classic quant strategies
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Callable
from datetime import datetime
import statsmodels.tsa.stattools as ts

from app.core.logging import get_logger

logger = get_logger(__name__)


class QuantitativeStrategies:
    """Library of quantitative trading strategies"""
    
    @staticmethod
    def momentum_strategy(
        prices: pd.Series,
        lookback_short: int = 21,
        lookback_long: int = 252,
        threshold: float = 0.0
    ) -> pd.Series:
        """
        Momentum strategy: Buy when short-term momentum > long-term momentum
        
        Args:
            prices: Price series
            lookback_short: Short-term lookback period (days)
            lookback_long: Long-term lookback period (days)
            threshold: Minimum momentum threshold
        """
        returns_short = prices.pct_change(lookback_short)
        returns_long = prices.pct_change(lookback_long)
        
        momentum = returns_short - returns_long
        signals = pd.Series(index=prices.index, data='hold')
        signals[momentum > threshold] = 'buy'
        signals[momentum < -threshold] = 'sell'
        
        return signals
    
    @staticmethod
    def mean_reversion_rsi(
        prices: pd.Series,
        period: int = 14,
        oversold: float = 30,
        overbought: float = 70
    ) -> pd.Series:
        """
        Mean reversion strategy using RSI
        
        Args:
            prices: Price series
            period: RSI period
            oversold: Oversold threshold
            overbought: Overbought threshold
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        signals = pd.Series(index=prices.index, data='hold')
        signals[rsi < oversold] = 'buy'
        signals[rsi > overbought] = 'sell'
        
        return signals
    
    @staticmethod
    def pairs_trading_cointegration(
        prices_1: pd.Series,
        prices_2: pd.Series,
        lookback: int = 60,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.5
    ) -> Dict[str, pd.Series]:
        """
        Pairs trading strategy based on cointegration
        
        Args:
            prices_1: First asset price series
            prices_2: Second asset price series
            lookback: Lookback period for spread calculation
            entry_threshold: Z-score threshold for entry
            exit_threshold: Z-score threshold for exit
        """
        # Calculate spread (price ratio)
        spread = prices_1 / prices_2
        
        # Calculate z-score
        spread_mean = spread.rolling(window=lookback).mean()
        spread_std = spread.rolling(window=lookback).std()
        z_score = (spread - spread_mean) / spread_std
        
        # Generate signals
        signals_1 = pd.Series(index=prices_1.index, data='hold')
        signals_2 = pd.Series(index=prices_2.index, data='hold')
        
        # When spread is too high (z > entry_threshold): short asset 1, long asset 2
        signals_1[z_score > entry_threshold] = 'sell'
        signals_2[z_score > entry_threshold] = 'buy'
        
        # When spread is too low (z < -entry_threshold): long asset 1, short asset 2
        signals_1[z_score < -entry_threshold] = 'buy'
        signals_2[z_score < -entry_threshold] = 'sell'
        
        # Exit when z-score returns to mean
        signals_1[abs(z_score) < exit_threshold] = 'hold'
        signals_2[abs(z_score) < exit_threshold] = 'hold'
        
        # Test for cointegration
        try:
            cointegration_result = ts.coint(prices_1.dropna(), prices_2.dropna())
            is_cointegrated = cointegration_result[1] < 0.05  # p-value < 0.05
        except:
            is_cointegrated = False
        
        return {
            'signals_1': signals_1,
            'signals_2': signals_2,
            'spread': spread,
            'z_score': z_score,
            'is_cointegrated': is_cointegrated
        }
    
    @staticmethod
    def value_strategy_pe(
        prices: pd.Series,
        earnings: pd.Series,
        threshold_percentile: float = 20
    ) -> pd.Series:
        """
        Value strategy based on P/E ratio (buy low P/E)
        
        Args:
            prices: Price series
            earnings: Earnings series
            threshold_percentile: Percentile threshold for value stocks
        """
        pe_ratio = prices / earnings
        threshold = pe_ratio.quantile(threshold_percentile / 100)
        
        signals = pd.Series(index=prices.index, data='hold')
        signals[pe_ratio <= threshold] = 'buy'
        signals[pe_ratio > threshold * 2] = 'sell'  # Sell when P/E becomes too high
        
        return signals
    
    @staticmethod
    def low_volatility_strategy(
        prices: pd.Series,
        lookback: int = 60,
        percentile: float = 30
    ) -> pd.Series:
        """
        Low volatility strategy: Buy stocks with lowest volatility
        
        Args:
            prices: Price series
            lookback: Lookback period for volatility calculation
            percentile: Percentile threshold for low volatility
        """
        returns = prices.pct_change()
        volatility = returns.rolling(window=lookback).std() * np.sqrt(252)
        
        threshold = volatility.quantile(percentile / 100)
        
        signals = pd.Series(index=prices.index, data='hold')
        signals[volatility <= threshold] = 'buy'
        
        return signals
    
    @staticmethod
    def moving_average_crossover(
        prices: pd.Series,
        short_period: int = 50,
        long_period: int = 200
    ) -> pd.Series:
        """
        Moving average crossover strategy
        
        Args:
            prices: Price series
            short_period: Short MA period
            long_period: Long MA period
        """
        ma_short = prices.rolling(window=short_period).mean()
        ma_long = prices.rolling(window=long_period).mean()
        
        signals = pd.Series(index=prices.index, data='hold')
        signals[(ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))] = 'buy'
        signals[(ma_short < ma_long) & (ma_short.shift(1) >= ma_long.shift(1))] = 'sell'
        
        return signals
    
    @staticmethod
    def bollinger_bands_strategy(
        prices: pd.Series,
        period: int = 20,
        num_std: float = 2.0
    ) -> pd.Series:
        """
        Bollinger Bands mean reversion strategy
        
        Args:
            prices: Price series
            period: Moving average period
            num_std: Number of standard deviations
        """
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = ma + (std * num_std)
        lower_band = ma - (std * num_std)
        
        signals = pd.Series(index=prices.index, data='hold')
        signals[prices < lower_band] = 'buy'  # Price below lower band
        signals[prices > upper_band] = 'sell'  # Price above upper band
        
        return signals
    
    @staticmethod
    def macd_strategy(
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> pd.Series:
        """
        MACD (Moving Average Convergence Divergence) strategy
        
        Args:
            prices: Price series
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
        """
        ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
        ema_slow = prices.ewm(span=slow_period, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()
        histogram = macd_line - signal_line
        
        signals = pd.Series(index=prices.index, data='hold')
        signals[(macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))] = 'buy'
        signals[(macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))] = 'sell'
        
        return signals


class StrategyTemplate:
    """Template for creating custom strategies"""
    
    def __init__(self, name: str, description: str, strategy_func: Callable):
        self.name = name
        self.description = description
        self.strategy_func = strategy_func
    
    def generate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Generate trading signals from data"""
        return self.strategy_func(data)


# Pre-built strategy templates
STRATEGY_TEMPLATES = {
    'momentum': StrategyTemplate(
        name='Momentum Strategy',
        description='Buy when short-term momentum exceeds long-term momentum',
        strategy_func=lambda data: QuantitativeStrategies.momentum_strategy(data['close'])
    ),
    'mean_reversion_rsi': StrategyTemplate(
        name='Mean Reversion (RSI)',
        description='Buy oversold, sell overbought based on RSI',
        strategy_func=lambda data: QuantitativeStrategies.mean_reversion_rsi(data['close'])
    ),
    'moving_average_crossover': StrategyTemplate(
        name='Moving Average Crossover',
        description='Buy when short MA crosses above long MA',
        strategy_func=lambda data: QuantitativeStrategies.moving_average_crossover(data['close'])
    ),
    'bollinger_bands': StrategyTemplate(
        name='Bollinger Bands',
        description='Mean reversion using Bollinger Bands',
        strategy_func=lambda data: QuantitativeStrategies.bollinger_bands_strategy(data['close'])
    ),
    'macd': StrategyTemplate(
        name='MACD Strategy',
        description='MACD crossover strategy',
        strategy_func=lambda data: QuantitativeStrategies.macd_strategy(data['close'])
    )
}

