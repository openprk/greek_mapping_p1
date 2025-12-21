# Quick Start Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## Installation (5 minutes)

1. **Navigate to project directory:**
   ```bash
   cd dealer-greeks-dashboard
   ```

2. **Create virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

## Running the Application

### Terminal 1 - Start Backend

```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Terminal 2 - Start Frontend

```bash
cd frontend
python3 -m http.server 8080
```

Or use the startup scripts:
```bash
./start_backend.sh    # Terminal 1
./start_frontend.sh   # Terminal 2
```

### Open Dashboard

Open your browser and go to:
```
http://localhost:8080
```

## First Use

1. The dashboard will automatically load with mock data for SPY
2. You should see:
   - Totals cards showing net dealer exposures
   - MM Response panel with regime classification
   - Charts showing Gamma and Delta by strike
   - Sortable table with per-strike breakdowns

3. Try changing the symbol or expiry date
4. Enable auto-refresh to see live updates

## Troubleshooting

**Backend won't start:**
- Check Python version: `python3 --version` (need 3.8+)
- Install dependencies: `pip install -r backend/requirements.txt`
- Check port 8000 is available

**Frontend can't connect:**
- Ensure backend is running on port 8000
- Check browser console for errors
- Verify CORS is enabled (it should be by default)

**No data showing:**
- Check `sample_chain.json` exists in project root
- Try refreshing the page
- Check browser console for API errors

## Next Steps

- Read the full README.md for detailed documentation
- See "Plugging in Your Real API" section to connect real data sources
- Customize Greeks calculations or MM response logic as needed

