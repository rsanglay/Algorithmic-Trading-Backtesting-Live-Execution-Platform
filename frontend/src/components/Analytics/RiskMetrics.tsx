import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const RiskMetrics: React.FC = () => {
  // Mock risk data
  const drawdownData = [
    { date: '2024-01-01', drawdown: 0 },
    { date: '2024-01-02', drawdown: -0.5 },
    { date: '2024-01-03', drawdown: -1.2 },
    { date: '2024-01-04', drawdown: -0.8 },
    { date: '2024-01-05', drawdown: -2.1 },
    { date: '2024-01-06', drawdown: -1.5 },
    { date: '2024-01-07', drawdown: -0.3 },
    { date: '2024-01-08', drawdown: -1.8 },
    { date: '2024-01-09', drawdown: -0.9 },
    { date: '2024-01-10', drawdown: -0.2 },
  ];

  const volatilityData = [
    { period: '1D', volatility: 0.8 },
    { period: '1W', volatility: 1.2 },
    { period: '1M', volatility: 1.5 },
    { period: '3M', volatility: 1.8 },
    { period: '6M', volatility: 2.1 },
    { period: '1Y', volatility: 2.3 },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Risk Metrics</h3>
        <p className="text-sm text-gray-500">Portfolio risk analysis</p>
      </div>
      <div className="card-body">
        <div className="space-y-6">
          {/* Drawdown Chart */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Drawdown Analysis</h4>
            <div className="chart-container" style={{ height: '200px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={drawdownData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value) => [`${value}%`, 'Drawdown']}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="drawdown" 
                    stroke="#EF4444" 
                    fill="#FEE2E2"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Volatility Analysis */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Volatility by Period</h4>
            <div className="space-y-2">
              {volatilityData.map((item) => (
                <div key={item.period} className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">{item.period}</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${(item.volatility / 3) * 100}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-medium text-gray-900">
                      {item.volatility}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">-3.2%</p>
              <p className="text-sm text-gray-500">Max Drawdown</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">2.3%</p>
              <p className="text-sm text-gray-500">Volatility</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">-1.8%</p>
              <p className="text-sm text-gray-500">VaR (95%)</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">0.85</p>
              <p className="text-sm text-gray-500">Beta</p>
            </div>
          </div>

          {/* Risk Assessment */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-gray-900 mb-2">Risk Assessment</h4>
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Overall Risk Level</span>
                <span className="badge-warning">Medium</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Diversification</span>
                <span className="badge-success">Good</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">Correlation Risk</span>
                <span className="badge-info">Low</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default RiskMetrics;
