import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import uuid
from scipy.stats import norm
from app.models import BacktestRequest, BacktestResult, Trade, PortfolioSnapshot
from app.services.option_pricing import black_scholes_call_price, find_strike_for_delta, black_scholes_put_price
from app.services.simulator import MarketSimulator

class LeapStrategyBacktester:
    def __init__(self, params: BacktestRequest):
        self.params = params
        self.portfolio = {
            'cash': params.initial_capital,
            'equity_qty': 0,
            'leap': None,  # {strike, expiry_date, qty, entry_price, current_price}
            'wheel_put': None, # {strike, expiry_date, qty, entry_price, current_price}
            'wheel_call': None # {strike, expiry_date, qty, entry_price, current_price}
        }
        self.trades = []
        self.history = []
        self.risk_free_rate = 0.04  # 4% assumption
        self.last_rebalance_date = None
        self.last_withdrawal_month = None

    def fetch_data(self):
        # Simulation Mode
        if self.params.use_simulation:
            data = MarketSimulator.generate_scenario(
                self.params.equity_symbol, 
                self.params.start_date, 
                self.params.end_date, 
                self.params.simulation_scenario
            )
            close_prices = data['Close']
            data['returns'] = close_prices.pct_change()
            data['volatility'] = data['returns'].rolling(window=21).std() * np.sqrt(252)
            
             # Calculate Moving Averages for Wheel Strategy
            if self.params.use_wheel_strategy:
                data['ma_short'] = close_prices.rolling(window=self.params.wheel_ma_short).mean()
                data['ma_long'] = close_prices.rolling(window=self.params.wheel_ma_long).mean()

            data['volatility'] = data['volatility'].bfill().fillna(0.20)
            return data

        # Add buffer for volatility calculation
        start_date_obj = datetime.strptime(self.params.start_date, "%Y-%m-%d")
        buffer_date = start_date_obj - timedelta(days=90) # Increased buffer for MA calculations
        
        data = yf.download(self.params.equity_symbol, start=buffer_date.strftime("%Y-%m-%d"), end=self.params.end_date, progress=False)
        
        if data.empty:
            raise ValueError(f"No data found for {self.params.equity_symbol}")
            
        close_prices = data['Close']
        if isinstance(close_prices, pd.DataFrame):
             close_prices = close_prices.iloc[:, 0] # Take the first column if it's a DF
             
        data['returns'] = close_prices.pct_change()
        data['volatility'] = data['returns'].rolling(window=21).std() * np.sqrt(252)
        
        # Calculate Moving Averages for Wheel Strategy
        if self.params.use_wheel_strategy:
            data['ma_short'] = close_prices.rolling(window=self.params.wheel_ma_short).mean()
            data['ma_long'] = close_prices.rolling(window=self.params.wheel_ma_long).mean()
        
        # Fill NaN volatility with mean or forward fill
        data['volatility'] = data['volatility'].bfill().fillna(0.20) # Default to 20% if no data
        
        # Filter back to requested start date
        mask = (data.index >= self.params.start_date)
        return data.loc[mask]

    def _calculate_portfolio_greeks(self, date, stock_price, vol):
        greeks = {'delta': 0.0, 'gamma': 0.0, 'theta': 0.0, 'vega': 0.0}
        
        # Helper for Call Greeks
        def call_greeks(S, K, T, r, sigma):
            if T <= 0: return 0, 0, 0, 0
            d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            delta = norm.cdf(d1)
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * K * np.exp(-r*T) * norm.cdf(d2)
            vega = S * norm.pdf(d1) * np.sqrt(T)
            return delta, gamma, theta/365, vega/100
            
        # Helper for Put Greeks
        def put_greeks(S, K, T, r, sigma):
            if T <= 0: return 0, 0, 0, 0
            d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
            d2 = d1 - sigma*np.sqrt(T)
            delta = norm.cdf(d1) - 1
            gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
            theta = -(S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * K * np.exp(-r*T) * norm.cdf(-d2)
            vega = S * norm.pdf(d1) * np.sqrt(T)
            return delta, gamma, theta/365, vega/100

        # Equity Delta
        greeks['delta'] += self.portfolio['equity_qty']
        
        # LEAP Greeks
        if self.portfolio['leap']:
            leap = self.portfolio['leap']
            days = (leap['expiry_date'] - date).days
            T = days / 365.0
            d, g, t, v = call_greeks(stock_price, leap['strike'], T, self.risk_free_rate, vol)
            qty = leap['qty'] * 100
            greeks['delta'] += d * qty
            greeks['gamma'] += g * qty
            greeks['theta'] += t * qty
            greeks['vega'] += v * qty

        # Wheel Put Greeks (Short)
        if self.portfolio['wheel_put']:
            put = self.portfolio['wheel_put']
            days = (put['expiry_date'] - date).days
            T = days / 365.0
            d, g, t, v = put_greeks(stock_price, put['strike'], T, self.risk_free_rate, vol)
            qty = put['qty'] * 100
            # Short position -> flip signs
            greeks['delta'] -= d * qty
            greeks['gamma'] -= g * qty
            greeks['theta'] -= t * qty
            greeks['vega'] -= v * qty

        # Wheel Call Greeks (Short)
        if self.portfolio['wheel_call']:
            call = self.portfolio['wheel_call']
            days = (call['expiry_date'] - date).days
            T = days / 365.0
            d, g, t, v = call_greeks(stock_price, call['strike'], T, self.risk_free_rate, vol)
            qty = call['qty'] * 100
            # Short position
            greeks['delta'] -= d * qty
            greeks['gamma'] -= g * qty
            greeks['theta'] -= t * qty
            greeks['vega'] -= v * qty
            
        return greeks

    def run(self) -> BacktestResult:
        df = self.fetch_data()
        return self._run_with_df(df)
    
    def run_with_data(self, df: pd.DataFrame) -> BacktestResult:
        """
        Run backtest with pre-fetched data (used for Monte Carlo simulations).
        """
        return self._run_with_df(df)
    
    def _run_with_df(self, df: pd.DataFrame) -> BacktestResult:
        
        # Initial Setup
        first_row = df.iloc[0]
        self._initial_allocation(df.index[0], first_row)
        
        max_portfolio_value = self.portfolio['cash'] # Initialize
        
        for date, row in df.iterrows():
            current_price = float(row['Close'].iloc[0]) if isinstance(row['Close'], pd.Series) else float(row['Close'])
            volatility = float(row['volatility'].iloc[0]) if isinstance(row['volatility'], pd.Series) else float(row['volatility'])
            
            # 1. Update Portfolio Values
            self._update_leap_price(date, current_price, volatility)
            self._update_wheel_prices(date, current_price, volatility)
            
            # 2. Check Logic
            self._check_monthly_withdrawal(date)
            self._check_leap_exit_conditions(date, current_price, volatility)
            self._check_rebalancing(date, current_price, volatility)
            
            if self.params.use_wheel_strategy:
                ma_short = float(row['ma_short'].iloc[0]) if isinstance(row['ma_short'], pd.Series) else float(row['ma_short'])
                ma_long = float(row['ma_long'].iloc[0]) if isinstance(row['ma_long'], pd.Series) else float(row['ma_long'])
                self._run_wheel_strategy(date, current_price, volatility, ma_short, ma_long)
            
            # 3. Record Snapshot
            equity_val = self.portfolio['equity_qty'] * current_price
            leap_val = (self.portfolio['leap']['qty'] * self.portfolio['leap']['current_price'] * 100) if self.portfolio['leap'] else 0
            
            wheel_put_val = (self.portfolio['wheel_put']['qty'] * self.portfolio['wheel_put']['current_price'] * 100) if self.portfolio['wheel_put'] else 0
            wheel_call_val = (self.portfolio['wheel_call']['qty'] * self.portfolio['wheel_call']['current_price'] * 100) if self.portfolio['wheel_call'] else 0
            
            total_val = self.portfolio['cash'] + equity_val + leap_val - wheel_put_val - wheel_call_val
            
            max_portfolio_value = max(max_portfolio_value, total_val)
            drawdown = (max_portfolio_value - total_val) / max_portfolio_value if max_portfolio_value > 0 else 0
            
            # Benchmark (Buy & Hold) Calculation
            if not hasattr(self, 'initial_equity_price'):
                self.initial_equity_price = float(df.iloc[0]['Close'].iloc[0]) if isinstance(df.iloc[0]['Close'], pd.Series) else float(df.iloc[0]['Close'])
            
            benchmark_val = (self.params.initial_capital / self.initial_equity_price) * current_price
            
            # Greeks
            greeks = self._calculate_portfolio_greeks(date, current_price, volatility)

            self.history.append(PortfolioSnapshot(
                date=date.strftime("%Y-%m-%d"),
                equity_value=round(equity_val, 2),
                leap_value=round(leap_val, 2),
                cash_value=round(self.portfolio['cash'], 2),
                total_value=round(total_val, 2),
                benchmark_value=round(benchmark_val, 2),
                equity_price=round(current_price, 2),
                drawdown=round(drawdown, 4),
                greeks=greeks
            ))

        return self._generate_result(df)

    def _initial_allocation(self, date, row):
        price = float(row['Close'].iloc[0]) if isinstance(row['Close'], pd.Series) else float(row['Close'])
        vol = float(row['volatility'].iloc[0]) if isinstance(row['volatility'], pd.Series) else float(row['volatility'])
        
        total_capital = self.portfolio['cash']
        
        target_equity = total_capital * (self.params.equity_allocation / 100)
        target_leap = total_capital * (self.params.leap_allocation / 100)
        
        # Buy Equity
        qty = target_equity / price
        cost = qty * price
        self.portfolio['equity_qty'] = qty
        self.portfolio['cash'] -= cost
        self.trades.append(Trade(
            date=date.strftime("%Y-%m-%d"), type="BUY", asset="EQUITY", 
            quantity=qty, price=price, value=cost, reason="Initial Allocation"
        ))
        
        # Buy LEAP
        self._open_new_leap(date, price, vol, target_leap)

    def _open_new_leap(self, date, stock_price, vol, target_amount):
        if target_amount <= 0:
            return

        # Calculate Expiry (approx 12-18 months)
        days_to_expiry = self.params.leap_expiration_months * 30
        expiry_date = date + timedelta(days=days_to_expiry)
        T = days_to_expiry / 365.0
        
        # Find Strike
        strike = find_strike_for_delta(stock_price, T, self.risk_free_rate, vol, self.params.leap_delta)
        
        # Calculate Price
        option_price = black_scholes_call_price(stock_price, strike, T, self.risk_free_rate, vol)
        
        # Calculate Qty (1 contract = 100 shares)
        # target_amount = qty * 100 * option_price
        num_contracts = target_amount / (100 * option_price)
        
        if num_contracts < 0.01: # Too small to buy
            return

        cost = num_contracts * 100 * option_price
        
        if self.portfolio['cash'] < cost:
            # Adjust if not enough cash (shouldn't happen in initial alloc, but possible in rebalance)
            cost = self.portfolio['cash']
            num_contracts = cost / (100 * option_price)
            
        self.portfolio['cash'] -= cost
        self.portfolio['leap'] = {
            'strike': strike,
            'expiry_date': expiry_date,
            'qty': num_contracts,
            'entry_price': option_price,
            'current_price': option_price
        }
        
        self.trades.append(Trade(
            date=date.strftime("%Y-%m-%d"), type="BUY", asset="LEAP",
            quantity=num_contracts, price=option_price, value=cost,
            reason=f"Open LEAP {expiry_date.strftime('%Y-%m')} Strike {strike:.2f}"
        ))

    def _update_leap_price(self, date, stock_price, vol):
        if not self.portfolio['leap']:
            return
            
        expiry = self.portfolio['leap']['expiry_date']
        days_to_expiry = (expiry - date).days
        T = days_to_expiry / 365.0
        
        if T <= 0:
            # Expired
            price = max(0, stock_price - self.portfolio['leap']['strike'])
        else:
            price = black_scholes_call_price(
                stock_price, self.portfolio['leap']['strike'], T, 
                self.risk_free_rate, vol
            )
            
        self.portfolio['leap']['current_price'] = price

    def _check_leap_exit_conditions(self, date, stock_price, vol):
        if not self.portfolio['leap']:
            return

        leap = self.portfolio['leap']
        
        # 1. Check Expiration
        days_to_expiry = (leap['expiry_date'] - date).days
        if days_to_expiry <= 5: # Close 5 days before expiry
            self._close_leap(date, "Expiration approaching")
            # Re-open immediately? The requirements imply continuous strategy.
            # We'll re-allocate in rebalancing step or immediately here.
            # Let's trigger a full rebalance to get back to target weights.
            self._rebalance_portfolio(date, stock_price, vol, reason="Post-Expiration Rebalance")
            return

        # 2. Check Profit/Loss Limits
        pnl_pct = (leap['current_price'] - leap['entry_price']) / leap['entry_price'] * 100
        
        should_close = False
        reason = ""
        
        if days_to_expiry > 180: # > 6 months
            if pnl_pct >= self.params.profit_limit_6m:
                should_close = True; reason = "Profit Limit (>6m)"
            elif pnl_pct <= -self.params.loss_limit_6m:
                should_close = True; reason = "Loss Limit (>6m)"
        elif days_to_expiry > 90: # 3-6 months
            if pnl_pct >= self.params.profit_limit_3m:
                should_close = True; reason = "Profit Limit (3-6m)"
            elif pnl_pct <= -self.params.loss_limit_3m:
                should_close = True; reason = "Loss Limit (3-6m)"
        else: # < 3 months
            if pnl_pct >= self.params.profit_limit_0m:
                should_close = True; reason = "Profit Limit (<3m)"
            elif pnl_pct <= -self.params.loss_limit_0m:
                should_close = True; reason = "Loss Limit (<3m)"
                
        if should_close:
            self._close_leap(date, reason)
            # After closing, we are cash heavy. 
            # Strategy: "Close the LEAP calls when profit or loss reaches..."
            # Implies we stay in cash? Or buy new LEAP? 
            # Usually in wheel/LEAP strategies, you roll.
            # I will re-open a new LEAP to maintain exposure, effectively "Rolling".
            
            # Calculate current total value to determine new target size
            # But simple approach: Rebalance to target weights.
            self._rebalance_portfolio(date, stock_price, vol, reason="Rolling after P/L Hit")

    def _close_leap(self, date, reason):
        if not self.portfolio['leap']:
            return
            
        leap = self.portfolio['leap']
        value = leap['qty'] * 100 * leap['current_price']
        self.portfolio['cash'] += value
        
        self.trades.append(Trade(
            date=date.strftime("%Y-%m-%d"), type="SELL", asset="LEAP",
            quantity=leap['qty'], price=leap['current_price'], value=value,
            reason=reason
        ))
        self.portfolio['leap'] = None

    def _check_rebalancing(self, date, stock_price, vol):
        # Trigger 1: Allocation Deviation
        equity_val = self.portfolio['equity_qty'] * stock_price
        leap_val = (self.portfolio['leap']['qty'] * self.portfolio['leap']['current_price'] * 100) if self.portfolio['leap'] else 0
        cash_val = self.portfolio['cash']
        total_val = equity_val + leap_val + cash_val
        
        if total_val == 0: return

        current_eq_pct = (equity_val / total_val) * 100
        current_leap_pct = (leap_val / total_val) * 100
        current_cash_pct = (cash_val / total_val) * 100
        
        # Check drift
        eq_drift = abs(current_eq_pct - self.params.equity_allocation)
        leap_drift = abs(current_leap_pct - self.params.leap_allocation)
        
        if eq_drift > self.params.rebalance_delta or leap_drift > self.params.rebalance_delta:
            self._rebalance_portfolio(date, stock_price, vol, reason=f"Allocation Drift (Eq: {eq_drift:.1f}%, Leap: {leap_drift:.1f}%)")
            return

        # Trigger 2: Equity Price Movement (from last rebalance)
        # Need to track last rebalance price. 
        # For P0, let's just track price movement from "entry" or "last check"?
        # Requirement: "when target equity is down by `delta_down` or up by `delta_up`"
        # This usually means from the last rebalancing point.
        
        # We need a state variable: self.last_rebalance_price
        if not hasattr(self, 'last_rebalance_price'):
            self.last_rebalance_price = stock_price
            
        price_change_pct = (stock_price - self.last_rebalance_price) / self.last_rebalance_price * 100
        
        if price_change_pct >= self.params.equity_up_trigger:
            self._rebalance_portfolio(date, stock_price, vol, reason=f"Equity Up {price_change_pct:.1f}%")
        elif price_change_pct <= -self.params.equity_down_trigger:
            self._rebalance_portfolio(date, stock_price, vol, reason=f"Equity Down {price_change_pct:.1f}%")

    def _rebalance_portfolio(self, date, stock_price, vol, reason):
        # 1. Close everything (virtual close to calculate total capital easily)
        # Or better: calculate target amounts and adjust.
        
        # Calculate Total Value
        equity_val = self.portfolio['equity_qty'] * stock_price
        leap_val = (self.portfolio['leap']['qty'] * self.portfolio['leap']['current_price'] * 100) if self.portfolio['leap'] else 0
        cash_val = self.portfolio['cash']
        total_val = equity_val + leap_val + cash_val
        
        target_equity_val = total_val * (self.params.equity_allocation / 100)
        target_leap_val = total_val * (self.params.leap_allocation / 100)
        
        # Adjust Equity
        eq_diff = target_equity_val - equity_val
        if abs(eq_diff) > 100: # Threshold to avoid tiny trades
            if eq_diff > 0: # Buy
                qty_to_buy = eq_diff / stock_price
                cost = qty_to_buy * stock_price
                if self.portfolio['cash'] >= cost:
                    self.portfolio['equity_qty'] += qty_to_buy
                    self.portfolio['cash'] -= cost
                    self.trades.append(Trade(date=date.strftime("%Y-%m-%d"), type="BUY", asset="EQUITY", quantity=qty_to_buy, price=stock_price, value=cost, reason=f"Rebalance: {reason}"))
            else: # Sell
                qty_to_sell = abs(eq_diff) / stock_price
                proceeds = qty_to_sell * stock_price
                self.portfolio['equity_qty'] -= qty_to_sell
                self.portfolio['cash'] += proceeds
                self.trades.append(Trade(date=date.strftime("%Y-%m-%d"), type="SELL", asset="EQUITY", quantity=qty_to_sell, price=stock_price, value=proceeds, reason=f"Rebalance: {reason}"))

        # Adjust LEAP
        # For LEAPs, we don't just "add/remove" contracts usually, we might need to roll if the delta has shifted significantly.
        # But for simple rebalancing, we can buy/sell contracts of the CURRENT LEAP if it exists and is healthy.
        # If no LEAP exists, open one.
        
        if self.portfolio['leap']:
            leap = self.portfolio['leap']
            current_leap_val = leap['qty'] * 100 * leap['current_price']
            leap_diff = target_leap_val - current_leap_val
            
            # If we need to change LEAP exposure significantly, or if we want to reset delta?
            # Requirement doesn't specify rolling on rebalance. Assume adjust quantity.
            
            if abs(leap_diff) > 500: # Threshold
                if leap_diff > 0: # Buy more
                    num_contracts = leap_diff / (100 * leap['current_price'])
                    cost = num_contracts * 100 * leap['current_price']
                    if self.portfolio['cash'] >= cost:
                        self.portfolio['leap']['qty'] += num_contracts
                        self.portfolio['cash'] -= cost
                        self.trades.append(Trade(date=date.strftime("%Y-%m-%d"), type="BUY", asset="LEAP", quantity=num_contracts, price=leap['current_price'], value=cost, reason=f"Rebalance: {reason}"))
                else: # Sell some
                    num_contracts = abs(leap_diff) / (100 * leap['current_price'])
                    proceeds = num_contracts * 100 * leap['current_price']
                    # Don't sell more than we have
                    if num_contracts > self.portfolio['leap']['qty']:
                         num_contracts = self.portfolio['leap']['qty']
                         proceeds = num_contracts * 100 * leap['current_price']
                    
                    self.portfolio['leap']['qty'] -= num_contracts
                    self.portfolio['cash'] += proceeds
                    self.trades.append(Trade(date=date.strftime("%Y-%m-%d"), type="SELL", asset="LEAP", quantity=num_contracts, price=leap['current_price'], value=proceeds, reason=f"Rebalance: {reason}"))
        else:
            # No leap, open new
            self._open_new_leap(date, stock_price, vol, target_leap_val)

        self.last_rebalance_price = stock_price

    def _update_wheel_prices(self, date, stock_price, vol):
        # Update Put Price
        if self.portfolio['wheel_put']:
            put = self.portfolio['wheel_put']
            days = (put['expiry_date'] - date).days
            T = days / 365.0
            if T <= 0:
                put['current_price'] = max(0, put['strike'] - stock_price)
            else:
                put['current_price'] = black_scholes_put_price(stock_price, put['strike'], T, self.risk_free_rate, vol)
                
        # Update Call Price
        if self.portfolio['wheel_call']:
            call = self.portfolio['wheel_call']
            days = (call['expiry_date'] - date).days
            T = days / 365.0
            if T <= 0:
                call['current_price'] = max(0, stock_price - call['strike'])
            else:
                call['current_price'] = black_scholes_call_price(stock_price, call['strike'], T, self.risk_free_rate, vol)

    def _run_wheel_strategy(self, date, stock_price, vol, ma_short, ma_long):
        # 1. Manage Existing Positions
        self._manage_wheel_positions(date, stock_price)
        
        # 2. Open New Positions based on Signal
        # Signal: MA Short > MA Long -> Bullish -> Sell Put
        # Signal: MA Short < MA Long -> Bearish -> (If holding stock, Sell Call)
        
        if pd.isna(ma_short) or pd.isna(ma_long):
            return
            
        is_bullish = ma_short > ma_long
        
        # Calculate available capital for Wheel (allocated from cash)
        # Note: In real world, this uses margin. Here we use "wheel_allocation" from params, or just remaining cash?
        # Params has `wheel_allocation`. Let's assume it's a fixed amount of cash reserved for this.
        # But `wheel_allocation` is a float amount? No, typically a %.
        # Let's check model.py -> `wheel_allocation: float` description "Allocation for Wheel Strategy (uses cash portion)"
        # If it's 0, maybe we don't do it.
        
        wheel_capital = self.params.wheel_allocation 
        if wheel_capital <= 0: return # Or use remaining cash?
        
        # Logic for Selling Put (Cash Secured Put)
        if is_bullish and not self.portfolio['wheel_put']:
            # Sell Put
            # Strike: ATM or slightly OTM? Let's say 0.30 Delta OTM Put, or just 5% OTM?
            # Simple rule: Strike = 95% of current price
            strike = stock_price * 0.95
            
            # Expiry: 30 days
            days_to_expiry = 30
            expiry_date = date + timedelta(days=days_to_expiry)
            T = days_to_expiry / 365.0
            
            price = black_scholes_put_price(stock_price, strike, T, self.risk_free_rate, vol)
            
            # Qty: Covered by wheel_capital
            # Cost to cover = Strike * 100 * Qty
            # Qty = wheel_capital / (Strike * 100)
            
            num_contracts = int(wheel_capital / (strike * 100))
            if num_contracts > 0:
                premium = num_contracts * 100 * price
                self.portfolio['cash'] += premium
                self.portfolio['wheel_put'] = {
                    'strike': strike,
                    'expiry_date': expiry_date,
                    'qty': num_contracts,
                    'entry_price': price,
                    'current_price': price
                }
                self.trades.append(Trade(
                    date=date.strftime("%Y-%m-%d"), type="SELL_OPEN", asset="PUT",
                    quantity=num_contracts, price=price, value=premium,
                    reason=f"Wheel: Sell Put (Bullish Signal)"
                ))

        # Logic for Selling Call (Covered Call)
        # We need to hold the underlying to sell a covered call? 
        # Or is this "Wheel" separate from the LEAP strategy?
        # Usually Wheel implies you own the stock.
        # In this combined app, we have 'equity_qty'. We can write calls against it.
        
        if not is_bullish and not self.portfolio['wheel_call'] and self.portfolio['equity_qty'] > 0:
            # Sell Call
            # Strike: 105% of current price
            strike = stock_price * 1.05
            
            # Expiry: 30 days
            days_to_expiry = 30
            expiry_date = date + timedelta(days=days_to_expiry)
            T = days_to_expiry / 365.0
            
            price = black_scholes_call_price(stock_price, strike, T, self.risk_free_rate, vol)
            
            # Qty: Covered by equity holdings
            # Max contracts = equity_qty / 100
            max_contracts = int(self.portfolio['equity_qty'] / 100)
            
            if max_contracts > 0:
                premium = max_contracts * 100 * price
                self.portfolio['cash'] += premium
                self.portfolio['wheel_call'] = {
                    'strike': strike,
                    'expiry_date': expiry_date,
                    'qty': max_contracts,
                    'entry_price': price,
                    'current_price': price
                }
                self.trades.append(Trade(
                    date=date.strftime("%Y-%m-%d"), type="SELL_OPEN", asset="CALL",
                    quantity=max_contracts, price=price, value=premium,
                    reason=f"Wheel: Sell Call (Bearish Signal)"
                ))

    def _manage_wheel_positions(self, date, stock_price):
        # Manage Put
        if self.portfolio['wheel_put']:
            put = self.portfolio['wheel_put']
            days = (put['expiry_date'] - date).days
            
            if days <= 0:
                # Expired
                if stock_price < put['strike']:
                    # Assigned! Buy stock at strike.
                    cost = put['qty'] * 100 * put['strike']
                    # Assuming we have the cash (secured)
                    self.portfolio['cash'] -= cost
                    self.portfolio['equity_qty'] += put['qty'] * 100
                    
                    self.trades.append(Trade(
                        date=date.strftime("%Y-%m-%d"), type="ASSIGNED", asset="PUT",
                        quantity=put['qty'], price=put['strike'], value=cost,
                        reason="Put Assigned (Wheel)"
                    ))
                else:
                    # Expired Worthless (Profit kept)
                    self.trades.append(Trade(
                        date=date.strftime("%Y-%m-%d"), type="EXPIRED", asset="PUT",
                        quantity=put['qty'], price=0, value=0,
                        reason="Put Expired Worthless (Wheel)"
                    ))
                self.portfolio['wheel_put'] = None

        # Manage Call
        if self.portfolio['wheel_call']:
            call = self.portfolio['wheel_call']
            days = (call['expiry_date'] - date).days
            
            if days <= 0:
                # Expired
                if stock_price > call['strike']:
                    # Assigned! Sell stock at strike.
                    proceeds = call['qty'] * 100 * call['strike']
                    self.portfolio['equity_qty'] -= call['qty'] * 100
                    self.portfolio['cash'] += proceeds
                    
                    self.trades.append(Trade(
                        date=date.strftime("%Y-%m-%d"), type="ASSIGNED", asset="CALL",
                        quantity=call['qty'], price=call['strike'], value=proceeds,
                        reason="Call Assigned (Wheel)"
                    ))
                else:
                    # Expired Worthless
                    self.trades.append(Trade(
                        date=date.strftime("%Y-%m-%d"), type="EXPIRED", asset="CALL",
                        quantity=call['qty'], price=0, value=0,
                        reason="Call Expired Worthless (Wheel)"
                    ))
                self.portfolio['wheel_call'] = None

    def _check_monthly_withdrawal(self, date):
        if self.params.monthly_withdrawal <= 0:
            return
            
        current_month = date.month
        if self.last_withdrawal_month != current_month:
            # Withdraw
            amount = self.params.monthly_withdrawal
            if self.portfolio['cash'] >= amount:
                self.portfolio['cash'] -= amount
                self.trades.append(Trade(
                    date=date.strftime("%Y-%m-%d"), type="WITHDRAW", asset="CASH",
                    quantity=1, price=amount, value=amount, reason="Monthly Spending"
                ))
            else:
                # Not enough cash? Liquidate?
                # For P0, let's just go negative cash (margin) or stop withdrawal?
                # Going negative cash is easiest to track "shortfall" or assume margin.
                self.portfolio['cash'] -= amount
                self.trades.append(Trade(
                    date=date.strftime("%Y-%m-%d"), type="WITHDRAW", asset="CASH",
                    quantity=1, price=amount, value=amount, reason="Monthly Spending (Margin)"
                ))
            
            self.last_withdrawal_month = current_month

    def _generate_result(self, df) -> BacktestResult:
        if not self.history:
            return BacktestResult(
                backtest_id=str(uuid.uuid4()), params=self.params,
                total_return=0, cagr=0, max_drawdown=0, sharpe_ratio=0, trades=[], history=[]
            )
            
        start_val = self.params.initial_capital
        end_val = self.history[-1].total_value
        
        total_return = (end_val - start_val) / start_val * 100
        
        # CAGR
        days = (datetime.strptime(self.params.end_date, "%Y-%m-%d") - datetime.strptime(self.params.start_date, "%Y-%m-%d")).days
        years = days / 365.25
        if years > 0:
            cagr = ((end_val / start_val) ** (1 / years) - 1) * 100
        else:
            cagr = total_return

        # Max Drawdown
        max_drawdown = max(h.drawdown for h in self.history) * 100
        
        # Sharpe Ratio
        # Calculate daily returns of portfolio
        portfolio_values = pd.Series([h.total_value for h in self.history])
        daily_returns = portfolio_values.pct_change().dropna()
        if daily_returns.std() > 0:
            sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(252)
        else:
            sharpe = 0
            
        return BacktestResult(
            backtest_id=str(uuid.uuid4()),
            params=self.params,
            total_return=round(total_return, 2),
            cagr=round(cagr, 2),
            max_drawdown=round(max_drawdown, 2),
            sharpe_ratio=round(sharpe, 2),
            trades=self.trades,
            history=self.history
        )
