# Dealer Greeks per Strike Dashboard

A live web application that computes and displays dealer Greeks exposures aggregated by strike price. Built for quantitative analysis of options market maker positioning.

## Features

- **Live Options Chain Processing**: Pulls options chain data for any underlying (default: SPY)
- **Black-Scholes Greeks**: Calculates Delta, Gamma, Vanna, and Charm per contract
- **Dealer Exposure Conversion**: Converts per-contract Greeks to dealer exposure using OI and contract multiplier
- **Strike Aggregation**: Aggregates exposures per strike (calls + puts)
- **Market Maker Response Classification**: Classifies regime (Positive Gamma / Mean Reversion vs Negative Gamma / Momentum)
- **Real-time Updates**: Auto-refresh with configurable interval (default: 10 seconds)
- **Interactive Dashboard**: Sortable table, charts, and totals display

## Project Structure

```
dealer-greeks-dashboard/
├── backend/              # FastAPI backend
│   ├── main.py          # FastAPI app and endpoints
│   ├── models.py        # Pydantic data models
│   ├── greeks.py        # Black-Scholes Greeks calculations
│   ├── aggregator.py    # Strike aggregation logic
│   ├── mm_response.py   # Market maker response classification
│   ├── data_provider.py # Data provider interface (mock, Tradier, Polygon)
│   └── requirements.txt # Python dependencies
├── frontend/            # Static frontend files
│   ├── index.html      # Main HTML
│   ├── styles.css      # Styling
│   └── app.js          # JavaScript application logic
├── sample_chain.json    # Sample options chain data for mock mode
├── .env.example        # Environment variables template
└── README.md           # This file
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Modern web browser

### Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd dealer-greeks-dashboard
   ```

2. **Set up Python virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install backend dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. **Configure environment variables (optional):**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys if using real data providers
   ```

## Running the Application

### Start the Backend

From the project root directory:

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

### Start the Frontend

You can serve the frontend using any static file server. Options:

**Option 1: Python HTTP server (simplest)**
```bash
cd frontend
python3 -m http.server 8080
```

**Option 2: Node.js http-server**
```bash
npx http-server frontend -p 8080
```

**Option 3: Open directly in browser**
Simply open `frontend/index.html` in your browser (note: CORS may be an issue, so use a server)

The frontend will be available at `http://localhost:8080`

### Access the Dashboard

Open your browser and navigate to:
```
http://localhost:8080
```

## Usage

1. **Select Symbol**: Enter an underlying symbol (default: SPY)
2. **Select Expiry**: Choose an expiry date (or leave blank for default/nearest)
3. **Choose Provider**: Select data provider (Mock mode works out of the box)
4. **Set Refresh Interval**: Configure auto-refresh interval in seconds
5. **View Results**: 
   - Totals cards show net dealer exposures
   - MM Response panel shows regime classification
   - Charts display Gamma and Delta by strike
   - Table shows detailed per-strike breakdowns

## Data Providers

### Mock Mode (Default)

The application includes a mock data provider that generates realistic sample data. This works immediately without any API keys.

Mock mode:
- Generates options chain around current spot
- Uses realistic IV, OI, and pricing
- Perfect for testing and development

### Tradier API

To use Tradier (sandbox or production):

1. Sign up at [Tradier](https://developer.tradier.com/)
2. Get your API key and account ID
3. Add to `.env`:
   ```
   TRADIER_API_KEY=your_key
   TRADIER_ACCOUNT_ID=your_account_id
   ```
4. Select "Tradier" as provider in the UI

**Note**: The Tradier provider is currently a placeholder. See "Plugging in Your Real API" below.

### Polygon.io API

To use Polygon.io:

1. Sign up at [Polygon.io](https://polygon.io/)
2. Get your API key
3. Add to `.env`:
   ```
   POLYGON_API_KEY=your_key
   ```
4. Select "Polygon" as provider in the UI

**Note**: The Polygon provider is currently a placeholder. See "Plugging in Your Real API" below.

## Plugging in Your Real API

The data provider system is designed to be easily extensible. Here's how to add your own provider:

### Step 1: Implement the Provider Class

Edit `backend/data_provider.py` and add a new class:

```python
class YourDataProvider(DataProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("YOUR_API_KEY")
    
    async def fetch_chain(self, symbol: str, expiry: Optional[str] = None) -> Optional[Dict[str, Any]]:
        # Your API call logic here
        # Return format:
        return {
            "symbol": symbol,
            "spot": spot_price,
            "expiry": expiry_date.isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "contracts": [
                {
                    "symbol": contract_symbol,
                    "underlying": symbol,
                    "expiry": expiry_date.isoformat(),
                    "strike": strike_price,
                    "right": "C" or "P",
                    "iv": implied_volatility,
                    "oi": open_interest,
                    "bid": bid_price,
                    "ask": ask_price,
                    "mid": (bid + ask) / 2,
                    "last": last_price,
                    "rate": risk_free_rate,
                    "dividend": dividend_yield,
                    "spot": spot_price,
                    "multiplier": 100  # or 50 for ES
                },
                # ... more contracts
            ]
        }
```

### Step 2: Register the Provider

In `backend/data_provider.py`, update the `get_data_provider()` function:

```python
def get_data_provider(provider_name: str) -> DataProvider:
    # ... existing code ...
    elif provider_name == "your_provider":
        return YourDataProvider()
```

### Step 3: Add to Frontend

In `frontend/index.html`, add an option to the provider select:

```html
<option value="your_provider">Your Provider</option>
```

### Example: Unusual Whales Integration

```python
import aiohttp

class UnusualWhalesProvider(DataProvider):
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("UNUSUAL_WHALES_API_KEY")
        self.base_url = "https://api.unusualwhales.com/api/v2"
    
    async def fetch_chain(self, symbol: str, expiry: Optional[str] = None):
        async with aiohttp.ClientSession() as session:
            headers = {"Authorization": f"Bearer {self.api_key}"}
            async with session.get(
                f"{self.base_url}/options/chain",
                params={"symbol": symbol, "expiry": expiry},
                headers=headers
            ) as response:
                data = await response.json()
                # Transform to our format
                return self._transform_response(data, symbol)
```

## API Endpoints

### GET `/api/health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-12-15T14:30:00"
}
```

### GET `/api/chain`

Fetch options chain and compute dealer Greeks.

**Query Parameters:**
- `symbol` (string, default: "SPY"): Underlying symbol
- `expiry` (string, optional): Expiry date in YYYY-MM-DD format
- `provider` (string, default: "mock"): Data provider name

**Response:**
```json
{
  "symbol": "SPY",
  "spot": 450.0,
  "expiry": "2024-12-20T16:00:00",
  "updated_at": "2024-12-15T14:30:00",
  "rows": [
    {
      "strike": 450.0,
      "dealer_delta_exp": -1234567.89,
      "dealer_gamma_exp": 987654.32,
      "dealer_vanna_exp": -456789.01,
      "dealer_charm_exp": 234567.89,
      "call_oi": 15000,
      "put_oi": 15000,
      "call_dealer_delta": -500000.0,
      "put_dealer_delta": -734567.89
    }
  ],
  "totals": {
    "net_dealer_delta": -5000000.0,
    "net_dealer_gamma": 10000000.0,
    "net_dealer_vanna": -2000000.0,
    "net_dealer_charm": 500000.0
  },
  "mm_response": {
    "regime": "POS GAMMA / Mean Reversion",
    "notes": [
      "Monitoring dealer positioning...",
      "Elevated pin/decay pressure into close"
    ]
  }
}
```

## Greeks Calculations

### Black-Scholes Formulas

- **d1**: `(ln(S/K) + (r - q + 0.5*σ²)*T) / (σ*√T)`
- **d2**: `d1 - σ*√T`

### Greeks (Per Contract)

- **Delta (Call)**: `e^(-qT) * N(d1)`
- **Delta (Put)**: `-e^(-qT) * N(-d1)`
- **Gamma**: `e^(-qT) * φ(d1) / (S * σ * √T)`
- **Vanna**: `-φ(d1) * d2 / σ`
- **Charm**: `-e^(-qT) * [φ(d1) * (r-q)/(σ*√T) - q*N(d1) - φ(d1)*d2/(2*T)]` (for calls)

Where:
- `N(x)` = standard normal CDF
- `φ(x)` = standard normal PDF
- `S` = spot price
- `K` = strike price
- `T` = time to expiry (years)
- `r` = risk-free rate
- `q` = dividend yield
- `σ` = implied volatility

### Exposure Conversion

Dealer exposure = -Customer exposure

- **Dealer Delta Exp**: `-Delta * OI * Multiplier * Spot`
- **Dealer Gamma Exp**: `-Gamma * OI * Multiplier * Spot²`
- **Dealer Vanna Exp**: `-Vanna * OI * Multiplier * Spot`
- **Dealer Charm Exp**: `-Charm * OI * Multiplier * Spot`

## Market Maker Response Classification

The MM Response panel classifies the market regime:

- **Positive Gamma**: Mean reversion regime (dealers buy dips, sell rips)
- **Negative Gamma**: Momentum regime (dealers amplify moves)

Additional notes are generated based on:
- Delta exposure magnitude
- Charm exposure (pin/decay pressure)
- Vanna exposure (vol-spot relationship)

## Troubleshooting

### Backend won't start

- Check Python version: `python3 --version` (need 3.8+)
- Verify dependencies: `pip list`
- Check port 8000 is available

### Frontend can't connect to backend

- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify API_BASE_URL in `frontend/app.js` matches your backend URL

### No data showing

- Check browser console for errors
- Verify `sample_chain.json` exists in project root
- Try mock mode first to verify setup

### Greeks seem incorrect

- Verify time-to-expiry calculation (check expiry dates)
- Check IV values are in decimal format (0.15 = 15%)
- Ensure spot price matches underlying

## License

This project is provided as-is for educational and research purposes.

## Contributing

Feel free to extend this dashboard with:
- Additional Greeks (Rho, Theta)
- More sophisticated MM response logic
- Historical tracking
- Export functionality
- Additional data providers

## Support

For issues or questions, check the code comments or create an issue in your repository.

