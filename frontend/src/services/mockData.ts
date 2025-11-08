/**
 * Mock Data Service
 * Provides sample data for demo/portfolio mode when backend is unavailable
 */

import { Strategy } from '../store/slices/strategiesSlice';
import { MLModel } from '../store/slices/mlModelsSlice';
import { Backtest } from '../store/slices/backtestingSlice';

// Generate random dates
const randomDate = (start: Date, end: Date): string => {
  return new Date(start.getTime() + Math.random() * (end.getTime() - start.getTime())).toISOString();
};

// Mock Strategies
export const mockStrategies: Strategy[] = [
  {
    id: '1',
    name: 'Momentum Breakout',
    description: 'Identifies stocks breaking out of consolidation patterns with high volume',
    strategy_type: 'momentum',
    code: `def execute(data):
    # Momentum breakout logic
    if data['volume'] > data['avg_volume'] * 1.5:
        if data['price'] > data['resistance']:
            return 'BUY'
    return 'HOLD'`,
    parameters: { lookback: 20, volume_threshold: 1.5 },
    is_active: true,
    is_live: false,
    created_by: 'user@example.com',
    created_at: randomDate(new Date(2024, 0, 1), new Date(2024, 5, 1)),
    updated_at: randomDate(new Date(2024, 5, 1), new Date()),
  },
  {
    id: '2',
    name: 'Mean Reversion RSI',
    description: 'Buys oversold stocks and sells overbought using RSI indicator',
    strategy_type: 'mean_reversion',
    code: `def execute(data):
    rsi = calculate_rsi(data, 14)
    if rsi < 30:
        return 'BUY'
    elif rsi > 70:
        return 'SELL'
    return 'HOLD'`,
    parameters: { rsi_period: 14, oversold: 30, overbought: 70 },
    is_active: true,
    is_live: true,
    created_by: 'user@example.com',
    created_at: randomDate(new Date(2024, 0, 1), new Date(2024, 5, 1)),
    updated_at: randomDate(new Date(2024, 5, 1), new Date()),
  },
  {
    id: '3',
    name: 'Pairs Trading',
    description: 'Statistical arbitrage between correlated pairs',
    strategy_type: 'pairs_trading',
    code: `def execute(data):
    spread = data['stock_a'] - data['stock_b']
    z_score = (spread - spread.mean()) / spread.std()
    if z_score > 2:
        return 'SELL_PAIR'
    elif z_score < -2:
        return 'BUY_PAIR'
    return 'HOLD'`,
    parameters: { lookback: 60, entry_threshold: 2, exit_threshold: 0.5 },
    is_active: false,
    is_live: false,
    created_by: 'user@example.com',
    created_at: randomDate(new Date(2024, 0, 1), new Date(2024, 5, 1)),
  },
  {
    id: '4',
    name: 'MACD Crossover',
    description: 'Trading signals based on MACD line crossovers',
    strategy_type: 'momentum',
    code: `def execute(data):
    macd, signal = calculate_macd(data)
    if macd > signal and macd_prev < signal_prev:
        return 'BUY'
    elif macd < signal and macd_prev > signal_prev:
        return 'SELL'
    return 'HOLD'`,
    parameters: { fast_period: 12, slow_period: 26, signal_period: 9 },
    is_active: true,
    is_live: false,
    created_by: 'user@example.com',
    created_at: randomDate(new Date(2024, 0, 1), new Date(2024, 5, 1)),
  },
];

// Mock ML Models
export const mockMLModels: MLModel[] = [
  {
    id: '1',
    name: 'LSTM Price Predictor',
    model_type: 'lstm',
    purpose: 'price_prediction',
    version: '1.0.0',
    features: ['price', 'volume', 'rsi', 'macd', 'bollinger_bands'],
    target: 'next_price',
    hyperparameters: { epochs: 100, batch_size: 32, learning_rate: 0.001 },
    accuracy: 0.87,
    precision: 0.85,
    recall: 0.82,
    f1_score: 0.83,
    mse: 0.023,
    mae: 0.018,
    is_active: true,
    is_training: false,
    status: 'trained',
    created_at: randomDate(new Date(2024, 0, 1), new Date(2024, 5, 1)),
    training_start_date: randomDate(new Date(2024, 0, 1), new Date(2024, 2, 1)),
    training_end_date: randomDate(new Date(2024, 2, 1), new Date(2024, 3, 1)),
    training_samples: 50000,
    validation_samples: 10000,
  },
  {
    id: '2',
    name: 'Random Forest Classifier',
    model_type: 'random_forest',
    purpose: 'signal_classification',
    version: '2.1.0',
    features: ['technical_indicators', 'market_sentiment', 'volume_profile'],
    target: 'buy_signal',
    hyperparameters: { n_estimators: 100, max_depth: 10, min_samples_split: 5 },
    accuracy: 0.79,
    precision: 0.76,
    recall: 0.81,
    f1_score: 0.78,
    is_active: true,
    is_training: false,
    status: 'trained',
    created_at: randomDate(new Date(2024, 0, 1), new Date(2024, 5, 1)),
    training_start_date: randomDate(new Date(2024, 1, 1), new Date(2024, 3, 1)),
    training_end_date: randomDate(new Date(2024, 3, 1), new Date(2024, 4, 1)),
    training_samples: 75000,
    validation_samples: 15000,
  },
  {
    id: '3',
    name: 'XGBoost Regressor',
    model_type: 'xgboost',
    purpose: 'return_prediction',
    version: '1.5.0',
    features: ['price_features', 'volume_features', 'market_features'],
    target: 'next_return',
    hyperparameters: { n_estimators: 200, max_depth: 6, learning_rate: 0.1 },
    accuracy: 0.82,
    mse: 0.019,
    mae: 0.015,
    is_active: false,
    is_training: true,
    status: 'training',
    created_at: randomDate(new Date(2024, 2, 1), new Date(2024, 5, 1)),
    training_start_date: new Date().toISOString(),
  },
];

// Mock Backtests
export const mockBacktests: Backtest[] = [
  {
    id: '1',
    strategy_id: '1',
    name: 'Momentum Breakout - Q1 2024',
    start_date: '2024-01-01T00:00:00Z',
    end_date: '2024-03-31T23:59:59Z',
    initial_capital: 100000,
    final_capital: 125450,
    total_return: 0.2545,
    annualized_return: 0.118,
    sharpe_ratio: 1.85,
    max_drawdown: -0.12,
    win_rate: 0.68,
    profit_factor: 2.1,
    status: 'completed',
    created_at: '2024-04-01T10:00:00Z',
    completed_at: '2024-04-01T10:15:00Z',
  },
  {
    id: '2',
    strategy_id: '2',
    name: 'Mean Reversion RSI - Full Year',
    start_date: '2023-01-01T00:00:00Z',
    end_date: '2023-12-31T23:59:59Z',
    initial_capital: 100000,
    final_capital: 118900,
    total_return: 0.189,
    annualized_return: 0.189,
    sharpe_ratio: 1.42,
    max_drawdown: -0.15,
    win_rate: 0.65,
    profit_factor: 1.8,
    status: 'completed',
    created_at: '2024-01-02T09:00:00Z',
    completed_at: '2024-01-02T09:30:00Z',
  },
  {
    id: '3',
    strategy_id: '3',
    name: 'Pairs Trading - H1 2024',
    start_date: '2024-01-01T00:00:00Z',
    end_date: '2024-06-30T23:59:59Z',
    initial_capital: 100000,
    final_capital: 105200,
    total_return: 0.052,
    annualized_return: 0.104,
    sharpe_ratio: 0.95,
    max_drawdown: -0.08,
    win_rate: 0.58,
    profit_factor: 1.4,
    status: 'completed',
    created_at: '2024-07-01T08:00:00Z',
    completed_at: '2024-07-01T08:20:00Z',
  },
  {
    id: '4',
    strategy_id: '4',
    name: 'MACD Crossover - Current',
    start_date: '2024-06-01T00:00:00Z',
    end_date: new Date().toISOString(),
    initial_capital: 100000,
    status: 'running',
    created_at: '2024-06-01T09:00:00Z',
  },
];

// Mock Market Data
export const mockMarketData = {
  tickers: ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'SPY'],
  latestPrices: [
    { symbol: 'AAPL', price: 178.45, change: 2.34, changePercent: 1.33 },
    { symbol: 'GOOGL', price: 142.56, change: -1.23, changePercent: -0.85 },
    { symbol: 'MSFT', price: 378.92, change: 5.67, changePercent: 1.52 },
    { symbol: 'AMZN', price: 145.23, change: 3.45, changePercent: 2.43 },
    { symbol: 'TSLA', price: 248.67, change: -4.56, changePercent: -1.80 },
    { symbol: 'META', price: 312.45, change: 7.89, changePercent: 2.59 },
    { symbol: 'NVDA', price: 456.78, change: 12.34, changePercent: 2.78 },
    { symbol: 'SPY', price: 445.67, change: 3.21, changePercent: 0.73 },
  ],
};

// Mock Analytics Data
export const mockAnalytics = {
  portfolioValue: 125450,
  totalReturn: 0.2545,
  sharpeRatio: 1.85,
  maxDrawdown: -0.12,
  winRate: 0.68,
  activePositions: 5,
  totalTrades: 142,
  avgTradeReturn: 0.015,
};

/**
 * Check if we should use mock data
 * Returns true if backend is unavailable or demo mode is enabled
 */
export const shouldUseMockData = (): boolean => {
  // Check if demo mode is enabled in localStorage
  const demoMode = localStorage.getItem('demoMode') === 'true';
  
  // Check if API URL is set to mock
  const apiUrl = process.env.REACT_APP_API_URL;
  const isMockApi = !apiUrl || apiUrl.includes('mock') || apiUrl === '';
  
  return demoMode || isMockApi;
};

/**
 * Simulate API delay for realistic demo
 */
export const mockDelay = (ms: number = 500): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Mock API responses that match the real API structure
 */
export const mockApi = {
  getStrategies: async (): Promise<Strategy[]> => {
    await mockDelay(800);
    return mockStrategies;
  },
  
  getMLModels: async (): Promise<MLModel[]> => {
    await mockDelay(600);
    return mockMLModels;
  },
  
  getBacktests: async (): Promise<Backtest[]> => {
    await mockDelay(700);
    return mockBacktests;
  },
  
  getMarketData: async () => {
    await mockDelay(400);
    return mockMarketData;
  },
  
  getAnalytics: async () => {
    await mockDelay(500);
    return mockAnalytics;
  },
};

