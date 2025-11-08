import React, { useState } from 'react';
import { useGetStrategiesQuery } from '../../store/api/api';
import StrategyCard from '../../components/Strategies/StrategyCard';
import CreateStrategyModal from '../../components/Strategies/CreateStrategyModal';
import { PlusIcon } from '@heroicons/react/24/outline';
import { Strategy } from '../../store/slices/strategiesSlice';

const Strategies: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data: strategies, isLoading, error } = useGetStrategiesQuery({});

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
        <p className="text-red-600">Error loading strategies</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Trading Strategies</h1>
          <p className="text-gray-600">Manage your algorithmic trading strategies</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Create Strategy</span>
        </button>
      </div>

      {/* Strategies Grid */}
      {strategies && strategies.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {strategies.map((strategy: Strategy) => (
            <StrategyCard key={strategy.id} strategy={strategy} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No strategies</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating a new strategy.</p>
          <div className="mt-6">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="btn-primary"
            >
              Create Strategy
            </button>
          </div>
        </div>
      )}

      {/* Create Strategy Modal */}
      <CreateStrategyModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
};

export default Strategies;
