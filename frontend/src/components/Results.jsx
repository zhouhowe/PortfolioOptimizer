import React, { useState } from 'react';
import { Line, Bar } from 'react-chartjs-2';
import FinancialChart from './FinancialChart';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const Results = ({ results, onBack }) => {
  if (!results) return null;

  // Calculate Distribution Data if simulation
  const getDistributionData = () => {
    if (!results.final_portfolio_values || results.final_portfolio_values.length === 0) return null;
    
    const values = results.final_portfolio_values;
    const min = Math.min(...values);
    const max = Math.max(...values);
    const bins = 20;
    const step = (max - min) / bins;
    
    const histogram = new Array(bins).fill(0);
    const labels = [];
    
    for (let i = 0; i < bins; i++) {
        const binStart = min + i * step;
        const binEnd = min + (i + 1) * step;
        labels.push(`${(binStart/1000).toFixed(1)}k - ${(binEnd/1000).toFixed(1)}k`);
    }
    
    values.forEach(v => {
        const binIndex = Math.min(Math.floor((v - min) / step), bins - 1);
        histogram[binIndex]++;
    });
    
    return {
        labels,
        datasets: [
            {
                label: 'Frequency',
                data: histogram,
                backgroundColor: 'rgba(79, 70, 229, 0.5)',
                borderColor: 'rgba(79, 70, 229, 1)',
                borderWidth: 1,
            }
        ]
    };
  };

  const distributionData = getDistributionData();

  return (
    <div className="space-y-8">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Backtest Results</h2>
        <div className="space-x-4">
            <button
            onClick={() => {
                const csvContent = "data:text/csv;charset=utf-8," 
                    + "Date,Type,Asset,Quantity,Price,Value,Reason\n"
                    + results.trades.map(t => `${t.date},${t.type},${t.asset},${t.quantity},${t.price},${t.value},${t.reason}`).join("\n");
                const encodedUri = encodeURI(csvContent);
                const link = document.createElement("a");
                link.setAttribute("href", encodedUri);
                link.setAttribute("download", `backtest_results_${results.backtest_id}.csv`);
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }}
            className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
            >
            Export CSV
            </button>
            <button
            onClick={onBack}
            className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300"
            >
            Adjust Strategy
            </button>
        </div>
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

      {/* Financial Chart (Interactive) */}
      <FinancialChart 
        data={results.history} 
        benchmarkData={results.history} 
        equitySymbol={results.params.equity_symbol}
        confidenceIntervals={results.confidence_intervals}
      />

      {/* Distribution Chart (Simulation Only) */}
      {distributionData && (
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200 h-[400px]">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Final Portfolio Value Distribution</h3>
            <Bar 
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { 
                        legend: { display: false },
                        title: { display: false }
                    },
                    scales: {
                        y: { title: { display: true, text: 'Frequency' } },
                        x: { title: { display: true, text: 'Portfolio Value ($)' } }
                    }
                }}
                data={distributionData} 
            />
        </div>
      )}

      {/* Greeks Chart (Historical Only) */}
      {results.history[0].greeks && !results.is_simulation && (
        <div className="bg-white p-4 rounded-lg shadow border border-gray-200 h-[600px]">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Greeks Exposure</h3>
            <Line 
                options={{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: { mode: 'index', intersect: false },
                    layout: {
                        padding: {
                            bottom: 30,
                            left: 10,
                            right: 10
                        }
                    },
                    plugins: { title: { display: false } },
                    scales: { 
                        y: { display: true, title: { display: true, text: 'Value' } },
                        x: { 
                            ticks: { 
                                autoSkip: true
                            } 
                        }
                    },
                    elements: {
                        point: {
                            radius: 0,
                            hitRadius: 10,
                            hoverRadius: 4
                        }
                    }
                }}
                data={{
                    labels: results.history.map(h => h.date),
                    datasets: [
                        { label: 'Delta', data: results.history.map(h => h.greeks.delta), borderColor: '#8884d8', fill: false, pointRadius: 0 },
                        { label: 'Gamma', data: results.history.map(h => h.greeks.gamma), borderColor: '#82ca9d', fill: false, pointRadius: 0 },
                        { label: 'Theta', data: results.history.map(h => h.greeks.theta), borderColor: '#ffc658', fill: false, pointRadius: 0 },
                        { label: 'Vega', data: results.history.map(h => h.greeks.vega), borderColor: '#ff7300', fill: false, pointRadius: 0 },
                    ]
                }} 
            />
        </div>
      )}

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
