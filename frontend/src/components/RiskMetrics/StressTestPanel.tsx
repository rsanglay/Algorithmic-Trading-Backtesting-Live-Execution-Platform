import React, { useState } from 'react';
import { useRunRiskStressTestMutation } from '../../store/api/api';

type ScenarioOption = {
  value: string;
  label: string;
  description: string;
};

const STRESS_SCENARIOS: ScenarioOption[] = [
  {
    value: 'crisis_2008',
    label: 'Global Financial Crisis (2008)',
    description: 'Severe equity drawdown and credit freeze scenario.',
  },
  {
    value: 'covid_2020',
    label: 'COVID-19 Crash (2020)',
    description: 'Rapid volatility spike with sharp drawdown and fast recovery.',
  },
  {
    value: 'flash_crash',
    label: 'Flash Crash',
    description: 'Intraday liquidity shock with extreme price dislocations.',
  },
  {
    value: 'dotcom_bubble',
    label: 'Dot-com Bust',
    description: 'Extended drawdown in tech equities with regime shift.',
  },
];

interface StressTestPanelProps {
  strategyId: string;
}

const StressTestPanel: React.FC<StressTestPanelProps> = ({ strategyId }) => {
  const [selectedScenario, setSelectedScenario] = useState<string>('crisis_2008');
  const [runStressTest, { data, isLoading, isSuccess, error }] = useRunRiskStressTestMutation();

  const handleRun = async () => {
    if (!strategyId) {
      return;
    }
    try {
      await runStressTest({ strategyId, scenario: selectedScenario }).unwrap();
    } catch (err) {
      console.error('Failed to run stress test', err);
    }
  };

  const scenarioDetails = STRESS_SCENARIOS.find((s) => s.value === selectedScenario);
  const stressResult = data as { pnl_impact?: number; scenario?: string } | undefined;

  return (
    <div className="card">
      <div className="card-header flex items-center justify-between">
        <div>
          <h3 className="text-lg font-medium text-gray-900">Stress Test Scenarios</h3>
          <p className="text-sm text-gray-500">Assess strategy resilience under extreme market regimes.</p>
        </div>
        <button
          onClick={handleRun}
          disabled={!strategyId || isLoading}
          className="btn-primary"
        >
          {isLoading ? 'Running...' : 'Run Stress Test'}
        </button>
      </div>
      <div className="card-body space-y-4">
        <div>
          <label htmlFor="stress-scenario" className="block text-sm font-medium text-gray-700">
            Scenario
          </label>
          <select
            id="stress-scenario"
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
          >
            {STRESS_SCENARIOS.map((scenario) => (
              <option key={scenario.value} value={scenario.value}>
                {scenario.label}
              </option>
            ))}
          </select>
          {scenarioDetails && (
            <p className="mt-2 text-sm text-gray-500">{scenarioDetails.description}</p>
          )}
        </div>

        {!strategyId && (
          <div className="rounded-md bg-yellow-50 p-4">
            <p className="text-sm text-yellow-800">
              Select a strategy to run stress scenarios and view impact on PnL.
            </p>
          </div>
        )}

        {error && (
          <div className="rounded-md bg-red-50 p-4">
            <p className="text-sm text-red-700">Failed to run stress test. Please try again.</p>
          </div>
        )}

        {isSuccess && stressResult && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <p className="text-sm text-gray-500">Scenario</p>
              <p className="text-lg font-semibold">{scenarioDetails?.label || stressResult.scenario}</p>
            </div>
            <div className="border rounded-lg p-4">
              <p className="text-sm text-gray-500">Estimated PnL Impact</p>
              <p className="text-lg font-semibold text-red-600">
                {stressResult.pnl_impact !== undefined
                  ? `${(stressResult.pnl_impact * 100).toFixed(2)}%`
                  : 'N/A'}
              </p>
            </div>
          </div>
        )}

        {!isLoading && isSuccess && !stressResult?.pnl_impact && (
          <p className="text-sm text-gray-500">
            Detailed stress test metrics will appear here as the backend implementation matures.
          </p>
        )}
      </div>
    </div>
  );
};

export default StressTestPanel;
