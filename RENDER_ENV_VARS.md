# Render Environment Variables Configuration

## Current Environment Variables in Render

Based on your Render dashboard, you have:
- ✅ `TRADIER_TOKEN` - Your Tradier API token
- ✅ `DATA_PROVIDER` - (if needed)

## Code Update

The code now supports **both** variable names:
- `TRADIER_API_KEY` (original)
- `TRADIER_TOKEN` (what you have in Render)

So your current `TRADIER_TOKEN` will work! ✅

## Still Need to Fix

### 1. Python Version (CRITICAL)
Render → Settings → Environment → **Python Version**
- Change to: `3.11.9` or `3.11`
- This is the #1 cause of deployment failures

### 2. Root Directory
Render → Settings → Build & Deploy → **Root Directory**
- Set to: `backend`

### 3. Start Command
Render → Settings → Build & Deploy → **Start Command**
- Set to: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## After These Settings

1. **Save Changes**
2. **Manual Deploy** → Deploy latest commit
3. Should deploy successfully!

