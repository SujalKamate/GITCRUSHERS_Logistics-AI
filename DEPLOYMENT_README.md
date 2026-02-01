# 🚀 Deploy Logistics AI System - Get Live URLs

## Quick Start (30 minutes to live URLs)

### Option 1: Railway + Vercel (Recommended - Free)

#### Step 1: Deploy API to Railway
1. **Go to [Railway](https://railway.app)** and sign up with GitHub
2. **New Project** → **Deploy from GitHub repo**
3. **Select this repository**
4. **Environment Variables**:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   PORT=8000
   CORS_ORIGINS=*
   ```
5. **Deploy** → Get your API URL: `https://your-app.railway.app`

#### Step 2: Deploy Frontend to Vercel
1. **Go to [Vercel](https://vercel.com)** and sign up with GitHub
2. **New Project** → **Import Git Repository**
3. **Configure**:
   - Root Directory: `GITCRUSHERS_Logistics-AI/frontend`
   - Framework: Next.js
4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://your-app.railway.app
   NEXT_PUBLIC_WS_BASE_URL=wss://your-app.railway.app
   ```
5. **Deploy** → Get your Frontend URL: `https://your-app.vercel.app`

### 🎉 Your Live URLs

After deployment, you'll have:

- **📊 Logistics Dashboard**: `https://your-app.vercel.app`
- **📱 Customer App**: `https://your-app.railway.app/customer-app/`
- **🚛 Driver App**: `https://your-app.railway.app/driver-app/`
- **🔧 API Health**: `https://your-app.railway.app/health`

## Alternative Deployment Options

### Option 2: Render (All-in-One)
- Deploy both API and Frontend on Render
- Single platform management
- Free tier available

### Option 3: Heroku (Classic)
- Reliable but requires payment
- $7/month per service
- Good for production use

## Deployment Helper Scripts

### 1. Prepare for Deployment
```bash
python deploy.py
```
This script will:
- Check requirements
- Create configuration files
- Show deployment instructions

### 2. Check Deployment Status
```bash
python check_deployment.py
```
This script will:
- Test all deployed services
- Verify functionality
- Show live URLs

## Configuration Files Created

The following files are automatically created for deployment:

- `railway.json` - Railway deployment config
- `vercel.json` - Vercel deployment config  
- `Procfile` - Heroku deployment config
- `runtime.txt` - Python version specification
- `railway.toml` - Railway template config

## Environment Variables Required

### For API (Railway/Render/Heroku):
```
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
CORS_ORIGINS=https://your-frontend-domain.vercel.app
PYTHONPATH=/app
```

### For Frontend (Vercel):
```
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.railway.app
NEXT_PUBLIC_WS_BASE_URL=wss://your-api-domain.railway.app
```

## Troubleshooting

### Common Issues

1. **Build Failures**:
   - Ensure Python 3.11+ is specified
   - Check all dependencies in requirements.txt

2. **CORS Errors**:
   - Add your frontend domain to CORS_ORIGINS
   - Use exact domain (no wildcards in production)

3. **WebSocket Issues**:
   - Use `wss://` for HTTPS sites
   - Ensure WebSocket endpoint is accessible

4. **Static Files Not Loading**:
   - Verify customer-app and driver-app folders exist
   - Check static file mounting in main.py

### Getting Help

1. **Check deployment status**: Run `python check_deployment.py`
2. **View logs**: Check your platform's logs (Railway/Vercel/etc.)
3. **Test locally**: Ensure everything works on `localhost` first
4. **Environment variables**: Double-check all required env vars are set

## Success Checklist

- [ ] API deployed and health check passes
- [ ] Frontend deployed and accessible
- [ ] Customer app loads on mobile
- [ ] Driver app receives notifications
- [ ] Dashboard shows real-time data
- [ ] All CORS configured correctly
- [ ] HTTPS enabled on all URLs
- [ ] Environment variables set
- [ ] WebSocket connections work

## Next Steps After Deployment

1. **Share URLs** with your team/users
2. **Set up monitoring** for uptime tracking
3. **Configure custom domain** (optional)
4. **Set up SSL certificates** (usually automatic)
5. **Monitor usage** and scale as needed

## Cost Estimates

### Free Tier Limits:
- **Railway**: 500 hours/month, 1GB RAM
- **Vercel**: 100GB bandwidth, unlimited requests
- **Render**: 750 hours/month

### Paid Upgrades:
- **Railway Pro**: $5/month
- **Vercel Pro**: $20/month  
- **Heroku**: $7/month per service

## Support

For deployment issues:
1. Check the logs on your deployment platform
2. Verify environment variables are set correctly
3. Test the health endpoint: `https://your-api.railway.app/health`
4. Ensure CORS is configured for your frontend domain

Your Logistics AI system will be live and accessible worldwide! 🌍