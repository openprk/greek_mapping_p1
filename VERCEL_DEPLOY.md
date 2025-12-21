# Deploying to Vercel

## Quick Deploy

### Option 1: Using Vercel CLI

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   vercel
   ```

4. **Follow the prompts**:
   - Link to existing project or create new
   - Project name: `greek_mapping_p1` (or your choice)
   - Directory: `.` (current directory)

### Option 2: Deploy via GitHub Integration

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New Project"
3. Import your GitHub repository: `openprk/greek_mapping_p1`
4. Configure:
   - **Framework Preset**: Other
   - **Root Directory**: `.` (or leave default)
   - **Build Command**: (leave empty)
   - **Output Directory**: `frontend`
5. Add Environment Variables (if needed):
   - `TRADIER_API_KEY` (if using Tradier)
   - `POLYGON_API_KEY` (if using Polygon)
6. Click "Deploy"

## Configuration Files

- `vercel.json`: Vercel configuration for routing
- `api/index.py`: Serverless function wrapper for FastAPI backend
- `.vercelignore`: Files to exclude from deployment

## Important Notes

1. **Backend API**: The FastAPI backend will be available at `/api/*` routes
2. **Frontend**: Static files in `frontend/` will be served at root
3. **API Base URL**: The frontend automatically detects if running on Vercel and uses `/api` instead of `http://localhost:8000`

## Environment Variables

Set these in Vercel Dashboard → Project Settings → Environment Variables:

- `TRADIER_API_KEY`: Your Tradier API key (if using)
- `POLYGON_API_KEY`: Your Polygon API key (if using)

## After Deployment

Your app will be available at:
- `https://your-project-name.vercel.app`
- Frontend: `https://your-project-name.vercel.app/`
- API: `https://your-project-name.vercel.app/api/chain`

## Troubleshooting

- If API routes don't work, check `vercel.json` routing configuration
- Ensure `requirements-vercel.txt` includes all dependencies
- Check Vercel function logs in the dashboard

