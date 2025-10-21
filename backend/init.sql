-- Initialize database for trading platform
CREATE DATABASE trading_platform;
CREATE DATABASE trading_platform_ts;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";

-- Create user for application
CREATE USER trading_user WITH PASSWORD 'trading_password';
GRANT ALL PRIVILEGES ON DATABASE trading_platform TO trading_user;
GRANT ALL PRIVILEGES ON DATABASE trading_platform_ts TO trading_user;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS market_data;
CREATE SCHEMA IF NOT EXISTS strategies;
CREATE SCHEMA IF NOT EXISTS ml_models;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA market_data TO trading_user;
GRANT ALL PRIVILEGES ON SCHEMA strategies TO trading_user;
GRANT ALL PRIVILEGES ON SCHEMA ml_models TO trading_user;
GRANT ALL PRIVILEGES ON SCHEMA analytics TO trading_user;
