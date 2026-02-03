#!/usr/bin/env python3
"""
Analysis and Summary of Strategy Optimization Results
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

def analyze_results():
    """Analyze the experiment results and create summary"""
    
    # Find the latest results file
    results_files = [f for f in os.listdir('.') if f.startswith('experiment_results_with_charts_') and f.endswith('.csv')]
    if not results_files:
        print("No results file found!")
        return
    
    latest_file = sorted(results_files)[-1]
    print(f"Analyzing results from: {latest_file}")
    
    # Load results
    df = pd.read_csv(latest_file)
    
    # Filter successful results
    successful = df[df['success'] == True].copy()
    
    print(f"\n{'='*60}")
    print("STRATEGY OPTIMIZATION RESULTS SUMMARY")
    print(f"{'='*60}")
    
    # Overall statistics
    print(f"\nTotal Tests: {len(df)}")
    print(f"Successful Tests: {len(successful)}")
    print(f"Success Rate: {len(successful)/len(df)*100:.1f}%")
    
    # Analysis by symbol
    print(f"\n{'='*40}")
    print("RESULTS BY EQUITY")
    print(f"{'='*40}")
    
    for symbol in successful['equity_symbol'].unique():
        symbol_data = successful[successful['equity_symbol'] == symbol]
        
        print(f"\n{symbol.upper()} Results:")
        print(f"  Tests: {len(symbol_data)}")
        print(f"  Average Total Return: {symbol_data['total_return'].mean():.1f}%")
        print(f"  Best Total Return: {symbol_data['total_return'].max():.1f}%")
        print(f"  Worst Total Return: {symbol_data['total_return'].min():.1f}%")
        print(f"  Average CAGR: {symbol_data['cagr'].mean():.1f}%")
        print(f"  Average Sharpe Ratio: {symbol_data['sharpe_ratio'].mean():.3f}")
        print(f"  Average Max Drawdown: {symbol_data['max_drawdown'].mean():.1f}%")
        print(f"  Average Excess Return: {symbol_data['excess_return'].mean():.1f}%")
        
        # Best configuration for each symbol
        best_return = symbol_data.loc[symbol_data['total_return'].idxmax()]
        best_sharpe = symbol_data.loc[symbol_data['sharpe_ratio'].idxmax()]
        lowest_drawdown = symbol_data.loc[symbol_data['max_drawdown'].idxmin()]
        
        print(f"\n  Best Return Config:")
        print(f"    Allocation: {best_return['equity_allocation']}% Equity, {best_return['leap_allocation']}% LEAP")
        print(f"    LEAP Delta: {best_return['leap_delta']}, Expiry: {best_return['leap_expiration_months']} months")
        print(f"    Total Return: {best_return['total_return']:.1f}%")
        print(f"    Max Drawdown: {best_return['max_drawdown']:.1f}%")
        
        print(f"\n  Best Sharpe Config:")
        print(f"    Allocation: {best_sharpe['equity_allocation']}% Equity, {best_sharpe['leap_allocation']}% LEAP")
        print(f"    LEAP Delta: {best_sharpe['leap_delta']}, Expiry: {best_sharpe['leap_expiration_months']} months")
        print(f"    Sharpe Ratio: {best_sharpe['sharpe_ratio']:.3f}")
        print(f"    Total Return: {best_sharpe['total_return']:.1f}%")
    
    # Analysis by allocation
    print(f"\n{'='*40}")
    print("RESULTS BY ALLOCATION")
    print(f"{'='*40}")
    
    allocation_analysis = successful.groupby(['equity_allocation', 'leap_allocation']).agg({
        'total_return': ['mean', 'min', 'max', 'std'],
        'max_drawdown': ['mean', 'min', 'max'],
        'sharpe_ratio': ['mean', 'min', 'max'],
        'excess_return': 'mean'
    }).round(2)
    
    for (eq_alloc, leap_alloc), group in successful.groupby(['equity_allocation', 'leap_allocation']):
        print(f"\nAllocation: {eq_alloc}% Equity, {leap_alloc}% LEAP")
        print(f"  Tests: {len(group)}")
        print(f"  Avg Total Return: {group['total_return'].mean():.1f}%")
        print(f"  Avg Max Drawdown: {group['max_drawdown'].mean():.1f}%")
        print(f"  Avg Sharpe Ratio: {group['sharpe_ratio'].mean():.3f}")
        print(f"  Return Range: {group['total_return'].min():.1f}% - {group['total_return'].max():.1f}%")
    
    # Analysis by LEAP parameters
    print(f"\n{'='*40}")
    print("RESULTS BY LEAP PARAMETERS")
    print(f"{'='*40}")
    
    leap_analysis = successful.groupby(['leap_delta', 'leap_expiration_months']).agg({
        'total_return': 'mean',
        'max_drawdown': 'mean',
        'sharpe_ratio': 'mean'
    }).round(2)
    
    for (delta, expiry), group in successful.groupby(['leap_delta', 'leap_expiration_months']):
        print(f"\nLEAP Delta: {delta}, Expiry: {expiry} months")
        print(f"  Tests: {len(group)}")
        print(f"  Avg Total Return: {group['total_return'].mean():.1f}%")
        print(f"  Avg Max Drawdown: {group['max_drawdown'].mean():.1f}%")
        print(f"  Avg Sharpe Ratio: {group['sharpe_ratio'].mean():.3f}")
    
    # Key insights
    print(f"\n{'='*40}")
    print("KEY INSIGHTS")
    print(f"{'='*40}")
    
    # Best overall configuration
    best_overall = successful.loc[successful['total_return'].idxmax()]
    print(f"\nBest Overall Configuration:")
    print(f"  Symbol: {best_overall['equity_symbol']}")
    print(f"  Allocation: {best_overall['equity_allocation']}% Equity, {best_overall['leap_allocation']}% LEAP")
    print(f"  LEAP Delta: {best_overall['leap_delta']}, Expiry: {best_overall['leap_expiration_months']} months")
    print(f"  Total Return: {best_overall['total_return']:.1f}%")
    print(f"  CAGR: {best_overall['cagr']:.1f}%")
    print(f"  Sharpe Ratio: {best_overall['sharpe_ratio']:.3f}")
    print(f"  Max Drawdown: {best_overall['max_drawdown']:.1f}%")
    
    # Risk-return analysis
    print(f"\nRisk-Return Analysis:")
    print(f"  TSLA average excess return: {successful[successful['equity_symbol']=='TSLA']['excess_return'].mean():.1f}%")
    print(f"  QQQ average excess return: {successful[successful['equity_symbol']=='QQQ']['excess_return'].mean():.1f}%")
    print(f"  Overall average excess return: {successful['excess_return'].mean():.1f}%")
    
    # Create a comprehensive summary chart
    create_summary_chart(successful)
    
    return successful

def create_summary_chart(successful_df):
    """Create a comprehensive summary chart"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Chart 1: Total Return by Symbol and Allocation
    pivot_return = successful_df.pivot_table(
        values='total_return', 
        index=['equity_allocation', 'leap_allocation'], 
        columns='equity_symbol', 
        aggfunc='mean'
    )
    
    pivot_return.plot(kind='bar', ax=ax1, width=0.8)
    ax1.set_title('Average Total Return by Allocation and Symbol')
    ax1.set_ylabel('Total Return (%)')
    ax1.legend(title='Symbol')
    ax1.tick_params(axis='x', rotation=45)
    
    # Chart 2: Max Drawdown by Symbol and Allocation
    pivot_dd = successful_df.pivot_table(
        values='max_drawdown', 
        index=['equity_allocation', 'leap_allocation'], 
        columns='equity_symbol', 
        aggfunc='mean'
    )
    
    pivot_dd.plot(kind='bar', ax=ax2, width=0.8, color=['orange', 'red'])
    ax2.set_title('Average Max Drawdown by Allocation and Symbol')
    ax2.set_ylabel('Max Drawdown (%)')
    ax2.legend(title='Symbol')
    ax2.tick_params(axis='x', rotation=45)
    
    # Chart 3: Sharpe Ratio by LEAP Delta
    leap_sharpe = successful_df.groupby(['equity_symbol', 'leap_delta'])['sharpe_ratio'].mean().unstack()
    leap_sharpe.plot(kind='bar', ax=ax3, width=0.8)
    ax3.set_title('Average Sharpe Ratio by LEAP Delta')
    ax3.set_ylabel('Sharpe Ratio')
    ax3.legend(title='LEAP Delta')
    ax3.tick_params(axis='x', rotation=0)
    
    # Chart 4: Excess Return Distribution
    successful_df.boxplot(column='excess_return', by='equity_symbol', ax=ax4)
    ax4.set_title('Excess Return Distribution by Symbol')
    ax4.set_ylabel('Excess Return (%)')
    ax4.set_xlabel('Symbol')
    
    plt.suptitle('Strategy Optimization Summary Analysis', fontsize=16, y=1.02)
    plt.tight_layout()
    
    # Save chart
    chart_file = 'charts/strategy_optimization_summary.png'
    plt.savefig(chart_file, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\nSummary chart saved to {chart_file}")

if __name__ == "__main__":
    analyze_results()