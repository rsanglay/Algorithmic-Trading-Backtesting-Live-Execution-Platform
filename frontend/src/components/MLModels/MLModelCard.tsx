import React from 'react';
import { Link } from 'react-router-dom';
import { 
  CpuChipIcon, 
  ChartBarIcon, 
  CogIcon, 
  TrashIcon,
  PlayIcon,
  PauseIcon
} from '@heroicons/react/24/outline';

interface MLModel {
  id: string;
  name: string;
  model_type: string;
  purpose: string;
  version: string;
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  mse?: number;
  mae?: number;
  is_active: boolean;
  is_training: boolean;
  status: string;
  created_at: string;
  updated_at?: string;
}

interface MLModelCardProps {
  model: MLModel;
}

const MLModelCard: React.FC<MLModelCardProps> = ({ model }) => {
  const getStatusBadge = () => {
    if (model.is_training) {
      return <span className="badge-warning">Training</span>;
    } else if (model.is_active) {
      return <span className="badge-success">Active</span>;
    } else if (model.status === 'ready') {
      return <span className="badge-info">Ready</span>;
    } else if (model.status === 'failed') {
      return <span className="badge-danger">Failed</span>;
    } else {
      return <span className="badge-gray">Draft</span>;
    }
  };

  const getModelTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      'random_forest': 'bg-green-100 text-green-800',
      'lstm': 'bg-blue-100 text-blue-800',
      'transformer': 'bg-purple-100 text-purple-800',
      'ensemble': 'bg-orange-100 text-orange-800',
      'svr': 'bg-pink-100 text-pink-800',
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  const formatMetric = (value: number | undefined) => {
    if (value === undefined) return 'N/A';
    return (value * 100).toFixed(1) + '%';
  };

  return (
    <div className="card hover:shadow-lg transition-shadow duration-200">
      <div className="card-header">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <CpuChipIcon className="w-5 h-5 text-gray-400" />
            <h3 className="text-lg font-medium text-gray-900">{model.name}</h3>
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
        <p className="mt-1 text-sm text-gray-500">{model.purpose}</p>
      </div>
      
      <div className="card-body">
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Type</span>
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getModelTypeColor(model.model_type)}`}>
              {model.model_type.replace('_', ' ')}
            </span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Version</span>
            <span className="text-sm font-medium text-gray-900">{model.version}</span>
          </div>
          
          {model.accuracy !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">Accuracy</span>
              <span className="text-sm font-medium text-gray-900">
                {formatMetric(model.accuracy)}
              </span>
            </div>
          )}
          
          {model.mse !== undefined && (
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-500">MSE</span>
              <span className="text-sm font-medium text-gray-900">
                {model.mse.toFixed(4)}
              </span>
            </div>
          )}
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-500">Created</span>
            <span className="text-sm text-gray-900">
              {new Date(model.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      </div>
      
      <div className="card-footer">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <button className="btn-outline text-sm">
              {model.is_active ? (
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
              to={`/ml-models/${model.id}`}
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

export default MLModelCard;
