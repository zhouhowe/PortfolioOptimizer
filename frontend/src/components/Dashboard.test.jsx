import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Dashboard from './Dashboard';

describe('Dashboard Component', () => {
  it('renders form inputs correctly', () => {
    render(<Dashboard onSubmit={() => {}} isLoading={false} />);
    
    expect(screen.getByText(/Initial Capital/i)).toBeInTheDocument();
    expect(screen.getByText(/Equity Alloc/i)).toBeInTheDocument();
    expect(screen.getByText(/LEAP Alloc/i)).toBeInTheDocument();
    
    // Check default values
    const capitalInput = screen.getByDisplayValue('100000');
    expect(capitalInput).toBeInTheDocument();
  });

  it('updates form state on input change', () => {
    render(<Dashboard onSubmit={() => {}} isLoading={false} />);
    
    const capitalInput = screen.getByDisplayValue('100000');
    fireEvent.change(capitalInput, { target: { value: '200000' } });
    
    expect(screen.getByDisplayValue('200000')).toBeInTheDocument();
  });

  it('calls onSubmit with form data when submitted', () => {
    const mockOnSubmit = vi.fn();
    render(<Dashboard onSubmit={mockOnSubmit} isLoading={false} />);
    
    const submitButton = screen.getByText(/Run Strategy Backtest/i);
    fireEvent.click(submitButton);
    
    expect(mockOnSubmit).toHaveBeenCalledTimes(1);
    expect(mockOnSubmit).toHaveBeenCalledWith(expect.objectContaining({
      initial_capital: 100000,
      equity_symbol: 'QQQ'
    }));
  });

  it('shows loading state when isLoading is true', () => {
    render(<Dashboard onSubmit={() => {}} isLoading={true} />);
    
    expect(screen.getByText(/Running Backtest.../i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Running Backtest.../i })).toBeDisabled();
  });
});
