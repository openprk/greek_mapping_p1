# CRITICAL: Render Python 3.13 → 3.11 Fix

## Problem
Render is using Python 3.13, causing Pydantic ForwardRef errors:
```
TypeError: ForwardRef._evaluate() missing 1 required keyword-on...
```

## Root Cause
Render is IGNORING `runtime.txt` files. You MUST set Python version manually in Render dashboard.

## IMMEDIATE FIX (Do This Now)

### Step 1: Set Python Version in Render Dashboard

1. Go to **Render Dashboard** → Your Service (`greek_mapping_backend`)
2. Click **Settings** tab
3. Scroll to **Environment** section
4. Find **Python Version** dropdown
5. **CHANGE IT TO**: `3.11.9` or `3.11`
6. **SAVE CHANGES**

### Step 2: Verify Root Directory and Start Command

While in Settings → **Build & Deploy**:

**Root Directory**: `backend`

**Start Command**: 
```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Step 3: Manual Deploy

1. Go to **Manual Deploy** dropdown
2. Click **Deploy latest commit**
3. Watch logs - you should now see:
   ```
   Using Python version: 3.11.9
   ```
   Instead of:
   ```
   Using Python version: 3.13.x
   ```

## Why This Happens

- Render's `runtime.txt` detection is unreliable
- Python 3.13 has breaking changes with Pydantic v1
- Manual Python version setting in dashboard ALWAYS works

## After Fix

Your logs should show:
```
Installing collected packages: httpx, fastapi, uvicorn...
Successfully installed httpx-0.25.2 fastapi-0.104.1...
INFO:     Uvicorn running on http://0.0.0.0:10000
```

## Test Endpoints

After successful deployment:
- Health: `https://greek-mapping-backend.onrender.com/api/health`
- Chain: `https://greek-mapping-backend.onrender.com/api/chain?symbol=SPY&provider=tradier`

---

**DO THIS NOW**: Set Python version to 3.11.9 in Render dashboard Settings → Environment.

