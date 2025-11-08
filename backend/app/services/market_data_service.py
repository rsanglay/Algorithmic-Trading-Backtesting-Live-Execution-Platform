"""
Market data service for data ingestion and management
"""
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime
import yfinance as yf
import pandas as pd
import requests
import json

from app.models.market_data import MarketData, TickerInfo, NewsData
from app.schemas.market_data import MarketDataCreate, TickerInfoCreate, NewsDataCreate
from app.core.config import settings


class MarketDataService:
    """Service for managing market data"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_market_data(self, symbol: str, start_date: datetime, end_date: datetime, interval: str = "1d") -> List[MarketData]:
        """Get OHLCV market data for a symbol"""
        return self.db.query(MarketData).filter(
            and_(
                MarketData.symbol == symbol,
                MarketData.timestamp >= start_date,
                MarketData.timestamp <= end_date
            )
        ).order_by(MarketData.timestamp).all()
    
    async def create_market_data(self, market_data: MarketDataCreate) -> MarketData:
        """Create market data entry"""
        data = MarketData(
            symbol=market_data.symbol,
            timestamp=market_data.timestamp,
            open_price=market_data.open_price,
            high_price=market_data.high_price,
            low_price=market_data.low_price,
            close_price=market_data.close_price,
            volume=market_data.volume,
            source=market_data.source
        )
        
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data
    
    async def get_tickers(self, skip: int = 0, limit: int = 100, exchange: Optional[str] = None, sector: Optional[str] = None) -> List[TickerInfo]:
        """Get ticker information"""
        query = self.db.query(TickerInfo)
        
        if exchange:
            query = query.filter(TickerInfo.exchange == exchange)
        if sector:
            query = query.filter(TickerInfo.sector == sector)
        
        return query.offset(skip).limit(limit).all()
    
    async def create_ticker_info(self, ticker_info: TickerInfoCreate) -> TickerInfo:
        """Create ticker information"""
        info = TickerInfo(
            symbol=ticker_info.symbol,
            name=ticker_info.name,
            exchange=ticker_info.exchange,
            sector=ticker_info.sector,
            industry=ticker_info.industry,
            market_cap=ticker_info.market_cap,
            currency=ticker_info.currency,
            is_active=ticker_info.is_active
        )
        
        self.db.add(info)
        self.db.commit()
        self.db.refresh(info)
        return info
    
    async def get_news_data(self, symbol: Optional[str] = None, start_date: Optional[datetime] = None, 
                          end_date: Optional[datetime] = None, sentiment_label: Optional[str] = None,
                          skip: int = 0, limit: int = 100) -> List[NewsData]:
        """Get news and sentiment data"""
        query = self.db.query(NewsData)
        
        if symbol:
            query = query.filter(NewsData.symbol == symbol)
        if start_date:
            query = query.filter(NewsData.timestamp >= start_date)
        if end_date:
            query = query.filter(NewsData.timestamp <= end_date)
        if sentiment_label:
            query = query.filter(NewsData.sentiment_label == sentiment_label)
        
        return query.order_by(desc(NewsData.timestamp)).offset(skip).limit(limit).all()
    
    async def create_news_data(self, news_data: NewsDataCreate) -> NewsData:
        """Create news data entry"""
        data = NewsData(
            symbol=news_data.symbol,
            timestamp=news_data.timestamp,
            title=news_data.title,
            content=news_data.content,
            source=news_data.source,
            sentiment_score=news_data.sentiment_score,
            sentiment_label=news_data.sentiment_label,
            url=news_data.url
        )
        
        self.db.add(data)
        self.db.commit()
        self.db.refresh(data)
        return data
    
    async def sync_market_data(self, symbols: List[str], start_date: datetime, end_date: datetime, source: str = "yfinance") -> Dict[str, Any]:
        """Sync market data from external sources"""
        results = {}
        
        for symbol in symbols:
            try:
                if source == "yfinance":
                    data = await self._fetch_yfinance_data(symbol, start_date, end_date)
                elif source == "alpha_vantage":
                    data = await self._fetch_alpha_vantage_data(symbol, start_date, end_date)
                else:
                    raise ValueError(f"Unsupported data source: {source}")
                
                # Store data in database
                for _, row in data.iterrows():
                    market_data = MarketData(
                        symbol=symbol,
                        timestamp=row.name,
                        open_price=row['Open'],
                        high_price=row['High'],
                        low_price=row['Low'],
                        close_price=row['Close'],
                        volume=row['Volume'],
                        source=source
                    )
                    self.db.add(market_data)
                
                self.db.commit()
                results[symbol] = {"status": "success", "records": len(data)}
                
            except Exception as e:
                results[symbol] = {"status": "error", "error": str(e)}
        
        return results
    
    async def _fetch_yfinance_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch data from Yahoo Finance"""
        ticker = yf.Ticker(symbol)
        data = ticker.history(start=start_date, end=end_date)
        return data
    
    async def _fetch_alpha_vantage_data(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Fetch data from Alpha Vantage API"""
        if not settings.ALPHA_VANTAGE_API_KEY:
            raise ValueError("Alpha Vantage API key not configured")
        
        url = f"https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": settings.ALPHA_VANTAGE_API_KEY,
            "outputsize": "full"
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
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
    
    async def get_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time market data for a symbol from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get current price data
            current_data = ticker.history(period="1d", interval="1m")
            
            if current_data.empty:
                # Fallback to latest daily data
                current_data = ticker.history(period="5d", interval="1d")
            
            if current_data.empty:
                return {"error": f"No data available for symbol {symbol}"}
            
            latest = current_data.iloc[-1]
            previous_close = info.get('previousClose', latest['Close'])
            
            current_price = latest['Close']
            change = current_price - previous_close
            change_percent = (change / previous_close * 100) if previous_close else 0
            
            return {
                "symbol": symbol,
                "name": info.get('longName', symbol),
                "price": float(current_price),
                "previous_close": float(previous_close),
                "change": float(change),
                "change_percent": round(change_percent, 2),
                "volume": int(latest['Volume']),
                "high": float(latest['High']),
                "low": float(latest['Low']),
                "open": float(latest['Open']),
                "market_cap": info.get('marketCap'),
                "currency": info.get('currency', 'USD'),
                "exchange": info.get('exchange', ''),
                "sector": info.get('sector', ''),
                "industry": info.get('industry', ''),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {"error": f"Error fetching data for {symbol}: {str(e)}"}
    
    async def fetch_yfinance_data_direct(
        self, 
        symbol: str, 
        period: str = "1y", 
        interval: str = "1d"
    ) -> Dict[str, Any]:
        """Fetch data directly from Yahoo Finance without storing in DB"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get historical data
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                return {"error": f"No data available for symbol {symbol}"}
            
            # Convert to list of dictionaries
            data = []
            for idx, row in hist.iterrows():
                data.append({
                    "timestamp": idx.isoformat(),
                    "open": float(row['Open']),
                    "high": float(row['High']),
                    "low": float(row['Low']),
                    "close": float(row['Close']),
                    "volume": int(row['Volume'])
                })
            
            return {
                "symbol": symbol,
                "name": info.get('longName', symbol),
                "exchange": info.get('exchange', ''),
                "sector": info.get('sector', ''),
                "industry": info.get('industry', ''),
                "currency": info.get('currency', 'USD'),
                "data": data,
                "count": len(data)
            }
        except Exception as e:
            return {"error": f"Error fetching data for {symbol}: {str(e)}"}
    
    async def search_instruments(self, query: str, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for instruments by name or symbol"""
        # Yahoo Finance doesn't have a direct search API, so we'll use a predefined list
        # In production, you might want to use a financial data provider API
        
        # Common instruments by category
        categories = {
            "stocks": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "META", "NVDA", "JPM", "V", "JNJ"],
            "etfs": ["SPY", "QQQ", "IWM", "GLD", "TLT", "VTI", "VOO", "DIA"],
            "crypto": ["BTC-USD", "ETH-USD", "BNB-USD", "ADA-USD", "SOL-USD"],
            "forex": ["EURUSD=X", "GBPUSD=X", "JPYUSD=X", "AUDUSD=X"],
            "commodities": ["GC=F", "CL=F", "NG=F", "SI=F"]
        }
        
        results = []
        search_lower = query.lower()
        
        # If category specified, search only in that category
        if category and category in categories:
            symbols = categories[category]
        else:
            # Search all categories
            symbols = []
            for cat_symbols in categories.values():
                symbols.extend(cat_symbols)
        
        # Filter symbols that match query
        matching_symbols = [s for s in symbols if search_lower in s.lower()]
        
        # Fetch info for matching symbols
        for symbol in matching_symbols[:20]:  # Limit to 20 results
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                results.append({
                    "symbol": symbol,
                    "name": info.get('longName', symbol),
                    "exchange": info.get('exchange', ''),
                    "sector": info.get('sector', ''),
                    "category": category or self._get_category(symbol, categories)
                })
            except:
                results.append({
                    "symbol": symbol,
                    "name": symbol,
                    "category": category or self._get_category(symbol, categories)
                })
        
        return results
    
    def _get_category(self, symbol: str, categories: Dict[str, List[str]]) -> str:
        """Determine category for a symbol"""
        for category, symbols in categories.items():
            if symbol in symbols:
                return category
        return "stocks"
