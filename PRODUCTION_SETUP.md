# Production Setup Guide

## Overview

This guide will help you set up the complete Logistics AI Control System for production use with all features enabled.

## Prerequisites

- Python 3.9+
- PostgreSQL 12+
- Node.js 18+
- xAI API Key (for Grok LLM)

## Quick Setup

Run the automated setup script:

```bash
python setup_system.py
```

This will:
- Install all dependencies
- Set up the database
- Configure environment variables
- Test all components
- Provide next steps

## Manual Setup

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements_production.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### 2. Database Setup

#### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

#### Create Database

```bash
# Connect to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE logistics_ai;
CREATE USER logistics_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE logistics_ai TO logistics_user;
\q
```

#### Initialize Database Schema

```bash
python database_setup.py
```

### 3. Environment Configuration

Create `.env` file:

```bash
cp .env.production .env
```

Edit `.env` with your settings:

```env
# Database
DATABASE_URL=postgresql://logistics_user:your_secure_password@localhost:5432/logistics_ai

# xAI API (Get from https://console.x.ai/)
XAI_API_KEY=your_xai_api_key_here

# Optional: External APIs
GOOGLE_MAPS_API_KEY=your_google_maps_key
HERE_API_KEY=your_here_api_key
```

### 4. Start Services

#### Backend API

```bash
# Development
uvicorn src.api.main:app --reload --port 8000

# Production
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### Frontend

```bash
cd frontend

# Development
npm run dev

# Production
npm run build
npm start
```

## Features Overview

### ✅ Fully Implemented

1. **Database Layer**
   - PostgreSQL with SQLAlchemy ORM
   - Persistent storage for all data
   - Automatic schema creation
   - Data migration support

2. **AI Integration**
   - Grok LLM client with retry logic
   - Structured prompt templates
   - Fallback to rule-based analysis
   - Confidence scoring

3. **Route Optimization**
   - Multi-objective optimization (time, cost, fuel)
   - Traffic-aware routing
   - 2-opt TSP improvement
   - Real-time route adjustments

4. **Load Assignment**
   - Hungarian algorithm approach
   - Priority-based assignment
   - Capacity and time constraints
   - Multi-strategy optimization

5. **Enhanced Simulation**
   - Realistic NYC-area scenarios
   - Physics-based movement
   - Dynamic traffic conditions
   - Automatic load generation

6. **Real-time Updates**
   - WebSocket broadcasting
   - Live truck tracking
   - Status notifications
   - Performance metrics

### 🔄 Ready for Integration

1. **External APIs**
   - Google Maps routing
   - HERE traffic data
   - Real GPS tracking
   - Weather services

2. **Advanced Features**
   - Machine learning models
   - Predictive analytics
   - Historical optimization
   - Custom algorithms

## API Endpoints

### Fleet Management
- `GET /api/fleet/status` - Complete fleet overview
- `GET /api/fleet/trucks` - List all trucks
- `PATCH /api/fleet/trucks/{id}` - Update truck
- `GET /api/fleet/loads` - List all loads

### Control Loop
- `POST /api/control-loop/start` - Start AI control loop
- `POST /api/control-loop/stop` - Stop control loop
- `GET /api/control-loop/status` - Current status

### Decisions
- `GET /api/decisions` - Pending decisions
- `POST /api/decisions/{id}/approve` - Approve decision

### WebSocket
- `WS /ws` - Real-time updates

## Configuration Options

### LLM Settings
```env
XAI_API_KEY=your_key_here
GROK_MODEL=grok-beta
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=4096
LLM_TIMEOUT=60
```

### Control Loop
```env
OBSERVATION_INTERVAL=30
MAX_PLANNING_SCENARIOS=5
DECISION_CONFIDENCE_THRESHOLD=0.7
```

### Performance
```env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000"]
```

## Monitoring

### Health Checks
- `GET /health` - System health status
- Database connectivity
- LLM availability
- WebSocket connections

### Metrics
- Fleet utilization rates
- Decision accuracy
- Response times
- System performance

## Troubleshooting

### Database Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Reset database
python database_setup.py

# Check connections
psql -h localhost -U logistics_user -d logistics_ai
```

### API Issues
```bash
# Check logs
tail -f logs/api.log

# Test endpoints
curl http://localhost:8000/health

# Restart service
pkill -f uvicorn
uvicorn src.api.main:app --reload
```

### LLM Issues
```bash
# Test API key
python -c "from src.reasoning.grok_client import get_groq_client; print(get_groq_client().is_available)"

# Check fallback mode
# System will use rule-based analysis if LLM unavailable
```

## Production Deployment

### Docker Setup
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements_production.txt .
RUN pip install -r requirements_production.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables
```bash
# Production settings
HEADLESS_MODE=true
CONTINUOUS_LOOP=true
LOG_LEVEL=INFO

# Security
DATABASE_URL=postgresql://user:pass@db:5432/logistics_ai
XAI_API_KEY=prod_key_here
```

### Scaling
- Use multiple uvicorn workers
- Load balancer for API
- Redis for caching
- Celery for background tasks

## Security Considerations

1. **API Keys**: Store in environment variables, never in code
2. **Database**: Use strong passwords, SSL connections
3. **Network**: Firewall rules, VPN access
4. **Authentication**: Add JWT tokens for production
5. **Monitoring**: Log all API access, monitor for anomalies

## Support

For issues or questions:
1. Check logs in `/logs/` directory
2. Run health checks: `GET /health`
3. Verify configuration: `python -c "from config.settings import settings; print(settings)"`
4. Test components individually using the setup script

## Next Steps

1. **Add Authentication**: Implement JWT-based auth
2. **External APIs**: Connect real GPS and traffic data
3. **Machine Learning**: Add predictive models
4. **Monitoring**: Set up Prometheus/Grafana
5. **Scaling**: Deploy with Kubernetes