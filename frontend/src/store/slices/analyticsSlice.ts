import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface AnalyticsState {
  performanceData: any;
  riskMetrics: any;
  portfolioAnalytics: any;
  correlationMatrix: any;
  volatilityAnalysis: any;
  drawdownAnalysis: any;
  sharpeRatio: any;
  varCalculation: any;
  stressTestResults: any;
  monteCarloResults: any;
  isLoading: boolean;
  error: string | null;
}

const initialState: AnalyticsState = {
  performanceData: null,
  riskMetrics: null,
  portfolioAnalytics: null,
  correlationMatrix: null,
  volatilityAnalysis: null,
  drawdownAnalysis: null,
  sharpeRatio: null,
  varCalculation: null,
  stressTestResults: null,
  monteCarloResults: null,
  isLoading: false,
  error: null,
};

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    setPerformanceData: (state, action: PayloadAction<any>) => {
      state.performanceData = action.payload;
    },
    setRiskMetrics: (state, action: PayloadAction<any>) => {
      state.riskMetrics = action.payload;
    },
    setPortfolioAnalytics: (state, action: PayloadAction<any>) => {
      state.portfolioAnalytics = action.payload;
    },
    setCorrelationMatrix: (state, action: PayloadAction<any>) => {
      state.correlationMatrix = action.payload;
    },
    setVolatilityAnalysis: (state, action: PayloadAction<any>) => {
      state.volatilityAnalysis = action.payload;
    },
    setDrawdownAnalysis: (state, action: PayloadAction<any>) => {
      state.drawdownAnalysis = action.payload;
    },
    setSharpeRatio: (state, action: PayloadAction<any>) => {
      state.sharpeRatio = action.payload;
    },
    setVarCalculation: (state, action: PayloadAction<any>) => {
      state.varCalculation = action.payload;
    },
    setStressTestResults: (state, action: PayloadAction<any>) => {
      state.stressTestResults = action.payload;
    },
    setMonteCarloResults: (state, action: PayloadAction<any>) => {
      state.monteCarloResults = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
  },
});

export const {
  setPerformanceData,
  setRiskMetrics,
  setPortfolioAnalytics,
  setCorrelationMatrix,
  setVolatilityAnalysis,
  setDrawdownAnalysis,
  setSharpeRatio,
  setVarCalculation,
  setStressTestResults,
  setMonteCarloResults,
  setLoading,
  setError,
} = analyticsSlice.actions;

export default analyticsSlice.reducer;
