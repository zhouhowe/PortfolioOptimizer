import React, { useState } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import Results from './components/Results';

function App() {
  const [results, setResults] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRunBacktest = async (params) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post('http://localhost:8000/api/backtest/run', params);
      setResults(response.data);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'An error occurred while running the backtest.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Strategy Optimizer <span className="text-sm font-normal text-gray-500 ml-2">v1.0 (P0)</span>
          </h1>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {error && (
            <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
              <strong className="font-bold">Error: </strong>
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          {!results ? (
            <Dashboard onSubmit={handleRunBacktest} isLoading={isLoading} />
          ) : (
            <Results results={results} onBack={handleReset} />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
