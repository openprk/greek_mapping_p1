"""
Market Maker Response classification logic
"""
from typing import Dict, List, Any


def classify_regime(totals: Dict[str, float], spot: float, previous_totals: Dict[str, float] = None) -> Dict[str, Any]:
    """
    Classify market regime based on dealer Greeks totals.
    
    Args:
        totals: Dictionary with net_dealer_delta, net_dealer_gamma, net_dealer_vanna, net_dealer_charm
        spot: Current spot price
        previous_totals: Optional previous totals for trend detection
    
    Returns:
        Dictionary with regime classification and notes
    """
    net_gamma = totals.get("net_dealer_gamma", 0.0)
    net_delta = totals.get("net_dealer_delta", 0.0)
    net_vanna = totals.get("net_dealer_vanna", 0.0)
    net_charm = totals.get("net_dealer_charm", 0.0)
    
    # Primary regime classification
    if net_gamma > 0:
        regime = "POS GAMMA / Mean Reversion"
    elif net_gamma < 0:
        regime = "NEG GAMMA / Momentum"
    else:
        regime = "NEUTRAL GAMMA"
    
    notes = []
    
    # Delta-based notes
    abs_delta = abs(net_delta)
    if abs_delta > 1e9:  # Large delta exposure threshold
        if net_delta > 0:
            notes.append("Significant long dealer delta exposure → potential hedge pressure on downside")
        else:
            notes.append("Significant short dealer delta exposure → potential hedge pressure on upside")
    
    # Trend detection if previous totals available
    if previous_totals:
        prev_abs_delta = abs(previous_totals.get("net_dealer_delta", 0.0))
        if abs_delta > prev_abs_delta * 1.1:  # 10% increase
            notes.append("Hedge pressure increasing")
    
    # Charm-based notes (pin/decay pressure)
    abs_charm = abs(net_charm)
    if abs_charm > 1e8:  # Large charm exposure threshold
        if net_charm > 0:
            notes.append("Elevated pin/decay pressure into close (positive charm)")
        else:
            notes.append("Elevated pin/decay pressure into close (negative charm)")
    
    # Vanna-based notes
    # Positive vanna: vol increases as spot rises (vol smile effect)
    # Negative vanna: vol decreases as spot rises
    if abs(net_vanna) > 1e8:  # Large vanna exposure threshold
        if net_vanna > 0:
            notes.append("Vanna suggests vol-up supports spot moves higher")
        else:
            notes.append("Vanna suggests vol-down supports spot moves lower")
    
    # Default note if no specific conditions
    if not notes:
        notes.append("Monitoring dealer positioning...")
    
    return {
        "regime": regime,
        "notes": notes
    }

