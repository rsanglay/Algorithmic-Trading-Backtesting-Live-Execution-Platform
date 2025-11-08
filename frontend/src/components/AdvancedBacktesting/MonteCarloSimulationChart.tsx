import React, { useMemo } from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  AreaChart,
  Area,
} from 'recharts';

interface MonteCarloSimulationChartProps {
  result: any;
}

const MonteCarloSimulationChart: React.FC<MonteCarloSimulationChartProps> = ({ result }) => {
  const { simulated_paths: simulatedPaths = [], confidence_level: confidenceLevel } = result || {};

  const chartData = useMemo(() => {
    if (!simulatedPaths || simulatedPaths.length === 0) {
      return [];
    }

    const samplePaths = simulatedPaths.slice(0, 5);
    const maxLength = Math.max(...samplePaths.map((path: number[]) => path.length));

    return Array.from({ length: maxLength }).map((_, idx) => {
      const point: Record<string, number> = { step: idx };
      samplePaths.forEach((path: number[], pathIndex: number) => {
        if (idx < path.length) {
          point[`Path ${pathIndex + 1}`] = path[idx];
        }
      });
      return point;
    });
  }, [simulatedPaths]);

  if (!result) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div>
        <h3 className="text-lg font-medium text-gray-900">Monte Carlo Simulation</h3>
        <p className="text-sm text-gray-500">
          Visualizing sample simulation paths. Confidence level: {confidenceLevel ? `${confidenceLevel * 100}%` : 'N/A'}
        </p>
      </div>

      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={320}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="step" label={{ value: 'Time Step', position: 'insideBottomRight', offset: -5 }} />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(chartData[0])
              .filter((key) => key !== 'step')
              .map((key) => (
                <Line key={key} type="monotone" dataKey={key} dot={false} strokeWidth={1.5} />
              ))}
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div className="rounded-md border border-dashed border-gray-300 p-8 text-center text-gray-500">
          Monte Carlo results will appear here once the backend completes the simulation.
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard label="Mean Final Value" value={result?.mean_final_value} prefix="$" fractionDigits={2} />
        <StatCard label="Standard Deviation" value={result?.std_final_value} prefix="$" fractionDigits={2} />
        <StatCard label="5th Percentile" value={result?.percentile_5} prefix="$" fractionDigits={2} />
        <StatCard label="95th Percentile" value={result?.percentile_95} prefix="$" fractionDigits={2} />
        <StatCard label="VaR" value={result?.var} prefix="$" fractionDigits={2} />
        <StatCard label="CVaR" value={result?.cvar} prefix="$" fractionDigits={2} />
      </div>
    </div>
  );
};

interface StatCardProps {
  label: string;
  value?: number;
  prefix?: string;
  fractionDigits?: number;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, prefix = '', fractionDigits = 2 }) => (
  <div className="border rounded-lg p-4">
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-lg font-semibold">
      {value !== undefined && value !== null ? `${prefix}${value.toFixed(fractionDigits)}` : 'N/A'}
    </p>
  </div>
);

export default MonteCarloSimulationChart;
