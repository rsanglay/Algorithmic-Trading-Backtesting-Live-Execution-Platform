import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface MarketData {
  id: string;
  symbol: string;
  timestamp: string;
  open_price: number;
  high_price: number;
  low_price: number;
  close_price: number;
  volume: number;
  source: string;
  created_at: string;
}

interface TickerInfo {
  id: string;
  symbol: string;
  name: string;
  exchange: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  currency: string;
  is_active: string;
  created_at: string;
  updated_at?: string;
}

interface NewsData {
  id: string;
  symbol: string;
  timestamp: string;
  title: string;
  content?: string;
  source: string;
  sentiment_score?: number;
  sentiment_label?: string;
  url?: string;
  created_at: string;
}

interface MarketDataState {
  marketData: MarketData[];
  tickers: TickerInfo[];
  newsData: NewsData[];
  technicalIndicators: any[];
  realtimeData: any;
  isLoading: boolean;
  error: string | null;
}

const initialState: MarketDataState = {
  marketData: [],
  tickers: [],
  newsData: [],
  technicalIndicators: [],
  realtimeData: null,
  isLoading: false,
  error: null,
};

const marketDataSlice = createSlice({
  name: 'marketData',
  initialState,
  reducers: {
    setMarketData: (state, action: PayloadAction<MarketData[]>) => {
      state.marketData = action.payload;
    },
    setTickers: (state, action: PayloadAction<TickerInfo[]>) => {
      state.tickers = action.payload;
    },
    setNewsData: (state, action: PayloadAction<NewsData[]>) => {
      state.newsData = action.payload;
    },
    setTechnicalIndicators: (state, action: PayloadAction<any[]>) => {
      state.technicalIndicators = action.payload;
    },
    setRealtimeData: (state, action: PayloadAction<any>) => {
      state.realtimeData = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
    },
    addMarketData: (state, action: PayloadAction<MarketData>) => {
      state.marketData.push(action.payload);
    },
    updateMarketData: (state, action: PayloadAction<MarketData>) => {
      const index = state.marketData.findIndex(m => m.id === action.payload.id);
      if (index !== -1) {
        state.marketData[index] = action.payload;
      }
    },
    removeMarketData: (state, action: PayloadAction<string>) => {
      state.marketData = state.marketData.filter(m => m.id !== action.payload);
    },
  },
});

export const {
  setMarketData,
  setTickers,
  setNewsData,
  setTechnicalIndicators,
  setRealtimeData,
  setLoading,
  setError,
  addMarketData,
  updateMarketData,
  removeMarketData,
} = marketDataSlice.actions;

export default marketDataSlice.reducer;
