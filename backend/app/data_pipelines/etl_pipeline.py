"""
ETL pipeline for market data processing
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.market_data import MarketData, TickerInfo, NewsData
from app.services.market_data_service import MarketDataService


class ETLPipeline:
    """ETL pipeline for market data processing"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
    
    async def extract_market_data(self, symbols: List[str], start_date: datetime, 
                                end_date: datetime, source: str = "yfinance") -> Dict[str, pd.DataFrame]:
        """Extract market data from external sources"""
        extracted_data = {}
        
        for symbol in symbols:
            try:
                if source == "yfinance":
                    data = await self._extract_yfinance_data(symbol, start_date, end_date)
                elif source == "alpha_vantage":
                    data = await self._extract_alpha_vantage_data(symbol, start_date, end_date)
                elif source == "iex_cloud":
                    data = await self._extract_iex_cloud_data(symbol, start_date, end_date)
                else:
                    raise ValueError(f"Unsupported data source: {source}")
                
                extracted_data[symbol] = data
                
            except Exception as e:
                print(f"Error extracting data for {symbol}: {str(e)}")
                continue
        
        return extracted_data
    
    async def _extract_yfinance_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract data from Yahoo Finance using yfinance"""
        import yfinance as yf
        
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        
        if data.empty:
            raise ValueError(f"No data found for {symbol}")
        
        return data
    
    async def _extract_alpha_vantage_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract data from Alpha Vantage API"""
        if not settings.ALPHA_VANTAGE_API_KEY:
            raise ValueError("Alpha Vantage API key not configured")
        
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
            "outputsize": "full"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
        
        if "Error Message" in data:
            raise ValueError(f"Alpha Vantage error: {data['Error Message']}")
        
        # Convert to DataFrame
        time_series = data.get("Time Series (Daily)", {})
        df = pd.DataFrame.from_dict(time_series, orient='index')
        df.index = pd.to_datetime(df.index)
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df = df.astype(float)
        
        # Filter by date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        return df
    
    async def _extract_iex_cloud_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Extract data from IEX Cloud API"""
        if not settings.IEX_CLOUD_API_KEY:
            raise ValueError("IEX Cloud API key not configured")
        
        url = f"https://cloud.iexapis.com/stable/stock/{symbol}/chart/1y"
        params = {
            "token": settings.IEX_CLOUD_API_KEY
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        
        # Filter by date range
        df = df[(df.index >= start_date) & (df.index <= end_date)]
        
        return df
    
    def transform_market_data(self, data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
        """Transform market data"""
        transformed_data = {}
        
        for symbol, df in data.items():
            # Clean data
            df_clean = df.copy()
            
            # Remove missing values
            df_clean = df_clean.dropna()
            
            # Remove outliers (prices that are more than 3 standard deviations from mean)
            for col in ['Open', 'High', 'Low', 'Close']:
                if col in df_clean.columns:
                    mean = df_clean[col].mean()
                    std = df_clean[col].std()
                    df_clean = df_clean[abs(df_clean[col] - mean) <= 3 * std]
            
            # Ensure High >= Low
            if 'High' in df_clean.columns and 'Low' in df_clean.columns:
                df_clean = df_clean[df_clean['High'] >= df_clean['Low']]
            
            # Ensure High >= Open and High >= Close
            if 'High' in df_clean.columns and 'Open' in df_clean.columns:
                df_clean = df_clean[df_clean['High'] >= df_clean['Open']]
            if 'High' in df_clean.columns and 'Close' in df_clean.columns:
                df_clean = df_clean[df_clean['High'] >= df_clean['Close']]
            
            # Ensure Low <= Open and Low <= Close
            if 'Low' in df_clean.columns and 'Open' in df_clean.columns:
                df_clean = df_clean[df_clean['Low'] <= df_clean['Open']]
            if 'Low' in df_clean.columns and 'Close' in df_clean.columns:
                df_clean = df_clean[df_clean['Low'] <= df_clean['Close']]
            
            # Add technical indicators
            df_clean = self._add_technical_indicators(df_clean)
            
            transformed_data[symbol] = df_clean
        
        return transformed_data
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add technical indicators to the data"""
        import ta
        
        # Moving averages
        df['SMA_20'] = ta.trend.sma_indicator(df['Close'], window=20)
        df['SMA_50'] = ta.trend.sma_indicator(df['Close'], window=50)
        df['EMA_12'] = ta.trend.ema_indicator(df['Close'], window=12)
        df['EMA_26'] = ta.trend.ema_indicator(df['Close'], window=26)
        
        # Momentum indicators
        df['RSI'] = ta.momentum.rsi(df['Close'], window=14)
        df['MACD'] = ta.trend.macd(df['Close'])
        df['MACD_Signal'] = ta.trend.macd_signal(df['Close'])
        df['MACD_Histogram'] = ta.trend.macd_diff(df['Close'])
        
        # Volatility indicators
        df['BB_Upper'] = ta.volatility.bollinger_hband(df['Close'])
        df['BB_Middle'] = ta.volatility.bollinger_mavg(df['Close'])
        df['BB_Lower'] = ta.volatility.bollinger_lband(df['Close'])
        df['ATR'] = ta.volatility.average_true_range(df['High'], df['Low'], df['Close'])
        
        # Volume indicators
        df['Volume_SMA'] = ta.volume.volume_sma(df['Close'], df['Volume'])
        df['OBV'] = ta.volume.on_balance_volume(df['Close'], df['Volume'])
        
        return df
    
    async def load_market_data(self, data: Dict[str, pd.DataFrame], source: str = "yfinance") -> Dict[str, Any]:
        """Load transformed data into database"""
        results = {}
        
        for symbol, df in data.items():
            try:
                # Convert DataFrame to list of MarketData objects
                market_data_objects = []
                
                for timestamp, row in df.iterrows():
                    market_data = MarketData(
                        symbol=symbol,
                        timestamp=timestamp,
                        open_price=row['Open'],
                        high_price=row['High'],
                        low_price=row['Low'],
                        close_price=row['Close'],
                        volume=row['Volume'],
                        source=source
                    )
                    market_data_objects.append(market_data)
                
                # Bulk insert
                self.db.add_all(market_data_objects)
                self.db.commit()
                
                results[symbol] = {
                    "status": "success",
                    "records": len(market_data_objects)
                }
                
            except Exception as e:
                self.db.rollback()
                results[symbol] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    async def run_etl_pipeline(self, symbols: List[str], start_date: datetime, 
                             end_date: datetime, source: str = "yfinance") -> Dict[str, Any]:
        """Run the complete ETL pipeline"""
        print(f"Starting ETL pipeline for {len(symbols)} symbols")
        
        # Extract
        print("Extracting data...")
        extracted_data = await self.extract_market_data(symbols, start_date, end_date, source)
        
        # Transform
        print("Transforming data...")
        transformed_data = self.transform_market_data(extracted_data)
        
        # Load
        print("Loading data...")
        load_results = await self.load_market_data(transformed_data, source)
        
        print("ETL pipeline completed")
        return load_results


class NewsETLPipeline:
    """ETL pipeline for news and sentiment data"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
    
    async def extract_news_data(self, symbols: List[str], start_date: datetime, 
                              end_date: datetime) -> Dict[str, List[Dict[str, Any]]]:
        """Extract news data from various sources"""
        news_data = {}
        
        for symbol in symbols:
            try:
                # Extract from News API
                news_api_data = await self._extract_news_api_data(symbol, start_date, end_date)
                
                # Extract from Alpha Vantage News
                alpha_vantage_data = await self._extract_alpha_vantage_news(symbol, start_date, end_date)
                
                # Combine data
                news_data[symbol] = news_api_data + alpha_vantage_data
                
            except Exception as e:
                print(f"Error extracting news for {symbol}: {str(e)}")
                news_data[symbol] = []
        
        return news_data
    
    async def _extract_news_api_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extract news from News API"""
        # This would integrate with News API
        # For now, return mock data
        return []
    
    async def _extract_alpha_vantage_news(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Extract news from Alpha Vantage News API"""
        if not settings.ALPHA_VANTAGE_API_KEY:
            return []
        
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
            "limit": 1000
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                data = await response.json()
        
        if "Error Message" in data:
            return []
        
        news_items = data.get("feed", [])
        return news_items
    
    def transform_news_data(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, List[Dict[str, Any]]]:
        """Transform news data"""
        transformed_data = {}
        
        for symbol, news_items in data.items():
            transformed_items = []
            
            for item in news_items:
                # Extract relevant information
                transformed_item = {
                    "symbol": symbol,
                    "timestamp": item.get("time_published", ""),
                    "title": item.get("title", ""),
                    "content": item.get("summary", ""),
                    "source": item.get("source", ""),
                    "url": item.get("url", ""),
                    "sentiment_score": item.get("overall_sentiment_score", 0),
                    "sentiment_label": item.get("overall_sentiment_label", "neutral")
                }
                
                transformed_items.append(transformed_item)
            
            transformed_data[symbol] = transformed_items
        
        return transformed_data
    
    async def load_news_data(self, data: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
        """Load news data into database"""
        results = {}
        
        for symbol, news_items in data.items():
            try:
                # Convert to NewsData objects
                news_data_objects = []
                
                for item in news_items:
                    news_data = NewsData(
                        symbol=item["symbol"],
                        timestamp=datetime.fromisoformat(item["timestamp"].replace('Z', '+00:00')),
                        title=item["title"],
                        content=item["content"],
                        source=item["source"],
                        sentiment_score=item["sentiment_score"],
                        sentiment_label=item["sentiment_label"],
                        url=item["url"]
                    )
                    news_data_objects.append(news_data)
                
                # Bulk insert
                self.db.add_all(news_data_objects)
                self.db.commit()
                
                results[symbol] = {
                    "status": "success",
                    "records": len(news_data_objects)
                }
                
            except Exception as e:
                self.db.rollback()
                results[symbol] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    async def run_news_etl_pipeline(self, symbols: List[str], start_date: datetime, 
                                   end_date: datetime) -> Dict[str, Any]:
        """Run the complete news ETL pipeline"""
        print(f"Starting news ETL pipeline for {len(symbols)} symbols")
        
        # Extract
        print("Extracting news data...")
        extracted_data = await self.extract_news_data(symbols, start_date, end_date)
        
        # Transform
        print("Transforming news data...")
        transformed_data = self.transform_news_data(extracted_data)
        
        # Load
        print("Loading news data...")
        load_results = await self.load_news_data(transformed_data)
        
        print("News ETL pipeline completed")
        return load_results
