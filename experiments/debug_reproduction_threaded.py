
import sys
import os
import pandas as pd
from datetime import datetime
import concurrent.futures
import time

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models import BacktestRequest
from app.services.backtest import LeapStrategyBacktester

def run_single_test(symbol):
    base_params = {
        'start_date': '2020-01-01',
        'end_date': '2023-12-31',
        'initial_capital': 100000,
        'use_simulation': False,
        'monthly_withdrawal': 0,
        'use_wheel_strategy': False,
        'wheel_allocation': 0,
        'wheel_ma_short': 10,
        'wheel_ma_long': 30,
        'rebalance_delta': 5.0,
        'equity_down_trigger': 10.0,
        'equity_up_trigger': 15.0,
        'profit_limit_6m': 100.0,
        'loss_limit_6m': 60.0,
        'profit_limit_3m': 30.0,
        'loss_limit_3m': 20.0,
        'profit_limit_0m': 10.0,
        'loss_limit_0m': 20.0,
        'equity_allocation': 60,
        'leap_allocation': 30,
        'leap_delta': 0.4,
        'leap_expiration_months': 18,
    }
    
    params = base_params.copy()
    params['equity_symbol'] = symbol
    
    print(f"Starting {symbol}...")
    backtester = LeapStrategyBacktester(BacktestRequest(**params))
    result = backtester.run()
    print(f"Finished {symbol}: Return={result.total_return}")
    return symbol, result.total_return

def run_threaded_test():
    symbols = ['TSLA', 'QQQ', 'TSLA', 'QQQ']
    
    print("Running threaded test...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(run_single_test, sym) for sym in symbols]
        
        for future in concurrent.futures.as_completed(futures):
            sym, ret = future.result()
            print(f"Result: {sym} -> {ret}")

if __name__ == "__main__":
    run_threaded_test()
