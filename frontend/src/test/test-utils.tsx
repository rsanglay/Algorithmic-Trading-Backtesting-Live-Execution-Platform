import React, { ReactElement } from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { Provider } from 'react-redux';
import { configureStore, PreloadedState } from '@reduxjs/toolkit';
import { MemoryRouter } from 'react-router-dom';

import { api } from '../store/api/api';
import strategiesReducer from '../store/slices/strategiesSlice';
import backtestingReducer from '../store/slices/backtestingSlice';
import analyticsReducer from '../store/slices/analyticsSlice';
import mlModelsReducer from '../store/slices/mlModelsSlice';
import marketDataReducer from '../store/slices/marketDataSlice';
import uiReducer from '../store/slices/uiSlice';
import type { RootState } from '../store/store';

const createTestStore = (preloadedState?: PreloadedState<RootState>) =>
  configureStore({
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
        serializableCheck: false,
      }).concat(api.middleware),
    preloadedState,
    devTools: false,
  });

type AppStore = ReturnType<typeof createTestStore>;

interface RenderOptionsWithStore extends Omit<RenderOptions, 'queries'> {
  preloadedState?: PreloadedState<RootState>;
  store?: AppStore;
  route?: string;
}

export function renderWithProviders(
  ui: ReactElement,
  { preloadedState, store = createTestStore(preloadedState), route = '/', ...renderOptions }: RenderOptionsWithStore = {}
) {
  const Wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <Provider store={store}>
      <MemoryRouter initialEntries={[route]}>{children}</MemoryRouter>
    </Provider>
  );

  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) };
}
