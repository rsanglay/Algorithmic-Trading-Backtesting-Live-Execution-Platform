import { configureStore } from '@reduxjs/toolkit';
import { setupListeners } from '@reduxjs/toolkit/query';

import { api } from './api/api';
import strategiesReducer from './slices/strategiesSlice';
import backtestingReducer from './slices/backtestingSlice';
import analyticsReducer from './slices/analyticsSlice';
import mlModelsReducer from './slices/mlModelsSlice';
import marketDataReducer from './slices/marketDataSlice';
import uiReducer from './slices/uiSlice';

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    strategies: strategiesReducer,
    backtesting: backtestingReducer,
    analytics: analyticsReducer,
    mlModels: mlModelsReducer,
    marketData: marketDataReducer,
    ui: uiReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [api.util.resetApiState.type],
      },
    }).concat(api.middleware),
  devTools: process.env.NODE_ENV !== 'production',
});

setupListeners(store.dispatch);

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
