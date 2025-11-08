import React from 'react';
import { useGetStrategiesQuery, useGetCurrentUserQuery } from '../../store/api/api';
import MetricCard from '../../components/Dashboard/MetricCard';
import PerformanceChart from '../../components/Dashboard/PerformanceChart';
import RecentStrategies from '../../components/Dashboard/RecentStrategies';
import MarketOverview from '../../components/Dashboard/MarketOverview';
import { Strategy } from '../../store/slices/strategiesSlice';

const Dashboard: React.FC = () => {
  const { data: strategies, isLoading } = useGetStrategiesQuery({ limit: 5 });
  const { data: user } = useGetCurrentUserQuery(undefined);
  
  // Get user preferences or use defaults
  const preferences = user?.dashboard_preferences || {
    widgets: ["metrics", "performance_chart", "recent_strategies", "market_overview"],
    default_timeframe: "1M"
  };
  
  const showMetrics = preferences.widgets?.includes("metrics") ?? true;
  const showPerformanceChart = preferences.widgets?.includes("performance_chart") ?? true;
  const showRecentStrategies = preferences.widgets?.includes("recent_strategies") ?? true;
  const showMarketOverview = preferences.widgets?.includes("market_overview") ?? true;

  const metrics = [
    {
      title: 'Total Strategies',
      value: strategies?.length || 0,
      change: '+2',
      changeType: 'positive' as const,
      icon: '📈',
    },
    {
      title: 'Active Strategies',
      value: strategies?.filter((s: Strategy) => s.is_active).length || 0,
      change: '+1',
      changeType: 'positive' as const,
      icon: '⚡',
    },
    {
      title: 'Total P&L',
      value: '$12,450.00',
      change: '+5.2%',
      changeType: 'positive' as const,
      icon: '💰',
    },
    {
      title: 'Win Rate',
      value: '68.5%',
      change: '+2.1%',
      changeType: 'positive' as const,
      icon: '🎯',
    },
  ];

  if (isLoading) {
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
        <h1 className="text-2xl font-bold text-gray-900">
          Dashboard{user?.full_name ? ` - Welcome, ${user.full_name}` : ''}
        </h1>
        <p className="text-gray-600">Overview of your trading platform</p>
      </div>

      {/* Metrics Grid */}
      {showMetrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {metrics.map((metric, index) => (
            <MetricCard
              key={index}
              title={metric.title}
              value={metric.value}
              change={metric.change}
              changeType={metric.changeType}
              icon={metric.icon}
            />
          ))}
        </div>
      )}

      {/* Charts and Tables */}
      {(showPerformanceChart || showRecentStrategies) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Performance Chart */}
          {showPerformanceChart && (
            <div className="lg:col-span-1">
              <PerformanceChart />
            </div>
          )}

          {/* Recent Strategies */}
          {showRecentStrategies && (
            <div className="lg:col-span-1">
              <RecentStrategies strategies={strategies || []} />
            </div>
          )}
        </div>
      )}

      {/* Market Overview */}
      {showMarketOverview && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <MarketOverview />
          </div>
          
          {/* Quick Actions */}
          <div className="card">
            <div className="card-header">
              <h3 className="text-lg font-medium text-gray-900">Quick Actions</h3>
            </div>
            <div className="card-body space-y-4">
              <button className="w-full btn-primary">
                Create Strategy
              </button>
              <button className="w-full btn-outline">
                Run Backtest
              </button>
              <button className="w-full btn-outline">
                Train ML Model
              </button>
              <button className="w-full btn-outline">
                View Analytics
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
