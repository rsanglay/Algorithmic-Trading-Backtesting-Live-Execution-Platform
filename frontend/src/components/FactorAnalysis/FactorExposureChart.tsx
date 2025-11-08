import React from 'react';
import { useGetFactorExposureQuery } from '../../store/api/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';

interface FactorExposureChartProps {
  portfolioId: string;
}

const FactorExposureChart: React.FC<FactorExposureChartProps> = ({ portfolioId }) => {
  const { data: exposureData, isLoading } = useGetFactorExposureQuery(portfolioId);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  // Mock data structure - replace with actual data when backend is ready
  const exposureChartData = [
    { factor: 'Market', exposure: exposureData?.market_beta || 1.0 },
    { factor: 'SMB', exposure: exposureData?.smb_beta || 0.0 },
    { factor: 'HML', exposure: exposureData?.hml_beta || 0.0 },
    { factor: 'RMW', exposure: exposureData?.rmw_beta || 0.0 },
    { factor: 'CMA', exposure: exposureData?.cma_beta || 0.0 },
  ];

  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-medium text-gray-900">Factor Exposures</h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={exposureChartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="factor" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey="exposure" fill="#3B82F6">
            {exposureChartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default FactorExposureChart;

