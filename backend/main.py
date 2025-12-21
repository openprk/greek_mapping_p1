"""
FastAPI backend for Dealer Greeks Dashboard
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import math
from decimal import Decimal
from scipy.stats import norm
import uvicorn

from models import OptionContract, ChainResponse, StrikeRow, Totals, MMResponse
from greeks import calculate_greeks, calculate_exposures
from data_provider import get_data_provider
from aggregator import aggregate_by_strike, calculate_totals
from mm_response import classify_regime

app = FastAPI(title="Dealer Greeks Dashboard API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/api/chain")
async def get_chain(
    symbol: str = Query(default="SPY", description="Underlying symbol"),
    expiry: Optional[str] = Query(default=None, description="Expiry date YYYY-MM-DD"),
    provider: str = Query(default="mock", description="Data provider: mock, tradier, polygon")
):
    """
    Fetch options chain and compute dealer Greeks exposures
    """
    try:
        # Get data provider
        data_provider = get_data_provider(provider)
        
        # Fetch chain data
        chain_data = await data_provider.fetch_chain(symbol, expiry)
        
        if not chain_data:
            raise HTTPException(status_code=404, detail=f"No chain data found for {symbol}")
        
        spot = chain_data["spot"]
        contracts = chain_data["contracts"]
        expiry_date = chain_data["expiry"]
        updated_at = chain_data.get("updated_at", datetime.utcnow().isoformat())
        
        # Calculate current time to expiry
        if isinstance(expiry_date, str):
            # Handle ISO format with or without timezone
            expiry_str = expiry_date.replace('Z', '+00:00')
            try:
                expiry_dt = datetime.fromisoformat(expiry_str)
            except ValueError:
                # Try parsing without timezone
                expiry_dt = datetime.fromisoformat(expiry_date)
        else:
            expiry_dt = expiry_date
        
        now = datetime.utcnow()
        # Make timezone-naive for comparison if needed
        if expiry_dt.tzinfo:
            expiry_dt = expiry_dt.replace(tzinfo=None)
        
        time_to_expiry = (expiry_dt - now).total_seconds() / (365.25 * 24 * 3600)
        
        # Edge case: if expired, set T to small positive value
        if time_to_expiry <= 0:
            time_to_expiry = 0.0001
        
        # Process each contract
        processed_contracts = []
        for contract in contracts:
            # Calculate Greeks
            greeks = calculate_greeks(
                S=spot,
                K=contract["strike"],
                T=time_to_expiry,
                r=contract.get("rate", 0.05),
                q=contract.get("dividend", 0.0),
                sigma=contract.get("iv", 0.2),
                right=contract["right"]
            )
            
            # Calculate exposures
            multiplier = contract.get("multiplier", 100)
            exposures = calculate_exposures(
                greeks=greeks,
                oi=contract.get("oi", 0),
                multiplier=multiplier,
                spot=spot
            )
            
            processed_contracts.append({
                "contract": contract,
                "greeks": greeks,
                "exposures": exposures
            })
        
        # Aggregate by strike
        strike_rows = aggregate_by_strike(processed_contracts)
        
        # Calculate totals
        totals = calculate_totals(strike_rows)
        
        # Classify MM response
        mm_response = classify_regime(totals, spot)
        
        # Format response
        response = ChainResponse(
            symbol=symbol,
            spot=spot,
            expiry=expiry_date.isoformat() if isinstance(expiry_date, datetime) else expiry_date,
            updated_at=updated_at,
            rows=[StrikeRow(**row) for row in strike_rows],
            totals=totals,
            mm_response=mm_response
        )
        
        # Use model_dump() for Pydantic v2, fallback to dict() for v1
        try:
            return response.model_dump()
        except AttributeError:
            return response.dict()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

