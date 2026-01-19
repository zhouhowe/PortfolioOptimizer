import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const Results = ({ results, onBack }) => {
  if (!results) return null;

  const chartData = {
    labels: results.history.map(h => h.date),
    datasets: [
      {
        label: 'Portfolio Value ($)',
        data: results.history.map(h => h.total_value),
        borderColor: '#1E3A8A',
        backgroundColor: 'rgba(30, 58, 138, 0.5)',
        yAxisID: 'y',
      },
      {
        label: 'Drawdown (%)',
        data: results.history.map(h => h.drawdown * 100),
        borderColor: '#DC2626',
        backgroundColor: 'rgba(220, 38, 38, 0.5)',
        yAxisID: 'y1',
        borderDash: [5, 5],
      },
    ],
  };

  const options = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: `Backtest Results: ${results.params.equity_symbol} (${results.params.start_date} to ${results.params.end_date})`,
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: { display: true, text: 'Portfolio Value ($)' }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: {
          drawOnChartArea: false,
        },
        title: { display: true, text: 'Drawdown (%)' }
      },
    },
  };

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Backtest Results</h2>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
        >
          Adjust Strategy
        </button>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <p className="text-sm text-gray-500">Total Return</p>
          <p className={`text-2xl font-bold ${results.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {results.total_return}%
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <p className="text-sm text-gray-500">CAGR</p>
          <p className={`text-2xl font-bold ${results.cagr >= 0 ? 'text-green-600' : 'text-red-600'}`}>
            {results.cagr}%
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <p className="text-sm text-gray-500">Max Drawdown</p>
          <p className="text-2xl font-bold text-red-600">
            {results.max_drawdown}%
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200">
          <p className="text-sm text-gray-500">Sharpe Ratio</p>
          <p className="text-2xl font-bold text-gray-900">
            {results.sharpe_ratio}
          </p>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-white p-4 rounded-lg shadow border border-gray-200 h-96">
        <Line options={options} data={chartData} />
      </div>

      {/* Trades Table */}
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <div className="px-4 py-5 sm:px-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Trade History</h3>
        </div>
        <div className="overflow-x-auto max-h-96">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Type</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Asset</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Qty</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Reason</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {results.trades.map((trade, idx) => (
                <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.date}</td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${trade.type === 'BUY' ? 'text-green-600' : trade.type === 'SELL' ? 'text-red-600' : 'text-gray-600'}`}>
                    {trade.type}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.asset}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.quantity.toFixed(4)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${trade.price.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${trade.value.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{trade.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default Results;
