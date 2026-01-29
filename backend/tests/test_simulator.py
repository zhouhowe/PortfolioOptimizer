import pytest
import pandas as pd
import numpy as np
from app.services.simulator import MarketSimulator

def test_generate_scenario_structure():
    symbol = "TEST"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    
    df = MarketSimulator.generate_scenario(symbol, start_date, end_date, "neutral")
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns
    assert "Open" in df.columns
    assert "High" in df.columns
    assert "Low" in df.columns
    assert "Volume" in df.columns

def test_generate_scenario_dates():
    symbol = "TEST"
    start_date = "2023-01-01"
    end_date = "2023-01-10" # 9 days diff
    
    df = MarketSimulator.generate_scenario(symbol, start_date, end_date, "neutral")
    
    # Check index
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index[0] == pd.Timestamp(start_date)
    # The simulator generates 'days' steps. 
    # (end_date - start_date).days = 9
    assert len(df) == 9

def test_bull_scenario_returns():
    # Bull scenario should generally be positive
    # Use a long period to average out noise
    symbol = "TEST"
    start_date = "2020-01-01"
    end_date = "2025-01-01" # 5 years
    
    # Set seed for reproducibility if possible, but GBM uses np.random
    np.random.seed(42)
    
    df_bull = MarketSimulator.generate_scenario(symbol, start_date, end_date, "bull")
    
    total_return = (df_bull['Close'].iloc[-1] / df_bull['Close'].iloc[0]) - 1
    assert total_return > 0 # Should be positive for bull market over 5 years

def test_bear_scenario_returns():
    symbol = "TEST"
    start_date = "2020-01-01"
    end_date = "2025-01-01"
    
    # Compare Bull vs Bear
    # Bull should definitely outperform Bear over same period/seed (mostly)
    # But different seeds might vary. 
    # Let's just check that Bear return is < Bull return with same seed.
    
    np.random.seed(42)
    df_bull = MarketSimulator.generate_scenario(symbol, start_date, end_date, "bull")
    bull_ret = (df_bull['Close'].iloc[-1] / df_bull['Close'].iloc[0]) - 1
    
    np.random.seed(42)
    df_bear = MarketSimulator.generate_scenario(symbol, start_date, end_date, "bear")
    bear_ret = (df_bear['Close'].iloc[-1] / df_bear['Close'].iloc[0]) - 1
    
    assert bull_ret > bear_ret

def test_generate_custom_scenario():
    symbol = "TEST"
    start_date = "2023-01-01"
    end_date = "2023-12-31"
    mu = 0.10  # 10% drift
    sigma = 0.20 # 20% volatility
    
    df = MarketSimulator.generate_custom_scenario(symbol, start_date, end_date, mu, sigma)
    
    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Close" in df.columns
    assert len(df) > 0
    
    # Check if custom parameters affect outcome (simple check)
    np.random.seed(42)
    df_high_drift = MarketSimulator.generate_custom_scenario(symbol, start_date, end_date, 0.50, 0.20)
    
    np.random.seed(42)
    df_low_drift = MarketSimulator.generate_custom_scenario(symbol, start_date, end_date, 0.0, 0.20)
    
    assert df_high_drift['Close'].iloc[-1] > df_low_drift['Close'].iloc[-1]