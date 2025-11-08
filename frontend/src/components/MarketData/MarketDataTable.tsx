import React from 'react';

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

interface MarketDataTableProps {
  data: MarketData[];
}

const MarketDataTable: React.FC<MarketDataTableProps> = ({ data }) => {
  const formatCurrency = (value: number | null) => {
    if (value === null) return '—';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatVolume = (value: number | null) => {
    if (value === null) return '—';
    return new Intl.NumberFormat('en-US', {
      notation: 'compact',
      maximumFractionDigits: 1,
    }).format(value);
  };

  if (data.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No market data available</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead className="table-header">
          <tr>
            <th className="table-header-cell">Date</th>
            <th className="table-header-cell">Open</th>
            <th className="table-header-cell">High</th>
            <th className="table-header-cell">Low</th>
            <th className="table-header-cell">Close</th>
            <th className="table-header-cell">Volume</th>
            <th className="table-header-cell">Source</th>
          </tr>
        </thead>
        <tbody className="table-body">
          {data.map((row) => (
            <tr key={row.id} className="table-row">
              <td className="table-cell">
                {new Date(row.timestamp).toLocaleDateString()}
              </td>
              <td className="table-cell">
                {formatCurrency(row.open_price)}
              </td>
              <td className="table-cell">
                {formatCurrency(row.high_price)}
              </td>
              <td className="table-cell">
                {formatCurrency(row.low_price)}
              </td>
              <td className="table-cell font-medium">
                {formatCurrency(row.close_price)}
              </td>
              <td className="table-cell">
                {formatVolume(row.volume)}
              </td>
              <td className="table-cell">
                <span className="badge-gray">{row.source}</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MarketDataTable;
