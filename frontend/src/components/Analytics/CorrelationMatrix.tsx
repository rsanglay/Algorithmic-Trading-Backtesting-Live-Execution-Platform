import React from 'react';

const CorrelationMatrix: React.FC = () => {
  // Mock correlation data
  const symbols = ['SPY', 'QQQ', 'IWM', 'GLD', 'TLT'];
  const correlations = [
    [1.00, 0.85, 0.78, -0.15, -0.25],
    [0.85, 1.00, 0.72, -0.12, -0.20],
    [0.78, 0.72, 1.00, -0.08, -0.18],
    [-0.15, -0.12, -0.08, 1.00, 0.45],
    [-0.25, -0.20, -0.18, 0.45, 1.00],
  ];

  const getColorClass = (value: number) => {
    const absValue = Math.abs(value);
    if (absValue >= 0.8) return 'bg-red-100 text-red-800';
    if (absValue >= 0.6) return 'bg-orange-100 text-orange-800';
    if (absValue >= 0.4) return 'bg-yellow-100 text-yellow-800';
    if (absValue >= 0.2) return 'bg-blue-100 text-blue-800';
    return 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Correlation Matrix</h3>
        <p className="text-sm text-gray-500">Asset correlation analysis</p>
      </div>
      <div className="card-body">
        <div className="overflow-x-auto">
          <table className="table">
            <thead className="table-header">
              <tr>
                <th className="table-header-cell"></th>
                {symbols.map((symbol) => (
                  <th key={symbol} className="table-header-cell text-center">
                    {symbol}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="table-body">
              {symbols.map((symbol, rowIndex) => (
                <tr key={symbol} className="table-row">
                  <td className="table-cell font-medium">{symbol}</td>
                  {correlations[rowIndex].map((correlation, colIndex) => (
                    <td key={colIndex} className="table-cell text-center">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getColorClass(correlation)}`}>
                        {correlation.toFixed(2)}
                      </span>
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Legend */}
        <div className="mt-4 flex flex-wrap gap-2">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-red-100 rounded"></div>
            <span className="text-xs text-gray-500">High (≥0.8)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-orange-100 rounded"></div>
            <span className="text-xs text-gray-500">Medium (0.6-0.8)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-yellow-100 rounded"></div>
            <span className="text-xs text-gray-500">Low (0.4-0.6)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-100 rounded"></div>
            <span className="text-xs text-gray-500">Very Low (0.2-0.4)</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-gray-100 rounded"></div>
            <span className="text-xs text-gray-500">Minimal (<0.2)</span>
          </div>
        </div>

        {/* Insights */}
        <div className="mt-4 bg-blue-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Key Insights</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• SPY and QQQ show high correlation (0.85)</li>
            <li>• GLD and TLT have positive correlation (0.45)</li>
            <li>• Bonds (TLT) show negative correlation with stocks</li>
            <li>• Diversification benefits from GLD and TLT</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CorrelationMatrix;
