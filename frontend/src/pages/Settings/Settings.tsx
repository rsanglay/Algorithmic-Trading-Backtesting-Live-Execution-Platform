import React from 'react';
import { CogIcon, UserIcon, BellIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';

const Settings: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600">Manage your account and application settings</p>
      </div>

      {/* Settings Sections */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Account Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <UserIcon className="w-5 h-5 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900">Account Settings</h3>
            </div>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div>
                <label className="form-label">Full Name</label>
                <input
                  type="text"
                  className="form-input"
                  defaultValue="John Doe"
                />
              </div>
              <div>
                <label className="form-label">Email</label>
                <input
                  type="email"
                  className="form-input"
                  defaultValue="john.doe@example.com"
                />
              </div>
              <div>
                <label className="form-label">Phone</label>
                <input
                  type="tel"
                  className="form-input"
                  defaultValue="+1 (555) 123-4567"
                />
              </div>
              <button className="btn-primary">
                Update Account
              </button>
            </div>
          </div>
        </div>

        {/* Trading Settings */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <CogIcon className="w-5 h-5 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900">Trading Settings</h3>
            </div>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div>
                <label className="form-label">Default Capital</label>
                <input
                  type="number"
                  className="form-input"
                  defaultValue="100000"
                />
              </div>
              <div>
                <label className="form-label">Commission Rate (%)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-input"
                  defaultValue="0.1"
                />
              </div>
              <div>
                <label className="form-label">Slippage (%)</label>
                <input
                  type="number"
                  step="0.01"
                  className="form-input"
                  defaultValue="0.05"
                />
              </div>
              <button className="btn-primary">
                Save Settings
              </button>
            </div>
          </div>
        </div>

        {/* Notifications */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <BellIcon className="w-5 h-5 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900">Notifications</h3>
            </div>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Email Notifications</span>
                <input type="checkbox" className="rounded" defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Strategy Alerts</span>
                <input type="checkbox" className="rounded" defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Risk Warnings</span>
                <input type="checkbox" className="rounded" defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-700">Market Updates</span>
                <input type="checkbox" className="rounded" />
              </div>
              <button className="btn-primary">
                Update Preferences
              </button>
            </div>
          </div>
        </div>

        {/* Security */}
        <div className="card">
          <div className="card-header">
            <div className="flex items-center space-x-2">
              <ShieldCheckIcon className="w-5 h-5 text-gray-400" />
              <h3 className="text-lg font-medium text-gray-900">Security</h3>
            </div>
          </div>
          <div className="card-body">
            <div className="space-y-4">
              <div>
                <label className="form-label">Current Password</label>
                <input
                  type="password"
                  className="form-input"
                  placeholder="Enter current password"
                />
              </div>
              <div>
                <label className="form-label">New Password</label>
                <input
                  type="password"
                  className="form-input"
                  placeholder="Enter new password"
                />
              </div>
              <div>
                <label className="form-label">Confirm Password</label>
                <input
                  type="password"
                  className="form-input"
                  placeholder="Confirm new password"
                />
              </div>
              <button className="btn-primary">
                Change Password
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* API Settings */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">API Configuration</h3>
          <p className="text-sm text-gray-500">Configure external API connections</p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="form-label">Alpha Vantage API Key</label>
              <input
                type="password"
                className="form-input"
                placeholder="Enter API key"
              />
            </div>
            <div>
              <label className="form-label">IEX Cloud API Key</label>
              <input
                type="password"
                className="form-input"
                placeholder="Enter API key"
              />
            </div>
            <div>
              <label className="form-label">Polygon API Key</label>
              <input
                type="password"
                className="form-input"
                placeholder="Enter API key"
              />
            </div>
            <div>
              <label className="form-label">News API Key</label>
              <input
                type="password"
                className="form-input"
                placeholder="Enter API key"
              />
            </div>
          </div>
          <div className="mt-4">
            <button className="btn-primary">
              Save API Keys
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
