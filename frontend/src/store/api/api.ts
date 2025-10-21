import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: `${API_BASE_URL}/api/v1`,
    prepareHeaders: (headers) => {
      // Add authentication headers if needed
      const token = localStorage.getItem('token');
      if (token) {
        headers.set('authorization', `Bearer ${token}`);
      }
      return headers;
    },
  }),
  tagTypes: [
    'Strategy',
    'Backtest',
    'MLModel',
    'MarketData',
    'Analytics',
    'Position',
    'Order',
  ],
  endpoints: (builder) => ({
    // Strategies
    getStrategies: builder.query({
      query: (params = {}) => ({
        url: '/strategies',
        params,
      }),
      providesTags: ['Strategy'],
    }),
    getStrategy: builder.query({
      query: (id) => `/strategies/${id}`,
      providesTags: (result, error, id) => [{ type: 'Strategy', id }],
    }),
    createStrategy: builder.mutation({
      query: (strategy) => ({
        url: '/strategies',
        method: 'POST',
        body: strategy,
      }),
      invalidatesTags: ['Strategy'],
    }),
    updateStrategy: builder.mutation({
      query: ({ id, ...strategy }) => ({
        url: `/strategies/${id}`,
        method: 'PUT',
        body: strategy,
      }),
    deleteStrategy: builder.mutation({
      query: (id) => ({
        url: `/strategies/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['Strategy'],
    }),
    activateStrategy: builder.mutation({
      query: (id) => ({
        url: `/strategies/${id}/activate`,
        method: 'POST',
      }),
      invalidatesTags: ['Strategy'],
    }),
    deactivateStrategy: builder.mutation({
      query: (id) => ({
        url: `/strategies/${id}/deactivate`,
        method: 'POST',
      }),
      invalidatesTags: ['Strategy'],
    }),

    // Backtests
    getBacktests: builder.query({
      query: (params = {}) => ({
        url: '/strategies/backtests',
        params,
      }),
      providesTags: ['Backtest'],
    }),
    getBacktest: builder.query({
      query: (id) => `/strategies/backtests/${id}`,
      providesTags: (result, error, id) => [{ type: 'Backtest', id }],
    }),
    createBacktest: builder.mutation({
      query: (backtest) => ({
        url: `/strategies/${backtest.strategy_id}/backtests`,
        method: 'POST',
        body: backtest,
      }),
      invalidatesTags: ['Backtest'],
    }),

    // ML Models
    getMLModels: builder.query({
      query: (params = {}) => ({
        url: '/ml-models',
        params,
      }),
      providesTags: ['MLModel'],
    }),
    getMLModel: builder.query({
      query: (id) => `/ml-models/${id}`,
      providesTags: (result, error, id) => [{ type: 'MLModel', id }],
    }),
    createMLModel: builder.mutation({
      query: (model) => ({
        url: '/ml-models',
        method: 'POST',
        body: model,
      }),
      invalidatesTags: ['MLModel'],
    }),
    updateMLModel: builder.mutation({
      query: ({ id, ...model }) => ({
        url: `/ml-models/${id}`,
        method: 'PUT',
        body: model,
      }),
      invalidatesTags: ['MLModel'],
    }),
    deleteMLModel: builder.mutation({
      query: (id) => ({
        url: `/ml-models/${id}`,
        method: 'DELETE',
      }),
      invalidatesTags: ['MLModel'],
    }),
    trainMLModel: builder.mutation({
      query: ({ id, trainingData }) => ({
        url: `/ml-models/${id}/train`,
        method: 'POST',
        body: trainingData,
      }),
      invalidatesTags: ['MLModel'],
    }),
    makePrediction: builder.mutation({
      query: ({ id, predictionData }) => ({
        url: `/ml-models/${id}/predict`,
        method: 'POST',
        body: predictionData,
      }),
    }),

    // Market Data
    getMarketData: builder.query({
      query: (params) => ({
        url: '/market-data/ohlcv',
        params,
      }),
      providesTags: ['MarketData'],
    }),
    getTickers: builder.query({
      query: (params = {}) => ({
        url: '/market-data/tickers',
        params,
      }),
      providesTags: ['MarketData'],
    }),
    getNewsData: builder.query({
      query: (params = {}) => ({
        url: '/market-data/news',
        params,
      }),
      providesTags: ['MarketData'],
    }),
    getTechnicalIndicators: builder.query({
      query: (params) => ({
        url: '/market-data/technical-indicators',
        params,
      }),
    }),
    syncMarketData: builder.mutation({
      query: (data) => ({
        url: '/market-data/sync',
        method: 'POST',
        body: data,
      }),
      invalidatesTags: ['MarketData'],
    }),

    // Analytics
    getStrategyPerformance: builder.query({
      query: ({ strategyId, ...params }) => ({
        url: `/analytics/performance/${strategyId}`,
        params,
      }),
    }),
    getRiskMetrics: builder.query({
      query: ({ strategyId, ...params }) => ({
        url: `/analytics/risk-metrics/${strategyId}`,
        params,
      }),
    }),
    getPortfolioAnalytics: builder.query({
      query: (params) => ({
        url: '/analytics/portfolio-analytics',
        params,
      }),
    }),
    getCorrelationMatrix: builder.query({
      query: (params) => ({
        url: '/analytics/correlation-matrix',
        params,
      }),
    }),
    getVolatilityAnalysis: builder.query({
      query: (params) => ({
        url: '/analytics/volatility-analysis',
        params,
      }),
    }),
    getDrawdownAnalysis: builder.query({
      query: ({ strategyId, ...params }) => ({
        url: `/analytics/drawdown-analysis/${strategyId}`,
        params,
      }),
    }),
    getSharpeRatio: builder.query({
      query: ({ strategyId, ...params }) => ({
        url: `/analytics/sharpe-ratio/${strategyId}`,
        params,
      }),
    }),
    calculateVaR: builder.query({
      query: (params) => ({
        url: '/analytics/var-calculation',
        params,
      }),
    }),
    stressTest: builder.query({
      query: ({ strategyId, ...params }) => ({
        url: `/analytics/stress-test/${strategyId}`,
        params,
      }),
    }),
    monteCarloSimulation: builder.query({
      query: (params) => ({
        url: '/analytics/monte-carlo-simulation',
        params,
      }),
    }),

    // Positions and Orders
    getStrategyPositions: builder.query({
      query: (strategyId) => `/strategies/${strategyId}/positions`,
      providesTags: ['Position'],
    }),
    getStrategyOrders: builder.query({
      query: ({ strategyId, ...params }) => ({
        url: `/strategies/${strategyId}/orders`,
        params,
      }),
      providesTags: ['Order'],
    }),
  }),
});

export const {
  // Strategies
  useGetStrategiesQuery,
  useGetStrategyQuery,
  useCreateStrategyMutation,
  useUpdateStrategyMutation,
  useDeleteStrategyMutation,
  useActivateStrategyMutation,
  useDeactivateStrategyMutation,

  // Backtests
  useGetBacktestsQuery,
  useGetBacktestQuery,
  useCreateBacktestMutation,

  // ML Models
  useGetMLModelsQuery,
  useGetMLModelQuery,
  useCreateMLModelMutation,
  useUpdateMLModelMutation,
  useDeleteMLModelMutation,
  useTrainMLModelMutation,
  useMakePredictionMutation,

  // Market Data
  useGetMarketDataQuery,
  useGetTickersQuery,
  useGetNewsDataQuery,
  useGetTechnicalIndicatorsQuery,
  useSyncMarketDataMutation,

  // Analytics
  useGetStrategyPerformanceQuery,
  useGetRiskMetricsQuery,
  useGetPortfolioAnalyticsQuery,
  useGetCorrelationMatrixQuery,
  useGetVolatilityAnalysisQuery,
  useGetDrawdownAnalysisQuery,
  useGetSharpeRatioQuery,
  useCalculateVaRQuery,
  useStressTestQuery,
  useMonteCarloSimulationQuery,

  // Positions and Orders
  useGetStrategyPositionsQuery,
  useGetStrategyOrdersQuery,
} = api;
