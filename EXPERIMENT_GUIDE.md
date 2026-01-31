# Strategy Optimization Experiment System

## Overview

This experiment system allows you to systematically test different parameter combinations for the One Stock + LEAP Option Portfolio strategy. It runs comprehensive backtests across multiple configurations and generates detailed performance analysis.

## Quick Start

### 1. Run a Quick Test

Test the system with a few parameter combinations:

```bash
python test_strategy_quick.py
```

This will run 2 test configurations (TSLA and QQQ) and show you the results.

### 2. Run Full Experiment

Run the complete experiment with all parameter combinations:

```bash
python run_strategy_experiments.py
```

**Warning**: This will run hundreds of backtests and may take several hours to complete.

### 3. Run Limited Experiment (Recommended)

For faster results, modify the experiment script to limit the number of combinations:

```python
# In run_strategy_experiments.py, change:
results_df = experiment.run_experiments(max_workers=4, limit=20)
```

## Parameter Configuration

### Target Equities
- **TSLA**: Tesla, Inc. - High volatility growth stock
- **QQQ**: Invesco QQQ Trust - NASDAQ-100 ETF, diversified tech exposure

### Allocation Combinations
- **Conservative**: 60% Equity + 25% LEAP + 15% Cash
- **Balanced**: 60% Equity + 30% LEAP + 10% Cash  
- **Aggressive**: 60% Equity + 35% LEAP + 5% Cash
- **High Leverage**: 50% Equity + 35% LEAP + 15% Cash

### LEAP Parameters
- **Target Delta**: 0.4, 0.5, 0.6 (higher delta = more aggressive)
- **Expiration**: 12, 18 months (longer expiration = less time decay)

### Rebalancing Triggers
- **Allocation Drift**: 5% deviation from target weights
- **Equity Down**: 10% price decline from last rebalance
- **Equity Up**: 15% price appreciation from last rebalance

### Profit/Loss Management
- **>6 Months to Expiry**: Take 100% profit, cut 60% loss
- **3-6 Months to Expiry**: Take 30% profit, cut 20% loss  
- **<3 Months to Expiry**: Take 10% profit, cut 20% loss

## Results Interpretation

### Key Metrics

1. **Total Return**: Cumulative percentage return over the test period
2. **CAGR**: Compound Annual Growth Rate (annualized return)
3. **Sharpe Ratio**: Risk-adjusted return (higher is better)
4. **Max Drawdown**: Largest peak-to-trough decline (lower is better)
5. **Excess Return**: Return above buy-and-hold benchmark

### Performance Analysis

The experiment system generates:
- **Best configurations** by different metrics (return, Sharpe, drawdown)
- **Summary statistics** across all tests
- **Symbol-specific analysis** (TSLA vs QQQ performance)
- **Allocation analysis** (which equity/LEAP ratios work best)

### Example Results Interpretation

From our quick test:
```
TSLA Results:
- Total Return: 4850.46% (vs ~1143% buy-and-hold)
- CAGR: 604.54%
- Sharpe Ratio: 2.030 (excellent risk-adjusted return)
- Max Drawdown: 65.89% (high but acceptable for the return)
- Excess Return: 3706.63% above benchmark

QQQ Results:
- Total Return: 366.91% (vs ~87% buy-and-hold)  
- CAGR: 116.19%
- Sharpe Ratio: 1.670 (good risk-adjusted return)
- Max Drawdown: 23.18% (much lower risk)
- Excess Return: 279.75% above benchmark
```

## Optimization Recommendations

### For Aggressive Investors
- **Target**: TSLA with 60% equity, 30% LEAP allocation
- **LEAP Delta**: 0.5-0.6 for higher leverage
- **Trade-off**: Higher returns but significant drawdowns (65%+)

### For Conservative Investors  
- **Target**: QQQ with 50-60% equity, 25-35% LEAP allocation
- **LEAP Delta**: 0.4-0.5 for more stability
- **Trade-off**: Lower returns but manageable risk (20-25% drawdowns)

### For Balanced Approach
- **Target**: Either equity with 60% equity, 30% LEAP allocation
- **LEAP Delta**: 0.5 for balanced risk/reward
- **Trade-off**: Good excess returns with moderate drawdowns

## Advanced Usage

### Custom Parameter Ranges

Modify the `generate_parameter_combinations()` method to test:
- Different profit/loss limits
- Alternative rebalancing triggers
- Other target equities
- Different time periods

### Monte Carlo Simulation

Enable simulation mode for robustness testing:

```python
params = {
    'use_simulation': True,
    'simulation_runs': 1000,
    'simulation_scenario': 'neutral',  # bull, bear, neutral, high_vol
}
```

### Batch Processing

For large experiments, consider:
- Running overnight or on cloud instances
- Using more CPU cores (`max_workers=8`)
- Saving intermediate results
- Processing results in chunks

## Output Files

The system generates three types of output files:

1. **CSV Results**: Raw backtest results for all configurations
2. **JSON Analysis**: Detailed statistical analysis and best configurations  
3. **Text Report**: Human-readable summary report

Files are saved in `experiment_results/` with timestamps.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure backend dependencies are installed
2. **Data Download Issues**: Check internet connection and yfinance availability
3. **Memory Issues**: Reduce `max_workers` or run smaller batches
4. **Timeout Errors**: Use shorter time periods for testing

### Performance Tips

1. **Use Simulation**: Faster than historical data for initial testing
2. **Limit Combinations**: Start with 10-20 configurations
3. **Shorter Periods**: Test with 1-2 years of data initially
4. **Parallel Processing**: Use multiple CPU cores (`max_workers=4-8`)

## Next Steps

1. **Run your first experiment** with limited parameters
2. **Analyze the results** and identify promising configurations
3. **Refine parameters** based on your risk tolerance
4. **Test with different time periods** to validate robustness
5. **Consider Monte Carlo simulation** for stress testing
6. **Paper trade** the best configurations before live implementation

Remember: Past performance doesn't guarantee future results. Use this system for research and education, not as investment advice.