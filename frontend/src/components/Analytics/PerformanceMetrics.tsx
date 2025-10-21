import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

const PerformanceMetrics: React.FC = () => {
  // Mock performance data
  const performanceData = [
    { date: '2024-01-01', portfolio: 10000, benchmark: 10000 },
    { date: '2024-01-02', portfolio: 10150, benchmark: 10050 },
    { date: '2024-01-03', portfolio: 10200, benchmark: 10100 },
    { date: '2024-01-04', portfolio: 10180, benchmark: 10080 },
    { date: '2024-01-05', portfolio: 10300, benchmark: 10150 },
    { date: '2024-01-06', portfolio: 10250, benchmark: 10120 },
    { date: '2024-01-07', portfolio: 10400, benchmark: 10200 },
    { date: '2024-01-08', portfolio: 10350, benchmark: 10180 },
    { date: '2024-01-09', portfolio: 10500, benchmark: 10250 },
    { date: '2024-01-10', portfolio: 10450, benchmark: 10220 },
  ];

  const monthlyReturns = [
    { month: 'Jan', return: 4.5 },
    { month: 'Feb', return: -2.1 },
    { month: 'Mar', return: 3.2 },
    { month: 'Apr', return: 1.8 },
    { month: 'May', return: -0.5 },
    { month: 'Jun', return: 2.7 },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Performance Metrics</h3>
        <p className="text-sm text-gray-500">Portfolio performance over time</p>
      </div>
      <div className="card-body">
        <div className="space-y-6">
          {/* Performance Chart */}
          <div className="chart-container">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={performanceData}>
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
                    `$${value.toLocaleString()}`, 
                    name === 'portfolio' ? 'Portfolio' : 'Benchmark'
                  ]}
                />
                <Line 
                  type="monotone" 
                  dataKey="portfolio" 
                  stroke="#3B82F6" 
                  strokeWidth={2}
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="benchmark" 
                  stroke="#6B7280" 
                  strokeWidth={2}
                  strokeDasharray="5 5"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Monthly Returns */}
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-3">Monthly Returns</h4>
            <div className="chart-container" style={{ height: '200px' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthlyReturns}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Return']}
                  />
                  <Bar 
                    dataKey="return" 
                    fill="#3B82F6"
                    radius={[2, 2, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">+12.5%</p>
              <p className="text-sm text-gray-500">Total Return</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">1.85</p>
              <p className="text-sm text-gray-500">Sharpe Ratio</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-red-600">-3.2%</p>
              <p className="text-sm text-gray-500">Max Drawdown</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">68%</p>
              <p className="text-sm text-gray-500">Win Rate</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMetrics;
