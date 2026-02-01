# 🚀 Quick Deployment Guide - Get Live URLs

## Goal: Deploy Logistics AI System with Public URLs

This guide will help you deploy the system and get working public links for:
- **Dashboard**: `https://your-app.vercel.app` (Logistics team)
- **Customer App**: `https://your-api.railway.app/customer-app/` (Customers)
- **Driver App**: `https://your-api.railway.app/driver-app/` (Drivers)

## 🎯 Fastest Deployment Options

### Option 1: Railway + Vercel (Recommended - Free Tier)
**Timeline: 30 minutes**
**Cost**: Free for development/demo

#### Step 1: Deploy API Backend to Railway
1. **Create Railway Account**: Go to [railway.app](https://railway.app)
2. **Connect GitHub**: Link your GitHub repository
3. **Deploy API**:
   ```bash
   # Create railway.json in project root
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "cd GITCRUSHERS_Logistics-AI && pip install -r requirements.txt && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
     }
   }
   ```
4. **Set Environment Variables**:
   - `GROQ_API_KEY`: Your Groq API key
   - `PORT`: 8000
   - `CORS_ORIGINS`: https://your-frontend.vercel.app

#### Step 2: Deploy Frontend to Vercel
1. **Create Vercel Account**: Go to [vercel.com](https://vercel.com)
2. **Import Project**: Connect GitHub and select frontend folder
3. **Configure Build**:
   - Build Command: `npm run build`
   - Output Directory: `.next`
   - Root Directory: `GITCRUSHERS_Logistics-AI/frontend`
4. **Set Environment Variables**:
   - `NEXT_PUBLIC_API_BASE_URL`: https://your-api.railway.app
   - `NEXT_PUBLIC_WS_BASE_URL`: wss://your-api.railway.app

### Option 2: Render (All-in-One)
**Timeline: 45 minutes**
**Cost**: Free tier available

#### Deploy Both Services to Render
1. **Create Render Account**: Go to [render.com](https://render.com)
2. **Deploy API Service**:
   - Service Type: Web Service
   - Build Command: `cd GITCRUSHERS_Logistics-AI && pip install -r requirements.txt`
   - Start Command: `cd GITCRUSHERS_Logistics-AI && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
3. **Deploy Frontend Service**:
   - Service Type: Static Site
   - Build Command: `cd GITCRUSHERS_Logistics-AI/frontend && npm install && npm run build`
   - Publish Directory: `GITCRUSHERS_Logistics-AI/frontend/out`

### Option 3: Heroku (Classic)
**Timeline: 1 hour**
**Cost**: $7/month per service

## 🛠 Step-by-Step: Railway + Vercel Deployment

### Prerequisites
- GitHub account with your code
- Groq API key
- 30 minutes of time

### Step 1: Prepare Repository

First, let's prepare the repository for deployment:

```bash
# 1. Create railway.json for API deployment
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "cd GITCRUSHERS_Logistics-AI && pip install -r requirements.txt && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT",
    "healthcheckPath": "/health"
  }
}

# 2. Create vercel.json for frontend deployment
{
  "builds": [
    {
      "src": "GITCRUSHERS_Logistics-AI/frontend/package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "GITCRUSHERS_Logistics-AI/frontend/$1"
    }
  ]
}

# 3. Update package.json for production
{
  "scripts": {
    "build": "next build",
    "start": "next start",
    "export": "next build && next export"
  }
}
```

### Step 2: Deploy API to Railway

1. **Go to Railway**: [railway.app](https://railway.app)
2. **New Project** → **Deploy from GitHub repo**
3. **Select Repository**: Choose your logistics AI repo
4. **Configure Service**:
   - Name: `logistics-ai-api`
   - Root Directory: `GITCRUSHERS_Logistics-AI`
   - Start Command: `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`

5. **Environment Variables**:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   PORT=8000
   CORS_ORIGINS=*
   PYTHONPATH=/app/GITCRUSHERS_Logistics-AI
   ```

6. **Deploy** → Get URL: `https://logistics-ai-api-production.up.railway.app`

### Step 3: Deploy Frontend to Vercel

1. **Go to Vercel**: [vercel.com](https://vercel.com)
2. **New Project** → **Import Git Repository**
3. **Configure Project**:
   - Framework Preset: Next.js
   - Root Directory: `GITCRUSHERS_Logistics-AI/frontend`
   - Build Command: `npm run build`
   - Output Directory: `.next`

4. **Environment Variables**:
   ```
   NEXT_PUBLIC_API_BASE_URL=https://logistics-ai-api-production.up.railway.app
   NEXT_PUBLIC_WS_BASE_URL=wss://logistics-ai-api-production.up.railway.app
   ```

5. **Deploy** → Get URL: `https://logistics-ai-frontend.vercel.app`

### Step 4: Update CORS Settings

Update the API to allow your frontend domain:

```python
# In src/api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://logistics-ai-frontend.vercel.app",
        "http://localhost:3002",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎉 Final URLs

After deployment, you'll have:

### 📊 **Logistics Dashboard**
**URL**: `https://logistics-ai-frontend.vercel.app`
- View pending requests
- Process with AI
- Monitor fleet
- Real-time analytics

### 📱 **Customer Mobile App**
**URL**: `https://logistics-ai-api-production.up.railway.app/customer-app/`
- Submit delivery requests
- Track status
- Mobile-optimized interface

### 🚛 **Driver Mobile App**
**URL**: `https://logistics-ai-api-production.up.railway.app/driver-app/`
- Receive notifications
- Manage deliveries
- Update status
- Navigation links

### 🔧 **API Health Check**
**URL**: `https://logistics-ai-api-production.up.railway.app/health`
- System status
- Health monitoring

## 🚀 Alternative: One-Click Deploy

### Deploy to Railway (Full Stack)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)

Create `railway.toml`:
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "cd GITCRUSHERS_Logistics-AI && pip install -r requirements.txt && uvicorn src.api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/health"
healthcheckTimeout = 100
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 10

[[services]]
name = "api"
source = "."

[[services]]
name = "frontend"
source = "./GITCRUSHERS_Logistics-AI/frontend"
buildCommand = "npm install && npm run build"
startCommand = "npm start"
```

### Deploy to Vercel (Frontend Only)

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone)

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**:
   ```bash
   # Check Python version
   python --version  # Should be 3.11+
   
   # Install dependencies locally first
   pip install -r requirements.txt
   ```

2. **CORS Errors**:
   ```python
   # Add your domain to CORS origins
   allow_origins=["https://your-frontend-domain.vercel.app"]
   ```

3. **Environment Variables**:
   ```bash
   # Verify all required env vars are set
   GROQ_API_KEY=gsk_...
   NEXT_PUBLIC_API_BASE_URL=https://...
   ```

4. **WebSocket Issues**:
   ```javascript
   // Use WSS for HTTPS sites
   const wsUrl = window.location.protocol === 'https:' 
     ? 'wss://your-api-domain.railway.app/ws'
     : 'ws://localhost:8000/ws';
   ```

## 📈 Scaling Options

### Free Tier Limits
- **Railway**: 500 hours/month, 1GB RAM
- **Vercel**: 100GB bandwidth, 6000 build minutes
- **Render**: 750 hours/month

### Upgrade Paths
- **Railway Pro**: $5/month - More resources
- **Vercel Pro**: $20/month - Team features
- **Custom Domain**: $10-15/year

## 🎯 Success Checklist

- [ ] API deployed and accessible
- [ ] Frontend deployed and accessible  
- [ ] Customer app works on mobile
- [ ] Driver app receives notifications
- [ ] Dashboard shows real-time data
- [ ] All three interfaces communicate
- [ ] HTTPS enabled on all URLs
- [ ] Environment variables configured
- [ ] CORS properly configured
- [ ] Health checks passing

## 🚀 Go Live!

Once deployed, share these URLs:

**For Logistics Team**: `https://logistics-ai-frontend.vercel.app`
**For Customers**: `https://logistics-ai-api-production.up.railway.app/customer-app/`
**For Drivers**: `https://logistics-ai-api-production.up.railway.app/driver-app/`

Your Logistics AI system is now live and accessible worldwide! 🌍