# 🚛 Logistics AI System

> **AI-Powered End-to-End Logistics Management Platform**

[![Live Demo] https://logistics-ai-gaxa.onrender.com/demo/index.html]
## 🎯 Overview

Complete logistics management system with AI-powered request processing, real-time fleet monitoring, and multi-interface coordination. Features three connected applications: customer delivery requests, logistics dashboard, and driver notifications.

## ✨ Key Features

- **🤖 AI Processing**: Groq LLM integration for intelligent truck assignment
- **📱 Multi-Interface**: Customer app, logistics dashboard, driver app
- **⚡ Real-time**: WebSocket notifications and live journey tracking
- **🗺️ Route Optimization**: Smart path planning with traffic consideration
- **📊 Fleet Management**: Live truck monitoring and status updates
- **🚀 Production Ready**: Deployed with single demo URL

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Customer App  │    │ Logistics       │    │   Driver App    │
│   (Mobile)      │    │ Dashboard       │    │   (Mobile)      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   FastAPI       │
                    │   Backend       │
                    │   + WebSocket   │
                    └─────────┬───────┘
                              │
                    ┌─────────────────┐
                    │   Groq LLM      │
                    │   AI Engine     │
                    └─────────────────┘
```

## 🚀 Quick Start

### Live Demo (Recommended)
Visit the live system: **[Demo URL](https://logistics-ai-gaxa.onrender.com/demo/index.html)**

### Local Development
```bash
# Clone repository
git clone https://github.com/SujalKamate/GITCRUSHERS_Logistics-AI
cd GITCRUSHERS_Logistics-AI

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your GROQ_API_KEY to .env

# Run the system
python start_system.py
```

## 🎮 How to Use

### Complete Workflow Test
1. **Submit Request**: Use Customer App to create delivery request
2. **Process with AI**: Go to Dashboard → Requests → "Start AI Processing"
3. **Driver Notification**: Check Driver App for real-time assignment notification
4. **Track Journey**: Monitor live route on Dashboard map

### Individual Interfaces
- **Customer App**: `/customer-app/` - Submit delivery requests
- **Logistics Dashboard**: `/dashboard/` - Process requests, monitor fleet
- **Driver App**: `/driver-app/` - Receive notifications, update status

## 🛠️ Tech Stack

**Backend**
- FastAPI (Python web framework)
- Groq LLM (AI processing)
- SQLAlchemy (Database ORM)
- WebSocket (Real-time communication)

**Frontend**
- Next.js (Dashboard)
- Tailwind CSS (Styling)
- Leaflet (Maps)
- Vanilla JS (Mobile apps)

**Deployment**
- Railway (API hosting)
- Docker (Containerization)
- GitHub Actions (CI/CD)

## 📁 Project Structure

```
GITCRUSHERS_Logistics-AI/
├── src/
│   ├── api/                 # FastAPI backend
│   ├── algorithms/          # Route optimization
│   ├── reasoning/           # AI processing
│   └── models.py           # Data models
├── frontend/               # Next.js dashboard
├── customer-app/           # Customer interface
├── driver-app/            # Driver interface
├── demo-landing/          # Unified demo page
├── config/                # Configuration
└── requirements.txt       # Dependencies
```

## 🔧 Configuration

### Environment Variables
```bash
GROQ_API_KEY=your_groq_api_key
PORT=8000
CORS_ORIGINS=*
PYTHONPATH=/app
```

### API Endpoints
- `GET /health` - System health check
- `POST /api/requests` - Submit delivery request
- `GET /api/requests/pending` - Get pending requests
- `POST /api/requests/process` - AI process request
- `GET /api/fleet/trucks` - Get truck status
- `WebSocket /ws` - Real-time updates

## 🚀 Deployment

### Railway (Recommended)
1. Fork this repository
2. Connect to Railway
3. Set environment variables
4. Deploy automatically

### Manual Deployment
```bash
# Build and run with Docker
docker build -t logistics-ai .
docker run -p 8000:8000 logistics-ai

# Or use the deployment script
python deploy_live.py
```

## 🧪 Testing

```bash
# Run system tests
python test_system.py

# Test specific components
python debug_allocation.py
python test_workflow.py
```

## 📊 Features Breakdown

### AI Processing
- **Smart Assignment**: Distance + capacity + availability optimization
- **Route Planning**: Real-time traffic consideration
- **Fallback Logic**: Rule-based backup when AI unavailable
- **Learning**: Improves from successful assignments

### Real-time Features
- **WebSocket Notifications**: Instant driver alerts
- **Live Tracking**: Journey visualization on map
- **Status Updates**: Real-time delivery progress
- **Fleet Monitoring**: Truck locations and status

### Mobile Optimization
- **Responsive Design**: Works on all devices
- **Touch-Friendly**: Optimized for mobile interaction
- **Offline Capable**: Basic functionality without internet
- **Fast Loading**: Minimal dependencies

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🎯 Demo for Judges

**Single URL Demo**: https://logistics-ai-gaxa.onrender.com/demo/index.html

This URL showcases:
- Complete system overview
- All three interfaces in one place
- Step-by-step testing guide
- Real-time AI processing demonstration

Perfect for evaluating the complete logistics workflow!

---

**Built with ❤️ for intelligent logistics management**
