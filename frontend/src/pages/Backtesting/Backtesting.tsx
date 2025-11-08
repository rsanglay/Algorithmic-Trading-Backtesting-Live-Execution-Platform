import React, { useState } from 'react';
import { useGetBacktestsQuery } from '../../store/api/api';
import BacktestCard from '../../components/Backtesting/BacktestCard';
import CreateBacktestModal from '../../components/Backtesting/CreateBacktestModal';
import AdvancedBacktestingPanel from '../../components/AdvancedBacktesting/AdvancedBacktestingPanel';
import { PlusIcon } from '@heroicons/react/24/outline';
import { Backtest } from '../../store/slices/backtestingSlice';

const Backtesting: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data: backtests, isLoading, error } = useGetBacktestsQuery({});

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">Error loading backtests</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Backtesting</h1>
          <p className="text-gray-600">Test your strategies against historical data and validate robustness.</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Run Backtest</span>
        </button>
      </div>

      {/* Advanced Backtesting */}
      <AdvancedBacktestingPanel />

      {/* Backtests Grid */}
      {backtests && backtests.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {backtests.map((backtest: Backtest) => (
            <BacktestCard key={backtest.id} backtest={backtest} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No backtests</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by running your first backtest.</p>
          <div className="mt-6">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="btn-primary"
            >
              Run Backtest
            </button>
          </div>
        </div>
      )}

      {/* Create Backtest Modal */}
      <CreateBacktestModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
};

export default Backtesting;
