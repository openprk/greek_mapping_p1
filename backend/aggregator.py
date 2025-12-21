"""
Aggregation logic for grouping by strike and calculating totals
"""
from typing import List, Dict, Any
from collections import defaultdict


def aggregate_by_strike(processed_contracts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Aggregate dealer exposures by strike across calls and puts.
    
    Args:
        processed_contracts: List of dicts with contract, greeks, and exposures
    
    Returns:
        List of strike rows with aggregated exposures
    """
    strike_dict = defaultdict(lambda: {
        "strike": 0.0,
        "dealer_delta_exp": 0.0,
        "dealer_gamma_exp": 0.0,
        "dealer_vanna_exp": 0.0,
        "dealer_charm_exp": 0.0,
        "call_oi": 0,
        "put_oi": 0,
        "call_dealer_delta": 0.0,
        "put_dealer_delta": 0.0
    })
    
    for item in processed_contracts:
        contract = item["contract"]
        exposures = item["exposures"]
        greeks = item["greeks"]
        
        strike = contract["strike"]
        
        # Initialize strike if first time
        if strike_dict[strike]["strike"] == 0.0:
            strike_dict[strike]["strike"] = strike
        
        # Aggregate exposures
        strike_dict[strike]["dealer_delta_exp"] += exposures["dealer_delta_exp"]
        strike_dict[strike]["dealer_gamma_exp"] += exposures["dealer_gamma_exp"]
        strike_dict[strike]["dealer_vanna_exp"] += exposures["dealer_vanna_exp"]
        strike_dict[strike]["dealer_charm_exp"] += exposures["dealer_charm_exp"]
        
        # Track call vs put breakdown
        if contract["right"].upper() == "C":
            strike_dict[strike]["call_oi"] += contract.get("oi", 0)
            strike_dict[strike]["call_dealer_delta"] += greeks["delta"] * contract.get("oi", 0) * contract.get("multiplier", 100)
        else:  # Put
            strike_dict[strike]["put_oi"] += contract.get("oi", 0)
            strike_dict[strike]["put_dealer_delta"] += greeks["delta"] * contract.get("oi", 0) * contract.get("multiplier", 100)
    
    # Convert to list and sort by strike
    strike_rows = list(strike_dict.values())
    strike_rows.sort(key=lambda x: x["strike"])
    
    return strike_rows


def calculate_totals(strike_rows: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Calculate total dealer exposures across all strikes.
    
    Args:
        strike_rows: List of strike row dictionaries
    
    Returns:
        Dictionary with total exposures
    """
    totals = {
        "net_dealer_delta": 0.0,
        "net_dealer_gamma": 0.0,
        "net_dealer_vanna": 0.0,
        "net_dealer_charm": 0.0
    }
    
    for row in strike_rows:
        totals["net_dealer_delta"] += row["dealer_delta_exp"]
        totals["net_dealer_gamma"] += row["dealer_gamma_exp"]
        totals["net_dealer_vanna"] += row["dealer_vanna_exp"]
        totals["net_dealer_charm"] += row["dealer_charm_exp"]
    
    return totals

