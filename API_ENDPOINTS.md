# Complete API Endpoints Reference

## Base URL
- **Development**: `http://localhost:8001/api/v1`
- **Production**: `https://your-domain.com/api/v1`

---

## 🔐 Authentication Endpoints

### `POST /auth/register`
Register a new user
- **Body**: `{ email, username, password, full_name }`
- **Response**: User object with JWT token
- **Status**: 201 Created

### `POST /auth/login`
Login and get access token
- **Body**: `{ username, password }`
- **Response**: `{ access_token, token_type, user }`
- **Status**: 200 OK

### `GET /auth/me`
Get current user information
- **Auth**: Required (Bearer token)
- **Response**: User object with preferences
- **Status**: 200 OK

### `PUT /auth/me/preferences`
Update user preferences
- **Auth**: Required (Bearer token)
- **Body**: `{ dashboard_preferences, trading_preferences }`
- **Response**: Updated user object
- **Status**: 200 OK

---

## 📊 Market Data Endpoints

### `GET /market-data/ohlcv`
Get OHLCV market data
- **Query Params**: `symbol`, `start_date`, `end_date`, `interval`
- **Response**: List of market data points
- **Status**: 200 OK

### `POST /market-data/ohlcv`
Create market data entry
- **Body**: MarketDataCreate schema
- **Response**: Created market data
- **Status**: 201 Created

### `GET /market-data/fetch/{symbol}`
Fetch data from Yahoo Finance
- **Path Params**: `symbol` (e.g., AAPL)
- **Query Params**: `period` (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max), `interval` (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
- **Response**: Historical price data
- **Status**: 200 OK

### `GET /market-data/realtime/{symbol}`
Get real-time quote from Yahoo Finance
- **Path Params**: `symbol` (e.g., AAPL)
- **Response**: Real-time quote with price, change, volume
- **Status**: 200 OK

### `GET /market-data/search`
Search for instruments
- **Query Params**: `query` (required), `category` (optional: stocks, etfs, crypto, forex, commodities)
- **Response**: List of matching instruments
- **Status**: 200 OK

### `GET /market-data/categories`
Get available instrument categories
- **Response**: List of categories with descriptions
- **Status**: 200 OK

### `GET /market-data/ticker/{symbol}`
Get ticker information
- **Path Params**: `symbol`
- **Response**: Ticker info (company details, sector, etc.)
- **Status**: 200 OK

### `GET /market-data/technical-indicators`
Get technical indicators
- **Query Params**: `symbol`, `start_date`, `end_date`, `indicators[]`
- **Response**: Technical indicators data
- **Status**: 200 OK

---

## 📈 Strategy Endpoints

### `POST /strategies`
Create a new trading strategy
- **Auth**: Required
- **Body**: StrategyCreate schema
- **Response**: Created strategy
- **Status**: 201 Created

### `GET /strategies`
Get all strategies
- **Auth**: Required
- **Query Params**: `skip`, `limit`
- **Response**: List of strategies
- **Status**: 200 OK

### `GET /strategies/{strategy_id}`
Get strategy by ID
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Response**: Strategy object
- **Status**: 200 OK

### `PUT /strategies/{strategy_id}`
Update strategy
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Body**: StrategyUpdate schema
- **Response**: Updated strategy
- **Status**: 200 OK

### `DELETE /strategies/{strategy_id}`
Delete strategy
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Status**: 204 No Content

### `POST /strategies/{strategy_id}/activate`
Activate strategy
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Response**: Activated strategy
- **Status**: 200 OK

### `POST /strategies/{strategy_id}/deactivate`
Deactivate strategy
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Response**: Deactivated strategy
- **Status**: 200 OK

### `POST /strategies/{strategy_id}/backtest`
Run backtest for strategy
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Body**: BacktestCreate schema
- **Response**: Backtest results
- **Status**: 201 Created

### `GET /strategies/{strategy_id}/backtests`
Get all backtests for strategy
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Response**: List of backtests
- **Status**: 200 OK

---

## 🤖 ML Model Endpoints

### `POST /ml-models`
Create a new ML model
- **Auth**: Required
- **Body**: MLModelCreate schema
- **Response**: Created model
- **Status**: 201 Created

### `GET /ml-models`
Get all ML models
- **Auth**: Required
- **Query Params**: `skip`, `limit`, `model_type`, `purpose`, `is_active`
- **Response**: List of models
- **Status**: 200 OK

### `GET /ml-models/{model_id}`
Get model by ID
- **Auth**: Required
- **Path Params**: `model_id` (UUID)
- **Response**: Model object
- **Status**: 200 OK

### `PUT /ml-models/{model_id}`
Update model
- **Auth**: Required
- **Path Params**: `model_id` (UUID)
- **Body**: MLModelUpdate schema
- **Response**: Updated model
- **Status**: 200 OK

### `DELETE /ml-models/{model_id}`
Delete model
- **Auth**: Required
- **Path Params**: `model_id` (UUID)
- **Status**: 204 No Content

### `POST /ml-models/{model_id}/train`
Train model
- **Auth**: Required
- **Path Params**: `model_id` (UUID)
- **Body**: Training parameters
- **Response**: Training job started
- **Status**: 202 Accepted

### `POST /ml-models/{model_id}/predict`
Get predictions from model
- **Auth**: Required
- **Path Params**: `model_id` (UUID)
- **Body**: Input features
- **Response**: Predictions
- **Status**: 200 OK

### `GET /ml-models/{model_id}/performance`
Get model performance metrics
- **Auth**: Required
- **Path Params**: `model_id` (UUID)
- **Response**: Performance metrics
- **Status**: 200 OK

---

## 📊 Analytics Endpoints

### `GET /analytics/performance/{strategy_id}`
Get strategy performance metrics
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Query Params**: `start_date`, `end_date`
- **Response**: Performance metrics (returns, Sharpe ratio, etc.)
- **Status**: 200 OK

### `GET /analytics/risk/{strategy_id}`
Get risk metrics for strategy
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Query Params**: `start_date`, `end_date`
- **Response**: Risk metrics (VaR, max drawdown, etc.)
- **Status**: 200 OK

### `GET /analytics/correlation`
Get correlation matrix
- **Auth**: Required
- **Query Params**: `symbols[]`, `start_date`, `end_date`
- **Response**: Correlation matrix
- **Status**: 200 OK

### `GET /analytics/volatility/{strategy_id}`
Get volatility analysis
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Query Params**: `start_date`, `end_date`, `window`
- **Response**: Volatility metrics
- **Status**: 200 OK

### `POST /analytics/var/{strategy_id}`
Calculate Value at Risk
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Query Params**: `confidence_level` (default: 0.95), `start_date`, `end_date`
- **Response**: VaR calculation
- **Status**: 200 OK

### `POST /analytics/stress-test/{strategy_id}`
Run stress test
- **Auth**: Required
- **Path Params**: `strategy_id` (UUID)
- **Body**: Stress test scenarios
- **Response**: Stress test results
- **Status**: 200 OK

---

## 🔍 Health & Info Endpoints

### `GET /`
Root endpoint
- **Response**: API information
- **Status**: 200 OK

### `GET /health`
Health check
- **Response**: Health status of all services
- **Status**: 200 OK or 503 Service Unavailable

### `GET /ready`
Readiness check (Kubernetes)
- **Response**: Ready status
- **Status**: 200 OK or 503 Service Unavailable

### `GET /live`
Liveness check (Kubernetes)
- **Response**: Alive status
- **Status**: 200 OK

---

## 📝 Notes

- All endpoints requiring authentication need a Bearer token in the Authorization header
- Format: `Authorization: Bearer <token>`
- Most endpoints support pagination with `skip` and `limit` query parameters
- Date formats: ISO 8601 (e.g., `2024-01-01T00:00:00Z`)
- UUIDs are used for resource IDs

---

## 🔗 API Documentation

- **Swagger UI**: `http://localhost:8001/docs` (development only)
- **ReDoc**: `http://localhost:8001/redoc` (development only)

