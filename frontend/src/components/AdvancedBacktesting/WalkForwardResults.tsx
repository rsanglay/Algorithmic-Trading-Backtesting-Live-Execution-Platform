import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface WalkForwardResultsProps {
  results: any;
}

const WalkForwardResults: React.FC<WalkForwardResultsProps> = ({ results }) => {
  if (!results || !results.walk_forward_results) {
    return (
      <div className="text-center text-gray-500 py-8">
        No walk-forward results available
      </div>
    );
  }

  const chartData = results.walk_forward_results.map((result: any, index: number) => ({
    period: `Period ${index + 1}`,
    inSample: result.metrics?.sharpe_ratio || 0,
    outOfSample: result.metrics?.sharpe_ratio || 0,
    return: (result.metrics?.annualized_return * 100) || 0,
  }));

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Walk-Forward Analysis Results</h3>

      {/* Summary */}
      {results.summary && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="card">
            <div className="card-header">
              <h4 className="text-sm font-medium text-gray-500">Avg Return</h4>
            </div>
            <div className="card-body">
              <p className="text-xl font-semibold">
                {(results.summary.avg_return * 100)?.toFixed(2) || '0.00'}%
              </p>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h4 className="text-sm font-medium text-gray-500">Avg Sharpe</h4>
            </div>
            <div className="card-body">
              <p className="text-xl font-semibold">
                {results.summary.avg_sharpe?.toFixed(2) || '0.00'}
              </p>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h4 className="text-sm font-medium text-gray-500">Consistency</h4>
            </div>
            <div className="card-body">
              <p className="text-xl font-semibold">
                {(results.summary.consistency * 100)?.toFixed(1) || '0.0'}%
              </p>
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <h4 className="text-sm font-medium text-gray-500">Avg Max DD</h4>
            </div>
            <div className="card-body">
              <p className="text-xl font-semibold text-red-600">
                {(results.summary.avg_max_drawdown * 100)?.toFixed(2) || '0.00'}%
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Performance Chart */}
      <div className="card">
        <div className="card-header">
          <h4 className="text-sm font-medium text-gray-500">Period Performance</h4>
        </div>
        <div className="card-body">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="period" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="return" stroke="#3B82F6" name="Return %" />
              <Line type="monotone" dataKey="inSample" stroke="#10B981" name="Sharpe Ratio" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default WalkForwardResults;

