import pytest
import numpy as np
from app.services.option_pricing import (
    black_scholes_call_price, 
    black_scholes_put_price, 
    calculate_delta, 
    find_strike_for_delta
)

def test_black_scholes_call_price():
    # Known value: S=100, K=100, T=1, r=0.05, sigma=0.2
    # Call price should be approx 10.45
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    price = black_scholes_call_price(S, K, T, r, sigma)
    assert abs(price - 10.45) < 0.1

def test_black_scholes_put_price():
    # Known value: S=100, K=100, T=1, r=0.05, sigma=0.2
    # Put price should be approx 5.57
    # Put-Call Parity: C - P = S - K * exp(-rT)
    # 10.45 - 5.57 = 4.88
    # 100 - 100 * exp(-0.05) = 100 - 95.12 = 4.88
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    price = black_scholes_put_price(S, K, T, r, sigma)
    assert abs(price - 5.57) < 0.1

def test_calculate_delta():
    # ATM Call Delta approx 0.5 (usually slightly more due to drift)
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
    delta = calculate_delta(S, K, T, r, sigma)
    assert 0.5 < delta < 0.7

def test_find_strike_for_delta():
    # Find strike for delta 0.80 (deep ITM)
    S, T, r, sigma = 100, 1, 0.05, 0.2
    target_delta = 0.80
    strike = find_strike_for_delta(S, T, r, sigma, target_delta)
    
    # Verify by calculating delta back
    calculated_delta = calculate_delta(S, strike, T, r, sigma)
    assert abs(calculated_delta - target_delta) < 0.01
