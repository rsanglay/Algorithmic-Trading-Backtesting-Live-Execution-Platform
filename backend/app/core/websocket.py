"""
WebSocket router for real-time data streaming
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime

from app.services.websocket_service import WebSocketService

router = APIRouter()


class ConnectionManager:
    """WebSocket connection manager"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[WebSocket, List[str]] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = []
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket"""
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        """Broadcast a message to all connected WebSockets"""
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)
    
    async def broadcast_to_subscribers(self, symbol: str, message: str):
        """Broadcast a message to subscribers of a specific symbol"""
        for websocket, subscriptions in self.subscriptions.items():
            if symbol in subscriptions:
                try:
                    await websocket.send_text(message)
                except:
                    self.disconnect(websocket)
    
    def subscribe(self, websocket: WebSocket, symbol: str):
        """Subscribe a WebSocket to a symbol"""
        if websocket in self.subscriptions:
            if symbol not in self.subscriptions[websocket]:
                self.subscriptions[websocket].append(symbol)
    
    def unsubscribe(self, websocket: WebSocket, symbol: str):
        """Unsubscribe a WebSocket from a symbol"""
        if websocket in self.subscriptions and symbol in self.subscriptions[websocket]:
            self.subscriptions[websocket].remove(symbol)


manager = ConnectionManager()


@router.websocket("/market-data")
async def websocket_market_data(websocket: WebSocket):
    """WebSocket endpoint for real-time market data"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for client message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe":
                symbol = message.get("symbol")
                if symbol:
                    manager.subscribe(websocket, symbol)
                    await manager.send_personal_message(
                        json.dumps({"type": "subscribed", "symbol": symbol}),
                        websocket
                    )
            
            elif message.get("type") == "unsubscribe":
                symbol = message.get("symbol")
                if symbol:
                    manager.unsubscribe(websocket, symbol)
                    await manager.send_personal_message(
                        json.dumps({"type": "unsubscribed", "symbol": symbol}),
                        websocket
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/trading-signals")
async def websocket_trading_signals(websocket: WebSocket):
    """WebSocket endpoint for trading signals"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for client message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe_strategy":
                strategy_id = message.get("strategy_id")
                if strategy_id:
                    # Subscribe to strategy signals
                    await manager.send_personal_message(
                        json.dumps({"type": "strategy_subscribed", "strategy_id": strategy_id}),
                        websocket
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@router.websocket("/portfolio-updates")
async def websocket_portfolio_updates(websocket: WebSocket):
    """WebSocket endpoint for portfolio updates"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Wait for client message
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message.get("type") == "subscribe_portfolio":
                portfolio_id = message.get("portfolio_id")
                if portfolio_id:
                    # Subscribe to portfolio updates
                    await manager.send_personal_message(
                        json.dumps({"type": "portfolio_subscribed", "portfolio_id": portfolio_id}),
                        websocket
                    )
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# Background task to send real-time data
async def send_realtime_data():
    """Background task to send real-time market data"""
    while True:
        try:
            # This would typically fetch real-time data from a data source
            # For now, we'll send a heartbeat
            await manager.broadcast(
                json.dumps({
                    "type": "heartbeat",
                    "timestamp": datetime.now().isoformat()
                })
            )
            await asyncio.sleep(1)  # Send every second
        except Exception as e:
            print(f"Error in real-time data task: {e}")
            await asyncio.sleep(5)
