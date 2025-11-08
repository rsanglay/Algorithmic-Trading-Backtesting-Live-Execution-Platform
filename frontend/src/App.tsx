import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import { Provider } from 'react-redux';

import { store } from './store/store';
import Layout from './components/Layout/Layout';
import ProtectedRoute from './components/Auth/ProtectedRoute';
import Dashboard from './pages/Dashboard/Dashboard';
import Strategies from './pages/Strategies/Strategies';
import Backtesting from './pages/Backtesting/Backtesting';
import Analytics from './pages/Analytics/Analytics';
import MLModels from './pages/MLModels/MLModels';
import MarketData from './pages/MarketData/MarketData';
import Settings from './pages/Settings/Settings';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import RiskManagement from './pages/RiskManagement/RiskManagement';
import FactorAnalysis from './pages/FactorAnalysis/FactorAnalysis';

import './App.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <Router>
          <div className="App">
            <Routes>
              {/* Public routes */}
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              
              {/* Protected routes */}
              <Route
                path="/*"
                element={
                  <ProtectedRoute>
                    <Layout>
                      <Routes>
                        <Route path="/" element={<Dashboard />} />
                        <Route path="/strategies" element={<Strategies />} />
                        <Route path="/backtesting" element={<Backtesting />} />
                        <Route path="/analytics" element={<Analytics />} />
                        <Route path="/risk-management" element={<RiskManagement />} />
                        <Route path="/factor-analysis" element={<FactorAnalysis />} />
                        <Route path="/ml-models" element={<MLModels />} />
                        <Route path="/market-data" element={<MarketData />} />
                        <Route path="/settings" element={<Settings />} />
                      </Routes>
                    </Layout>
                  </ProtectedRoute>
                }
              />
            </Routes>
            <Toaster
              position="top-right"
              toastOptions={{
                duration: 4000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                },
                error: {
                  duration: 5000,
                },
              }}
            />
          </div>
        </Router>
      </QueryClientProvider>
    </Provider>
  );
}

export default App;
