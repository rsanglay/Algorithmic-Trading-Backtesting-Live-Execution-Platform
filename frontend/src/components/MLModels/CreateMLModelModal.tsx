import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useCreateMLModelMutation } from '../../store/api/api';
import { XMarkIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface CreateMLModelModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface MLModelFormData {
  name: string;
  model_type: string;
  purpose: string;
  version: string;
  features: string[];
  target: string;
  hyperparameters: Record<string, any>;
}

const CreateMLModelModal: React.FC<CreateMLModelModalProps> = ({ isOpen, onClose }) => {
  const [createMLModel, { isLoading }] = useCreateMLModelMutation();
  const { register, handleSubmit, formState: { errors }, reset } = useForm<MLModelFormData>();

  const modelTypes = [
    { value: 'random_forest', label: 'Random Forest' },
    { value: 'lstm', label: 'LSTM' },
    { value: 'transformer', label: 'Transformer' },
    { value: 'ensemble', label: 'Ensemble' },
    { value: 'svr', label: 'Support Vector Regression' },
  ];

  const purposes = [
    { value: 'price_prediction', label: 'Price Prediction' },
    { value: 'volatility_forecast', label: 'Volatility Forecast' },
    { value: 'regime_detection', label: 'Regime Detection' },
    { value: 'sentiment_analysis', label: 'Sentiment Analysis' },
  ];

  const onSubmit = async (data: MLModelFormData) => {
    try {
      await createMLModel(data).unwrap();
      
      toast.success('ML model created successfully');
      reset();
      onClose();
    } catch (error) {
      toast.error('Failed to create ML model');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity" onClick={onClose}>
          <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Create ML Model</h3>
                <button
                  type="button"
                  onClick={onClose}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <XMarkIcon className="w-6 h-6" />
                </button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="form-label">Model Name</label>
                  <input
                    {...register('name', { required: 'Model name is required' })}
                    className="form-input"
                    placeholder="Enter model name"
                  />
                  {errors.name && (
                    <p className="form-error">{errors.name.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Model Type</label>
                    <select
                      {...register('model_type', { required: 'Model type is required' })}
                      className="form-input"
                    >
                      <option value="">Select model type</option>
                      {modelTypes.map((type) => (
                        <option key={type.value} value={type.value}>
                          {type.label}
                        </option>
                      ))}
                    </select>
                    {errors.model_type && (
                      <p className="form-error">{errors.model_type.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="form-label">Purpose</label>
                    <select
                      {...register('purpose', { required: 'Purpose is required' })}
                      className="form-input"
                    >
                      <option value="">Select purpose</option>
                      {purposes.map((purpose) => (
                        <option key={purpose.value} value={purpose.value}>
                          {purpose.label}
                        </option>
                      ))}
                    </select>
                    {errors.purpose && (
                      <p className="form-error">{errors.purpose.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="form-label">Version</label>
                  <input
                    {...register('version', { required: 'Version is required' })}
                    className="form-input"
                    placeholder="1.0.0"
                  />
                  {errors.version && (
                    <p className="form-error">{errors.version.message}</p>
                  )}
                </div>

                <div>
                  <label className="form-label">Features (comma-separated)</label>
                  <input
                    {...register('features', { 
                      required: 'Features are required',
                      setValueAs: (value) => value.split(',').map((s: string) => s.trim())
                    })}
                    className="form-input"
                    placeholder="feature1, feature2, feature3"
                  />
                  {errors.features && (
                    <p className="form-error">{errors.features.message}</p>
                  )}
                </div>

                <div>
                  <label className="form-label">Target Variable</label>
                  <input
                    {...register('target', { required: 'Target variable is required' })}
                    className="form-input"
                    placeholder="price_change"
                  />
                  {errors.target && (
                    <p className="form-error">{errors.target.message}</p>
                  )}
                </div>

                <div>
                  <label className="form-label">Hyperparameters (JSON)</label>
                  <textarea
                    {...register('hyperparameters', {
                      setValueAs: (value) => {
                        try {
                          return JSON.parse(value);
                        } catch {
                          return {};
                        }
                      }
                    })}
                    className="form-input font-mono"
                    rows={4}
                    placeholder='{"n_estimators": 100, "max_depth": 10}'
                  />
                </div>
              </div>
            </div>

            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary sm:ml-3 sm:w-auto"
              >
                {isLoading ? 'Creating...' : 'Create Model'}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="btn-outline sm:mt-0 sm:w-auto"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreateMLModelModal;
