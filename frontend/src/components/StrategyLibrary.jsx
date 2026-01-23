import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrashIcon, PlayIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

const StrategyLibrary = ({ onLoadStrategy }) => {
  const [strategies, setStrategies] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchStrategies = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/api/strategies');
      setStrategies(response.data);
    } catch (error) {
      console.error('Error fetching strategies:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStrategies();
  }, []);

  const handleDelete = async (id) => {
    if (!confirm('Are you sure you want to delete this strategy?')) return;
    try {
      await axios.delete(`http://localhost:8000/api/strategies/${id}`);
      fetchStrategies();
    } catch (error) {
      console.error('Error deleting strategy:', error);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold text-gray-900">Strategy Library</h2>
        <button 
          onClick={fetchStrategies}
          className="p-2 text-gray-500 hover:text-gray-700"
          title="Refresh"
        >
          <ArrowPathIcon className="h-5 w-5" />
        </button>
      </div>

      {isLoading ? (
        <div className="text-center py-4">Loading...</div>
      ) : strategies.length === 0 ? (
        <div className="text-center py-8 text-gray-500 bg-gray-50 rounded-lg border border-dashed border-gray-300">
          No saved strategies yet. Run a backtest and save it!
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {strategies.map((strategy) => (
            <div key={strategy.id} className="bg-white p-4 rounded-lg shadow border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-lg text-gray-900 truncate" title={strategy.name}>
                  {strategy.name}
                </h3>
                <div className="flex space-x-2">
                  <button
                    onClick={() => onLoadStrategy(strategy.parameters)}
                    className="p-1 text-blue-600 hover:text-blue-800"
                    title="Load Strategy"
                  >
                    <PlayIcon className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => handleDelete(strategy.id)}
                    className="p-1 text-red-600 hover:text-red-800"
                    title="Delete"
                  >
                    <TrashIcon className="h-5 w-5" />
                  </button>
                </div>
              </div>
              
              <p className="text-sm text-gray-500 mb-3 line-clamp-2 h-10">
                {strategy.description || 'No description'}
              </p>
              
              <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded">
                <div className="flex justify-between">
                    <span>Equity: {strategy.parameters.equity_symbol}</span>
                    <span>Alloc: {strategy.parameters.equity_allocation}/{strategy.parameters.leap_allocation}</span>
                </div>
                <div className="mt-1">
                    <span>Created: {new Date(strategy.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default StrategyLibrary;
