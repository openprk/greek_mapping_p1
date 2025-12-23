"""
Data provider interface for fetching options chain data
Supports mock mode and pluggable real providers
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import os
import asyncio
import httpx


class DataProvider(ABC):
    """Abstract base class for data providers"""
    
    @abstractmethod
    async def fetch_chain(self, symbol: str, expiry: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch options chain data
        
        Args:
            symbol: Underlying symbol (e.g., "SPY")
            expiry: Optional expiry date string (YYYY-MM-DD)
        
        Returns:
            Dictionary with spot, expiry, contracts list, updated_at
        """
        pass


class MockDataProvider(DataProvider):
    """Mock data provider that loads from sample_chain.json"""
    
    async def fetch_chain(self, symbol: str, expiry: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Load mock chain data from sample_chain.json"""
        try:
            # Try to load from backend directory first, then root
            json_paths = [
                os.path.join(os.path.dirname(__file__), "..", "sample_chain.json"),
                os.path.join(os.path.dirname(__file__), "sample_chain.json"),
                "sample_chain.json"
            ]
            
            chain_data = None
            for path in json_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        chain_data = json.load(f)
                    break
            
            if not chain_data:
                # Generate default mock data
                return self._generate_mock_data(symbol, expiry)
            
            # Filter by symbol if specified
            if chain_data.get("symbol") != symbol:
                # Still return it but update symbol
                chain_data["symbol"] = symbol
            
            # Filter by expiry if specified
            if expiry and chain_data.get("expiry"):
                # For mock mode, just use the provided expiry or default
                chain_data["expiry"] = expiry or chain_data.get("expiry")
            
            return chain_data
        
        except Exception as e:
            print(f"Error loading mock data: {e}")
            return self._generate_mock_data(symbol, expiry)
    
    def _generate_mock_data(self, symbol: str, expiry: Optional[str] = None) -> Dict[str, Any]:
        """Generate realistic mock options chain data"""
        # Default expiry: next Friday
        if not expiry:
            today = datetime.now()
            days_ahead = (4 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            expiry_date = (today + timedelta(days=days_ahead)).replace(hour=16, minute=0, second=0, microsecond=0)
        else:
            expiry_date = datetime.fromisoformat(expiry)
        
        spot = 450.0  # Default SPY spot
        if symbol == "SPY":
            spot = 450.0
        elif symbol == "SPX":
            spot = 4500.0
        elif symbol == "QQQ":
            spot = 380.0
        
        # Generate strikes around spot
        strikes = []
        for i in range(-20, 21, 2):
            strike = round(spot + i * (spot * 0.01), 2)
            strikes.append(strike)
        
        contracts = []
        for strike in strikes:
            # Call
            iv = 0.15 + abs(strike - spot) / spot * 0.1  # Higher IV for OTM
            oi = int(1000 + abs(strike - spot) / spot * 5000)
            contracts.append({
                "symbol": f"{symbol}{expiry_date.strftime('%y%m%d')}C{int(strike*1000):08d}",
                "underlying": symbol,
                "expiry": expiry_date.isoformat(),
                "strike": strike,
                "right": "C",
                "iv": iv,
                "oi": oi,
                "bid": max(0.01, spot - strike + 5),
                "ask": max(0.01, spot - strike + 6),
                "mid": max(0.01, spot - strike + 5.5),
                "last": max(0.01, spot - strike + 5.5),
                "rate": 0.05,
                "dividend": 0.015,
                "spot": spot,
                "multiplier": 100
            })
            
            # Put
            contracts.append({
                "symbol": f"{symbol}{expiry_date.strftime('%y%m%d')}P{int(strike*1000):08d}",
                "underlying": symbol,
                "expiry": expiry_date.isoformat(),
                "strike": strike,
                "right": "P",
                "iv": iv,
                "oi": oi,
                "bid": max(0.01, strike - spot + 5),
                "ask": max(0.01, strike - spot + 6),
                "mid": max(0.01, strike - spot + 5.5),
                "last": max(0.01, strike - spot + 5.5),
                "rate": 0.05,
                "dividend": 0.015,
                "spot": spot,
                "multiplier": 100
            })
        
        return {
            "symbol": symbol,
            "spot": spot,
            "expiry": expiry_date.isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "contracts": contracts
        }


class TradierDataProvider(DataProvider):
    """Tradier API provider (requires API key)"""
    
    def __init__(self, api_key: Optional[str] = None, account_id: Optional[str] = None):
        self.api_key = api_key or os.getenv("TRADIER_API_KEY")
        self.account_id = account_id or os.getenv("TRADIER_ACCOUNT_ID")
        # Use production API if API key looks like production key, otherwise sandbox
        base_url_env = os.getenv("TRADIER_BASE_URL")
        if base_url_env:
            self.base_url = base_url_env
        else:
            # Default to production API
            self.base_url = "https://api.tradier.com/v1"
    
    async def fetch_chain(self, symbol: str, expiry: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch chain from Tradier API"""
        if not self.api_key:
            raise ValueError("TRADIER_API_KEY not set. Please set TRADIER_API_KEY environment variable in Render.")
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        
        try:
            timeout = httpx.Timeout(30.0)
            async with httpx.AsyncClient(timeout=timeout) as client:
                # First, get quotes to get current spot price
                quote_url = f"{self.base_url}/markets/quotes"
                quote_resp = await client.get(quote_url, headers=headers, params={"symbols": symbol})
                if quote_resp.status_code != 200:
                    raise ValueError(f"Tradier quote API error: {quote_resp.status_code}")
                quote_data = quote_resp.json()
                
                if "quotes" not in quote_data or "quote" not in quote_data["quotes"]:
                    raise ValueError(f"No quote data for {symbol}")
                
                quote = quote_data["quotes"]["quote"]
                if isinstance(quote, list):
                    quote = quote[0]
                
                spot = float(quote.get("last", quote.get("close", 0)))
                if spot == 0:
                    raise ValueError(f"Invalid spot price for {symbol}")
                
                # Get options expirations
                expirations_url = f"{self.base_url}/markets/options/expirations"
                exp_resp = await client.get(expirations_url, headers=headers, params={"symbol": symbol})
                if exp_resp.status_code != 200:
                    raise ValueError(f"Tradier expirations API error: {exp_resp.status_code}")
                exp_data = exp_resp.json()
                
                if "expirations" not in exp_data or "date" not in exp_data["expirations"]:
                    raise ValueError(f"No expiration dates for {symbol}")
                
                expirations = exp_data["expirations"]["date"]
                if isinstance(expirations, str):
                    expirations = [expirations]
                
                # Use provided expiry or nearest one
                if expiry:
                    expiry_date_str = expiry
                else:
                    expiry_date_str = expirations[0] if expirations else None
                
                if not expiry_date_str:
                    raise ValueError(f"No valid expiration dates found for {symbol}")
                
                # Get options chain for the expiration
                chain_url = f"{self.base_url}/markets/options/chains"
                params = {
                    "symbol": symbol,
                    "expiration": expiry_date_str
                }
                
                chain_resp = await client.get(chain_url, headers=headers, params=params)
                if chain_resp.status_code != 200:
                    raise ValueError(f"Tradier chain API error: {chain_resp.status_code}")
                chain_data = chain_resp.json()
                
                if "options" not in chain_data or "option" not in chain_data["options"]:
                    raise ValueError(f"No options data for {symbol} expiring {expiry_date_str}")
                
                options = chain_data["options"]["option"]
                if isinstance(options, dict):
                    options = [options]
                elif not isinstance(options, list):
                    options = []
                
                # Transform Tradier format to our format
                contracts = []
                for opt in options:
                    strike = float(opt.get("strike", 0))
                    right = opt.get("option_type", "").upper()
                    if right not in ["C", "P"]:
                        continue
                    
                    # Parse expiry date
                    expiry_dt = datetime.strptime(expiry_date_str, "%Y-%m-%d")
                    expiry_dt = expiry_dt.replace(hour=16, minute=0, second=0, microsecond=0)
                    
                    # Calculate time to expiry
                    now = datetime.utcnow()
                    time_to_expiry = (expiry_dt - now).total_seconds() / (365.25 * 24 * 3600)
                    
                    contracts.append({
                        "symbol": opt.get("symbol", ""),
                        "underlying": symbol,
                        "expiry": expiry_dt.isoformat(),
                        "strike": strike,
                        "right": right,
                        "iv": float(opt.get("greeks", {}).get("mid_iv", 0.2)) if isinstance(opt.get("greeks"), dict) else 0.2,
                        "oi": int(opt.get("open_interest", 0)),
                        "bid": float(opt.get("bid", 0)),
                        "ask": float(opt.get("ask", 0)),
                        "mid": float(opt.get("bid", 0) + opt.get("ask", 0)) / 2 if opt.get("bid") and opt.get("ask") else None,
                        "last": float(opt.get("last", 0)),
                        "rate": 0.05,  # Default risk-free rate
                        "dividend": 0.015,  # Default dividend yield
                        "spot": spot,
                        "multiplier": 100
                    })
                
                return {
                    "symbol": symbol,
                    "spot": spot,
                    "expiry": expiry_dt.isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                    "contracts": contracts
                }
        
        except Exception as e:
            print(f"Tradier API error: {e}")
            raise ValueError(f"Failed to fetch Tradier data: {str(e)}")


class PolygonDataProvider(DataProvider):
    """Polygon.io API provider (requires API key)"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("POLYGON_API_KEY")
        self.base_url = "https://api.polygon.io"
    
    async def fetch_chain(self, symbol: str, expiry: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch chain from Polygon API"""
        if not self.api_key:
            raise ValueError("POLYGON_API_KEY not set")
        
        # TODO: Implement Polygon API calls
        raise NotImplementedError("Polygon provider not yet implemented. Use mock mode or implement API calls.")


def get_data_provider(provider_name: str) -> DataProvider:
    """
    Factory function to get the appropriate data provider
    
    Args:
        provider_name: "mock", "tradier", "polygon", etc.
    
    Returns:
        DataProvider instance
    """
    provider_name = provider_name.lower()
    
    if provider_name == "mock":
        return MockDataProvider()
    elif provider_name == "tradier":
        return TradierDataProvider()
    elif provider_name == "polygon":
        return PolygonDataProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")

