import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface MarketData {
  id: string;
  symbol: string;
  timestamp: string;
  open_price: number | null;
  high_price: number | null;
  low_price: number | null;
  close_price: number | null;
  volume: number | null;
  source: string;
  created_at: string;
}

interface MarketDataChartProps {
  data: MarketData[];
}

const MarketDataChart: React.FC<MarketDataChartProps> = ({ data }) => {
  // Transform data for chart
  const chartData = data
    .filter(item => item.close_price !== null)
    .map(item => ({
      date: item.timestamp,
      open: item.open_price,
      high: item.high_price,
      low: item.low_price,
      close: item.close_price,
      volume: item.volume,
    }));

  if (chartData.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No data available for chart</p>
      </div>
    );
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => new Date(value).toLocaleDateString()}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `$${value}`}
          />
          <Tooltip 
            labelFormatter={(value) => new Date(value).toLocaleDateString()}
            formatter={(value, name) => [
              `$${value}`, 
              name === 'close' ? 'Close' : 
              name === 'open' ? 'Open' : 
              name === 'high' ? 'High' : 
              name === 'low' ? 'Low' : name
            ]}
          />
          <Line 
            type="monotone" 
            dataKey="close" 
            stroke="#3B82F6" 
            strokeWidth={2}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="open" 
            stroke="#10B981" 
            strokeWidth={1}
            strokeDasharray="5 5"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MarketDataChart;
