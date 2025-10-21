import React, { useState } from 'react';
import { useGetMarketDataQuery, useGetTickersQuery } from '../../store/api/api';
import MarketDataTable from '../../components/MarketData/MarketDataTable';
import TickerSelector from '../../components/MarketData/TickerSelector';
import MarketDataChart from '../../components/MarketData/MarketDataChart';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

const MarketData: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState('SPY');
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  
  const { data: marketData, isLoading: isMarketDataLoading } = useGetMarketDataQuery({
    symbol: selectedSymbol,
    start_date: startDate,
    end_date: endDate,
  });
  
  const { data: tickers, isLoading: isTickersLoading } = useGetTickersQuery({});

  if (isMarketDataLoading || isTickersLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Market Data</h1>
        <p className="text-gray-600">Real-time and historical market data</p>
      </div>

      {/* Controls */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="form-label">Symbol</label>
              <TickerSelector
                value={selectedSymbol}
                onChange={setSelectedSymbol}
                tickers={tickers || []}
              />
            </div>
            
            <div>
              <label className="form-label">Start Date</label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="form-input"
              />
            </div>
            
            <div>
              <label className="form-label">End Date</label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="form-input"
              />
            </div>
            
            <div className="flex items-end">
              <button className="btn-primary w-full">
                <MagnifyingGlassIcon className="w-4 h-4 mr-2" />
                Load Data
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Price Chart</h3>
          <p className="text-sm text-gray-500">{selectedSymbol} - {startDate} to {endDate}</p>
        </div>
        <div className="card-body">
          <MarketDataChart data={marketData || []} />
        </div>
      </div>

      {/* Data Table */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Market Data</h3>
          <p className="text-sm text-gray-500">Historical OHLCV data</p>
        </div>
        <div className="card-body p-0">
          <MarketDataTable data={marketData || []} />
        </div>
      </div>
    </div>
  );
};

export default MarketData;
