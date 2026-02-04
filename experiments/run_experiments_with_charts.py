#!/usr/bin/env python3
"""
Strategy Optimization Experiment with Chart Generation

This script runs experiments and generates bar charts comparing baseline vs all scenarios.
"""

import pandas as pd
import numpy as np
import json
import time
import concurrent.futures
from datetime import datetime
import sys
import os
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict, Any, Tuple

# Add the backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.models import BacktestRequest
from app.services.backtest import LeapStrategyBacktester

def run_single_backtest(params: Dict[str, Any]) -> Dict[str, Any]:
    """Run a single backtest with given parameters (standalone function for pickling)"""
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
            'benchmark_max_drawdown': 0, # Placeholder
            'excess_return': 0,
            'success': True,
            'error': None
        }
        
        # Calculate benchmark max drawdown
        if result.history:
            benchmark_values = [h.benchmark_value for h in result.history]
            running_max = np.maximum.accumulate(benchmark_values)
            drawdowns = (running_max - benchmark_values) / running_max
            metrics['benchmark_max_drawdown'] = np.max(drawdowns) * 100
        
        # Calculate excess return over benchmark
        metrics['excess_return'] = metrics['total_return'] - metrics['benchmark_return']
        
        return metrics
        
    except Exception as e:
        print(f"Error running backtest for {params.get('equity_symbol', 'Unknown')}: {str(e)}")
        return {
            'params': params,
            'total_return': 0,
            'cagr': 0,
            'max_drawdown': 0,
            'sharpe_ratio': 0,
            'num_trades': 0,
            'final_value': params['initial_capital'],
            'benchmark_return': 0,
            'benchmark_max_drawdown': 0,
            'excess_return': 0,
            'success': False,
            'error': str(e)
        }

class StrategyExperimentWithCharts:
    def __init__(self):
        self.results = []
        self.experiment_configs = []
        
    def generate_parameter_combinations(self) -> List[Dict[str, Any]]:
        """Generate a manageable set of parameter combinations for charting"""
        
        # Base parameters
        base_params = {
            'start_date': '2020-01-01',
            'end_date': '2025-12-31',  # Shorter period for faster execution
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
        }
        
        # Parameter ranges - reduced for manageable charting
        equity_symbols = ['TSLA', 'QQQ']
        
        # Allocation combinations (equity %, leap %, cash %)
        allocation_combinations = [
            (60, 30, 10),  # 60% equity + 30% LEAP + 10% cash
            (60, 35, 5),   # 60% equity + 35% LEAP + 5% cash
            (50, 35, 15),  # 50% equity + 35% LEAP + 15% cash
            (65, 25, 10),  # 65% equity + 25% LEAP + 10% cash
        ]
        
        # LEAP parameters - reduced set
        leap_deltas = [0.4, 0.5, 0.6]
        leap_expirations = [12, 18]  # months
        
        combinations = []
        
        # Generate combinations - limit to manageable number
        for symbol in equity_symbols:
            for equity_pct, leap_pct, cash_pct in allocation_combinations:
                for leap_delta in leap_deltas:
                    for leap_expiry in leap_expirations:
                        config = base_params.copy()
                        config.update({
                            'equity_symbol': symbol,
                            'equity_allocation': equity_pct,
                            'leap_allocation': leap_pct,
                            'leap_delta': leap_delta,
                            'leap_expiration_months': leap_expiry,
                        })
                        combinations.append(config)
        
        print(f"Generated {len(combinations)} parameter combinations for charting")
        return combinations
    
    def run_experiments(self, max_workers: int = 4) -> pd.DataFrame:
        """Run all experiments in parallel using ProcessPoolExecutor"""
        
        # Generate parameter combinations
        combinations = self.generate_parameter_combinations()
        
        print(f"Running {len(combinations)} backtests with {max_workers} workers (ProcessPoolExecutor)...")
        
        start_time = time.time()
        
        # Run experiments in parallel using ProcessPoolExecutor to avoid shared state/threading issues
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(run_single_backtest, params) for params in combinations]
            
            results = []
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Exception in worker: {e}")
                
                if (i + 1) % 5 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed * 60  # tests per minute
                    remaining = (len(combinations) - (i + 1)) / (rate / 60)
                    print(f"Progress: {i + 1}/{len(combinations)} completed, "
                          f"Rate: {rate:.1f} tests/hour, "
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
    
    def create_charts(self, results_df: pd.DataFrame, output_dir: str = 'charts'):
        """Create bar charts comparing baseline vs all scenarios"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Filter successful results
        successful = results_df[results_df['success'] == True].copy()
        
        if len(successful) == 0:
            print("No successful results to chart")
            return
        
        # Set style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create charts for each equity
        for symbol in successful['equity_symbol'].unique():
            symbol_data = successful[successful['equity_symbol'] == symbol].copy()
            
            # Sort by total return for better visualization
            symbol_data = symbol_data.sort_values('total_return', ascending=True)
            
            # Create configuration labels
            symbol_data['config_label'] = symbol_data.apply(
                lambda row: f"{row['equity_allocation']}/{row['leap_allocation']}/Δ{row['leap_delta']}/{row['leap_expiration_months']}m", 
                axis=1
            )
            
            # Chart 1: Total Return Comparison
            plt.figure(figsize=(14, 8))
            
            # Create subplot for total return
            plt.subplot(2, 1, 1)
            
            # Bar chart for total returns
            bars1 = plt.barh(range(len(symbol_data)), symbol_data['total_return'], 
                           alpha=0.7, label='Strategy Return')
            
            # Add benchmark line
            benchmark_return = symbol_data['benchmark_return'].iloc[0]  # Same for all configs of same symbol
            plt.axvline(x=benchmark_return, color='red', linestyle='--', 
                       linewidth=2, label=f'Buy & Hold ({benchmark_return:.1f}%)')
            
            # Customize
            plt.ylabel('Configuration')
            plt.xlabel('Total Return (%)')
            plt.title(f'{symbol} - Total Return Comparison: Strategy vs Buy & Hold')
            plt.yticks(range(len(symbol_data)), symbol_data['config_label'])
            plt.legend()
            plt.grid(axis='x', alpha=0.3)
            
            # Add value labels on bars
            for i, (idx, row) in enumerate(symbol_data.iterrows()):
                plt.text(row['total_return'] + 50, i, f"{row['total_return']:.1f}%", 
                        va='center', fontsize=9)
            
            # Chart 2: Max Drawdown Comparison
            plt.subplot(2, 1, 2)
            
            # Bar chart for max drawdown (negative values)
            bars2 = plt.barh(range(len(symbol_data)), symbol_data['max_drawdown'], 
                           alpha=0.7, color='orange', label='Strategy Max Drawdown')
            
            # Add benchmark drawdown line
            benchmark_dd = symbol_data['benchmark_max_drawdown'].iloc[0]
            plt.axvline(x=benchmark_dd, color='red', linestyle='--', 
                       linewidth=2, label=f'Buy & Hold Max DD ({benchmark_dd:.1f}%)')
            
            # For comparison, we'll show the strategy drawdowns
            plt.xlabel('Maximum Drawdown (%)')
            plt.ylabel('Configuration')
            plt.title(f'{symbol} - Maximum Drawdown by Configuration')
            plt.yticks(range(len(symbol_data)), symbol_data['config_label'])
            # Place legend outside the plot area to avoid overlap
            plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
            plt.grid(axis='x', alpha=0.3)
            
            # Add value labels on bars
            for i, (idx, row) in enumerate(symbol_data.iterrows()):
                plt.text(row['max_drawdown'] + 1, i, f"{row['max_drawdown']:.1f}%", 
                        va='center', fontsize=9)
            
            plt.tight_layout()
            
            # Save chart
            chart_file = os.path.join(output_dir, f'{symbol}_strategy_comparison.png')
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Saved {symbol} comparison chart to {chart_file}")
            
            # Create separate focused charts
            self.create_focused_charts(symbol_data, symbol, output_dir)
    
    def create_focused_charts(self, symbol_data: pd.DataFrame, symbol: str, output_dir: str = 'charts'):
        """Create focused charts for total return and max drawdown separately"""
        
        # Chart 1: Total Return Focus
        plt.figure(figsize=(12, 8))
        
        # Sort by total return for better visualization
        symbol_data_sorted = symbol_data.sort_values('total_return', ascending=False)
        
        bars = plt.bar(range(len(symbol_data_sorted)), symbol_data_sorted['total_return'], 
                      alpha=0.7, color='steelblue', label='Strategy Return')
        
        # Add benchmark line
        benchmark_return = symbol_data_sorted['benchmark_return'].iloc[0]
        plt.axhline(y=benchmark_return, color='red', linestyle='--', 
                   linewidth=3, label=f'Buy & Hold Benchmark ({benchmark_return:.1f}%)')
        
        # Customize
        plt.xlabel('Configuration')
        plt.ylabel('Total Return (%)')
        plt.title(f'{symbol} - Total Return by Configuration')
        
        # Create x-axis labels
        x_labels = symbol_data_sorted.apply(
            lambda row: f"{row['equity_allocation']}/{row['leap_allocation']}\nΔ{row['leap_delta']}/{row['leap_expiration_months']}m", 
            axis=1
        )
        plt.xticks(range(len(symbol_data_sorted)), x_labels, rotation=45, ha='right')
        
        plt.legend()
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, (idx, row) in enumerate(symbol_data_sorted.iterrows()):
            plt.text(i, row['total_return'] + 50, f"{row['total_return']:.0f}%", 
                    ha='center', va='bottom', fontsize=9, rotation=90)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = os.path.join(output_dir, f'{symbol}_total_return_focus.png')
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved {symbol} total return chart to {chart_file}")
        
        # Chart 2: Max Drawdown Focus
        plt.figure(figsize=(12, 8))
        
        # Sort by max drawdown (ascending - lower is better)
        symbol_data_sorted = symbol_data.sort_values('max_drawdown', ascending=True)
        
        bars = plt.bar(range(len(symbol_data_sorted)), symbol_data_sorted['max_drawdown'], 
                      alpha=0.7, color='orange', label='Max Drawdown')
        
        # Add benchmark drawdown line
        benchmark_dd = symbol_data_sorted['benchmark_max_drawdown'].iloc[0]
        plt.axhline(y=benchmark_dd, color='red', linestyle='--', 
                   linewidth=3, label=f'Buy & Hold Max DD ({benchmark_dd:.1f}%)')
        
        # Customize
        plt.xlabel('Configuration')
        plt.ylabel('Maximum Drawdown (%)')
        plt.title(f'{symbol} - Maximum Drawdown by Configuration')
        
        # Create x-axis labels
        x_labels = symbol_data_sorted.apply(
            lambda row: f"{row['equity_allocation']}/{row['leap_allocation']}\nΔ{row['leap_delta']}/{row['leap_expiration_months']}m", 
            axis=1
        )
        plt.xticks(range(len(symbol_data_sorted)), x_labels, rotation=45, ha='right')
        
        # Place legend outside the plot area to avoid overlap
        plt.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
        plt.grid(axis='y', alpha=0.3)
        
        # Add value labels on bars
        for i, (idx, row) in enumerate(symbol_data_sorted.iterrows()):
            plt.text(i, row['max_drawdown'] + 1, f"{row['max_drawdown']:.0f}%", 
                    ha='center', va='bottom', fontsize=9, rotation=90)
        
        plt.tight_layout()
        
        # Save chart
        chart_file = os.path.join(output_dir, f'{symbol}_max_drawdown_focus.png')
        plt.savefig(chart_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved {symbol} max drawdown chart to {chart_file}")

def main():
    """Main function to run experiments and generate charts"""
    
    print("Strategy Optimization Experiment with Chart Generation")
    print("=" * 60)
    
    # Create experiment runner
    experiment = StrategyExperimentWithCharts()
    
    # Run experiments
    results_df = experiment.run_experiments(max_workers=4)
    
    # Generate charts
    print("\nGenerating charts...")
    experiment.create_charts(results_df)
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_file = f'results/experiment_results_with_charts_{timestamp}.csv'
    results_df.to_csv(results_file, index=False)
    print(f"\nResults saved to {results_file}")
    
    # Print summary
    successful = results_df[results_df['success'] == True]
    print(f"\nExperiment Summary:")
    print(f"Total tests: {len(results_df)}")
    print(f"Successful tests: {len(successful)}")
    
    if len(successful) > 0:
        print(f"Best total return: {successful['total_return'].max():.1f}%")
        print(f"Best Sharpe ratio: {successful['sharpe_ratio'].max():.3f}")
        print(f"Lowest drawdown: {successful['max_drawdown'].min():.1f}%")
    
    print(f"\nCharts saved to charts directory")

if __name__ == "__main__":
    main()
