import React from 'react';
import { Link } from 'react-router-dom';

interface Strategy {
  id: string;
  name: string;
  strategy_type: string;
  is_active: boolean;
  is_live: boolean;
  created_at: string;
}

interface RecentStrategiesProps {
  strategies: Strategy[];
}

const RecentStrategies: React.FC<RecentStrategiesProps> = ({ strategies }) => {
  const getStatusBadge = (strategy: Strategy) => {
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
    <div className="card">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">Recent Strategies</h3>
          <Link to="/strategies" className="text-sm text-blue-600 hover:text-blue-500">
            View all
          </Link>
        </div>
      </div>
      <div className="card-body p-0">
        {strategies.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <p>No strategies found</p>
            <Link to="/strategies" className="text-blue-600 hover:text-blue-500">
              Create your first strategy
            </Link>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {strategies.map((strategy) => (
              <div key={strategy.id} className="p-4 hover:bg-gray-50">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <h4 className="text-sm font-medium text-gray-900">
                        {strategy.name}
                      </h4>
                      {getStatusBadge(strategy)}
                    </div>
                    <div className="mt-1 flex items-center space-x-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStrategyTypeColor(strategy.strategy_type)}`}>
                        {strategy.strategy_type.replace('_', ' ')}
                      </span>
                      <span className="text-xs text-gray-500">
                        {new Date(strategy.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Link
                      to={`/strategies/${strategy.id}`}
                      className="text-blue-600 hover:text-blue-500 text-sm"
                    >
                      View
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default RecentStrategies;
