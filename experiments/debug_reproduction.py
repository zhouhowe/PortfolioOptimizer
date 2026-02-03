
import sys
import os
import pandas as pd
from datetime import datetime

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models import BacktestRequest
from app.services.backtest import LeapStrategyBacktester

def run_test():
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

    # Test TSLA
    print("Running TSLA...")
    tsla_params = base_params.copy()
    tsla_params['equity_symbol'] = 'TSLA'
    backtester_tsla = LeapStrategyBacktester(BacktestRequest(**tsla_params))
    result_tsla = backtester_tsla.run()
    print(f"TSLA Return: {result_tsla.total_return}")
    print(f"TSLA Benchmark: {result_tsla.history[-1].benchmark_value}")

    # Test QQQ
    print("\nRunning QQQ...")
    qqq_params = base_params.copy()
    qqq_params['equity_symbol'] = 'QQQ'
    backtester_qqq = LeapStrategyBacktester(BacktestRequest(**qqq_params))
    result_qqq = backtester_qqq.run()
    print(f"QQQ Return: {result_qqq.total_return}")
    print(f"QQQ Benchmark: {result_qqq.history[-1].benchmark_value}")

if __name__ == "__main__":
    run_test()
