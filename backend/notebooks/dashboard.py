import marimo

__generated_with = "0.1.0"
app = marimo.App()


@app.cell
def __():
    import marimo as mo
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from app.services.backtest import LeapStrategyBacktester
    from app.models import BacktestRequest
    import sys
    import os

    # Ensure backend is in path
    if os.getcwd() not in sys.path:
        sys.path.append(os.getcwd())
    return (
        BacktestRequest,
        LeapStrategyBacktester,
        mo,
        np,
        os,
        pd,
        plt,
        sys,
    )


@app.cell
def __(mo):
    mo.md(
        """
        # Strategy Optimizer - Marimo Frontend
        
        This is a lightweight frontend for the Strategy Optimizer (P0).
        """
    )
    return


@app.cell
def __(mo):
    # Inputs
    equity_symbol = mo.ui.dropdown(["QQQ", "TSLA", "SPY"], value="QQQ", label="Equity Symbol")
    initial_capital = mo.ui.number(value=100000, label="Initial Capital")
    
    equity_alloc = mo.ui.slider(0, 100, value=60, label="Equity Allocation (%)")
    leap_alloc = mo.ui.slider(0, 100, value=30, label="LEAP Allocation (%)")
    
    start_date = mo.ui.date(value="2020-01-01", label="Start Date")
    end_date = mo.ui.date(value="2023-12-31", label="End Date")
    
    run_btn = mo.ui.run_button(label="Run Backtest")
    
    mo.vstack([
        mo.hstack([equity_symbol, initial_capital]),
        mo.hstack([equity_alloc, leap_alloc]),
        mo.hstack([start_date, end_date]),
        run_btn
    ])
    return (
        end_date,
        equity_alloc,
        equity_symbol,
        initial_capital,
        leap_alloc,
        run_btn,
        start_date,
    )


@app.cell
def __(
    BacktestRequest,
    LeapStrategyBacktester,
    end_date,
    equity_alloc,
    equity_symbol,
    initial_capital,
    leap_alloc,
    mo,
    pd,
    plt,
    run_btn,
):
    # Execution Logic
    result = None
    if run_btn.value:
        try:
            req = BacktestRequest(
                equity_symbol=equity_symbol.value,
                start_date=str(start_date.value),
                end_date=str(end_date.value),
                initial_capital=float(initial_capital.value),
                equity_allocation=float(equity_alloc.value),
                leap_allocation=float(leap_alloc.value),
                leap_delta=0.7,
                leap_expiration_months=12,
                rebalance_delta=5.0,
                equity_down_trigger=10.0,
                equity_up_trigger=15.0,
                profit_limit_6m=50.0,
                loss_limit_6m=30.0,
                profit_limit_3m=30.0,
                loss_limit_3m=20.0,
                profit_limit_0m=10.0,
                loss_limit_0m=10.0,
                monthly_withdrawal=0.0
            )
            
            backtester = LeapStrategyBacktester(req)
            result = backtester.run()
            
            # Visualization
            df_history = pd.DataFrame([h.dict() for h in result.history])
            
            # Plot
            fig, ax1 = plt.subplots(figsize=(10, 6))
            
            color = 'tab:blue'
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Portfolio Value', color=color)
            ax1.plot(pd.to_datetime(df_history['date']), df_history['total_value'], color=color)
            ax1.tick_params(axis='y', labelcolor=color)
            
            ax2 = ax1.twinx() 
            color = 'tab:red'
            ax2.set_ylabel('Drawdown', color=color)
            ax2.plot(pd.to_datetime(df_history['date']), df_history['drawdown'], color=color, linestyle='--')
            ax2.tick_params(axis='y', labelcolor=color)
            
            plt.title(f"Backtest Result: {equity_symbol.value}")
            fig.tight_layout()
            
            # Stats
            stats = mo.md(
                f"""
                **Total Return:** {result.total_return}%
                **CAGR:** {result.cagr}%
                **Max Drawdown:** {result.max_drawdown}%
                **Sharpe Ratio:** {result.sharpe_ratio}
                """
            )
            
            output = mo.vstack([
                stats,
                mo.as_html(fig)
            ])
        except Exception as e:
            output = mo.md(f"**Error:** {str(e)}")
    else:
        output = mo.md("Click 'Run Backtest' to see results.")
        
    output
    return (
        ax1,
        ax2,
        backtester,
        color,
        df_history,
        fig,
        output,
        req,
        result,
        stats,
    )


if __name__ == "__main__":
    app.run()
