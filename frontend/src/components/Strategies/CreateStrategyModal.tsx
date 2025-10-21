import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useCreateStrategyMutation } from '../../store/api/api';
import { XMarkIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface CreateStrategyModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface StrategyFormData {
  name: string;
  description: string;
  strategy_type: string;
  code: string;
  parameters: Record<string, any>;
}

const CreateStrategyModal: React.FC<CreateStrategyModalProps> = ({ isOpen, onClose }) => {
  const [createStrategy, { isLoading }] = useCreateStrategyMutation();
  const { register, handleSubmit, formState: { errors }, reset } = useForm<StrategyFormData>();

  const strategyTypes = [
    { value: 'momentum', label: 'Momentum' },
    { value: 'mean_reversion', label: 'Mean Reversion' },
    { value: 'pairs_trading', label: 'Pairs Trading' },
    { value: 'statistical_arbitrage', label: 'Statistical Arbitrage' },
  ];

  const onSubmit = async (data: StrategyFormData) => {
    try {
      await createStrategy({
        ...data,
        created_by: 'user', // This would come from auth context
      }).unwrap();
      
      toast.success('Strategy created successfully');
      reset();
      onClose();
    } catch (error) {
      toast.error('Failed to create strategy');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity" onClick={onClose}>
          <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Create New Strategy</h3>
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
                  <label className="form-label">Strategy Name</label>
                  <input
                    {...register('name', { required: 'Strategy name is required' })}
                    className="form-input"
                    placeholder="Enter strategy name"
                  />
                  {errors.name && (
                    <p className="form-error">{errors.name.message}</p>
                  )}
                </div>

                <div>
                  <label className="form-label">Description</label>
                  <textarea
                    {...register('description')}
                    className="form-input"
                    rows={3}
                    placeholder="Enter strategy description"
                  />
                </div>

                <div>
                  <label className="form-label">Strategy Type</label>
                  <select
                    {...register('strategy_type', { required: 'Strategy type is required' })}
                    className="form-input"
                  >
                    <option value="">Select strategy type</option>
                    {strategyTypes.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                  {errors.strategy_type && (
                    <p className="form-error">{errors.strategy_type.message}</p>
                  )}
                </div>

                <div>
                  <label className="form-label">Strategy Code</label>
                  <textarea
                    {...register('code', { required: 'Strategy code is required' })}
                    className="form-input font-mono"
                    rows={10}
                    placeholder="Enter your strategy code here..."
                  />
                  {errors.code && (
                    <p className="form-error">{errors.code.message}</p>
                  )}
                </div>
              </div>
            </div>

            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                type="submit"
                disabled={isLoading}
                className="btn-primary sm:ml-3 sm:w-auto"
              >
                {isLoading ? 'Creating...' : 'Create Strategy'}
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

export default CreateStrategyModal;
