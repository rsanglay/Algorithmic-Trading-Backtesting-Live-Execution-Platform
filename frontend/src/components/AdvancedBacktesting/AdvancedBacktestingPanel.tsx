import React, { useMemo, useState } from 'react';
import {
  useRunWalkForwardAnalysisMutation,
  useRunMonteCarloSimulationMutation,
  useGetStrategiesQuery,
} from '../../store/api/api';
import { Strategy } from '../../store/slices/strategiesSlice';
import WalkForwardResults from './WalkForwardResults';
import MonteCarloSimulationChart from './MonteCarloSimulationChart';

const AdvancedBacktestingPanel: React.FC = () => {
  const { data: strategies } = useGetStrategiesQuery({ limit: 100 });
  const [selectedStrategyId, setSelectedStrategyId] = useState<string>('');
  const [trainPeriod, setTrainPeriod] = useState<number>(252);
  const [testPeriod, setTestPeriod] = useState<number>(63);
  const [step, setStep] = useState<number>(21);

  const [walkForwardResult, setWalkForwardResult] = useState<any>(null);
  const [monteCarloResult, setMonteCarloResult] = useState<any>(null);

  const [runWalkForward, { isLoading: walkForwardLoading }] = useRunWalkForwardAnalysisMutation();
  const [runMonteCarlo, { isLoading: monteCarloLoading }] = useRunMonteCarloSimulationMutation();

  const defaultStrategyId = useMemo(() => {
    if (!strategies || strategies.length === 0) {
      return '';
    }
    return strategies[0].id;
  }, [strategies]);

  React.useEffect(() => {
    if (!selectedStrategyId && defaultStrategyId) {
      setSelectedStrategyId(defaultStrategyId);
    }
  }, [defaultStrategyId, selectedStrategyId]);

  const handleRunWalkForward = async () => {
    if (!selectedStrategyId) return;
    try {
      const response = await runWalkForward({
        strategyId: selectedStrategyId,
        trainPeriod,
        testPeriod,
        step,
      }).unwrap();
      setWalkForwardResult(response);
    } catch (error) {
      console.error('Failed to run walk-forward analysis', error);
    }
  };

  const handleRunMonteCarlo = async () => {
    if (!selectedStrategyId) return;
    try {
      const response = await runMonteCarlo({
        strategyId: selectedStrategyId,
        nSimulations: 1000,
        nPeriods: 252,
        confidenceLevel: 0.95,
      }).unwrap();
      setMonteCarloResult(response);
    } catch (error) {
      console.error('Failed to run Monte Carlo simulation', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="card">
        <div className="card-header">
          <h2 className="text-xl font-semibold text-gray-900">Advanced Backtesting</h2>
          <p className="text-sm text-gray-500">
            Run walk-forward analysis and Monte Carlo simulations to validate strategy robustness.
          </p>
        </div>
        <div className="card-body space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Strategy</label>
              <select
                value={selectedStrategyId}
                onChange={(e) => setSelectedStrategyId(e.target.value)}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              >
                <option value="">Select a strategy...</option>
                {strategies?.map((strategy: Strategy) => (
                  <option key={strategy.id} value={strategy.id}>
                    {strategy.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Train Period (days)</label>
                <input
                  type="number"
                  min={30}
                  value={trainPeriod}
                  onChange={(e) => setTrainPeriod(Number(e.target.value))}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Test Period (days)</label>
                <input
                  type="number"
                  min={10}
                  value={testPeriod}
                  onChange={(e) => setTestPeriod(Number(e.target.value))}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Step (days)</label>
                <input
                  type="number"
                  min={5}
                  value={step}
                  onChange={(e) => setStep(Number(e.target.value))}
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
                />
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-4">
            <button
              onClick={handleRunWalkForward}
              disabled={!selectedStrategyId || walkForwardLoading}
              className="btn-primary"
            >
              {walkForwardLoading ? 'Running...' : 'Run Walk-Forward'}
            </button>
            <button
              onClick={handleRunMonteCarlo}
              disabled={!selectedStrategyId || monteCarloLoading}
              className="btn-secondary"
            >
              {monteCarloLoading ? 'Running...' : 'Run Monte Carlo'}
            </button>
          </div>

          {!selectedStrategyId && (
            <div className="rounded-md bg-yellow-50 p-4">
              <p className="text-sm text-yellow-800">
                Select a strategy to enable advanced backtesting workflows.
              </p>
            </div>
          )}
        </div>
      </div>

      {walkForwardResult && (
        <div className="card">
          <div className="card-body">
            <WalkForwardResults results={walkForwardResult} />
          </div>
        </div>
      )}

      {monteCarloResult && (
        <div className="card">
          <div className="card-body">
            <MonteCarloSimulationChart result={monteCarloResult} />
          </div>
        </div>
      )}
    </div>
  );
};

export default AdvancedBacktestingPanel;
