"""
Real-time streaming data pipeline
"""
import asyncio
import aiohttp
import json
from typing import Dict, Any, List, Callable
from datetime import datetime
import websockets
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.market_data import MarketData
from app.services.market_data_service import MarketDataService


class StreamingPipeline:
    """Real-time streaming data pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.subscribers: List[Callable] = []
        self.is_running = False
    
    def subscribe(self, callback: Callable):
        """Subscribe to real-time data updates"""
        self.subscribers.append(callback)
    
    def unsubscribe(self, callback: Callable):
        """Unsubscribe from real-time data updates"""
        if callback in self.subscribers:
            self.subscribers.remove(callback)
    
    async def notify_subscribers(self, data: Dict[str, Any]):
        """Notify all subscribers of new data"""
        for callback in self.subscribers:
            try:
                await callback(data)
            except Exception as e:
                print(f"Error notifying subscriber: {str(e)}")
    
    async def start_streaming(self, symbols: List[str]):
        """Start streaming real-time data"""
        self.is_running = True
        
        # Start multiple streaming tasks
        tasks = []
        for symbol in symbols:
            task = asyncio.create_task(self._stream_symbol_data(symbol))
            tasks.append(task)
        
        # Wait for all tasks
        await asyncio.gather(*tasks)
    
    async def stop_streaming(self):
        """Stop streaming real-time data"""
        self.is_running = False
    
    async def _stream_symbol_data(self, symbol: str):
        """Stream data for a specific symbol"""
        while self.is_running:
            try:
                # Get real-time data
                data = await self._get_realtime_data(symbol)
                
                if data:
                    # Store in database
                    await self._store_realtime_data(symbol, data)
                    
                    # Notify subscribers
                    await self.notify_subscribers({
                        "symbol": symbol,
                        "data": data,
                        "timestamp": datetime.now()
                    })
                
                # Wait before next update
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"Error streaming data for {symbol}: {str(e)}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _get_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time data for a symbol"""
        # This would integrate with real-time data providers
        # For now, return mock data
        import random
        
        base_price = 100 + hash(symbol) % 50
        change = random.uniform(-0.02, 0.02)
        price = base_price * (1 + change)
        
        return {
            "symbol": symbol,
            "price": price,
            "change": change,
            "volume": random.randint(1000, 10000),
            "timestamp": datetime.now()
        }
    
    async def _store_realtime_data(self, symbol: str, data: Dict[str, Any]):
        """Store real-time data in database"""
        try:
            market_data = MarketData(
                symbol=symbol,
                timestamp=data["timestamp"],
                open_price=data["price"],
                high_price=data["price"] * 1.01,
                low_price=data["price"] * 0.99,
                close_price=data["price"],
                volume=data["volume"],
                source="realtime"
            )
            
            self.db.add(market_data)
            self.db.commit()
            
        except Exception as e:
            print(f"Error storing real-time data: {str(e)}")
            self.db.rollback()


class WebSocketStreamingPipeline:
    """WebSocket-based streaming pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
        self.connections: List[websockets.WebSocketServerProtocol] = []
        self.is_running = False
    
    async def start_websocket_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server for real-time data"""
        self.is_running = True
        
        async def handle_client(websocket, path):
            self.connections.append(websocket)
            print(f"Client connected: {websocket.remote_address}")
            
            try:
                async for message in websocket:
                    data = json.loads(message)
                    await self._handle_client_message(websocket, data)
            except websockets.exceptions.ConnectionClosed:
                pass
            finally:
                self.connections.remove(websocket)
                print(f"Client disconnected: {websocket.remote_address}")
        
        print(f"Starting WebSocket server on {host}:{port}")
        await websockets.serve(handle_client, host, port)
    
    async def _handle_client_message(self, websocket, data: Dict[str, Any]):
        """Handle client messages"""
        message_type = data.get("type")
        
        if message_type == "subscribe":
            symbol = data.get("symbol")
            if symbol:
                # Start streaming data for this symbol
                asyncio.create_task(self._stream_symbol_to_client(websocket, symbol))
        
        elif message_type == "unsubscribe":
            symbol = data.get("symbol")
            # Stop streaming for this symbol
            pass
    
    async def _stream_symbol_to_client(self, websocket, symbol: str):
        """Stream data for a specific symbol to a client"""
        while self.is_running and websocket in self.connections:
            try:
                # Get real-time data
                data = await self._get_realtime_data(symbol)
                
                if data:
                    # Send to client
                    message = {
                        "type": "market_data",
                        "symbol": symbol,
                        "data": data,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    await websocket.send(json.dumps(message))
                
                # Wait before next update
                await asyncio.sleep(1)
                
            except websockets.exceptions.ConnectionClosed:
                break
            except Exception as e:
                print(f"Error streaming to client: {str(e)}")
                break
    
    async def _get_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time data for a symbol"""
        # This would integrate with real-time data providers
        import random
        
        base_price = 100 + hash(symbol) % 50
        change = random.uniform(-0.02, 0.02)
        price = base_price * (1 + change)
        
        return {
            "symbol": symbol,
            "price": price,
            "change": change,
            "volume": random.randint(1000, 10000),
            "timestamp": datetime.now().isoformat()
        }
    
    async def broadcast_to_all_clients(self, data: Dict[str, Any]):
        """Broadcast data to all connected clients"""
        if not self.connections:
            return
        
        message = json.dumps(data)
        
        # Send to all connections
        for websocket in self.connections.copy():
            try:
                await websocket.send(message)
            except websockets.exceptions.ConnectionClosed:
                self.connections.remove(websocket)
            except Exception as e:
                print(f"Error broadcasting to client: {str(e)}")
                self.connections.remove(websocket)
    
    async def stop_websocket_server(self):
        """Stop WebSocket server"""
        self.is_running = False
        
        # Close all connections
        for websocket in self.connections:
            await websocket.close()


class DataQualityPipeline:
    """Data quality monitoring and validation pipeline"""
    
    def __init__(self, db: Session):
        self.db = db
        self.market_data_service = MarketDataService(db)
    
    async def validate_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate market data quality"""
        validation_results = {
            "is_valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check required fields
        required_fields = ["symbol", "timestamp", "open_price", "high_price", "low_price", "close_price", "volume"]
        for field in required_fields:
            if field not in data:
                validation_results["is_valid"] = False
                validation_results["errors"].append(f"Missing required field: {field}")
        
        if not validation_results["is_valid"]:
            return validation_results
        
        # Check data types
        try:
            float(data["open_price"])
            float(data["high_price"])
            float(data["low_price"])
            float(data["close_price"])
            float(data["volume"])
        except (ValueError, TypeError):
            validation_results["is_valid"] = False
            validation_results["errors"].append("Invalid data types for price/volume fields")
        
        # Check price relationships
        if data["high_price"] < data["low_price"]:
            validation_results["is_valid"] = False
            validation_results["errors"].append("High price cannot be less than low price")
        
        if data["high_price"] < data["open_price"]:
            validation_results["warnings"].append("High price is less than open price")
        
        if data["high_price"] < data["close_price"]:
            validation_results["warnings"].append("High price is less than close price")
        
        if data["low_price"] > data["open_price"]:
            validation_results["warnings"].append("Low price is greater than open price")
        
        if data["low_price"] > data["close_price"]:
            validation_results["warnings"].append("Low price is greater than close price")
        
        # Check for reasonable values
        if data["volume"] < 0:
            validation_results["is_valid"] = False
            validation_results["errors"].append("Volume cannot be negative")
        
        if data["open_price"] <= 0 or data["high_price"] <= 0 or data["low_price"] <= 0 or data["close_price"] <= 0:
            validation_results["is_valid"] = False
            validation_results["errors"].append("Prices must be positive")
        
        return validation_results
    
    async def detect_anomalies(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies in market data"""
        anomalies = {
            "has_anomalies": False,
            "anomalies": []
        }
        
        # Get historical data for comparison
        historical_data = await self._get_historical_data(symbol, days=30)
        
        if not historical_data:
            return anomalies
        
        # Calculate statistics
        prices = [row["close_price"] for row in historical_data]
        mean_price = sum(prices) / len(prices)
        std_price = (sum((p - mean_price) ** 2 for p in prices) / len(prices)) ** 0.5
        
        # Check for price anomalies
        current_price = data["close_price"]
        if abs(current_price - mean_price) > 3 * std_price:
            anomalies["has_anomalies"] = True
            anomalies["anomalies"].append({
                "type": "price_anomaly",
                "description": f"Price {current_price} is more than 3 standard deviations from mean {mean_price}",
                "severity": "high"
            })
        
        # Check for volume anomalies
        volumes = [row["volume"] for row in historical_data]
        mean_volume = sum(volumes) / len(volumes)
        std_volume = (sum((v - mean_volume) ** 2 for v in volumes) / len(volumes)) ** 0.5
        
        current_volume = data["volume"]
        if current_volume > mean_volume + 3 * std_volume:
            anomalies["has_anomalies"] = True
            anomalies["anomalies"].append({
                "type": "volume_anomaly",
                "description": f"Volume {current_volume} is unusually high",
                "severity": "medium"
            })
        
        return anomalies
    
    async def _get_historical_data(self, symbol: str, days: int) -> List[Dict[str, Any]]:
        """Get historical data for anomaly detection"""
        # This would query the database for historical data
        # For now, return mock data
        return []
    
    async def run_data_quality_check(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete data quality check"""
        results = {
            "validation": await self.validate_market_data(data),
            "anomalies": await self.detect_anomalies(data.get("symbol", ""), data)
        }
        
        return results
