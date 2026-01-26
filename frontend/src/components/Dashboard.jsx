import React, { useState } from 'react';
import { Switch } from '@headlessui/react';
import axios from 'axios';
import clsx from 'clsx';

const Dashboard = ({ onSubmit, isLoading, initialData }) => {
  const [formData, setFormData] = useState(initialData || {
    equity_symbol: 'QQQ',
    start_date: '2020-01-01',
    end_date: '2023-12-31',
    initial_capital: 100000,
    equity_allocation: 60,
    leap_allocation: 30,
    leap_delta: 0.7,
    leap_expiration_months: 12,
    rebalance_delta: 5,
    equity_down_trigger: 10,
    equity_up_trigger: 15,
    profit_limit_6m: 50,
    loss_limit_6m: 30,
    profit_limit_3m: 30,
    loss_limit_3m: 20,
    profit_limit_0m: 10,
    loss_limit_0m: 10,
    monthly_withdrawal: 0
  });

  // Update form data if initialData changes (e.g. loaded from library)
  React.useEffect(() => {
    if (initialData) {
        setFormData(initialData);
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  const [isSaving, setIsSaving] = useState(false);
  const [saveName, setSaveName] = useState('');
  const [showSaveModal, setShowSaveModal] = useState(false);

  const handleSaveStrategy = async () => {
    if (!saveName) return;
    setIsSaving(true);
    try {
        await axios.post('http://localhost:8000/api/strategies', {
            name: saveName,
            description: `Strategy for ${formData.equity_symbol} (${formData.start_date} - ${formData.end_date})`,
            parameters: formData
        });
        setShowSaveModal(false);
        setSaveName('');
        alert('Strategy saved successfully!');
    } catch (err) {
        console.error(err);
        alert('Failed to save strategy');
    } finally {
        setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
    <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow border border-gray-200 space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Core Strategy */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Strategy Configuration</h3>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Target Equity</label>
            <select name="equity_symbol" value={formData.equity_symbol} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm border p-2">
              <option value="QQQ">QQQ (Nasdaq 100)</option>
              <option value="TSLA">TSLA (Tesla)</option>
              <option value="SPY">SPY (S&P 500)</option>
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Start Date</label>
              <input type="date" name="start_date" value={formData.start_date} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">End Date</label>
              <input type="date" name="end_date" value={formData.end_date} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" required />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Initial Capital ($)</label>
            <input type="number" name="initial_capital" value={formData.initial_capital} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" required />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Equity Alloc (%)</label>
              <input type="number" name="equity_allocation" value={formData.equity_allocation} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">LEAP Alloc (%)</label>
              <input type="number" name="leap_allocation" value={formData.leap_allocation} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
            </div>
          </div>
          <p className="text-sm text-gray-500">Cash Allocation: {100 - formData.equity_allocation - formData.leap_allocation}%</p>
        </div>

        {/* LEAP Parameters */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900 border-b pb-2">LEAP Settings</h3>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Target Delta</label>
              <input type="number" step="0.05" name="leap_delta" value={formData.leap_delta} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Expiry (Months)</label>
              <input type="number" name="leap_expiration_months" value={formData.leap_expiration_months} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Monthly Withdrawal ($)</label>
            <input type="number" name="monthly_withdrawal" value={formData.monthly_withdrawal} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
          </div>
        </div>

        {/* Rebalancing Rules */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Rebalancing Triggers</h3>
          
          <div className="grid grid-cols-3 gap-4">
             <div>
              <label className="block text-sm font-medium text-gray-700">Alloc Drift (%)</label>
              <input type="number" name="rebalance_delta" value={formData.rebalance_delta} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Equity Down (%)</label>
              <input type="number" name="equity_down_trigger" value={formData.equity_down_trigger} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700">Equity Up (%)</label>
              <input type="number" name="equity_up_trigger" value={formData.equity_up_trigger} onChange={handleChange} className="mt-1 block w-full rounded-md border-gray-300 shadow-sm border p-2" />
            </div>
          </div>
        </div>

        {/* Profit Limits */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900 border-b pb-2">Profit/Loss Limits</h3>
          
          <div className="grid grid-cols-2 gap-x-4 gap-y-2">
            <p className="col-span-2 text-sm font-medium text-gray-500"> Over 6 Months</p>
            <div>
              <label className="block text-xs text-gray-500">Profit %</label>
              <input type="number" name="profit_limit_6m" value={formData.profit_limit_6m} onChange={handleChange} className="block w-full rounded-md border-gray-300 shadow-sm border p-1" />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Loss %</label>
              <input type="number" name="loss_limit_6m" value={formData.loss_limit_6m} onChange={handleChange} className="block w-full rounded-md border-gray-300 shadow-sm border p-1" />
            </div>

            <p className="col-span-2 text-sm font-medium text-gray-500 mt-2">3-6 Months</p>
            <div>
              <label className="block text-xs text-gray-500">Profit %</label>
              <input type="number" name="profit_limit_3m" value={formData.profit_limit_3m} onChange={handleChange} className="block w-full rounded-md border-gray-300 shadow-sm border p-1" />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Loss %</label>
              <input type="number" name="loss_limit_3m" value={formData.loss_limit_3m} onChange={handleChange} className="block w-full rounded-md border-gray-300 shadow-sm border p-1" />
            </div>
            
            <p className="col-span-2 text-sm font-medium text-gray-500 mt-2">&lt; 3 Months</p>
            <div>
              <label className="block text-xs text-gray-500">Profit %</label>
              <input type="number" name="profit_limit_0m" value={formData.profit_limit_0m} onChange={handleChange} className="block w-full rounded-md border-gray-300 shadow-sm border p-1" />
            </div>
            <div>
              <label className="block text-xs text-gray-500">Loss %</label>
              <input type="number" name="loss_limit_0m" value={formData.loss_limit_0m} onChange={handleChange} className="block w-full rounded-md border-gray-300 shadow-sm border p-1" />
            </div>
          </div>
        </div>

      </div>

      <div className="flex justify-between pt-4">
        <button
            type="button"
            onClick={() => setShowSaveModal(true)}
            className="inline-flex justify-center py-3 px-6 border border-gray-300 shadow-sm text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
            Save Strategy
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex justify-center py-3 px-6 border border-transparent shadow-sm text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Running Backtest...' : 'Run Strategy Backtest'}
        </button>
      </div>
    </form>

    {showSaveModal && (
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-sm w-full">
                <h3 className="text-lg font-medium text-gray-900 mb-4">Save Strategy</h3>
                <input
                    type="text"
                    placeholder="Strategy Name"
                    value={saveName}
                    onChange={(e) => setSaveName(e.target.value)}
                    className="block w-full rounded-md border-gray-300 shadow-sm border p-2 mb-4"
                />
                <div className="flex justify-end space-x-3">
                    <button
                        onClick={() => setShowSaveModal(false)}
                        className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                    >
                        Cancel
                    </button>
                    <button
                        onClick={handleSaveStrategy}
                        disabled={!saveName || isSaving}
                        className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 disabled:opacity-50"
                    >
                        {isSaving ? 'Saving...' : 'Save'}
                    </button>
                </div>
            </div>
        </div>
    )}
    </div>
  );
};

export default Dashboard;
