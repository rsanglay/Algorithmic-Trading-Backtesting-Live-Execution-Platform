import React, { useState } from 'react';
import { useGetMLModelsQuery } from '../../store/api/api';
import MLModelCard from '../../components/MLModels/MLModelCard';
import CreateMLModelModal from '../../components/MLModels/CreateMLModelModal';
import { PlusIcon } from '@heroicons/react/24/outline';
import { MLModel } from '../../store/slices/mlModelsSlice';

const MLModels: React.FC = () => {
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const { data: models, isLoading, error } = useGetMLModelsQuery({});

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
        <p className="text-red-600">Error loading ML models</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">ML Models</h1>
          <p className="text-gray-600">Machine learning models for trading predictions</p>
        </div>
        <button
          onClick={() => setIsCreateModalOpen(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <PlusIcon className="w-5 h-5" />
          <span>Create Model</span>
        </button>
      </div>

      {/* Models Grid */}
      {models && models.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {models.map((model: MLModel) => (
            <MLModelCard key={model.id} model={model} />
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <div className="mx-auto h-12 w-12 text-gray-400">
            <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No ML models</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating your first ML model.</p>
          <div className="mt-6">
            <button
              onClick={() => setIsCreateModalOpen(true)}
              className="btn-primary"
            >
              Create Model
            </button>
          </div>
        </div>
      )}

      {/* Create ML Model Modal */}
      <CreateMLModelModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
      />
    </div>
  );
};

export default MLModels;
