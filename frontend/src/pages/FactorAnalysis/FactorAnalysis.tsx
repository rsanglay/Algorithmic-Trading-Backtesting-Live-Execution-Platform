import React, { useState } from 'react';
import FactorExposureChart from '../../components/FactorAnalysis/FactorExposureChart';
import FactorCorrelationMatrix from '../../components/FactorAnalysis/FactorCorrelationMatrix';
import { useGetFamaFrench3FactorQuery, useGetFamaFrench5FactorQuery } from '../../store/api/api';

const FactorAnalysis: React.FC = () => {
  const [portfolioId, setPortfolioId] = useState<string>('default');
  const [showFiveFactor, setShowFiveFactor] = useState<boolean>(false);

  const {
    data: ff3Data,
    isLoading: ff3Loading,
    refetch: refetchFF3,
  } = useGetFamaFrench3FactorQuery({ portfolioId });

  const {
    data: ff5Data,
    isLoading: ff5Loading,
  } = useGetFamaFrench5FactorQuery({ portfolioId }, { skip: !showFiveFactor });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Factor Analysis</h1>
          <p className="text-gray-600">
            Understand portfolio exposure to systematic risk factors, correlations, and attribution.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <label htmlFor="portfolio-id" className="text-sm font-medium text-gray-700">
            Portfolio ID
          </label>
          <input
            id="portfolio-id"
            value={portfolioId}
            onChange={(e) => setPortfolioId(e.target.value)}
            className="block w-40 rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
            placeholder="portfolio-123"
          />
          <button onClick={() => refetchFF3()} className="btn-secondary">
            Refresh
          </button>
        </div>
      </div>

      {/* Fama-French 3-Factor Model */}
      <div className="card">
        <div className="card-header flex items-center justify-between">
          <h2 className="text-lg font-medium text-gray-900">Fama-French 3-Factor Model</h2>
          <div className="flex items-center space-x-2 text-sm text-gray-600">
            <label htmlFor="ff5-toggle" className="cursor-pointer">
              Include Quality & Investment Factors (FF5)
            </label>
            <input
              id="ff5-toggle"
              type="checkbox"
              checked={showFiveFactor}
              onChange={(e) => setShowFiveFactor(e.target.checked)}
              className="h-4 w-4 text-blue-600 border-gray-300 rounded"
            />
          </div>
        </div>
        <div className="card-body space-y-4">
          {ff3Loading ? (
            <div className="flex items-center justify-center h-64">
              <div className="loading-spinner"></div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <Stat label="Alpha" value={ff3Data?.alpha} fractionDigits={4} suffix="" />
              <Stat label="Market Beta" value={ff3Data?.market_beta} />
              <Stat label="SMB Beta" value={ff3Data?.smb_beta} />
              <Stat label="HML Beta" value={ff3Data?.hml_beta} />
              <Stat label="R-Squared" value={ff3Data?.r_squared} suffix="%" transform={(v) => (v || 0) * 100} />
            </div>
          )}

          {showFiveFactor && (
            <div className="border rounded-lg p-4 bg-gray-50">
              {ff5Loading ? (
                <div className="flex items-center justify-center h-32">
                  <div className="loading-spinner"></div>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Stat label="RMW Beta" value={ff5Data?.rmw_beta} />
                  <Stat label="CMA Beta" value={ff5Data?.cma_beta} />
                  <Stat label="Adjusted R-Squared" value={ff5Data?.adjusted_r_squared} suffix="%" transform={(v) => (v || 0) * 100} />
                  <Stat label="Standard Error" value={ff5Data?.standard_error} fractionDigits={4} />
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Factor Exposure Chart */}
      <div className="card">
        <div className="card-body">
          <FactorExposureChart portfolioId={portfolioId} />
        </div>
      </div>

      {/* Factor Correlation */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-lg font-medium text-gray-900">Factor Correlation Matrix</h2>
          <p className="text-sm text-gray-500">
            Inspect how risk factors co-move to manage diversification and avoid unintended bets.
          </p>
        </div>
        <div className="card-body">
          <FactorCorrelationMatrix refreshToken={portfolioId.length} />
        </div>
      </div>
    </div>
  );
};

interface StatProps {
  label: string;
  value?: number;
  suffix?: string;
  fractionDigits?: number;
  transform?: (value?: number) => number;
}

const Stat: React.FC<StatProps> = ({ label, value, suffix = '', fractionDigits = 2, transform }) => {
  const transformedValue = transform ? transform(value) : value;
  return (
    <div className="border rounded-lg p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-lg font-semibold">
        {transformedValue !== undefined && transformedValue !== null
          ? `${transformedValue.toFixed(fractionDigits)}${suffix}`
          : 'N/A'}
      </p>
    </div>
  );
};

export default FactorAnalysis;

