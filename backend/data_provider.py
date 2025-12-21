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
        self.base_url = os.getenv("TRADIER_BASE_URL", "https://sandbox.tradier.com/v1")
    
    async def fetch_chain(self, symbol: str, expiry: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetch chain from Tradier API"""
        if not self.api_key:
            raise ValueError("TRADIER_API_KEY not set")
        
        # TODO: Implement Tradier API calls
        # This is a placeholder for when you plug in your Tradier credentials
        raise NotImplementedError("Tradier provider not yet implemented. Use mock mode or implement API calls.")


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

