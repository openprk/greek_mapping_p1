# Project Structure

```
dealer-greeks-dashboard/
│
├── backend/                          # FastAPI Backend
│   ├── __init__.py                  # Package marker
│   ├── main.py                      # FastAPI app & endpoints
│   ├── models.py                    # Pydantic data models
│   ├── greeks.py                    # Black-Scholes Greeks calculations
│   ├── aggregator.py                # Strike aggregation logic
│   ├── mm_response.py               # Market maker response classification
│   ├── data_provider.py             # Data provider interface (mock/Tradier/Polygon)
│   └── requirements.txt              # Python dependencies
│
├── frontend/                        # Static Frontend
│   ├── index.html                   # Main HTML dashboard
│   ├── styles.css                   # Dark theme styling
│   └── app.js                       # JavaScript application logic
│
├── sample_chain.json                # Sample options chain for mock mode
├── env.example                      # Environment variables template
├── .gitignore                       # Git ignore rules
│
├── README.md                        # Full documentation
├── QUICKSTART.md                    # Quick start guide
├── PROJECT_STRUCTURE.md             # This file
│
└── start_backend.sh                 # Backend startup script
    start_frontend.sh                 # Frontend startup script
```

## File Descriptions

### Backend Files

- **main.py**: FastAPI application with `/api/chain` and `/api/health` endpoints. Handles request processing, calls data providers, computes Greeks, aggregates by strike, and returns formatted responses.

- **models.py**: Pydantic models for type safety:
  - `OptionContract`: Single options contract data
  - `Greeks`: Calculated Greeks per contract
  - `Exposures`: Dealer exposure values
  - `StrikeRow`: Aggregated data per strike
  - `Totals`: Total exposures across all strikes
  - `MMResponse`: Market maker regime classification
  - `ChainResponse`: Complete API response

- **greeks.py**: Black-Scholes Greeks implementation:
  - `calculate_greeks()`: Computes Delta, Gamma, Vanna, Charm, Vega, Theta
  - `calculate_exposures()`: Converts per-contract Greeks to dealer exposure
  - Handles edge cases (T <= 0, sigma <= 0)

- **aggregator.py**: Aggregation logic:
  - `aggregate_by_strike()`: Groups calls/puts by strike and sums exposures
  - `calculate_totals()`: Computes net dealer exposures across all strikes

- **mm_response.py**: Market maker response classification:
  - `classify_regime()`: Determines POS/NEG GAMMA regime
  - Generates notes based on Delta, Vanna, Charm magnitudes

- **data_provider.py**: Pluggable data provider system:
  - `DataProvider`: Abstract base class
  - `MockDataProvider`: Generates realistic sample data (works out of box)
  - `TradierDataProvider`: Placeholder for Tradier API
  - `PolygonDataProvider`: Placeholder for Polygon.io API
  - `get_data_provider()`: Factory function

### Frontend Files

- **index.html**: Single-page dashboard with:
  - Control panel (symbol, expiry, refresh interval, provider)
  - Status bar
  - Totals cards (Delta, Gamma, Vanna, Charm)
  - MM Response panel
  - Charts (Gamma and Delta by strike)
  - Sortable strike table

- **styles.css**: Modern dark theme styling with:
  - Responsive grid layouts
  - Color-coded values (positive/negative)
  - Interactive hover effects
  - Mobile-friendly design

- **app.js**: JavaScript application:
  - `loadData()`: Fetches chain data from API
  - `renderDashboard()`: Updates all UI components
  - `updateCharts()`: Creates/updates Chart.js visualizations
  - `renderTable()`: Populates sortable strike table
  - Auto-refresh functionality

### Configuration Files

- **sample_chain.json**: Sample options chain data with realistic SPY contracts for mock mode testing

- **env.example**: Template for environment variables (API keys, etc.)

- **requirements.txt**: Python dependencies:
  - fastapi
  - uvicorn
  - pydantic
  - scipy (for normal distribution functions)

### Documentation

- **README.md**: Comprehensive documentation including:
  - Setup instructions
  - API endpoint documentation
  - Greeks formulas
  - How to plug in real APIs
  - Troubleshooting

- **QUICKSTART.md**: Quick 5-minute setup guide

## Data Flow

1. **User Input** → Frontend sends request to `/api/chain?symbol=SPY&provider=mock`
2. **Backend** → Gets data provider, fetches chain data
3. **Processing** → For each contract:
   - Calculate Greeks (Black-Scholes)
   - Convert to dealer exposure
4. **Aggregation** → Group by strike, sum exposures
5. **Classification** → Determine MM response regime
6. **Response** → Return JSON with rows, totals, mm_response
7. **Frontend** → Render table, charts, cards, MM panel

## Key Features

✅ Live options chain processing  
✅ Black-Scholes Greeks (Delta, Gamma, Vanna, Charm)  
✅ Dealer exposure conversion  
✅ Strike-level aggregation  
✅ MM response classification  
✅ Auto-refresh dashboard  
✅ Sortable table  
✅ Interactive charts  
✅ Mock mode (no API keys required)  
✅ Pluggable data providers  

