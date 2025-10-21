import React from 'react';
import { Link } from 'react-router-dom';
import { 
  PlayIcon, 
  PauseIcon, 
  CogIcon, 
  ChartBarIcon,
  TrashIcon 
} from '@heroicons/react/24/outline';

interface Strategy {
  id: string;
  name: string;
  description: string;
  strategy_type: string;
  is_active: boolean;
  is_live: boolean;
  created_at: string;
}

interface StrategyCardProps {
  strategy: Strategy;
}

const StrategyCard: React.FC<StrategyCardProps> = ({ strategy }) => {
  const getStatusBadge = () => {
    if (strategy.is_live) {
      return <span className="badge-success">Live</span>;
    } else if (strategy.is_active) {
      return <span className="badge-warning">Active</span>;
    } else {
      return <span className="badge-gray">Inactive</span>;
    }
  };

  const getStrategyTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      'momentum': 'bg-blue-100 text-blue-800',
      'mean_reversion': 'bg-green-100 text-green-800',
      'pairs_trading': 'bg-purple-100 text-purple-800',
      'statistical_arbitrage': 'bg-orange-100 text-orange-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="card hover:shadow-lg transition-shadow duration-200">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-medium text-gray-900">{strategy.name}</h3>
            {getStatusBadge()}
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-1 text-gray-400 hover:text-gray-600">
              <CogIcon className="w-4 h-4" />
            </button>
            <button className="p-1 text-gray-400 hover:text-red-600">
              <TrashIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
        <p className="mt-1 text-sm text-gray-500">{strategy.description}</p>
      </div>
      
      <div className="card-body">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Type</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStrategyTypeColor(strategy.strategy_type)}`}>
              {strategy.strategy_type.replace('_', ' ')}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Created</span>
            <span className="text-sm text-gray-900">
              {new Date(strategy.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
      
      <div className="card-footer">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button className="btn-outline text-sm">
              {strategy.is_active ? (
                <>
                  <PauseIcon className="w-4 h-4 mr-1" />
                  Deactivate
                </>
              ) : (
                <>
                  <PlayIcon className="w-4 h-4 mr-1" />
                  Activate
                </>
              )}
            </button>
            <Link
              to={`/strategies/${strategy.id}`}
              className="btn-primary text-sm"
            >
              <ChartBarIcon className="w-4 h-4 mr-1" />
              View
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StrategyCard;
