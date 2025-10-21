import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

const VolatilityAnalysis: React.FC = () => {
  // Mock volatility data
  const volatilityData = [
    { date: '2024-01-01', volatility: 1.2, vix: 18.5 },
    { date: '2024-01-02', volatility: 1.5, vix: 19.2 },
    { date: '2024-01-03', volatility: 1.8, vix: 21.1 },
    { date: '2024-01-04', volatility: 1.6, vix: 20.3 },
    { date: '2024-01-05', volatility: 2.1, vix: 22.8 },
    { date: '2024-01-06', volatility: 1.9, vix: 21.5 },
    { date: '2024-01-07', volatility: 1.7, vix: 20.1 },
    { date: '2024-01-08', volatility: 1.4, vix: 19.8 },
    { date: '2024-01-09', volatility: 1.3, vix: 18.9 },
    { date: '2024-01-10', volatility: 1.1, vix: 17.5 },
  ];

  const volatilityByPeriod = [
    { period: '1D', volatility: 1.1, percentile: 25 },
    { period: '1W', volatility: 1.3, percentile: 35 },
    { period: '1M', volatility: 1.8, percentile: 60 },
    { period: '3M', volatility: 2.1, percentile: 75 },
    { period: '6M', volatility: 2.3, percentile: 85 },
    { period: '1Y', volatility: 2.5, percentile: 90 },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Volatility Analysis</h3>
        <p className="text-sm text-gray-500">Market volatility trends</p>
      </div>
      <div className="card-body">
        <div className="space-y-6">
          {/* Volatility Chart */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Volatility Over Time</h4>
            <div className="chart-container" style={{ height: '200px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={volatilityData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => new Date(value).toLocaleDateString()}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString()}
                    formatter={(value, name) => [
                      `${value}%`, 
                      name === 'volatility' ? 'Portfolio Volatility' : 'VIX'
                    ]}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="volatility" 
                    stroke="#3B82F6" 
                    fill="#DBEAFE"
                    strokeWidth={2}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="vix" 
                    stroke="#EF4444" 
                    strokeWidth={2}
                    dot={false}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Volatility by Period */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Volatility by Period</h4>
            <div className="space-y-3">
              {volatilityByPeriod.map((item) => (
                <div key={item.period} className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-sm font-medium text-gray-900 w-8">
                      {item.period}
                    </span>
                    <div className="w-32 bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-blue-600 h-2 rounded-full" 
                        style={{ width: `${item.percentile}%` }}
                      ></div>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-sm font-medium text-gray-900">
                      {item.volatility}%
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      ({item.percentile}th percentile)
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Volatility Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">2.3%</p>
              <p className="text-sm text-gray-500">Current Volatility</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">1.8%</p>
              <p className="text-sm text-gray-500">Average Volatility</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-orange-600">3.2%</p>
              <p className="text-sm text-gray-500">Max Volatility</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">0.9%</p>
              <p className="text-sm text-gray-500">Min Volatility</p>
            </div>
          </div>

          {/* Volatility Insights */}
          <div className="bg-yellow-50 rounded-lg p-4">
            <h4 className="text-sm font-medium text-yellow-900 mb-2">Volatility Insights</h4>
            <ul className="text-sm text-yellow-800 space-y-1">
              <li>• Current volatility is above average</li>
              <li>• VIX correlation: 0.78</li>
              <li>• Volatility clustering detected</li>
              <li>• Consider hedging strategies</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VolatilityAnalysis;
