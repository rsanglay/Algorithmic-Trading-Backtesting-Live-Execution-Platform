import React, { useState, useEffect } from 'react';
import { useGetInstrumentCategoriesQuery, useSearchInstrumentsQuery } from '../../store/api/api';
import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface Instrument {
  symbol: string;
  name: string;
  exchange?: string;
  sector?: string;
  category: string;
}

interface InstrumentSelectorProps {
  onSelect: (instrument: Instrument) => void;
  selectedInstrument?: Instrument | null;
  category?: string;
  className?: string;
}

const InstrumentSelector: React.FC<InstrumentSelectorProps> = ({
  onSelect,
  selectedInstrument,
  category,
  className = '',
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>(category || 'all');
  const [isOpen, setIsOpen] = useState(false);

  const { data: categoriesData } = useGetInstrumentCategoriesQuery(undefined);
  const { data: searchResults, isLoading } = useSearchInstrumentsQuery(
    { query: searchQuery, category: selectedCategory === 'all' ? undefined : selectedCategory },
    { skip: !searchQuery || searchQuery.length < 2 }
  );

  const categories = categoriesData?.categories || [];

  const handleSelect = (instrument: Instrument) => {
    onSelect(instrument);
    setIsOpen(false);
    setSearchQuery('');
  };

  return (
    <div className={`relative ${className}`}>
      {/* Selected Instrument Display */}
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <div className="flex items-center space-x-2">
          {selectedInstrument ? (
            <>
              <span className="font-medium text-gray-900">{selectedInstrument.symbol}</span>
              <span className="text-sm text-gray-500">- {selectedInstrument.name}</span>
            </>
          ) : (
            <span className="text-gray-500">Select an instrument...</span>
          )}
        </div>
        <svg
          className={`w-5 h-5 text-gray-400 transition-transform ${isOpen ? 'transform rotate-180' : ''}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg">
          {/* Category Filter */}
          <div className="p-2 border-b border-gray-200">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setSelectedCategory('all')}
                className={`px-3 py-1 text-xs rounded-full ${
                  selectedCategory === 'all'
                    ? 'bg-blue-500 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                All
              </button>
              {categories.map((cat: any) => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-3 py-1 text-xs rounded-full ${
                    selectedCategory === cat.id
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>

          {/* Search Input */}
          <div className="p-2 border-b border-gray-200">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search by symbol or name..."
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          {/* Results */}
          <div className="max-h-64 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-gray-500">Searching...</div>
            ) : searchResults && searchResults.length > 0 ? (
              <ul className="py-1">
                {searchResults.map((instrument: Instrument) => (
                  <li key={instrument.symbol}>
                    <button
                      type="button"
                      onClick={() => handleSelect(instrument)}
                      className={`w-full px-4 py-2 text-left hover:bg-gray-100 ${
                        selectedInstrument?.symbol === instrument.symbol ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="font-medium text-gray-900">{instrument.symbol}</div>
                          <div className="text-sm text-gray-500">{instrument.name}</div>
                        </div>
                        <span className="text-xs text-gray-400 capitalize">{instrument.category}</span>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            ) : searchQuery.length >= 2 ? (
              <div className="p-4 text-center text-gray-500">No instruments found</div>
            ) : (
              <div className="p-4 text-center text-gray-500">Start typing to search...</div>
            )}
          </div>
        </div>
      )}

      {/* Overlay to close dropdown */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default InstrumentSelector;

