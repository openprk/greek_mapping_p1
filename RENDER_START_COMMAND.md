# Render Start Command Configuration

## Critical: Set Start Command in Render

The "exited with status 1" error usually means Render doesn't know how to start your app.

### Fix Steps:

1. **Go to Render Dashboard** → Your Service (`greek_mapping_backend`)
2. **Settings** tab
3. **Build & Deploy** section
4. **Start Command** field - Set this exactly:

```
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

OR if Render sets root directory to `backend/`:

```
uvicorn main:app --host 0.0.0.0 --port $PORT
```

5. **Save Changes**
6. **Manual Deploy** → Deploy latest commit

### Alternative: Root Directory Method

If you prefer, set:
- **Root Directory**: `backend`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Verify Environment Variables

Also check in **Environment** section:
- `TRADIER_API_KEY` - Your Tradier API key
- `PORT` - Should be auto-set by Render (don't override)

### Expected Logs After Fix

You should see:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:10000
```

### If Still Failing

Check the **Logs** tab for the actual error message. Common issues:
- Import errors → Check Python version is 3.11
- Missing dependencies → Check requirements.txt is correct
- Port binding → Make sure using `$PORT` variable

