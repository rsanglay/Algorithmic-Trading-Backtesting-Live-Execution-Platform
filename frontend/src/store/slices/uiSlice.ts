import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface UIState {
  sidebarOpen: boolean;
  theme: 'light' | 'dark';
  notifications: any[];
  modals: {
    createStrategy: boolean;
    createBacktest: boolean;
    createMLModel: boolean;
    settings: boolean;
  };
  selectedTimeRange: string;
  selectedSymbols: string[];
  chartType: 'line' | 'candlestick' | 'bar';
  isLoading: boolean;
}

const initialState: UIState = {
  sidebarOpen: false,
  theme: 'light',
  notifications: [],
  modals: {
    createStrategy: false,
    createBacktest: false,
    createMLModel: false,
    settings: false,
  },
  selectedTimeRange: '1D',
  selectedSymbols: [],
  chartType: 'line',
  isLoading: false,
};

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    addNotification: (state, action: PayloadAction<any>) => {
      state.notifications.push(action.payload);
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    setModalOpen: (state, action: PayloadAction<{ modal: keyof UIState['modals']; open: boolean }>) => {
      state.modals[action.payload.modal] = action.payload.open;
    },
    setSelectedTimeRange: (state, action: PayloadAction<string>) => {
      state.selectedTimeRange = action.payload;
    },
    setSelectedSymbols: (state, action: PayloadAction<string[]>) => {
      state.selectedSymbols = action.payload;
    },
    setChartType: (state, action: PayloadAction<'line' | 'candlestick' | 'bar'>) => {
      state.chartType = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
  },
});

export const {
  setSidebarOpen,
  toggleSidebar,
  setTheme,
  addNotification,
  removeNotification,
  clearNotifications,
  setModalOpen,
  setSelectedTimeRange,
  setSelectedSymbols,
  setChartType,
  setLoading,
} = uiSlice.actions;

export default uiSlice.reducer;
