import numpy as np
from scipy.stats import norm

def calculate_d1(S, K, T, r, sigma):
    """
    Calculate d1 for Black-Scholes model
    """
    if T <= 0 or sigma <= 0:
        return 0
    return (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))

def calculate_d2(d1, T, sigma):
    """
    Calculate d2 for Black-Scholes model
    """
    if T <= 0 or sigma <= 0:
        return 0
    return d1 - sigma * np.sqrt(T)

def black_scholes_call_price(S, K, T, r, sigma):
    """
    Calculate Black-Scholes price for a call option.
    
    Args:
        S (float): Current stock price
        K (float): Strike price
        T (float): Time to expiration in years
        r (float): Risk-free interest rate (annual)
        sigma (float): Volatility (annual)
        
    Returns:
        float: Call option price
    """
    if T <= 0:
        return max(0, S - K)
        
    d1 = calculate_d1(S, K, T, r, sigma)
    d2 = calculate_d2(d1, T, sigma)
    
    call_price = S * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return call_price

def black_scholes_put_price(S, K, T, r, sigma):
    """
    Calculate Black-Scholes price for a put option.
    """
    if T <= 0:
        return max(0, K - S)
        
    d1 = calculate_d1(S, K, T, r, sigma)
    d2 = calculate_d2(d1, T, sigma)
    
    put_price = K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    return put_price

def calculate_delta(S, K, T, r, sigma):
    """
    Calculate Delta for a call option.
    
    Args:
        S (float): Current stock price
        K (float): Strike price
        T (float): Time to expiration in years
        r (float): Risk-free interest rate (annual)
        sigma (float): Volatility (annual)
        
    Returns:
        float: Delta value (0 to 1)
    """
    if T <= 0:
        return 1.0 if S > K else 0.0
        
    d1 = calculate_d1(S, K, T, r, sigma)
    return norm.cdf(d1)

def find_strike_for_delta(S, T, r, sigma, target_delta):
    """
    Find the strike price that gives a specific target delta.
    
    Since Delta = N(d1), d1 = N^(-1)(Delta)
    d1 = (ln(S/K) + (r + sigma^2/2)T) / (sigma * sqrt(T))
    
    We can solve for K.
    
    Args:
        S (float): Current stock price
        T (float): Time to expiration in years
        r (float): Risk-free interest rate (annual)
        sigma (float): Volatility (annual)
        target_delta (float): Target delta (0 to 1)
        
    Returns:
        float: Strike price
    """
    if target_delta <= 0 or target_delta >= 1 or T <= 0 or sigma <= 0:
        return S # Fallback
        
    d1 = norm.ppf(target_delta)
    
    # Rearranging d1 formula to solve for K:
    # d1 * sigma * sqrt(T) = ln(S/K) + (r + sigma^2/2)T
    # ln(S/K) = d1 * sigma * sqrt(T) - (r + sigma^2/2)T
    # S/K = exp(d1 * sigma * sqrt(T) - (r + sigma^2/2)T)
    # K = S / exp(...)
    
    exponent = d1 * sigma * np.sqrt(T) - (r + 0.5 * sigma ** 2) * T
    K = S / np.exp(exponent)
    
    return K
