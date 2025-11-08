import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface MLModel {
  id: string;
  name: string;
  model_type: string;
  purpose: string;
  version: string;
  features: string[];
  target?: string;
  hyperparameters: Record<string, any>;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  mse?: number;
  mae?: number;
  model_path?: string;
  scaler_path?: string;
  feature_importance?: Record<string, number>;
  training_start_date?: string;
  training_end_date?: string;
  training_samples?: number;
  validation_samples?: number;
  is_active: boolean;
  is_training: boolean;
  status: string;
  created_at: string;
  updated_at?: string;
}

interface MLModelsState {
  models: MLModel[];
  selectedModel: MLModel | null;
  predictions: any[];
  modelPerformance: any[];
  isLoading: boolean;
  error: string | null;
}

const initialState: MLModelsState = {
  models: [],
  selectedModel: null,
  predictions: [],
  modelPerformance: [],
  isLoading: false,
  error: null,
};

const mlModelsSlice = createSlice({
  name: 'mlModels',
  initialState,
  reducers: {
    setModels: (state, action: PayloadAction<MLModel[]>) => {
      state.models = action.payload;
    },
    setSelectedModel: (state, action: PayloadAction<MLModel | null>) => {
      state.selectedModel = action.payload;
    },
    setPredictions: (state, action: PayloadAction<any[]>) => {
      state.predictions = action.payload;
    },
    setModelPerformance: (state, action: PayloadAction<any[]>) => {
      state.modelPerformance = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    addModel: (state, action: PayloadAction<MLModel>) => {
      state.models.push(action.payload);
    },
    updateModel: (state, action: PayloadAction<MLModel>) => {
      const index = state.models.findIndex(m => m.id === action.payload.id);
      if (index !== -1) {
        state.models[index] = action.payload;
      }
    },
    removeModel: (state, action: PayloadAction<string>) => {
      state.models = state.models.filter(m => m.id !== action.payload);
    },
  },
});

export const {
  setModels,
  setSelectedModel,
  setPredictions,
  setModelPerformance,
  setLoading,
  setError,
  addModel,
  updateModel,
  removeModel,
} = mlModelsSlice.actions;

export default mlModelsSlice.reducer;
