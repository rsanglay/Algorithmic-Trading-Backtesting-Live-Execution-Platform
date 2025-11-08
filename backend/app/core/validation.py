"""
Input validation and sanitization utilities
"""
import re
from typing import Any, Dict, List, Optional
from datetime import datetime
import html

from app.core.exceptions import ValidationError


class InputValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_symbol(symbol: str) -> bool:
        """Validate trading symbol format"""
        # Symbols should be 1-10 alphanumeric characters
        pattern = r'^[A-Z0-9]{1,10}$'
        return bool(re.match(pattern, symbol.upper()))
    
    @staticmethod
    def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
        """Validate date range"""
        if start_date >= end_date:
            return False
        if (end_date - start_date).days > 365 * 10:  # Max 10 years
            return False
        return True
    
    @staticmethod
    def validate_price(price: float) -> bool:
        """Validate price value"""
        if price <= 0:
            return False
        if price > 1e6:  # Max price
            return False
        return True
    
    @staticmethod
    def validate_quantity(quantity: float) -> bool:
        """Validate quantity value"""
        if quantity <= 0:
            return False
        if quantity > 1e9:  # Max quantity
            return False
        return True
    
    @staticmethod
    def validate_percentage(value: float) -> bool:
        """Validate percentage value"""
        return -100 <= value <= 100
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        # Remove HTML tags
        value = html.escape(value)
        
        # Trim whitespace
        value = value.strip()
        
        # Limit length
        if len(value) > max_length:
            value = value[:max_length]
        
        return value
    
    @staticmethod
    def validate_strategy_code(code: str) -> bool:
        """Validate strategy code"""
        # Check for dangerous operations
        dangerous_patterns = [
            r'__import__',
            r'eval\(',
            r'exec\(',
            r'open\(',
            r'file\(',
            r'input\(',
            r'raw_input\(',
            r'subprocess',
            r'os\.system',
            r'shell=True',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, code, re.IGNORECASE):
                return False
        
        return True
    
    @staticmethod
    def validate_json_structure(data: Dict[str, Any], required_fields: List[str]) -> bool:
        """Validate JSON structure has required fields"""
        for field in required_fields:
            if field not in data:
                return False
        return True


def validate_market_data(data: Dict[str, Any]) -> None:
    """Validate market data input"""
    validator = InputValidator()
    
    # Validate symbol
    if "symbol" in data and not validator.validate_symbol(data["symbol"]):
        raise ValidationError("Invalid symbol format")
    
    # Validate prices
    price_fields = ["open_price", "high_price", "low_price", "close_price"]
    for field in price_fields:
        if field in data and not validator.validate_price(data[field]):
            raise ValidationError(f"Invalid {field} value")
    
    # Validate volume
    if "volume" in data and data["volume"] < 0:
        raise ValidationError("Volume cannot be negative")
    
    # Validate price relationships
    if all(field in data for field in ["high_price", "low_price"]):
        if data["high_price"] < data["low_price"]:
            raise ValidationError("High price cannot be less than low price")
    
    if all(field in data for field in ["high_price", "open_price", "close_price"]):
        if data["high_price"] < data["open_price"] or data["high_price"] < data["close_price"]:
            raise ValidationError("High price must be >= open and close prices")
    
    if all(field in data for field in ["low_price", "open_price", "close_price"]):
        if data["low_price"] > data["open_price"] or data["low_price"] > data["close_price"]:
            raise ValidationError("Low price must be <= open and close prices")


def validate_strategy_input(data: Dict[str, Any]) -> None:
    """Validate strategy input"""
    validator = InputValidator()
    
    # Validate required fields
    required_fields = ["name", "strategy_type", "code"]
    if not validator.validate_json_structure(data, required_fields):
        raise ValidationError("Missing required fields")
    
    # Validate name
    if len(data["name"]) > 200:
        raise ValidationError("Strategy name too long")
    
    # Validate strategy code
    if not validator.validate_strategy_code(data["code"]):
        raise ValidationError("Strategy code contains potentially dangerous operations")
    
    # Validate strategy type
    valid_types = ["momentum", "mean_reversion", "pairs_trading", "statistical_arbitrage"]
    if data["strategy_type"] not in valid_types:
        raise ValidationError(f"Invalid strategy type. Must be one of: {', '.join(valid_types)}")


def validate_backtest_input(data: Dict[str, Any]) -> None:
    """Validate backtest input"""
    validator = InputValidator()
    
    # Validate required fields
    required_fields = ["start_date", "end_date", "initial_capital"]
    if not validator.validate_json_structure(data, required_fields):
        raise ValidationError("Missing required fields")
    
    # Validate dates
    start_date = datetime.fromisoformat(data["start_date"]) if isinstance(data["start_date"], str) else data["start_date"]
    end_date = datetime.fromisoformat(data["end_date"]) if isinstance(data["end_date"], str) else data["end_date"]
    
    if not validator.validate_date_range(start_date, end_date):
        raise ValidationError("Invalid date range")
    
    # Validate initial capital
    if data["initial_capital"] <= 0:
        raise ValidationError("Initial capital must be positive")
    
    if data["initial_capital"] > 1e9:  # Max 1 billion
        raise ValidationError("Initial capital too large")


def sanitize_user_input(value: Any) -> Any:
    """Sanitize user input"""
    validator = InputValidator()
    
    if isinstance(value, str):
        return validator.sanitize_string(value)
    elif isinstance(value, dict):
        return {k: sanitize_user_input(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [sanitize_user_input(item) for item in value]
    else:
        return value
