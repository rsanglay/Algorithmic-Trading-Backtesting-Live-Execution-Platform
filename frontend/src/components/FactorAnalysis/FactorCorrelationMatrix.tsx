import React, { useMemo } from 'react';
import { useGetFactorCorrelationQuery } from '../../store/api/api';

interface FactorCorrelationMatrixProps {
  refreshToken?: number;
}

const FactorCorrelationMatrix: React.FC<FactorCorrelationMatrixProps> = ({ refreshToken }) => {
  const { data, isLoading, error, refetch } = useGetFactorCorrelationQuery(undefined);

  React.useEffect(() => {
    if (refreshToken !== undefined) {
      refetch();
    }
  }, [refreshToken, refetch]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-48">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <p className="text-sm text-red-700">Failed to load factor correlation data.</p>
      </div>
    );
  }

  const correlationMatrix: Record<string, Record<string, number>> | undefined = data?.correlation_matrix;

  if (!correlationMatrix || Object.keys(correlationMatrix).length === 0) {
    return (
      <div className="rounded-md border border-dashed border-gray-300 p-6 text-center text-gray-500">
        Factor correlation analytics will appear here once the backend provides the matrix.
      </div>
    );
  }

  const factors = Object.keys(correlationMatrix);

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Factor</th>
            {factors.map((factor) => (
              <th key={factor} className="px-4 py-2 text-xs font-medium text-gray-500 uppercase tracking-wider text-right">
                {factor}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {factors.map((rowFactor) => (
            <tr key={rowFactor}>
              <td className="px-4 py-2 text-sm font-medium text-gray-900">{rowFactor}</td>
              {factors.map((colFactor) => {
                const value = correlationMatrix[rowFactor][colFactor];
                const severity = Math.abs(value);
                const bgColor = getHeatmapColor(severity, value >= 0);
                return (
                  <td
                    key={`${rowFactor}-${colFactor}`}
                    className="px-4 py-2 text-sm text-right font-mono"
                    style={{ backgroundColor: bgColor, color: severity > 0.7 ? '#fff' : '#1f2937' }}
                  >
                    {value.toFixed(2)}
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

function getHeatmapColor(strength: number, isPositive: boolean): string {
  const intensity = Math.min(1, strength);
  if (intensity === 0) return 'transparent';

  const base = isPositive ? [59, 130, 246] : [220, 38, 38];
  const backgroundAlpha = 0.15 + 0.35 * intensity;
  return `rgba(${base[0]}, ${base[1]}, ${base[2]}, ${backgroundAlpha})`;
}

export default FactorCorrelationMatrix;
