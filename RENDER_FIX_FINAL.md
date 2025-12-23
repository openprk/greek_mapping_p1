# Render Deployment Fix - Final Solution

## Problem
Render error: `bash: line 1: cd: backend: No such file or directory`

This means Render can't find the `backend/` folder when trying to run the start command.

## Solution: Set Root Directory in Render

Since your `main.py` is in `backend/main.py`, you need to tell Render to use `backend` as the root directory.

### Step-by-Step Fix

1. **Go to Render Dashboard** → Your Service (`greek_mapping_backend`)
2. **Settings** tab
3. **Build & Deploy** section
4. **Root Directory** field:
   - Set to: `backend`
   - (This tells Render to treat `backend/` as the root)
5. **Start Command** field:
   - Change to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - (Remove the `cd backend &&` part since Root Directory is already set)
6. **Save Changes**
7. **Manual Deploy** → Deploy latest commit

### Why This Works

- **Root Directory = `backend`**: Render will look for files starting from the `backend/` folder
- **Start Command**: Since we're already "in" backend, just run `uvicorn main:app` directly
- **No `cd` needed**: Root Directory handles the path

### Alternative (If Root Directory doesn't work)

If Render doesn't support Root Directory, use this Start Command instead:
```
python -m uvicorn main:app --host 0.0.0.0 --port $PORT --app-dir backend
```

But the Root Directory method is cleaner and preferred.

### Verify After Fix

Check Render logs. You should see:
```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:10000
```

Then test:
```
https://greek-mapping-backend.onrender.com/api/health
```

