"""
Black-Scholes Greeks calculations
"""
import math
from scipy.stats import norm
from typing import Dict


def calculate_greeks(
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    sigma: float,
    right: str
) -> Dict[str, float]:
    """
    Calculate Black-Scholes Greeks for a single option contract.
    
    Args:
        S: Spot price
        K: Strike price
        T: Time to expiry (years)
        r: Risk-free rate (decimal)
        q: Dividend yield (decimal)
        sigma: Implied volatility (decimal)
        right: "C" for call, "P" for put
    
    Returns:
        Dictionary with delta, gamma, vanna, charm, vega, theta
    """
    # Edge case handling
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        return {
            "delta": 0.0,
            "gamma": 0.0,
            "vanna": 0.0,
            "charm": 0.0,
            "vega": 0.0,
            "theta": 0.0
        }
    
    # Calculate d1 and d2
    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    
    # Standard normal PDF and CDF
    pdf_d1 = norm.pdf(d1)
    cdf_d1 = norm.cdf(d1)
    cdf_d2 = norm.cdf(d2)
    cdf_neg_d1 = norm.cdf(-d1)
    cdf_neg_d2 = norm.cdf(-d2)
    
    # Delta
    if right.upper() == "C":
        delta = math.exp(-q * T) * cdf_d1
    else:  # Put
        delta = -math.exp(-q * T) * cdf_neg_d1
    
    # Gamma (same for calls and puts)
    gamma = math.exp(-q * T) * pdf_d1 / (S * sigma * sqrt_T)
    
    # Vanna = dDelta/dVol = dGamma/dSpot (partial derivative)
    # Vanna = -pdf(d1) * d2 / sigma
    vanna = -pdf_d1 * d2 / sigma
    
    # Charm (delta decay) = dDelta/dTime
    # For calls: charm = -exp(-q*T) * [pdf(d1) * (r-q)/(sigma*sqrt(T)) - q*cdf(d1) - pdf(d1)*d2/(2*T)]
    # For puts: charm = -exp(-q*T) * [pdf(d1) * (r-q)/(sigma*sqrt(T)) + q*cdf(-d1) - pdf(d1)*d2/(2*T)]
    if T > 0:
        if right.upper() == "C":
            charm = -math.exp(-q * T) * (
                pdf_d1 * (r - q) / (sigma * sqrt_T) -
                q * cdf_d1 -
                pdf_d1 * d2 / (2 * T)
            )
        else:  # Put
            charm = -math.exp(-q * T) * (
                pdf_d1 * (r - q) / (sigma * sqrt_T) +
                q * cdf_neg_d1 -
                pdf_d1 * d2 / (2 * T)
            )
    else:
        charm = 0.0
    
    # Vega (same for calls and puts)
    vega = S * math.exp(-q * T) * pdf_d1 * sqrt_T / 100.0  # Divide by 100 for 1% vol change
    
    # Theta (time decay)
    if right.upper() == "C":
        theta = (
            -S * math.exp(-q * T) * pdf_d1 * sigma / (2 * sqrt_T) -
            r * K * math.exp(-r * T) * cdf_d2 +
            q * S * math.exp(-q * T) * cdf_d1
        ) / 365.0  # Per day
    else:  # Put
        theta = (
            -S * math.exp(-q * T) * pdf_d1 * sigma / (2 * sqrt_T) +
            r * K * math.exp(-r * T) * cdf_neg_d2 -
            q * S * math.exp(-q * T) * cdf_neg_d1
        ) / 365.0  # Per day
    
    return {
        "delta": delta,
        "gamma": gamma,
        "vanna": vanna,
        "charm": charm,
        "vega": vega,
        "theta": theta
    }


def calculate_exposures(
    greeks: Dict[str, float],
    oi: int,
    multiplier: int,
    spot: float
) -> Dict[str, float]:
    """
    Convert per-contract Greeks to dealer exposure.
    
    Dealer exposure = -Customer exposure
    Exposure = Greek * OI * Multiplier * Spot (with appropriate scaling)
    
    Args:
        greeks: Dictionary with delta, gamma, vanna, charm
        oi: Open interest
        multiplier: Contract multiplier (100 for SPY/SPX, 50 for ES)
        spot: Current spot price
    
    Returns:
        Dictionary with dealer exposure values
    """
    delta = greeks["delta"]
    gamma = greeks["gamma"]
    vanna = greeks["vanna"]
    charm = greeks["charm"]
    
    # Dealer exposure = -Customer exposure
    # Delta exposure: -Delta * OI * Multiplier * Spot
    dealer_delta_exp = -delta * oi * multiplier * spot
    
    # Gamma exposure: -Gamma * OI * Multiplier * Spot^2
    dealer_gamma_exp = -gamma * oi * multiplier * spot * spot
    
    # Vanna exposure: -Vanna * OI * Multiplier * Spot
    dealer_vanna_exp = -vanna * oi * multiplier * spot
    
    # Charm exposure: -Charm * OI * Multiplier * Spot
    dealer_charm_exp = -charm * oi * multiplier * spot
    
    return {
        "dealer_delta_exp": dealer_delta_exp,
        "dealer_gamma_exp": dealer_gamma_exp,
        "dealer_vanna_exp": dealer_vanna_exp,
        "dealer_charm_exp": dealer_charm_exp
    }

