import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface Strategy {
  id: string;
  name: string;
  description: string;
  strategy_type: string;
  code: string;
  parameters: Record<string, any>;
  is_active: boolean;
  is_live: boolean;
  created_by: string;
  created_at: string;
  updated_at?: string;
}

interface StrategiesState {
  strategies: Strategy[];
  selectedStrategy: Strategy | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: StrategiesState = {
  strategies: [],
  selectedStrategy: null,
  isLoading: false,
  error: null,
};

const strategiesSlice = createSlice({
  name: 'strategies',
  initialState,
  reducers: {
    setStrategies: (state, action: PayloadAction<Strategy[]>) => {
      state.strategies = action.payload;
    },
    setSelectedStrategy: (state, action: PayloadAction<Strategy | null>) => {
      state.selectedStrategy = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    addStrategy: (state, action: PayloadAction<Strategy>) => {
      state.strategies.push(action.payload);
    },
    updateStrategy: (state, action: PayloadAction<Strategy>) => {
      const index = state.strategies.findIndex(s => s.id === action.payload.id);
      if (index !== -1) {
        state.strategies[index] = action.payload;
      }
    },
    removeStrategy: (state, action: PayloadAction<string>) => {
      state.strategies = state.strategies.filter(s => s.id !== action.payload);
    },
  },
});

export const {
  setStrategies,
  setSelectedStrategy,
  setLoading,
  setError,
  addStrategy,
  updateStrategy,
  removeStrategy,
} = strategiesSlice.actions;

export default strategiesSlice.reducer;
