# Quick Redeployment Guide

## Fixed Issues
1. **CORS_ORIGINS Parsing Error**: Updated settings.py to handle various environment variable formats
2. **Demo Landing Page**: Fixed localhost references to use relative paths for production
3. **Dashboard Route**: Added proper dashboard routing in the API

## How to Redeploy on Railway

### Option 1: Automatic Redeploy (Recommended)
1. Commit and push your changes to GitHub:
   ```bash
   git add .
   git commit -m "Fix: CORS parsing and demo landing page routes"
   git push origin main
   ```

2. Railway will automatically detect the changes and redeploy
3. Wait 2-3 minutes for deployment to complete
4. Test your URL

### Option 2: Manual Redeploy
1. Go to your Railway project dashboard
2. Click on your service
3. Go to "Deployments" tab
4. Click "Redeploy" on the latest deployment

## Environment Variables to Set on Railway

Make sure these are set in your Railway project:

```
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
CORS_ORIGINS=*
PYTHONPATH=/app
```

## Testing After Deployment

Once deployed, test these URLs (replace with your Railway URL):

1. **Main Demo**: `https://your-app.railway.app/`
2. **Health Check**: `https://your-app.railway.app/health`
3. **Customer App**: `https://your-app.railway.app/customer-app/`
4. **Driver App**: `https://your-app.railway.app/driver-app/`
5. **Dashboard**: `https://your-app.railway.app/dashboard/`

## What's Fixed

### CORS_ORIGINS Error
- Now handles string, comma-separated, and JSON array formats
- Defaults to "*" (allow all) for easier deployment
- More robust parsing with error handling

### Demo Landing Page
- Fixed hardcoded localhost:3002 references
- Now uses relative paths that work in production
- Dashboard iframe and button now point to `/dashboard/`

### Dashboard Routing
- Added `/dashboard/` route in the API
- Currently redirects to demo page (can be updated to serve actual frontend)

## Next Steps

If you want to deploy the actual Next.js frontend separately:

1. Deploy the Next.js frontend to Vercel
2. Update the dashboard route in `src/api/main.py` to redirect to your Vercel URL
3. Update CORS_ORIGINS to include your Vercel domain

## Troubleshooting

If you still get errors:

1. Check Railway logs in the "Deployments" tab
2. Ensure all environment variables are set correctly
3. Verify your GitHub repository has the latest changes
4. Try a fresh deployment by clicking "Redeploy"

## Single URL Demo

Your Railway URL now serves everything:
- Landing page with all interfaces
- Customer app for submitting requests
- Driver app for receiving notifications
- API endpoints for the system
- Health check for monitoring

Perfect for judges - one URL showcases the complete system!