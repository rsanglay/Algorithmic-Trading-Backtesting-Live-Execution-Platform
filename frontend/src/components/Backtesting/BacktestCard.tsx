import React from 'react';
import { Link } from 'react-router-dom';
import { 
  ChartBarIcon, 
  ClockIcon, 
  CurrencyDollarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon
} from '@heroicons/react/24/outline';

interface Backtest {
  id: string;
  strategy_id: string;
  name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
  final_capital?: number;
  total_return?: number;
  annualized_return?: number;
  sharpe_ratio?: number;
  max_drawdown?: number;
  win_rate?: number;
  profit_factor?: number;
  status: string;
  created_at: string;
  completed_at?: string;
}

interface BacktestCardProps {
  backtest: Backtest;
}

const BacktestCard: React.FC<BacktestCardProps> = ({ backtest }) => {
  const getStatusBadge = () => {
    switch (backtest.status) {
      case 'completed':
        return <span className="badge-success">Completed</span>;
      case 'running':
        return <span className="badge-warning">Running</span>;
      case 'failed':
        return <span className="badge-danger">Failed</span>;
      default:
        return <span className="badge-gray">Pending</span>;
    }
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(value);
  };

  const formatPercentage = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const getReturnColor = (value: number) => {
    return value >= 0 ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="card hover:shadow-lg transition-shadow duration-200">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <h3 className="text-lg font-medium text-gray-900">{backtest.name}</h3>
            {getStatusBadge()}
          </div>
        </div>
        <p className="mt-1 text-sm text-gray-500">
          {new Date(backtest.start_date).toLocaleDateString()} - {new Date(backtest.end_date).toLocaleDateString()}
        </p>
      </div>
      
      <div className="card-body">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Initial Capital</span>
            <span className="text-sm font-medium text-gray-900">
              {formatCurrency(backtest.initial_capital)}
            </span>
          </div>
          
          {backtest.final_capital && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Final Capital</span>
              <span className="text-sm font-medium text-gray-900">
                {formatCurrency(backtest.final_capital)}
              </span>
            </div>
          )}
          
          {backtest.total_return !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Total Return</span>
              <span className={`text-sm font-medium ${getReturnColor(backtest.total_return)}`}>
                {formatPercentage(backtest.total_return)}
              </span>
            </div>
          )}
          
          {backtest.sharpe_ratio !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Sharpe Ratio</span>
              <span className="text-sm font-medium text-gray-900">
                {backtest.sharpe_ratio.toFixed(2)}
              </span>
            </div>
          )}
          
          {backtest.max_drawdown !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Max Drawdown</span>
              <span className="text-sm font-medium text-red-600">
                {formatPercentage(backtest.max_drawdown)}
              </span>
            </div>
          )}
        </div>
      </div>
      
      <div className="card-footer">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <ClockIcon className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-500">
              {backtest.completed_at 
                ? `Completed ${new Date(backtest.completed_at).toLocaleDateString()}`
                : `Created ${new Date(backtest.created_at).toLocaleDateString()}`
              }
            </span>
          </div>
          <Link
            to={`/backtesting/${backtest.id}`}
            className="btn-primary text-sm"
          >
            <ChartBarIcon className="w-4 h-4 mr-1" />
            View Results
          </Link>
        </div>
      </div>
    </div>
  );
};

export default BacktestCard;
