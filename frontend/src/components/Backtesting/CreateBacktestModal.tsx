import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useCreateBacktestMutation, useGetStrategiesQuery } from '../../store/api/api';
import { XMarkIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface CreateBacktestModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface BacktestFormData {
  strategy_id: string;
  name: string;
  start_date: string;
  end_date: string;
  initial_capital: number;
}

const CreateBacktestModal: React.FC<CreateBacktestModalProps> = ({ isOpen, onClose }) => {
  const [createBacktest, { isLoading }] = useCreateBacktestMutation();
  const { data: strategies } = useGetStrategiesQuery({});
  const { register, handleSubmit, formState: { errors }, reset } = useForm<BacktestFormData>();

  const onSubmit = async (data: BacktestFormData) => {
    try {
      await createBacktest(data).unwrap();
      
      toast.success('Backtest started successfully');
      reset();
      onClose();
    } catch (error) {
      toast.error('Failed to start backtest');
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 transition-opacity" onClick={onClose}>
          <div className="absolute inset-0 bg-gray-500 opacity-75"></div>
        </div>

        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-medium text-gray-900">Run Backtest</h3>
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
                  <label className="form-label">Strategy</label>
                  <select
                    {...register('strategy_id', { required: 'Strategy is required' })}
                    className="form-input"
                  >
                    <option value="">Select a strategy</option>
                    {strategies?.map((strategy) => (
                      <option key={strategy.id} value={strategy.id}>
                        {strategy.name}
                      </option>
                    ))}
                  </select>
                  {errors.strategy_id && (
                    <p className="form-error">{errors.strategy_id.message}</p>
                  )}
                </div>

                <div>
                  <label className="form-label">Backtest Name</label>
                  <input
                    {...register('name', { required: 'Backtest name is required' })}
                    className="form-input"
                    placeholder="Enter backtest name"
                  />
                  {errors.name && (
                    <p className="form-error">{errors.name.message}</p>
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="form-label">Start Date</label>
                    <input
                      type="date"
                      {...register('start_date', { required: 'Start date is required' })}
                      className="form-input"
                    />
                    {errors.start_date && (
                      <p className="form-error">{errors.start_date.message}</p>
                    )}
                  </div>

                  <div>
                    <label className="form-label">End Date</label>
                    <input
                      type="date"
                      {...register('end_date', { required: 'End date is required' })}
                      className="form-input"
                    />
                    {errors.end_date && (
                      <p className="form-error">{errors.end_date.message}</p>
                    )}
                  </div>
                </div>

                <div>
                  <label className="form-label">Initial Capital</label>
                  <input
                    type="number"
                    step="0.01"
                    {...register('initial_capital', { 
                      required: 'Initial capital is required',
                      min: { value: 0, message: 'Initial capital must be positive' }
                    })}
                    className="form-input"
                    placeholder="100000"
                  />
                  {errors.initial_capital && (
                    <p className="form-error">{errors.initial_capital.message}</p>
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
                {isLoading ? 'Starting...' : 'Start Backtest'}
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

export default CreateBacktestModal;
