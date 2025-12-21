# Render Python Version Fix

## Problem
Render is using Python 3.13 instead of Python 3.11, causing Pydantic forward reference errors.

## Solution: Set Python Version in Render Dashboard

Render may not be reading `runtime.txt` correctly. Set it manually in the dashboard:

### Steps:
1. Go to Render Dashboard → Your Service (`greek_mapping_backend`)
2. Go to **Settings** tab
3. Scroll to **Environment** section
4. Find **Python Version** setting
5. Set it to: `3.11.9` or `3.11`
6. **Save Changes**
7. **Manual Deploy** → Deploy latest commit

### Alternative: Check Root Directory
If Render has a "Root Directory" set to `backend/`, make sure `backend/runtime.txt` exists (it does).

### Verify
After setting Python version, check the build logs. You should see:
```
Using Python version: 3.11.9
```

Instead of:
```
Using Python version: 3.13.x
```

## Current Files
- ✅ `runtime.txt` in repo root: `python-3.11.9`
- ✅ `backend/runtime.txt`: `python-3.11.9`
- ✅ `backend/requirements.txt` uses Pydantic v1 (no Rust)

