"""
Technical analysis service for calculating indicators
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np
import ta

from app.models.market_data import MarketData
from app.schemas.market_data import TechnicalIndicators


class TechnicalAnalysisService:
    """Service for technical analysis calculations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def calculate_indicators(self, symbol: str, start_date: datetime, end_date: datetime, indicators: List[str]) -> List[TechnicalIndicators]:
        """Calculate technical indicators for a symbol"""
        # Get market data
        market_data = self.db.query(MarketData).filter(
            and_(
                MarketData.symbol == symbol,
                MarketData.timestamp >= start_date,
                MarketData.timestamp <= end_date
            )
        ).order_by(MarketData.timestamp).all()
        
        if not market_data:
            return []
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': row.timestamp,
            'open': row.open_price,
            'high': row.high_price,
            'low': row.low_price,
            'close': row.close_price,
            'volume': row.volume
        } for row in market_data])
        
        df.set_index('timestamp', inplace=True)
        
        # Calculate indicators
        results = []
        for _, row in df.iterrows():
            indicator_data = {
                'symbol': symbol,
                'timestamp': row.name
            }
            
            # Calculate each requested indicator
            for indicator in indicators:
                if indicator == 'sma_20':
                    indicator_data['sma_20'] = self._calculate_sma(df['close'], 20).loc[row.name] if len(df) >= 20 else None
                elif indicator == 'sma_50':
                    indicator_data['sma_50'] = self._calculate_sma(df['close'], 50).loc[row.name] if len(df) >= 50 else None
                elif indicator == 'ema_12':
                    indicator_data['ema_12'] = self._calculate_ema(df['close'], 12).loc[row.name] if len(df) >= 12 else None
                elif indicator == 'ema_26':
                    indicator_data['ema_26'] = self._calculate_ema(df['close'], 26).loc[row.name] if len(df) >= 26 else None
                elif indicator == 'rsi':
                    indicator_data['rsi'] = self._calculate_rsi(df['close']).loc[row.name] if len(df) >= 14 else None
                elif indicator == 'macd':
                    macd_line, signal_line, histogram = self._calculate_macd(df['close'])
                    indicator_data['macd'] = macd_line.loc[row.name] if len(df) >= 26 else None
                    indicator_data['macd_signal'] = signal_line.loc[row.name] if len(df) >= 26 else None
                    indicator_data['macd_histogram'] = histogram.loc[row.name] if len(df) >= 26 else None
                elif indicator == 'bollinger':
                    upper, middle, lower = self._calculate_bollinger_bands(df['close'])
                    indicator_data['bollinger_upper'] = upper.loc[row.name] if len(df) >= 20 else None
                    indicator_data['bollinger_middle'] = middle.loc[row.name] if len(df) >= 20 else None
                    indicator_data['bollinger_lower'] = lower.loc[row.name] if len(df) >= 20 else None
                elif indicator == 'atr':
                    indicator_data['atr'] = self._calculate_atr(df['high'], df['low'], df['close']).loc[row.name] if len(df) >= 14 else None
                elif indicator == 'adx':
                    indicator_data['adx'] = self._calculate_adx(df['high'], df['low'], df['close']).loc[row.name] if len(df) >= 14 else None
                elif indicator == 'stochastic':
                    k_percent, d_percent = self._calculate_stochastic(df['high'], df['low'], df['close'])
                    indicator_data['stochastic_k'] = k_percent.loc[row.name] if len(df) >= 14 else None
                    indicator_data['stochastic_d'] = d_percent.loc[row.name] if len(df) >= 14 else None
            
            results.append(TechnicalIndicators(**indicator_data))
        
        return results
    
    def _calculate_sma(self, prices: pd.Series, window: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return ta.trend.sma_indicator(prices, window=window)
    
    def _calculate_ema(self, prices: pd.Series, window: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return ta.trend.ema_indicator(prices, window=window)
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        return ta.momentum.rsi(prices, window=window)
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9):
        """Calculate MACD"""
        macd_line = ta.trend.macd(prices, window_slow=slow, window_fast=fast)
        signal_line = ta.trend.macd_signal(prices, window_slow=slow, window_fast=fast, window_sign=signal)
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def _calculate_bollinger_bands(self, prices: pd.Series, window: int = 20, std_dev: int = 2):
        """Calculate Bollinger Bands"""
        upper = ta.volatility.bollinger_hband(prices, window=window, window_dev=std_dev)
        middle = ta.volatility.bollinger_mavg(prices, window=window)
        lower = ta.volatility.bollinger_lband(prices, window=window, window_dev=std_dev)
        return upper, middle, lower
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        return ta.volatility.average_true_range(high, low, close, window=window)
    
    def _calculate_adx(self, high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """Calculate Average Directional Index"""
        return ta.trend.adx(high, low, close, window=window)
    
    def _calculate_stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series, 
                            k_window: int = 14, d_window: int = 3) -> tuple:
        """Calculate Stochastic Oscillator"""
        k_percent = ta.momentum.stoch(high, low, close, window=k_window)
        d_percent = ta.momentum.stoch_signal(high, low, close, window=k_window, smooth_window=d_window)
        return k_percent, d_percent
    
    async def get_support_resistance(self, symbol: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Calculate support and resistance levels"""
        market_data = self.db.query(MarketData).filter(
            and_(
                MarketData.symbol == symbol,
                MarketData.timestamp >= start_date,
                MarketData.timestamp <= end_date
            )
        ).order_by(MarketData.timestamp).all()
        
        if not market_data:
            return {"error": "No data available"}
        
        # Convert to DataFrame
        df = pd.DataFrame([{
            'timestamp': row.timestamp,
            'high': row.high_price,
            'low': row.low_price,
            'close': row.close_price
        } for row in market_data])
        
        # Calculate support and resistance levels
        highs = df['high'].values
        lows = df['low'].values
        
        # Simple support/resistance calculation
        resistance_levels = self._find_pivot_highs(highs)
        support_levels = self._find_pivot_lows(lows)
        
        return {
            "resistance_levels": resistance_levels,
            "support_levels": support_levels,
            "current_price": df['close'].iloc[-1],
            "analysis_period": {
                "start": start_date,
                "end": end_date
            }
        }
    
    def _find_pivot_highs(self, highs: np.ndarray, window: int = 5) -> List[float]:
        """Find pivot highs in price data"""
        pivot_highs = []
        for i in range(window, len(highs) - window):
            if all(highs[i] > highs[i-j] for j in range(1, window+1)) and \
               all(highs[i] > highs[i+j] for j in range(1, window+1)):
                pivot_highs.append(float(highs[i]))
        return pivot_highs
    
    def _find_pivot_lows(self, lows: np.ndarray, window: int = 5) -> List[float]:
        """Find pivot lows in price data"""
        pivot_lows = []
        for i in range(window, len(lows) - window):
            if all(lows[i] < lows[i-j] for j in range(1, window+1)) and \
               all(lows[i] < lows[i+j] for j in range(1, window+1)):
                pivot_lows.append(float(lows[i]))
        return pivot_lows
