import React from 'react';
import { useGetStrategiesQuery } from '../../store/api/api';
import PerformanceMetrics from '../../components/Analytics/PerformanceMetrics';
import RiskMetrics from '../../components/Analytics/RiskMetrics';
import CorrelationMatrix from '../../components/Analytics/CorrelationMatrix';
import VolatilityAnalysis from '../../components/Analytics/VolatilityAnalysis';

const Analytics: React.FC = () => {
  const { data: strategies, isLoading } = useGetStrategiesQuery({});

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-gray-600">Comprehensive analysis of your trading strategies</p>
      </div>

      {/* Performance Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PerformanceMetrics />
        <RiskMetrics />
      </div>

      {/* Correlation and Volatility */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CorrelationMatrix />
        <VolatilityAnalysis />
      </div>

      {/* Additional Analytics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Portfolio Overview</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Total Strategies</span>
                <span className="text-sm font-medium text-gray-900">{strategies?.length || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Active Strategies</span>
                <span className="text-sm font-medium text-gray-900">
                  {strategies?.filter(s => s.is_active).length || 0}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Live Strategies</span>
                <span className="text-sm font-medium text-gray-900">
                  {strategies?.filter(s => s.is_live).length || 0}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Risk Assessment</h3>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Overall Risk</span>
                <span className="badge-warning">Medium</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Diversification</span>
                <span className="badge-success">Good</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Correlation</span>
                <span className="badge-info">Low</span>
              </div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
          </div>
          <div className="card-body">
            <div className="space-y-2">
              <button className="w-full btn-outline text-sm">
                Run Stress Test
              </button>
              <button className="w-full btn-outline text-sm">
                Monte Carlo Simulation
              </button>
              <button className="w-full btn-outline text-sm">
                Generate Report
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
