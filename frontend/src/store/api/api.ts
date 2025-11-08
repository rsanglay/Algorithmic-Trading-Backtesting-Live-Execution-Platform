import { createApi, fetchBaseQuery, FetchBaseQueryError } from '@reduxjs/toolkit/query/react';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const rawBaseQuery = fetchBaseQuery({
  baseUrl: `${API_BASE_URL}/api/v1`,
  prepareHeaders: (headers) => {
    const token = localStorage.getItem('token');
    if (token) {
      headers.set('authorization', `Bearer ${token}`);
    }
    return headers;
  },
});

const baseQueryWithRefresh: typeof rawBaseQuery = async (args, api, extraOptions) => {
  let result = await rawBaseQuery(args, api, extraOptions);
  if (result.error && (result.error as FetchBaseQueryError)?.status === 401) {
    const refreshToken = localStorage.getItem('refreshToken');
    if (refreshToken) {
      const refreshResult = await rawBaseQuery(
        {
          url: '/auth/refresh',
          method: 'POST',
          body: { refresh_token: refreshToken },
        },
        api,
        extraOptions
      );

      if (!refreshResult.error && refreshResult.data) {
        const data: any = refreshResult.data;
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('refreshToken', data.refresh_token);
        if (data.user) {
          localStorage.setItem('user', JSON.stringify(data.user));
        }
        result = await rawBaseQuery(args, api, extraOptions);
      } else {
        localStorage.removeItem('token');
        localStorage.removeItem('refreshToken');
        localStorage.removeItem('user');
      }
    }
  }
  return result;
};

export const api = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithRefresh,
  tagTypes: [
    'Strategy',
    'Backtest',
    'MLModel',
    'MarketData',
    'Analytics',
    'Position',
    'Order',
    'User',
  ],
  endpoints: (builder) => ({
    // Authentication
    register: builder.mutation({
      query: (userData) => ({
        url: '/auth/register',
        method: 'POST',
        body: userData,
      }),
    }),
    login: builder.mutation({
      query: (credentials) => ({
        url: '/auth/login',
        method: 'POST',
        body: credentials,
      }),
    }),
    refreshToken: builder.mutation({
      query: (refreshToken: string) => ({
        url: '/auth/refresh',
        method: 'POST',
        body: { refresh_token: refreshToken },
      }),
    }),
    getCurrentUser: builder.query({
      query: () => ({
        url: '/auth/me',
      }),
      providesTags: ['User'],
    }),
    updateUserPreferences: builder.mutation({
      query: (preferences) => ({
        url: '/auth/me/preferences',
        method: 'PUT',
        body: preferences,
      }),
      invalidatesTags: ['User'],
    }),
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
      invalidatesTags: ['Strategy'],
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
    fetchYFinanceData: builder.query({
      query: ({ symbol, period = '1y', interval = '1d' }) => ({
        url: `/market-data/fetch/${symbol}`,
        params: { period, interval },
      }),
      providesTags: ['MarketData'],
    }),
    getRealtimeData: builder.query({
      query: (symbol) => ({
        url: `/market-data/realtime/${symbol}`,
      }),
      providesTags: ['MarketData'],
    }),
    searchInstruments: builder.query({
      query: ({ query, category }) => ({
        url: '/market-data/search',
        params: { query, category },
      }),
    }),
    getInstrumentCategories: builder.query({
      query: () => ({
        url: '/market-data/categories',
      }),
    }),

    // Advanced Backtesting
    runWalkForwardAnalysis: builder.mutation({
      query: ({ strategyId, trainPeriod, testPeriod, step }) => ({
        url: '/advanced-backtesting/walk-forward',
        method: 'POST',
        params: { strategy_id: strategyId, train_period: trainPeriod, test_period: testPeriod, step },
      }),
    }),
    runMonteCarloSimulation: builder.mutation({
      query: ({ strategyId, nSimulations, nPeriods, confidenceLevel }) => ({
        url: '/advanced-backtesting/monte-carlo',
        method: 'POST',
        params: { strategy_id: strategyId, n_simulations: nSimulations, n_periods: nPeriods, confidence_level: confidenceLevel },
      }),
    }),
    getAdvancedMetrics: builder.query({
      query: (backtestId) => ({
        url: `/advanced-backtesting/metrics/${backtestId}`,
      }),
    }),

    // Factor Analysis
    getFamaFrench3Factor: builder.query({
      query: ({ portfolioId, startDate, endDate }) => ({
        url: '/factors/fama-french-3',
        params: { portfolio_id: portfolioId, start_date: startDate, end_date: endDate },
      }),
    }),
    getFamaFrench5Factor: builder.query({
      query: ({ portfolioId, startDate, endDate }) => ({
        url: '/factors/fama-french-5',
        params: { portfolio_id: portfolioId, start_date: startDate, end_date: endDate },
      }),
    }),
    getFactorExposure: builder.query({
      query: (portfolioId) => ({
        url: '/factors/exposure',
        params: { portfolio_id: portfolioId },
      }),
    }),
    getFactorAttribution: builder.query({
      query: ({ portfolioId, startDate, endDate }) => ({
        url: '/factors/attribution',
        params: { portfolio_id: portfolioId, start_date: startDate, end_date: endDate },
      }),
    }),
    getFactorCorrelation: builder.query({
      query: () => ({
        url: '/factors/correlation',
      }),
    }),

    // Risk Metrics (New)
    getRiskVar: builder.query({
      query: ({ strategyId, confidenceLevel, method }) => ({
        url: `/risk/var/${strategyId}`,
        params: { confidence_level: confidenceLevel, method },
      }),
    }),
    getRiskCvar: builder.query({
      query: ({ strategyId, confidenceLevel }) => ({
        url: `/risk/cvar/${strategyId}`,
        params: { confidence_level: confidenceLevel },
      }),
    }),
    getComprehensiveRiskMetrics: builder.query({
      query: ({ strategyId, startDate, endDate }) => ({
        url: `/risk/metrics/${strategyId}`,
        params: { start_date: startDate, end_date: endDate },
      }),
    }),
    runRiskStressTest: builder.mutation({
      query: ({ strategyId, scenario }) => ({
        url: `/risk/stress-test/${strategyId}`,
        method: 'GET',
        params: { scenario },
      }),
    }),

    // Strategy Templates
    getStrategyTemplates: builder.query({
      query: () => ({
        url: '/strategy-templates',
      }),
    }),
    getStrategyTemplate: builder.query({
      query: (templateId) => ({
        url: `/strategy-templates/${templateId}`,
      }),
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
  // Auth
  useRegisterMutation,
  useLoginMutation,
  useRefreshTokenMutation,
  useGetCurrentUserQuery,
  useUpdateUserPreferencesMutation,

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
  useFetchYFinanceDataQuery,
  useGetRealtimeDataQuery,
  useSearchInstrumentsQuery,
  useGetInstrumentCategoriesQuery,

  // Advanced Backtesting
  useRunWalkForwardAnalysisMutation,
  useRunMonteCarloSimulationMutation,
  useGetAdvancedMetricsQuery,

  // Factor Analysis
  useGetFamaFrench3FactorQuery,
  useGetFamaFrench5FactorQuery,
  useGetFactorExposureQuery,
  useGetFactorAttributionQuery,
  useGetFactorCorrelationQuery,

  // Risk Metrics (New)
  useGetRiskVarQuery,
  useGetRiskCvarQuery,
  useGetComprehensiveRiskMetricsQuery,
  useRunRiskStressTestMutation,

  // Strategy Templates
  useGetStrategyTemplatesQuery,
  useGetStrategyTemplateQuery,

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
