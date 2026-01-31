#!/usr/bin/env python3
"""
Strategy Optimization Experiment Runner

This script systematically tests different parameter combinations for the One Stock + LEAP Option Portfolio strategy.
It runs backtests across multiple parameter configurations and generates comprehensive performance analysis.
"""

import pandas as pd
import numpy as np
import json
import time
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any, Tuple
import sys
import os

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.models import BacktestRequest
from app.services.backtest import LeapStrategyBacktester

class StrategyExperiment:
    def __init__(self):
        self.results = []
        self.experiment_configs = []
        
    def generate_parameter_combinations(self) -> List[Dict[str, Any]]:
        """Generate all parameter combinations for testing"""
        
        # Base parameters
        base_params = {
            'start_date': '2020-01-01',
            'end_date': '2025-12-31',
            'initial_capital': 100000,
            'use_simulation': False,
            'monthly_withdrawal': 0,
            'use_wheel_strategy': False,
            'wheel_allocation': 0,
            'wheel_ma_short': 10,
            'wheel_ma_long': 30
        }
        
        # Parameter ranges
        equity_symbols = ['TSLA', 'QQQ']
        
        # Allocation combinations (equity %, leap %, cash %)
        allocation_combinations = [
            (60, 30, 10),  # 60% equity + 30% LEAP + 10% cash
            (60, 35, 5),   # 60% equity + 35% LEAP + 5% cash
            (50, 35, 15),  # 50% equity + 35% LEAP + 15% cash
            (65, 25, 10),  # 65% equity + 25% LEAP + 10% cash
        ]
        
        # Rebalancing triggers
        rebalance_deltas = [5.0]  # Allocation drift trigger
        equity_down_triggers = [10.0]  # Equity down trigger
        equity_up_triggers = [15.0]  # Equity up trigger
        
        # LEAP parameters
        leap_deltas = [0.4, 0.5, 0.6]
        leap_expirations = [12, 18]  # months
        
        # Profit/loss limits
        profit_limits_6m = [100.0]
        loss_limits_6m = [60.0]
        profit_limits_3m = [30.0]
        loss_limits_3m = [20.0]
        profit_limits_0m = [10.0]
        loss_limits_0m = [20.0]
        
        combinations = []
        
        # Generate all combinations
        for symbol in equity_symbols:
            for equity_pct, leap_pct, cash_pct in allocation_combinations:
                for leap_delta in leap_deltas:
                    for leap_expiry in leap_expirations:
                        for rebalance_delta in rebalance_deltas:
                            for eq_down in equity_down_triggers:
                                for eq_up in equity_up_triggers:
                                    for p6m in profit_limits_6m:
                                        for l6m in loss_limits_6m:
                                            for p3m in profit_limits_3m:
                                                for l3m in loss_limits_3m:
                                                    for p0m in profit_limits_0m:
                                                        for l0m in loss_limits_0m:
                                                            config = base_params.copy()
                                                            config.update({
                                                                'equity_symbol': symbol,
                                                                'equity_allocation': equity_pct,
                                                                'leap_allocation': leap_pct,
                                                                'leap_delta': leap_delta,
                                                                'leap_expiration_months': leap_expiry,
                                                                'rebalance_delta': rebalance_delta,
                                                                'equity_down_trigger': eq_down,
                                                                'equity_up_trigger': eq_up,
                                                                'profit_limit_6m': p6m,
                                                                'loss_limit_6m': l6m,
                                                                'profit_limit_3m': p3m,
                                                                'loss_limit_3m': l3m,
                                                                'profit_limit_0m': p0m,
                                                                'loss_limit_0m': l0m,
                                                            })
                                                            combinations.append(config)
        
        print(f"Generated {len(combinations)} parameter combinations")
        return combinations
    
    def run_single_backtest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single backtest with given parameters"""
        try:
            # Create BacktestRequest
            request = BacktestRequest(**params)
            
            # Create backtester and run
            backtester = LeapStrategyBacktester(request)
            result = backtester.run()
            
            # Extract key metrics
            metrics = {
                'params': params,
                'total_return': result.total_return,
                'cagr': result.cagr,
                'max_drawdown': result.max_drawdown,
                'sharpe_ratio': result.sharpe_ratio,
                'num_trades': len(result.trades),
                'final_value': result.history[-1].total_value if result.history else params['initial_capital'],
                'benchmark_return': ((result.history[-1].benchmark_value - params['initial_capital']) / params['initial_capital'] * 100) if result.history else 0,
                'excess_return': 0,  # Will calculate later
                'success': True,
                'error': None
            }
            
            # Calculate excess return over benchmark
            metrics['excess_return'] = metrics['total_return'] - metrics['benchmark_return']
            
            return metrics
            
        except Exception as e:
            print(f"Error running backtest: {str(e)}")
            return {
                'params': params,
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
            }
    
    def run_experiments(self, max_workers: int = 4, limit: int = None) -> pd.DataFrame:
        """Run all experiments in parallel"""
        
        # Generate parameter combinations
        combinations = self.generate_parameter_combinations()
        
        if limit:
            combinations = combinations[:limit]
            print(f"Limited to first {limit} combinations")
        
        print(f"Running {len(combinations)} backtests with {max_workers} workers...")
        
        start_time = time.time()
        
        # Run experiments in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.run_single_backtest, params) for params in combinations]
            
            results = []
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                result = future.result()
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed
                    remaining = (len(combinations) - (i + 1)) / rate
                    print(f"Progress: {i + 1}/{len(combinations)} completed, "
                          f"Rate: {rate:.2f} tests/min, "
                          f"ETA: {remaining/60:.1f} minutes")
        
        elapsed = time.time() - start_time
        print(f"Completed {len(results)} backtests in {elapsed/60:.1f} minutes")
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        # Add parameter columns for easier analysis
        df['equity_symbol'] = df['params'].apply(lambda x: x['equity_symbol'])
        df['equity_allocation'] = df['params'].apply(lambda x: x['equity_allocation'])
        df['leap_allocation'] = df['params'].apply(lambda x: x['leap_allocation'])
        df['leap_delta'] = df['params'].apply(lambda x: x['leap_delta'])
        df['leap_expiration_months'] = df['params'].apply(lambda x: x['leap_expiration_months'])
        
        return df
    
    def analyze_results(self, results_df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze experiment results and find best configurations"""
        
        # Filter successful results
        successful = results_df[results_df['success'] == True].copy()
        
        if len(successful) == 0:
            return {'error': 'No successful backtests'}
        
        analysis = {}
        
        # Overall statistics
        analysis['total_tests'] = len(results_df)
        analysis['successful_tests'] = len(successful)
        analysis['success_rate'] = len(successful) / len(results_df) * 100
        
        # Best configurations by different metrics
        analysis['best_total_return'] = successful.loc[successful['total_return'].idxmax()]
        analysis['best_cagr'] = successful.loc[successful['cagr'].idxmax()]
        analysis['best_sharpe'] = successful.loc[successful['sharpe_ratio'].idxmax()]
        analysis['lowest_drawdown'] = successful.loc[successful['max_drawdown'].idxmin()]
        analysis['best_excess_return'] = successful.loc[successful['excess_return'].idxmax()]
        
        # Summary statistics
        analysis['summary_stats'] = {
            'total_return': {
                'mean': successful['total_return'].mean(),
                'std': successful['total_return'].std(),
                'min': successful['total_return'].min(),
                'max': successful['total_return'].max(),
                'median': successful['total_return'].median()
            },
            'cagr': {
                'mean': successful['cagr'].mean(),
                'std': successful['cagr'].std(),
                'min': successful['cagr'].min(),
                'max': successful['cagr'].max(),
                'median': successful['cagr'].median()
            },
            'sharpe_ratio': {
                'mean': successful['sharpe_ratio'].mean(),
                'std': successful['sharpe_ratio'].std(),
                'min': successful['sharpe_ratio'].min(),
                'max': successful['sharpe_ratio'].max(),
                'median': successful['sharpe_ratio'].median()
            },
            'max_drawdown': {
                'mean': successful['max_drawdown'].mean(),
                'std': successful['max_drawdown'].std(),
                'min': successful['max_drawdown'].min(),
                'max': successful['max_drawdown'].max(),
                'median': successful['max_drawdown'].median()
            },
            'excess_return': {
                'mean': successful['excess_return'].mean(),
                'std': successful['excess_return'].std(),
                'min': successful['excess_return'].min(),
                'max': successful['excess_return'].max(),
                'median': successful['excess_return'].median()
            }
        }
        
        # Analysis by symbol
        symbol_analysis = {}
        for symbol in successful['equity_symbol'].unique():
            symbol_data = successful[successful['equity_symbol'] == symbol]
            symbol_analysis[symbol] = {
                'count': len(symbol_data),
                'avg_total_return': symbol_data['total_return'].mean(),
                'avg_cagr': symbol_data['cagr'].mean(),
                'avg_sharpe': symbol_data['sharpe_ratio'].mean(),
                'avg_drawdown': symbol_data['max_drawdown'].mean(),
                'best_config': symbol_data.loc[symbol_data['total_return'].idxmax()]
            }
        analysis['by_symbol'] = symbol_analysis
        
        # Analysis by allocation
        allocation_analysis = {}
        for _, row in successful.iterrows():
            allocation_key = f"{row['equity_allocation']}/{row['leap_allocation']}"
            if allocation_key not in allocation_analysis:
                allocation_analysis[allocation_key] = []
            allocation_analysis[allocation_key].append(row['total_return'])
        
        for key in allocation_analysis:
            returns = allocation_analysis[key]
            allocation_analysis[key] = {
                'count': len(returns),
                'avg_return': np.mean(returns),
                'std_return': np.std(returns),
                'min_return': np.min(returns),
                'max_return': np.max(returns)
            }
        analysis['by_allocation'] = allocation_analysis
        
        return analysis
    
    def save_results(self, results_df: pd.DataFrame, analysis: Dict[str, Any], output_dir: str = 'experiment_results'):
        """Save experiment results and analysis"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save raw results
        results_file = os.path.join(output_dir, f'strategy_experiment_results_{timestamp}.csv')
        results_df.to_csv(results_file, index=False)
        print(f"Saved results to {results_file}")
        
        # Save analysis
        analysis_file = os.path.join(output_dir, f'strategy_experiment_analysis_{timestamp}.json')
        with open(analysis_file, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        print(f"Saved analysis to {analysis_file}")
        
        # Generate summary report
        report_file = os.path.join(output_dir, f'strategy_experiment_report_{timestamp}.txt')
        self.generate_summary_report(analysis, report_file)
        print(f"Saved report to {report_file}")
        
        return results_file, analysis_file, report_file
    
    def generate_summary_report(self, analysis: Dict[str, Any], report_file: str):
        """Generate a human-readable summary report"""
        
        with open(report_file, 'w') as f:
            f.write("Strategy Optimization Experiment Report\n")
            f.write("=" * 50 + "\n\n")
            
            # Overall statistics
            f.write(f"Total Tests: {analysis['total_tests']}\n")
            f.write(f"Successful Tests: {analysis['successful_tests']}\n")
            f.write(f"Success Rate: {analysis['success_rate']:.1f}%\n\n")
            
            # Summary statistics
            f.write("Summary Statistics\n")
            f.write("-" * 30 + "\n")
            
            for metric, stats in analysis['summary_stats'].items():
                f.write(f"\n{metric.upper()}:\n")
                f.write(f"  Mean: {stats['mean']:.2f}\n")
                f.write(f"  Std:  {stats['std']:.2f}\n")
                f.write(f"  Min:  {stats['min']:.2f}\n")
                f.write(f"  Max:  {stats['max']:.2f}\n")
                f.write(f"  Median: {stats['median']:.2f}\n")
            
            # Best configurations
            f.write("\n\nBest Configurations\n")
            f.write("-" * 30 + "\n")
            
            metrics = ['best_total_return', 'best_cagr', 'best_sharpe', 'lowest_drawdown', 'best_excess_return']
            metric_names = ['Total Return', 'CAGR', 'Sharpe Ratio', 'Max Drawdown', 'Excess Return']
            
            for metric_key, metric_name in zip(metrics, metric_names):
                best = analysis[metric_key]
                f.write(f"\nBest {metric_name}:\n")
                f.write(f"  Symbol: {best['equity_symbol']}\n")
                f.write(f"  Allocation: {best['equity_allocation']}% Equity, {best['leap_allocation']}% LEAP\n")
                f.write(f"  LEAP Delta: {best['leap_delta']}\n")
                f.write(f"  LEAP Expiry: {best['leap_expiration_months']} months\n")
                f.write(f"  Total Return: {best['total_return']:.2f}%\n")
                f.write(f"  CAGR: {best['cagr']:.2f}%\n")
                f.write(f"  Sharpe Ratio: {best['sharpe_ratio']:.3f}\n")
                f.write(f"  Max Drawdown: {best['max_drawdown']:.2f}%\n")
                f.write(f"  Excess Return: {best['excess_return']:.2f}%\n")
            
            # Symbol analysis
            f.write("\n\nAnalysis by Symbol\n")
            f.write("-" * 30 + "\n")
            
            for symbol, stats in analysis['by_symbol'].items():
                f.write(f"\n{symbol}:\n")
                f.write(f"  Tests: {stats['count']}\n")
                f.write(f"  Avg Total Return: {stats['avg_total_return']:.2f}%\n")
                f.write(f"  Avg CAGR: {stats['avg_cagr']:.2f}%\n")
                f.write(f"  Avg Sharpe: {stats['avg_sharpe']:.3f}\n")
                f.write(f"  Avg Drawdown: {stats['avg_drawdown']:.2f}%\n")
            
            # Allocation analysis
            f.write("\n\nAnalysis by Allocation\n")
            f.write("-" * 30 + "\n")
            
            for allocation, stats in analysis['by_allocation'].items():
                f.write(f"\nAllocation {allocation}:\n")
                f.write(f"  Tests: {stats['count']}\n")
                f.write(f"  Avg Return: {stats['avg_return']:.2f}%\n")
                f.write(f"  Std Return: {stats['std_return']:.2f}%\n")
                f.write(f"  Min Return: {stats['min_return']:.2f}%\n")
                f.write(f"  Max Return: {stats['max_return']:.2f}%\n")

def main():
    """Main function to run the experiment"""
    
    print("Strategy Optimization Experiment Runner")
    print("=" * 50)
    
    # Create experiment runner
    experiment = StrategyExperiment()
    
    # Run experiments (you can adjust max_workers and limit for testing)
    results_df = experiment.run_experiments(max_workers=4, limit=None)
    
    # Analyze results
    print("\nAnalyzing results...")
    analysis = experiment.analyze_results(results_df)
    
    # Save results
    print("\nSaving results...")
    results_file, analysis_file, report_file = experiment.save_results(results_df, analysis)
    
    # Print summary
    print(f"\nExperiment completed successfully!")
    print(f"Total tests: {analysis['total_tests']}")
    print(f"Successful tests: {analysis['successful_tests']}")
    print(f"Success rate: {analysis['success_rate']:.1f}%")
    
    if analysis['successful_tests'] > 0:
        print(f"\nBest total return: {analysis['best_total_return']['total_return']:.2f}%")
        print(f"Best CAGR: {analysis['best_cagr']['cagr']:.2f}%")
        print(f"Best Sharpe ratio: {analysis['best_sharpe']['sharpe_ratio']:.3f}")
        print(f"Lowest drawdown: {analysis['lowest_drawdown']['max_drawdown']:.2f}%")
    
    print(f"\nResults saved to experiment_results/")

if __name__ == "__main__":
    main()