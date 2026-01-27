import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Results from './Results';

// Mock child components that rely on Canvas/ResizeObserver
vi.mock('./FinancialChart', () => ({
  default: () => <div data-testid="financial-chart">Mock Financial Chart</div>
}));

vi.mock('react-chartjs-2', () => ({
  Line: () => <div data-testid="greeks-chart">Mock Greeks Chart</div>
}));

const mockResults = {
  backtest_id: "test-id",
  params: { equity_symbol: "QQQ" },
  total_return: 15.5,
  cagr: 10.2,
  max_drawdown: 5.5,
  sharpe_ratio: 1.8,
  trades: [
    {
      date: "2023-01-01",
      type: "BUY",
      asset: "EQUITY",
      quantity: 10,
      price: 100,
      value: 1000,
      reason: "Initial"
    },
    {
      date: "2023-06-01",
      type: "SELL",
      asset: "LEAP",
      quantity: 1,
      price: 500,
      value: 500,
      reason: "Profit"
    }
  ],
  history: [
    {
      date: "2023-01-01",
      total_value: 100000,
      greeks: { delta: 100, gamma: 0.1, theta: -5, vega: 20 }
    }
  ]
};

describe('Results Component', () => {
  it('renders metrics correctly', () => {
    render(<Results results={mockResults} onBack={() => {}} />);
    
    expect(screen.getByText('15.5%')).toBeInTheDocument(); // Total Return
    expect(screen.getByText('10.2%')).toBeInTheDocument(); // CAGR
    expect(screen.getByText('5.5%')).toBeInTheDocument(); // Max Drawdown
    expect(screen.getByText('1.8')).toBeInTheDocument(); // Sharpe Ratio
  });

  it('renders trade history table', () => {
    render(<Results results={mockResults} onBack={() => {}} />);
    
    expect(screen.getByText('Trade History')).toBeInTheDocument();
    expect(screen.getByText('BUY')).toBeInTheDocument();
    expect(screen.getByText('SELL')).toBeInTheDocument();
    expect(screen.getByText('$1000.00')).toBeInTheDocument();
  });

  it('renders mocked charts', () => {
    render(<Results results={mockResults} onBack={() => {}} />);
    
    expect(screen.getByTestId('financial-chart')).toBeInTheDocument();
    expect(screen.getByTestId('greeks-chart')).toBeInTheDocument();
  });
});
