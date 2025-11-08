import React, { useState } from 'react';
import RiskMetricsDashboard from '../../components/RiskMetrics/RiskMetricsDashboard';
import StressTestPanel from '../../components/RiskMetrics/StressTestPanel';
import { useGetStrategiesQuery } from '../../store/api/api';
import { Strategy } from '../../store/slices/strategiesSlice';

const RiskManagement: React.FC = () => {
  const { data: strategies, isLoading } = useGetStrategiesQuery({ limit: 100 });
  const [selectedStrategyId, setSelectedStrategyId] = useState<string>('');

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Risk Management</h1>
          <p className="text-gray-600">Quantify downside risk, monitor drawdowns, and run scenario analysis.</p>
        </div>
      </div>

      {/* Strategy Selector */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-medium text-gray-900">Select Strategy</h2>
          <p className="text-sm text-gray-500">
            Choose the strategy you want to analyze. Metrics will update automatically.
          </p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
            <select
              value={selectedStrategyId}
              onChange={(e) => setSelectedStrategyId(e.target.value)}
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            >
              <option value="">Select a strategy...</option>
              {strategies?.map((strategy: Strategy) => (
                <option key={strategy.id} value={strategy.id}>
                  {strategy.name}
                </option>
              ))}
            </select>
            {isLoading && (
              <span className="text-sm text-gray-500">Loading strategies...</span>
            )}
          </div>
          {!selectedStrategyId && (
            <p className="mt-2 text-sm text-gray-500">
              Tip: set up dashboards per strategy to tailor risk views for each portfolio or client.
            </p>
          )}
        </div>
      </div>

      {/* Risk Metrics Dashboard */}
      {selectedStrategyId ? (
        <RiskMetricsDashboard strategyId={selectedStrategyId} />
      ) : (
        <div className="rounded-md border border-dashed border-gray-300 p-8 text-center text-gray-500">
          Select a strategy to load VaR, CVaR, drawdown, and factor-adjusted metrics.
        </div>
      )}

      {/* Stress Test */}
      {selectedStrategyId && <StressTestPanel strategyId={selectedStrategyId} />}
    </div>
  );
};

export default RiskManagement;

