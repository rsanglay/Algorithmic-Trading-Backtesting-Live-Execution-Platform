"""
WebSocket service for real-time data streaming
"""
from typing import Dict, List, Any
import asyncio
import json
from datetime import datetime
import redis

from app.core.config import settings
from app.core.database import get_redis


class WebSocketService:
    """Service for WebSocket connections and real-time data"""
    
    def __init__(self):
        self.redis_client = get_redis()
        self.subscribers: Dict[str, List[Any]] = {}
    
    async def subscribe_to_symbol(self, websocket, symbol: str):
        """Subscribe a WebSocket to real-time data for a symbol"""
        if symbol not in self.subscribers:
            self.subscribers[symbol] = []
        
        self.subscribers[symbol].append(websocket)
        
        # Send confirmation
        await websocket.send_text(json.dumps({
            "type": "subscription_confirmed",
            "symbol": symbol,
            "timestamp": datetime.now().isoformat()
        }))
    
    async def unsubscribe_from_symbol(self, websocket, symbol: str):
        """Unsubscribe a WebSocket from a symbol"""
        if symbol in self.subscribers and websocket in self.subscribers[symbol]:
            self.subscribers[symbol].remove(websocket)
            
            # Send confirmation
            await websocket.send_text(json.dumps({
                "type": "unsubscription_confirmed",
                "symbol": symbol,
                "timestamp": datetime.now().isoformat()
            }))
    
    async def broadcast_market_data(self, symbol: str, data: Dict[str, Any]):
        """Broadcast market data to all subscribers of a symbol"""
        if symbol not in self.subscribers:
            return
        
        message = json.dumps({
            "type": "market_data",
            "symbol": symbol,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })
        
        # Send to all subscribers
        disconnected = []
        for websocket in self.subscribers[symbol]:
            try:
                await websocket.send_text(message)
            except:
                disconnected.append(websocket)
        
        # Remove disconnected WebSockets
        for websocket in disconnected:
            self.subscribers[symbol].remove(websocket)
    
    async def broadcast_trading_signal(self, strategy_id: str, signal: Dict[str, Any]):
        """Broadcast trading signal to subscribers"""
        message = json.dumps({
            "type": "trading_signal",
            "strategy_id": strategy_id,
            "signal": signal,
            "timestamp": datetime.now().isoformat()
        })
        
        # Broadcast to all connected WebSockets
        # In a real implementation, you'd track strategy subscribers
        pass
    
    async def broadcast_portfolio_update(self, portfolio_id: str, update: Dict[str, Any]):
        """Broadcast portfolio update to subscribers"""
        message = json.dumps({
            "type": "portfolio_update",
            "portfolio_id": portfolio_id,
            "update": update,
            "timestamp": datetime.now().isoformat()
        })
        
        # Broadcast to all connected WebSockets
        # In a real implementation, you'd track portfolio subscribers
        pass
    
    async def start_market_data_stream(self):
        """Start streaming market data from external sources"""
        # This would typically connect to a real-time data feed
        # For now, we'll simulate with periodic updates
        while True:
            try:
                # Simulate market data updates
                symbols = list(self.subscribers.keys())
                for symbol in symbols:
                    # Generate mock market data
                    mock_data = {
                        "price": 100 + (hash(symbol) % 20) - 10,  # Mock price
                        "volume": 1000 + (hash(symbol) % 5000),
                        "change": (hash(symbol) % 10) - 5,
                        "change_percent": ((hash(symbol) % 10) - 5) / 100
                    }
                    
                    await self.broadcast_market_data(symbol, mock_data)
                
                await asyncio.sleep(1)  # Update every second
                
            except Exception as e:
                print(f"Error in market data stream: {e}")
                await asyncio.sleep(5)
    
    async def start_trading_signal_stream(self):
        """Start streaming trading signals"""
        # This would typically connect to strategy execution engines
        # For now, we'll simulate with periodic signals
        while True:
            try:
                # Simulate trading signals
                # In a real implementation, this would come from active strategies
                pass
                
                await asyncio.sleep(5)  # Check for signals every 5 seconds
                
            except Exception as e:
                print(f"Error in trading signal stream: {e}")
                await asyncio.sleep(10)
    
    async def start_portfolio_update_stream(self):
        """Start streaming portfolio updates"""
        # This would typically connect to portfolio management systems
        # For now, we'll simulate with periodic updates
        while True:
            try:
                # Simulate portfolio updates
                # In a real implementation, this would come from portfolio management
                pass
                
                await asyncio.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                print(f"Error in portfolio update stream: {e}")
                await asyncio.sleep(15)
    
    def get_subscriber_count(self, symbol: str) -> int:
        """Get number of subscribers for a symbol"""
        return len(self.subscribers.get(symbol, []))
    
    def get_total_subscribers(self) -> int:
        """Get total number of subscribers across all symbols"""
        return sum(len(subscribers) for subscribers in self.subscribers.values())
    
    def get_active_symbols(self) -> List[str]:
        """Get list of symbols with active subscribers"""
        return [symbol for symbol, subscribers in self.subscribers.items() if subscribers]
