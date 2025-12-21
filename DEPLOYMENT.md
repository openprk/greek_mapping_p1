# Deployment Guide

## Vercel Frontend Deployment

### Vercel Project Settings

When importing or configuring your project in Vercel Dashboard:

1. **Framework Preset**: `Other`
2. **Root Directory**: `frontend`
3. **Build Command**: (leave blank)
4. **Output Directory**: (leave blank or `.`)
5. **Install Command**: (leave blank)

### Repository Setup

- **Repository**: `openprk/greek_mapping_p1`
- **Branch**: `main` (or `dev` if testing)
- **Root Directory**: `frontend`

### Backend Connection

- **Backend URL**: `https://greek-mapping-backend.onrender.com`
- **Health Endpoint**: `https://greek-mapping-backend.onrender.com/api/health`
- **Chain Endpoint**: `https://greek-mapping-backend.onrender.com/api/chain?symbol=SPY&provider=mock`

### Environment Variables

No environment variables needed for frontend (backend handles API keys).

### After Deployment

1. Vercel will auto-deploy on every push to `main` branch
2. Frontend will be available at: `https://your-project.vercel.app`
3. Frontend automatically calls Render backend API

### Troubleshooting

**CORS Errors:**
- Backend CORS is configured to allow all origins (`*`)
- If issues persist, check Render backend logs

**404 Errors:**
- Verify backend URL in `frontend/app.js` is correct
- Check Render service is running and healthy

**JSON Parse Errors:**
- Check browser console for response shape
- Verify backend returns expected JSON structure

