import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PerformanceChart: React.FC = () => {
  // Mock data - in real app, this would come from API
  const data = [
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

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Portfolio Performance</h3>
        <p className="text-sm text-gray-500">Last 10 days</p>
      </div>
      <div className="card-body">
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data}>
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
      </div>
    </div>
  );
};

export default PerformanceChart;
