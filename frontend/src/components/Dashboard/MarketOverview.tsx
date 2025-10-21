import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MarketOverview: React.FC = () => {
  // Mock market data
  const marketData = [
    { symbol: 'SPY', price: 445.50, change: 2.15, changePercent: 0.48 },
    { symbol: 'QQQ', price: 378.20, change: -1.80, changePercent: -0.47 },
    { symbol: 'IWM', price: 198.75, change: 0.95, changePercent: 0.48 },
    { symbol: 'GLD', price: 185.30, change: -0.45, changePercent: -0.24 },
  ];

  const chartData = [
    { time: '09:30', SPY: 443.50, QQQ: 380.20 },
    { time: '10:00', SPY: 444.20, QQQ: 379.80 },
    { time: '10:30', SPY: 445.10, QQQ: 378.90 },
    { time: '11:00', SPY: 444.80, QQQ: 378.50 },
    { time: '11:30', SPY: 445.30, QQQ: 378.20 },
    { time: '12:00', SPY: 445.50, QQQ: 378.20 },
  ];

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Market Overview</h3>
        <p className="text-sm text-gray-500">Real-time market data</p>
      </div>
      <div className="card-body">
        {/* Market Data Table */}
        <div className="mb-6">
          <div className="overflow-hidden">
            <table className="table">
              <thead className="table-header">
                <tr>
                  <th className="table-header-cell">Symbol</th>
                  <th className="table-header-cell">Price</th>
                  <th className="table-header-cell">Change</th>
                  <th className="table-header-cell">%</th>
                </tr>
              </thead>
              <tbody className="table-body">
                {marketData.map((item) => (
                  <tr key={item.symbol} className="table-row">
                    <td className="table-cell font-medium">{item.symbol}</td>
                    <td className="table-cell">${item.price.toFixed(2)}</td>
                    <td className={`table-cell ${item.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {item.change >= 0 ? '+' : ''}{item.change.toFixed(2)}
                    </td>
                    <td className={`table-cell ${item.changePercent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {item.changePercent >= 0 ? '+' : ''}{item.changePercent.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Price Chart */}
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip 
                formatter={(value, name) => [
                  `$${value}`, 
                  name === 'SPY' ? 'SPY' : 'QQQ'
                ]}
              />
              <Line 
                type="monotone" 
                dataKey="SPY" 
                stroke="#3B82F6" 
                strokeWidth={2}
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="QQQ" 
                stroke="#10B981" 
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default MarketOverview;
