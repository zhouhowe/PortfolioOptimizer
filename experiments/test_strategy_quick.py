#!/usr/bin/env python3
"""
Quick Test Script for Strategy Optimization

This script tests a small subset of parameter combinations to validate the experiment framework.
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models import BacktestRequest
from app.services.backtest import LeapStrategyBacktester

def run_quick_test():
    """Run a quick test with a few parameter combinations"""
    
    print("Running Quick Strategy Test...")
    print("=" * 40)
    
    # Test parameters
    test_configs = [
        {
            'equity_symbol': 'TSLA',
            'equity_allocation': 60,
            'leap_allocation': 30,
            'leap_delta': 0.5,
            'leap_expiration_months': 12,
            'start_date': '2020-01-01',
            'end_date': '2021-12-31',  # Shorter period for quick test
            'initial_capital': 100000,
            'use_simulation': False,
            'monthly_withdrawal': 0,
            'use_wheel_strategy': False,
            'wheel_allocation': 0,
            'rebalance_delta': 5.0,
            'equity_down_trigger': 10.0,
            'equity_up_trigger': 15.0,
            'profit_limit_6m': 100.0,
            'loss_limit_6m': 60.0,
            'profit_limit_3m': 30.0,
            'loss_limit_3m': 20.0,
            'profit_limit_0m': 10.0,
            'loss_limit_0m': 20.0,
        },
        {
            'equity_symbol': 'QQQ',
            'equity_allocation': 50,
            'leap_allocation': 35,
            'leap_delta': 0.6,
            'leap_expiration_months': 18,
            'start_date': '2020-01-01',
            'end_date': '2021-12-31',
            'initial_capital': 100000,
            'use_simulation': False,
            'monthly_withdrawal': 0,
            'use_wheel_strategy': False,
            'wheel_allocation': 0,
            'rebalance_delta': 5.0,
            'equity_down_trigger': 10.0,
            'equity_up_trigger': 15.0,
            'profit_limit_6m': 100.0,
            'loss_limit_6m': 60.0,
            'profit_limit_3m': 30.0,
            'loss_limit_3m': 20.0,
            'profit_limit_0m': 10.0,
            'loss_limit_0m': 20.0,
        }
    ]
    
    results = []
    
    for i, params in enumerate(test_configs):
        print(f"\nTest {i+1}: {params['equity_symbol']} - {params['equity_allocation']}% Equity, {params['leap_allocation']}% LEAP")
        
        try:
            # Create BacktestRequest
            request = BacktestRequest(**params)
            
            # Create backtester and run
            backtester = LeapStrategyBacktester(request)
            result = backtester.run()
            
            # Extract metrics
            metrics = {
                'symbol': params['equity_symbol'],
                'equity_allocation': params['equity_allocation'],
                'leap_allocation': params['leap_allocation'],
                'leap_delta': params['leap_delta'],
                'leap_expiry': params['leap_expiration_months'],
                'total_return': result.total_return,
                'cagr': result.cagr,
                'max_drawdown': result.max_drawdown,
                'sharpe_ratio': result.sharpe_ratio,
                'num_trades': len(result.trades),
                'final_value': result.history[-1].total_value if result.history else params['initial_capital'],
                'benchmark_return': ((result.history[-1].benchmark_value - params['initial_capital']) / params['initial_capital'] * 100) if result.history else 0,
                'excess_return': 0,
                'success': True,
                'error': None
            }
            
            # Calculate excess return
            metrics['excess_return'] = metrics['total_return'] - metrics['benchmark_return']
            
            print(f"  Total Return: {metrics['total_return']:.2f}%")
            print(f"  CAGR: {metrics['cagr']:.2f}%")
            print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
            print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")
            print(f"  Excess Return: {metrics['excess_return']:.2f}%")
            print(f"  Number of Trades: {metrics['num_trades']}")
            
            results.append(metrics)
            
        except Exception as e:
            print(f"  ERROR: {str(e)}")
            results.append({
                'symbol': params['equity_symbol'],
                'equity_allocation': params['equity_allocation'],
                'leap_allocation': params['leap_allocation'],
                'leap_delta': params['leap_delta'],
                'leap_expiry': params['leap_expiration_months'],
                'total_return': 0,
                'cagr': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0,
                'num_trades': 0,
                'final_value': params['initial_capital'],
                'benchmark_return': 0,
                'excess_return': 0,
                'success': False,
                'error': str(e)
            })
    
    # Create summary
    print(f"\n{'='*40}")
    print("TEST SUMMARY")
    print(f"{'='*40}")
    
    successful = [r for r in results if r['success']]
    
    if successful:
        best_return = max(successful, key=lambda x: x['total_return'])
        best_sharpe = max(successful, key=lambda x: x['sharpe_ratio'])
        lowest_dd = min(successful, key=lambda x: x['max_drawdown'])
        
        print(f"Best Total Return: {best_return['symbol']} - {best_return['total_return']:.2f}%")
        print(f"Best Sharpe Ratio: {best_sharpe['symbol']} - {best_sharpe['sharpe_ratio']:.3f}")
        print(f"Lowest Drawdown: {lowest_dd['symbol']} - {lowest_dd['max_drawdown']:.2f}%")
        
        # Create comparison table
        df = pd.DataFrame(results)
        print(f"\n{'='*40}")
        print("DETAILED RESULTS")
        print(f"{'='*40}")
        print(df[['symbol', 'equity_allocation', 'leap_allocation', 'leap_delta', 
                  'total_return', 'cagr', 'sharpe_ratio', 'max_drawdown']].round(2))
    
    return results

if __name__ == "__main__":
    run_quick_test()