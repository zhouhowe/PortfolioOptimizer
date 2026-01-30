#!/usr/bin/env python3
"""
Formal test for benchmark withdrawal logic implementation.
Tests fair comparison between portfolio and benchmark with monthly withdrawals.
"""

import sys
import os
import unittest
from unittest.mock import MagicMock
import pandas as pd
import numpy as np

# Mock yfinance before importing app.services.backtest
sys.modules['yfinance'] = MagicMock()

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models import BacktestRequest
from app.services.backtest import LeapStrategyBacktester

class TestBenchmarkWithdrawal(unittest.TestCase):
    """Test cases for benchmark withdrawal logic implementation."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.params = BacktestRequest(
            equity_symbol="SPY",
            start_date="2023-01-01",
            end_date="2023-12-31",
            initial_capital=100000,
            monthly_withdrawal=1000,  # $1,000 monthly withdrawal
            equity_allocation=60,
            leap_allocation=40,
            leap_delta=0.7,
            leap_expiration_months=12,
            rebalance_frequency_months=3,
            use_wheel_strategy=False,
            wheel_allocation=0,
            wheel_delta=0.3,
            wheel_ma_short=20,
            wheel_ma_long=50,
            use_simulation=True,
            simulation_scenario="bullish"
        )
        self.backtester = LeapStrategyBacktester(self.params)
        
        # Create mock data
        self.dates = pd.date_range(start="2023-01-01", periods=10)
        self.mock_data = pd.DataFrame({
            'Close': [100.0] * 10,
            'volatility': [0.2] * 10
        }, index=self.dates)
        self.mock_data['returns'] = 0.0
        
        self.current_price = 100.0
        self.first_date = self.dates[0]
        self.first_row = self.mock_data.iloc[0]
    
    def test_benchmark_initialization(self):
        """Test that benchmark state is properly initialized."""
        self.backtester._initial_allocation(self.first_date, self.first_row)
        
        # Check that benchmark shares are initialized correctly
        expected_shares = self.params.initial_capital / self.current_price
        self.assertAlmostEqual(self.backtester.benchmark['shares'], expected_shares)
        
        # Check that benchmark cash starts at 0
        self.assertEqual(self.backtester.benchmark['cash'], 0.0)
    
    def test_benchmark_withdrawal_logic(self):
        """Test that benchmark withdrawal logic correctly reduces shares."""
        self.backtester._initial_allocation(self.first_date, self.first_row)
        
        # Force a month change to trigger withdrawal
        self.backtester.last_withdrawal_month = 12  # Previous month was 12
        
        # Record initial shares
        initial_shares = self.backtester.benchmark['shares']
        
        # Apply withdrawal
        self.backtester._check_monthly_withdrawal(self.first_date, self.current_price)
        
        # Calculate expected shares after withdrawal
        shares_to_sell = self.params.monthly_withdrawal / self.current_price
        expected_shares = initial_shares - shares_to_sell
        
        # Verify shares were reduced correctly
        self.assertAlmostEqual(self.backtester.benchmark['shares'], expected_shares)
    
    def test_benchmark_value_calculation(self):
        """Test that benchmark value calculation reflects withdrawals."""
        self.backtester._initial_allocation(self.first_date, self.first_row)
        
        # Force a month change to trigger withdrawal
        self.backtester.last_withdrawal_month = 12
        self.backtester._check_monthly_withdrawal(self.first_date, self.current_price)
        
        # Calculate benchmark value
        benchmark_val = self.backtester.benchmark['shares'] * self.current_price
        
        # Expected value after withdrawal
        expected_val = self.params.initial_capital - self.params.monthly_withdrawal
        
        # Verify benchmark value is correct
        self.assertAlmostEqual(benchmark_val, expected_val)
    
    def test_multiple_withdrawals(self):
        """Test that multiple withdrawals correctly reduce benchmark shares."""
        self.backtester._initial_allocation(self.first_date, self.first_row)
        
        # Apply first withdrawal (month 1)
        # Simulate that we haven't withdrawn for January yet (last withdrawal was Dec)
        self.backtester.last_withdrawal_month = 12
        self.backtester._check_monthly_withdrawal(self.first_date, self.current_price)
        
        # Apply second withdrawal (month 2)
        # Create a date in February
        second_date = pd.Timestamp("2023-02-01")
        # The first withdrawal set last_withdrawal_month to 1.
        # Now current_month is 2, so 1 != 2, it should withdraw.
        self.backtester._check_monthly_withdrawal(second_date, self.current_price)
        
        # Calculate expected shares after two withdrawals
        shares_per_withdrawal = self.params.monthly_withdrawal / self.current_price
        initial_shares = self.params.initial_capital / self.current_price
        expected_shares = initial_shares - (2 * shares_per_withdrawal)
        
        # Verify shares were reduced correctly
        self.assertAlmostEqual(self.backtester.benchmark['shares'], expected_shares)
    
    def test_no_withdrawal_when_zero(self):
        """Test that no withdrawal occurs when monthly_withdrawal is 0."""
        # Create params with no withdrawal
        params_no_withdrawal = self.params.copy()
        params_no_withdrawal.monthly_withdrawal = 0
        backtester_no_withdrawal = LeapStrategyBacktester(params_no_withdrawal)
        
        backtester_no_withdrawal._initial_allocation(self.first_date, self.first_row)
        initial_shares = backtester_no_withdrawal.benchmark['shares']
        
        # Try to apply withdrawal (should not do anything)
        backtester_no_withdrawal._check_monthly_withdrawal(self.first_date, self.current_price)
        
        # Shares should remain unchanged
        self.assertAlmostEqual(backtester_no_withdrawal.benchmark['shares'], initial_shares)

if __name__ == "__main__":
    unittest.main()