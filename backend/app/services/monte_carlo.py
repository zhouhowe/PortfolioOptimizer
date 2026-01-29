import numpy as np
from typing import List, Dict
from app.models import BacktestRequest, BacktestResult
from app.services.backtest import LeapStrategyBacktester
from app.services.simulator import MarketSimulator
from datetime import datetime
import pandas as pd

class MonteCarloSimulator:
    def __init__(self, params: BacktestRequest):
        self.params = params
        
    def run_monte_carlo(self) -> BacktestResult:
        """
        Run multiple backtest simulations using Monte Carlo method.
        """
        all_results = []
        all_final_portfolio_values = []
        all_final_benchmark_values = []
        
        # Run simulations
        for run in range(self.params.simulation_runs):
            # Create a copy of params for this run
            run_params = self.params.model_copy()
            run_params.simulation_runs = 1  # Set to 1 for individual run
            
            # Generate custom scenario with specified drift and volatility
            if run_params.simulation_drift is not None and run_params.simulation_volatility is not None:
                # Use custom parameters
                scenario_data = MarketSimulator.generate_custom_scenario(
                    run_params.equity_symbol,
                    run_params.start_date,
                    run_params.end_date,
                    run_params.simulation_drift,
                    run_params.simulation_volatility
                )
            else:
                # Fallback to predefined scenario
                scenario_data = MarketSimulator.generate_scenario(
                    run_params.equity_symbol,
                    run_params.start_date,
                    run_params.end_date,
                    run_params.simulation_scenario
                )
            
            # Prepare data (calculate volatility and moving averages)
            scenario_data = self._prepare_data(scenario_data, run_params)

            # Run backtest with this scenario
            backtester = LeapStrategyBacktester(run_params)
            result = backtester.run_with_data(scenario_data)
            
            all_results.append(result)
            all_final_portfolio_values.append(result.history[-1].total_value)
            all_final_benchmark_values.append(result.history[-1].benchmark_value)
        
        # Calculate confidence intervals and statistics
        confidence_intervals = self._calculate_confidence_intervals(all_results)
        
        # Use the first result as the base and add Monte Carlo statistics
        base_result = all_results[0]
        base_result.confidence_intervals = confidence_intervals
        base_result.final_portfolio_values = all_final_portfolio_values
        base_result.final_benchmark_values = all_final_benchmark_values
        base_result.is_simulation = True
        
        return base_result

    def _prepare_data(self, data: pd.DataFrame, params: BacktestRequest) -> pd.DataFrame:
        """
        Calculate volatility and moving averages for the simulated data.
        """
        # Calculate volatility
        data['returns'] = data['Close'].pct_change()
        data['volatility'] = data['returns'].rolling(window=21).std() * np.sqrt(252)
        
        # Fill NaN volatility with mean or default
        data['volatility'] = data['volatility'].bfill().fillna(0.20)
        
        # Calculate Moving Averages for Wheel Strategy if enabled
        if params.use_wheel_strategy:
            data['ma_short'] = data['Close'].rolling(window=params.wheel_ma_short).mean()
            data['ma_long'] = data['Close'].rolling(window=params.wheel_ma_long).mean()
            
            # Fill NaNs for MAs
            data['ma_short'] = data['ma_short'].bfill()
            data['ma_long'] = data['ma_long'].bfill()
            
        return data
    
    def _calculate_confidence_intervals(self, results: List[BacktestResult]) -> Dict[str, Dict[str, float]]:
        """
        Calculate confidence intervals for portfolio and benchmark values over time.
        """
        # Get all portfolio and benchmark values at each time point
        portfolio_values = []
        benchmark_values = []
        
        # Assume all results have the same time points
        num_time_points = len(results[0].history)
        
        for i in range(num_time_points):
            portfolio_at_time = [result.history[i].total_value for result in results]
            benchmark_at_time = [result.history[i].benchmark_value for result in results]
            
            portfolio_values.append(portfolio_at_time)
            benchmark_values.append(benchmark_at_time)
        
        # Calculate 5th and 95th percentiles for each time point
        portfolio_lower = [np.percentile(values, 5) for values in portfolio_values]
        portfolio_upper = [np.percentile(values, 95) for values in portfolio_values]
        benchmark_lower = [np.percentile(values, 5) for values in benchmark_values]
        benchmark_upper = [np.percentile(values, 95) for values in benchmark_values]
        
        return {
            "portfolio": {"lower": portfolio_lower, "upper": portfolio_upper},
            "benchmark": {"lower": benchmark_lower, "upper": benchmark_upper}
        }