import React, { useState } from 'react';
import { useFetchYFinanceDataQuery, useGetRealtimeDataQuery } from '../../store/api/api';
import MarketDataTable from '../../components/MarketData/MarketDataTable';
import InstrumentSelector from '../../components/MarketData/InstrumentSelector';
import MarketDataChart from '../../components/MarketData/MarketDataChart';
import { MagnifyingGlassIcon, ArrowTrendingUpIcon, ArrowTrendingDownIcon } from '@heroicons/react/24/outline';

interface Instrument {
  symbol: string;
  name: string;
  exchange?: string;
  sector?: string;
  category: string;
}

const MarketData: React.FC = () => {
  const [selectedInstrument, setSelectedInstrument] = useState<Instrument | null>({
    symbol: 'AAPL',
    name: 'Apple Inc.',
    category: 'stocks'
  });
  const [period, setPeriod] = useState('1y');
  const [interval, setInterval] = useState('1d');
  
  const { data: yfinanceData, isLoading: isDataLoading, refetch } = useFetchYFinanceDataQuery(
    {
      symbol: selectedInstrument?.symbol || 'AAPL',
      period,
      interval,
    },
    { skip: !selectedInstrument }
  );
  
  const { data: realtimeData, isLoading: isRealtimeLoading } = useGetRealtimeDataQuery(
    selectedInstrument?.symbol || 'AAPL',
    { skip: !selectedInstrument, pollingInterval: 30000 } // Poll every 30 seconds
  );

  const handleInstrumentSelect = (instrument: Instrument) => {
    setSelectedInstrument(instrument);
  };

  const rawSeries = yfinanceData?.data || [];
  const toNumber = (value: any) => {
    const num = Number(value);
    return Number.isFinite(num) ? num : null;
  };
  const marketData = rawSeries.map((row: any, index: number) => {
    const timestamp = row.timestamp || row.date || row.Date;
    return {
      id: `${selectedInstrument?.symbol || 'instrument'}-${timestamp || index}`,
      symbol: selectedInstrument?.symbol || '',
      timestamp: timestamp ? new Date(timestamp).toISOString() : new Date().toISOString(),
      open_price: toNumber(row.open ?? row.Open ?? row.open_price),
      high_price: toNumber(row.high ?? row.High ?? row.high_price),
      low_price: toNumber(row.low ?? row.Low ?? row.low_price),
      close_price: toNumber(row.close ?? row.Close ?? row.close_price),
      volume: toNumber(row.volume ?? row.Volume ?? row.volume_price),
      source: row.source || (yfinanceData?.note ? 'cache' : 'yfinance'),
      created_at: new Date().toISOString(),
    };
  });
  const hasError = yfinanceData?.error || realtimeData?.error;

  if (isDataLoading && !yfinanceData && !hasError) {
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
        <p className="text-gray-600">Real-time and historical market data from Yahoo Finance</p>
      </div>

      {/* Real-time Quote */}
      {realtimeData && !realtimeData.error && (
        <div className="card bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="card-body">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-gray-900">{realtimeData.symbol}</h3>
                <p className="text-sm text-gray-600">{realtimeData.name}</p>
                {realtimeData.exchange && (
                  <p className="text-xs text-gray-500">{realtimeData.exchange}</p>
                )}
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-gray-900">
                  ${realtimeData.price?.toFixed(2)}
                </div>
                <div className={`flex items-center space-x-1 ${
                  realtimeData.change_percent >= 0 ? 'text-green-600' : 'text-red-600'
                }`}>
                  {realtimeData.change_percent >= 0 ? (
                    <ArrowTrendingUpIcon className="w-5 h-5" />
                  ) : (
                    <ArrowTrendingDownIcon className="w-5 h-5" />
                  )}
                  <span className="font-medium">
                    {realtimeData.change_percent >= 0 ? '+' : ''}{realtimeData.change_percent}%
                  </span>
                  <span className="text-gray-600">
                    ({realtimeData.change >= 0 ? '+' : ''}${realtimeData.change?.toFixed(2)})
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Prev Close: ${realtimeData.previous_close?.toFixed(2)}
                </p>
              </div>
            </div>
            {realtimeData.sector && (
              <div className="mt-4 flex flex-wrap gap-2">
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                  {realtimeData.sector}
                </span>
                {realtimeData.industry && (
                  <span className="px-2 py-1 bg-indigo-100 text-indigo-800 text-xs rounded">
                    {realtimeData.industry}
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="card">
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="form-label">Instrument</label>
              <InstrumentSelector
                onSelect={handleInstrumentSelect}
                selectedInstrument={selectedInstrument}
              />
            </div>
            
            <div>
              <label className="form-label">Period</label>
              <select
                value={period}
                onChange={(e) => setPeriod(e.target.value)}
                className="form-input"
              >
                <option value="1d">1 Day</option>
                <option value="5d">5 Days</option>
                <option value="1mo">1 Month</option>
                <option value="3mo">3 Months</option>
                <option value="6mo">6 Months</option>
                <option value="1y">1 Year</option>
                <option value="2y">2 Years</option>
                <option value="5y">5 Years</option>
                <option value="10y">10 Years</option>
                <option value="max">Max</option>
              </select>
            </div>
            
            <div>
              <label className="form-label">Interval</label>
              <select
                value={interval}
                onChange={(e) => setInterval(e.target.value)}
                className="form-input"
              >
                <option value="1m">1 Minute</option>
                <option value="5m">5 Minutes</option>
                <option value="15m">15 Minutes</option>
                <option value="30m">30 Minutes</option>
                <option value="1h">1 Hour</option>
                <option value="1d">1 Day</option>
                <option value="1wk">1 Week</option>
                <option value="1mo">1 Month</option>
              </select>
            </div>
            
            <div className="flex items-end">
              <button 
                onClick={() => refetch()}
                className="btn-primary w-full"
                disabled={isDataLoading}
              >
                <MagnifyingGlassIcon className="w-4 h-4 mr-2" />
                {isDataLoading ? 'Loading...' : 'Refresh'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {hasError && (
        <div className="card bg-red-50 border-red-200">
          <div className="card-body">
            <p className="text-red-800">{hasError}</p>
          </div>
        </div>
      )}

      {/* Chart */}
      {marketData.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Price Chart</h3>
            <p className="text-sm text-gray-500">
              {selectedInstrument?.symbol} - {yfinanceData?.name} ({period}, {interval})
            </p>
          </div>
          <div className="card-body">
            <MarketDataChart data={marketData} />
          </div>
        </div>
      )}

      {/* Data Table */}
      {marketData.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-gray-900">Historical Data</h3>
            <p className="text-sm text-gray-500">{marketData.length} data points</p>
          </div>
          <div className="card-body p-0">
            <MarketDataTable data={marketData} />
          </div>
        </div>
      )}
    </div>
  );
};

export default MarketData;
