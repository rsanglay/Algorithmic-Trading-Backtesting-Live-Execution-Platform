import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Backtest {
  id: string;
  strategy_id: string;
  name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital?: number;
  total_return?: number;
  annualized_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  profit_factor?: number;
  metrics?: Record<string, any>;
  trades?: any[];
  status: string;
  created_at: string;
  completed_at?: string;
}

interface BacktestingState {
  backtests: Backtest[];
  selectedBacktest: Backtest | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: BacktestingState = {
  backtests: [],
  selectedBacktest: null,
  isLoading: false,
  error: null,
};

const backtestingSlice = createSlice({
  name: 'backtesting',
  initialState,
  reducers: {
    setBacktests: (state, action: PayloadAction<Backtest[]>) => {
      state.backtests = action.payload;
    },
    setSelectedBacktest: (state, action: PayloadAction<Backtest | null>) => {
      state.selectedBacktest = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    addBacktest: (state, action: PayloadAction<Backtest>) => {
      state.backtests.push(action.payload);
    },
    updateBacktest: (state, action: PayloadAction<Backtest>) => {
      const index = state.backtests.findIndex(b => b.id === action.payload.id);
      if (index !== -1) {
        state.backtests[index] = action.payload;
      }
    },
    removeBacktest: (state, action: PayloadAction<string>) => {
      state.backtests = state.backtests.filter(b => b.id !== action.payload);
    },
  },
});

export const {
  setBacktests,
  setSelectedBacktest,
  setLoading,
  setError,
  addBacktest,
  updateBacktest,
  removeBacktest,
} = backtestingSlice.actions;

export default backtestingSlice.reducer;
