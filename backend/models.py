"""
Data models for the Dealer Greeks Dashboard
"""
from __future__ import annotations  # Enable postponed evaluation of annotations

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime


class OptionContract(BaseModel):
    """Represents a single options contract"""
    symbol: str
    underlying: str
    expiry: str  # ISO datetime string
    strike: float
    right: str  # "C" or "P"
    iv: float  # Implied volatility (decimal)
    oi: int  # Open interest
    bid: float
    ask: float
    mid: Optional[float] = None
    last: Optional[float] = None
    rate: float = 0.05  # Risk-free rate (decimal)
    dividend: float = 0.0  # Dividend yield (decimal)
    spot: float  # Current spot price
    time_to_expiry_years: float
    multiplier: int = 100  # Contract multiplier


class Greeks(BaseModel):
    """Greeks for a single contract"""
    delta: float
    gamma: float
    vanna: float
    charm: float
    vega: Optional[float] = None
    theta: Optional[float] = None


class Exposures(BaseModel):
    """Dealer exposure for a single contract"""
    dealer_delta_exp: float
    dealer_gamma_exp: float
    dealer_vanna_exp: float
    dealer_charm_exp: float


class StrikeRow(BaseModel):
    """Aggregated data per strike"""
    strike: float
    dealer_delta_exp: float
    dealer_gamma_exp: float
    dealer_vanna_exp: float
    dealer_charm_exp: float
    call_oi: int = 0
    put_oi: int = 0
    call_dealer_delta: float = 0.0
    put_dealer_delta: float = 0.0


class Totals(BaseModel):
    """Total dealer exposures across all strikes"""
    net_dealer_delta: float
    net_dealer_gamma: float
    net_dealer_vanna: float
    net_dealer_charm: float


class MMResponse(BaseModel):
    """Market maker response classification"""
    regime: str  # "POS GAMMA / Mean Reversion" or "NEG GAMMA / Momentum"
    notes: List[str]


class ChainResponse(BaseModel):
    """Full chain response with aggregated Greeks"""
    symbol: str
    spot: float
    expiry: str
    updated_at: str
    rows: List[StrikeRow]
    totals: Totals
    mm_response: MMResponse

