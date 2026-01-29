import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock, patch
from app.models import BacktestRequest, BacktestResult, PortfolioSnapshot
from app.services.monte_carlo import MonteCarloSimulator

@pytest.fixture
def sample_request():
    return BacktestRequest(
        equity_symbol="TEST",
        start_date="2023-01-01",
        end_date="2023-01-10",
        initial_capital=100000,
        equity_allocation=60,
        leap_allocation=30,
        use_simulation=True,
        simulation_runs=5,
        simulation_drift=0.1,
        simulation_volatility=0.2
    )

@patch('app.services.monte_carlo.LeapStrategyBacktester')
@patch('app.services.monte_carlo.MarketSimulator')
def test_run_monte_carlo(mock_simulator, mock_backtester_cls, sample_request):
    # Mock MarketSimulator
    mock_df = pd.DataFrame({
        'Close': [100] * 10,
        'Open': [100] * 10,
        'High': [101] * 10,
        'Low': [99] * 10,
        'Volume': [1000] * 10
    }, index=pd.date_range(start="2023-01-01", periods=10))
    mock_simulator.generate_custom_scenario.return_value = mock_df
    
    # Mock BacktestResult
    mock_result = MagicMock(spec=BacktestResult)
    mock_result.history = [
        PortfolioSnapshot(
            date=f"2023-01-{i+1:02d}",
            equity_value=60000,
            leap_value=30000,
            cash_value=10000,
            total_value=100000 + i * 100, # Increasing value
            benchmark_value=100000 + i * 50,
            equity_price=100,
            drawdown=0
        ) for i in range(10)
    ]
    
    # Mock Backtester instance
    mock_backtester_instance = mock_backtester_cls.return_value
    mock_backtester_instance.run_with_data.return_value = mock_result
    
    # Run Monte Carlo
    mc = MonteCarloSimulator(sample_request)
    result = mc.run_monte_carlo()
    
    # Assertions
    assert result.is_simulation is True
    assert result.confidence_intervals is not None
    assert "portfolio" in result.confidence_intervals
    assert "benchmark" in result.confidence_intervals
    assert len(result.final_portfolio_values) == 5
    assert len(result.final_benchmark_values) == 5
    
    # Verify mock calls
    assert mock_simulator.generate_custom_scenario.call_count == 5
    assert mock_backtester_cls.call_count == 5
    assert mock_backtester_instance.run_with_data.call_count == 5

def test_calculate_confidence_intervals():
    # Create dummy results with known values
    results = []
    for i in range(10): # 10 runs
        mock_result = MagicMock(spec=BacktestResult)
        mock_result.history = [
            PortfolioSnapshot(
                date="2023-01-01",
                equity_value=0, leap_value=0, cash_value=0,
                total_value=100 + i, # 100, 101, ..., 109
                benchmark_value=200 + i, # 200, 201, ..., 209
                equity_price=0, drawdown=0
            )
        ]
        results.append(mock_result)
        
    mc = MonteCarloSimulator(MagicMock())
    intervals = mc._calculate_confidence_intervals(results)
    
    # 5th percentile of 0..9 is approx 0.45
    # 95th percentile of 0..9 is approx 8.55
    # Values are 100+i, so 100.45 and 108.55
    
    port_lower = intervals['portfolio']['lower'][0]
    port_upper = intervals['portfolio']['upper'][0]
    
    assert 100 <= port_lower <= 101
    assert 108 <= port_upper <= 109
    
    bench_lower = intervals['benchmark']['lower'][0]
    bench_upper = intervals['benchmark']['upper'][0]
    
    assert 200 <= bench_lower <= 201
    assert 208 <= bench_upper <= 209

def test_prepare_data(sample_request):
    mc = MonteCarloSimulator(sample_request)
    
    # Create dummy DataFrame without volatility
    df = pd.DataFrame({
        'Close': [100, 101, 102, 103, 104, 105] * 5 # 30 days
    }, index=pd.date_range(start="2023-01-01", periods=30))
    
    # Enable wheel strategy to test MA calculation
    sample_request.use_wheel_strategy = True
    sample_request.wheel_ma_short = 5
    sample_request.wheel_ma_long = 10
    
    prepared_df = mc._prepare_data(df, sample_request)
    
    assert 'volatility' in prepared_df.columns
    assert 'ma_short' in prepared_df.columns
    assert 'ma_long' in prepared_df.columns
    assert not prepared_df['volatility'].isna().any()
    assert not prepared_df['ma_short'].isna().any()
