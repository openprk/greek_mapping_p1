# Render Settings Checklist - EXACT VALUES TO SET

## ⚠️ CRITICAL: Python 3.13 is Still Being Used

Your logs show: `/opt/render/project/python/Python-3.13.4/lib/python3.13/`

This means Render is **IGNORING** your Python version setting or it's not set correctly.

## Step-by-Step: Set These EXACT Values

### 1. Go to Render Dashboard
- Service: `greek_mapping_backend`
- Click **Settings** tab

### 2. Environment Section

**Python Version:**
- **MUST BE SET TO**: `3.11.9` (or `3.11`)
- **NOT**: `3.13` or blank
- If you see a dropdown, select `3.11.9`
- If it's a text field, type: `3.11.9`
- **SAVE**

### 3. Build & Deploy Section

**Root Directory:**
- Set to: `backend`
- (This tells Render your code is in the `backend/` folder)

**Start Command:**
- Set to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- (No `cd backend &&` since Root Directory handles it)

**Build Command:**
- Leave blank or: `pip install -r requirements.txt`

### 4. Environment Variables Section

Verify these exist:
- ✅ `TRADIER_TOKEN` - Your Tradier API token (you have this)
- Optional: `DATA_PROVIDER` - (if you set this)

### 5. Save All Changes

Click **Save Changes** button

### 6. Manual Deploy

- Click **Manual Deploy** dropdown
- Select **Deploy latest commit**
- Watch the logs

## What to Look For in Logs

### ✅ SUCCESS Indicators:
```
Using Python version: 3.11.9
Installing collected packages: httpx, fastapi, uvicorn...
Successfully installed httpx-0.25.2 fastapi-0.104.1...
INFO:     Uvicorn running on http://0.0.0.0:10000
```

### ❌ FAILURE Indicators:
```
Using Python version: 3.13.x  ← WRONG! Go back and set Python version
cd: backend: No such file or directory  ← Set Root Directory to "backend"
```

## If Python Version Still Shows 3.13

1. **Double-check** the Python Version field in Settings
2. Try **deleting** the field and **re-typing** `3.11.9`
3. Make sure you **Saved Changes** before deploying
4. Check if there's a **"Runtime"** or **"Python Runtime"** field elsewhere

## API Connection Verification

Once deployed successfully, test:

1. **Health Check:**
   ```
   https://greek-mapping-backend.onrender.com/api/health
   ```
   Should return: `{"status": "healthy", "timestamp": "..."}`

2. **Chain Endpoint (Mock):**
   ```
   https://greek-mapping-backend.onrender.com/api/chain?symbol=SPY&provider=mock
   ```
   Should return JSON with options chain data

3. **Chain Endpoint (Tradier):**
   ```
   https://greek-mapping-backend.onrender.com/api/chain?symbol=SPY&provider=tradier
   ```
   Should return live Tradier data (if TRADIER_TOKEN is set correctly)

## Current Code Status

✅ All code is correct:
- Supports `TRADIER_TOKEN` environment variable
- httpx instead of aiohttp (no compilation)
- Proper error handling
- CORS enabled
- All pushed to GitHub

❌ Only issue: Python version must be manually set to 3.11.9 in Render dashboard

