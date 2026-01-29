from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date

class BacktestRequest(BaseModel):
    equity_symbol: str = Field(..., description="Target equity symbol (e.g., QQQ, TSLA)")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    initial_capital: float = Field(..., gt=0, description="Initial portfolio value")
    
    # Portfolio Allocation
    equity_allocation: float = Field(..., ge=0, le=100, description="Percentage allocation to equity")
    leap_allocation: float = Field(..., ge=0, le=100, description="Percentage allocation to LEAP calls")
    # Cash allocation is derived: 100 - equity - leap
    
    # LEAP Parameters
    leap_delta: float = Field(0.7, ge=0.1, le=0.95, description="Target delta for LEAP options")
    leap_expiration_months: int = Field(12, ge=6, le=24, description="LEAP expiration timeframe in months")
    
    # Rebalancing Parameters
    rebalance_delta: float = Field(5.0, description="Allocation deviation trigger (%)")
    equity_down_trigger: float = Field(10.0, description="Equity price drop trigger (%)")
    equity_up_trigger: float = Field(15.0, description="Equity price rise trigger (%)")
    
    # Profit/Loss Limits
    profit_limit_6m: float = Field(50.0, description="Profit limit for >6 months to expiration (%)")
    loss_limit_6m: float = Field(30.0, description="Loss limit for >6 months to expiration (%)")
    profit_limit_3m: float = Field(30.0, description="Profit limit for 3-6 months to expiration (%)")
    loss_limit_3m: float = Field(20.0, description="Loss limit for 3-6 months to expiration (%)")
    profit_limit_0m: float = Field(10.0, description="Profit limit for <3 months to expiration (%)")
    loss_limit_0m: float = Field(10.0, description="Loss limit for <3 months to expiration (%)")
    
    # Wheel Strategy Parameters
    use_wheel_strategy: bool = Field(False, description="Enable Wheel Strategy")
    wheel_ma_short: int = Field(10, description="Short-term Moving Average window")
    wheel_ma_long: int = Field(30, description="Long-term Moving Average window")
    wheel_allocation: float = Field(0.0, description="Allocation for Wheel Strategy (uses cash portion)")

    # Cash Management
    monthly_withdrawal: float = Field(0.0, ge=0, description="Monthly cash withdrawal amount")
    
    # Simulation
    use_simulation: bool = Field(False, description="Use synthetic data instead of historical")
    simulation_scenario: str = Field("neutral", description="bull, bear, neutral, high_vol")
    simulation_runs: int = Field(1, ge=1, le=1000, description="Number of Monte Carlo simulation runs")
    simulation_drift: Optional[float] = Field(None, description="Expected annual drift (mu) for custom simulation")
    simulation_volatility: Optional[float] = Field(None, description="Expected annual volatility (sigma) for custom simulation")

class Trade(BaseModel):
    date: str
    type: str # BUY, SELL
    asset: str # EQUITY, LEAP, CASH
    quantity: float
    price: float
    value: float
    reason: str

class PortfolioSnapshot(BaseModel):
    date: str
    equity_value: float
    leap_value: float
    cash_value: float
    total_value: float
    benchmark_value: float
    equity_price: float
    drawdown: float
    greeks: Optional[Dict[str, float]] = None

class BacktestResult(BaseModel):
    backtest_id: str
    params: BacktestRequest
    total_return: float
    cagr: float
    max_drawdown: float
    sharpe_ratio: float
    trades: List[Trade]
    history: List[PortfolioSnapshot]
    
    # Monte Carlo Results
    confidence_intervals: Optional[Dict[str, Dict[str, float]]] = None  # {"portfolio": {"lower": 0.1, "upper": 0.9}, "benchmark": {"lower": 0.1, "upper": 0.9}}
    final_portfolio_values: Optional[List[float]] = None  # For distribution chart
    final_benchmark_values: Optional[List[float]] = None  # For distribution chart
    is_simulation: bool = False  # Flag to indicate if this is a simulation result
