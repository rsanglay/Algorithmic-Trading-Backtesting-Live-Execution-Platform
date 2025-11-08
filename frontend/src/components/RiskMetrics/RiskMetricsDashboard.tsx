import React from 'react';
import { useGetComprehensiveRiskMetricsQuery, useGetRiskVarQuery, useGetRiskCvarQuery } from '../../store/api/api';

interface RiskMetricsDashboardProps {
  strategyId: string;
}

const RiskMetricsDashboard: React.FC<RiskMetricsDashboardProps> = ({ strategyId }) => {
  const { data: riskMetrics, isLoading } = useGetComprehensiveRiskMetricsQuery({
    strategyId,
  });
  const { data: varData } = useGetRiskVarQuery({
    strategyId,
    confidenceLevel: 0.95,
    method: 'historical',
  });
  const { data: cvarData } = useGetRiskCvarQuery({
    strategyId,
    confidenceLevel: 0.95,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  const metrics = riskMetrics?.metrics || {};

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-900">Risk Metrics Dashboard</h2>

      {/* VaR and CVaR Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Value at Risk (95%)</h3>
          </div>
          <div className="card-body">
            <p className="text-2xl font-bold text-red-600">
              ${varData?.var?.toFixed(2) || '0.00'}
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Conditional VaR (95%)</h3>
          </div>
          <div className="card-body">
            <p className="text-2xl font-bold text-red-700">
              ${cvarData?.cvar?.toFixed(2) || '0.00'}
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Maximum Drawdown</h3>
          </div>
          <div className="card-body">
            <p className="text-2xl font-bold text-red-600">
              {(metrics.max_drawdown * 100)?.toFixed(2) || '0.00'}%
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Sharpe Ratio</h3>
          </div>
          <div className="card-body">
            <p className="text-2xl font-bold text-green-600">
              {metrics.sharpe_ratio?.toFixed(2) || '0.00'}
            </p>
          </div>
        </div>
      </div>

      {/* Additional Risk Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Sortino Ratio</h3>
          </div>
          <div className="card-body">
            <p className="text-xl font-semibold">{metrics.sortino_ratio?.toFixed(2) || '0.00'}</p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Calmar Ratio</h3>
          </div>
          <div className="card-body">
            <p className="text-xl font-semibold">{metrics.calmar_ratio?.toFixed(2) || '0.00'}</p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Volatility</h3>
          </div>
          <div className="card-body">
            <p className="text-xl font-semibold">
              {(metrics.volatility * 100)?.toFixed(2) || '0.00'}%
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Beta</h3>
          </div>
          <div className="card-body">
            <p className="text-xl font-semibold">{metrics.beta?.toFixed(2) || '0.00'}</p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Alpha</h3>
          </div>
          <div className="card-body">
            <p className="text-xl font-semibold">
              {(metrics.alpha * 100)?.toFixed(2) || '0.00'}%
            </p>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h3 className="text-sm font-medium text-gray-500">Information Ratio</h3>
          </div>
          <div className="card-body">
            <p className="text-xl font-semibold">{metrics.information_ratio?.toFixed(2) || '0.00'}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskMetricsDashboard;

