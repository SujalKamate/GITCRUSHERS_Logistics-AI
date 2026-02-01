# 🚀 Logistics AI System - Startup Guide

## Quick Start (2 Steps)

### 1. Start the API Server (Backend)
```bash
cd GITCRUSHERS_Logistics-AI
python src/api/main.py
```
**Expected Output:**
```
Initializing simulation data...
Generated 10 trucks, X loads
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start the Frontend (Dashboard)
```bash
# New terminal window
cd GITCRUSHERS_Logistics-AI/frontend
npm run dev
```
**Expected Output:**
```
▲ Next.js 14.x.x
- Local:        http://localhost:3002
- Network:      http://192.168.x.x:3002

✓ Ready in 2.1s
```

## 🌐 Access All Interfaces

Once both servers are running:

### Customer Interface (Submit Requests)
**URL**: http://localhost:8000/customer-app/
- Submit delivery requests
- Mobile-friendly interface

### Driver Interface (Manage Deliveries)  
**URL**: http://localhost:8000/driver-app/
- View assigned deliveries
- Update delivery status
- Real-time notifications

### Logistics Dashboard (Management)
**URL**: http://localhost:3002
- Process requests with AI
- Fleet management with journey tracking
- Real-time map visualization

## 🐛 Troubleshooting

### "Failed to fetch" Errors

**Problem**: Frontend shows "Failed to fetch" errors in console

**Solutions**:

1. **Check API Server is Running**
   ```bash
   # Test API directly
   curl http://localhost:8000/health
   # Should return: {"status":"healthy",...}
   ```

2. **Check Frontend Environment**
   - Ensure `.env.local` exists in `frontend/` folder
   - Should contain:
     ```
     NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
     NEXT_PUBLIC_WS_BASE_URL=ws://localhost:8000
     ```

3. **Restart Frontend Server**
   ```bash
   # In frontend terminal
   Ctrl+C  # Stop server
   npm run dev  # Restart
   ```

4. **Check Connection Status**
   - Look for connection test widget in bottom-right corner of dashboard
   - Should show green checkmarks for API and WebSocket

### Empty Interfaces

**Problem**: Driver app shows "No active deliveries" or map shows no journeys

**Solution**: Create a test delivery request:

1. **Submit Request**: http://localhost:8000/customer-app/
   - Use NYC addresses (e.g., "123 Broadway, New York, NY")
   - Fill all required fields

2. **Process Request**: http://localhost:3002/requests
   - Find your pending request
   - Click "Start AI Processing"
   - Wait for truck allocation

3. **View Results**:
   - Driver app should show delivery
   - Fleet map should show journey route

### Port Conflicts

**Problem**: "Port already in use" errors

**Solutions**:
- **API Server (8000)**: Change port in `src/api/main.py`
- **Frontend (3002)**: Change port with `npm run dev -- -p 3003`

### CORS Errors

**Problem**: Cross-origin request blocked

**Solution**: API server includes CORS middleware for ports 3000-3002. If using different port, update `src/api/main.py`:

```python
allow_origins=[
    "http://localhost:3000",
    "http://localhost:3001", 
    "http://localhost:3002",
    "http://localhost:YOUR_PORT",  # Add your port
],
```

## 🧪 Test Everything Works

### 1. API Health Check
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy",...}
```

### 2. Journey Tracking Test
Open: http://localhost:8000/test_journey_tracking.html
- Click all buttons to test API endpoints
- Verify data is returned

### 3. Complete Workflow Test
1. Submit request → Customer app
2. Process request → Dashboard  
3. View delivery → Driver app
4. See journey → Fleet map

## 📊 System Status

When everything is working correctly:

- **API Server**: Running on port 8000
- **Frontend**: Running on port 3002  
- **Connection Test**: Green checkmarks
- **Console**: No "Failed to fetch" errors
- **Journey Map**: Shows blue/purple route lines
- **Driver App**: Shows assigned deliveries

## 🆘 Still Having Issues?

1. **Check Console Logs**: Look for specific error messages
2. **Restart Both Servers**: Sometimes fixes connection issues
3. **Clear Browser Cache**: Refresh with Ctrl+F5
4. **Check Firewall**: Ensure ports 8000 and 3002 are accessible

The system should work seamlessly once both servers are running! 🎉