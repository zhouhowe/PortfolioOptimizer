import numpy as np
import pandas as pd
from datetime import datetime, timedelta

class MarketSimulator:
    @staticmethod
    def geometric_brownian_motion(S0, mu, sigma, T, dt, steps):
        """
        Generate a GBM path.
        S0: Initial stock price
        mu: Drift (annualized return)
        sigma: Volatility (annualized)
        T: Time horizon in years
        dt: Time step in years
        steps: Number of steps
        """
        t = np.linspace(0, T, steps)
        W = np.random.standard_normal(size=steps) 
        W = np.cumsum(W)*np.sqrt(dt) ### standard brownian motion ###
        X = (mu-0.5*sigma**2)*t + sigma*W 
        S = S0*np.exp(X) ### geometric brownian motion ###
        return S

    @staticmethod
    def generate_custom_scenario(symbol, start_date_str, end_date_str, mu, sigma):
        """
        Generate synthetic OHLC data with custom drift and volatility.
        mu: Expected annual drift (e.g., 0.08 for 8%)
        sigma: Expected annual volatility (e.g., 0.20 for 20%)
        """
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        days = (end_date - start_date).days
        
        if days <= 0:
            raise ValueError("End date must be after start date")

        # Parameters based on custom input
        S0 = 100.0 # Base price
        
        dt = 1/252
        steps = days
        T = days/365.0
        
        prices = MarketSimulator.geometric_brownian_motion(S0, mu, sigma, T, dt, steps)
        
        # Create DataFrame
        date_range = pd.date_range(start=start_date, periods=steps, freq='D')
        df = pd.DataFrame(index=date_range)
        df['Close'] = prices
        # Add synthetic OHLC (simple approximation)
        df['Open'] = df['Close'].shift(1).fillna(S0)
        df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + np.random.rand(steps) * 0.01)
        df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - np.random.rand(steps) * 0.01)
        df['Volume'] = 1000000
        
        return df

    @staticmethod
    def generate_scenario(symbol, start_date_str, end_date_str, scenario_type="neutral"):
        """
        Generate synthetic OHLC data.
        Scenario Types:
        - neutral: 8% return, 20% vol
        - bull: 20% return, 15% vol
        - bear: -15% return, 30% vol
        - high_vol: 0% return, 50% vol
        """
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
        days = (end_date - start_date).days
        
        if days <= 0:
            raise ValueError("End date must be after start date")

        # Parameters based on scenario
        S0 = 100.0 # Base price
        if scenario_type == "bull":
            mu = 0.20
            sigma = 0.15
        elif scenario_type == "bear":
            mu = -0.15
            sigma = 0.30
        elif scenario_type == "high_vol":
            mu = 0.0
            sigma = 0.50
        else: # Neutral
            mu = 0.08
            sigma = 0.20
            
        dt = 1/252
        steps = days
        T = days/365.0
        
        prices = MarketSimulator.geometric_brownian_motion(S0, mu, sigma, T, dt, steps)
        
        # Create DataFrame
        date_range = pd.date_range(start=start_date, periods=steps, freq='D')
        df = pd.DataFrame(index=date_range)
        df['Close'] = prices
        # Add synthetic OHLC (simple approximation)
        df['Open'] = df['Close'].shift(1).fillna(S0)
        df['High'] = df[['Open', 'Close']].max(axis=1) * (1 + np.random.rand(steps) * 0.01)
        df['Low'] = df[['Open', 'Close']].min(axis=1) * (1 - np.random.rand(steps) * 0.01)
        df['Volume'] = 1000000
        
        return df