import React, { useState } from 'react';
import { ChevronDownIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface TickerInfo {
  id: string;
  symbol: string;
  name: string;
  exchange: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  currency: string;
  is_active: string;
  created_at: string;
  updated_at?: string;
}

interface TickerSelectorProps {
  value: string;
  onChange: (value: string) => void;
  tickers: TickerInfo[];
}

const TickerSelector: React.FC<TickerSelectorProps> = ({ value, onChange, tickers }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredTickers = tickers.filter(ticker =>
    ticker.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ticker.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedTicker = tickers.find(ticker => ticker.symbol === value);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="form-input flex items-center justify-between w-full"
      >
        <span className="block truncate">
          {selectedTicker ? `${selectedTicker.symbol} - ${selectedTicker.name}` : 'Select ticker'}
        </span>
        <ChevronDownIcon className="w-5 h-5 text-gray-400" />
      </button>

      {isOpen && (
        <div className="absolute z-10 mt-1 w-full bg-white shadow-lg max-h-60 rounded-md py-1 text-base ring-1 ring-black ring-opacity-5 overflow-auto focus:outline-none sm:text-sm">
          <div className="px-3 py-2 border-b border-gray-200">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                placeholder="Search tickers..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>
          
          <div className="py-1">
            {filteredTickers.length === 0 ? (
              <div className="px-3 py-2 text-sm text-gray-500">No tickers found</div>
            ) : (
              filteredTickers.map((ticker) => (
                <button
                  key={ticker.id}
                  type="button"
                  className="w-full text-left px-3 py-2 text-sm hover:bg-gray-100 focus:outline-none focus:bg-gray-100"
                  onClick={() => {
                    onChange(ticker.symbol);
                    setIsOpen(false);
                    setSearchTerm('');
                  }}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-gray-900">{ticker.symbol}</div>
                      <div className="text-gray-500 text-xs">{ticker.name}</div>
                    </div>
                    <div className="text-xs text-gray-400">{ticker.exchange}</div>
                  </div>
                </button>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default TickerSelector;
