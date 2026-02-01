"""
FastAPI application entry point for the Logistics AI Dashboard.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.websocket import ws_manager
from src.api.routes import fleet_router, control_loop_router, decisions_router, requests_router
from src.api.services.simulation import simulation_service
from src.api.services.state_manager import state_manager

# Optional database service
try:
    from src.api.services.database_service import DatabaseService
    from database_setup import get_database_service
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Database service not available - using in-memory storage")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup: Initialize database and simulation data
    if DATABASE_AVAILABLE:
        print("Initializing database...")
        try:
            from database_setup import init_database
            await init_database()
            print("Database initialized successfully")
        except Exception as e:
            print(f"Database initialization failed: {e}")
            print("Falling back to in-memory storage")
    else:
        print("Using in-memory storage (database not available)")
    
    print("Initializing simulation data...")
    simulation_service.generate_initial_data(num_trucks=10)
    print(f"Generated {len(state_manager.trucks)} trucks, {len(state_manager.loads)} loads")

    yield

    # Shutdown: Clean up background tasks
    print("Shutting down background tasks...")
    await simulation_service.stop_background_updates()


# Create FastAPI app
app = FastAPI(
    title="Logistics AI Dashboard API",
    description="Backend API for the Agentic Logistics Control System",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
import os

# Get allowed origins from environment or use defaults
cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001", 
    "http://127.0.0.1:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3002",
]

# Add common production domains
cors_origins.extend([
    "https://*.vercel.app",
    "https://*.railway.app", 
    "https://*.render.com",
    "https://*.herokuapp.com",
    "https://*.netlify.app"
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(fleet_router)
app.include_router(control_loop_router)
app.include_router(decisions_router)
app.include_router(requests_router)

# Add demo landing page redirect
@app.get("/demo")
async def demo_landing():
    """Redirect to demo landing page."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/demo/")

@app.get("/demo/")
async def demo_landing_index():
    """Redirect to demo landing page index."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/demo/index.html")

# Add customer app redirect before mounting static files
@app.get("/customer-app/")
async def customer_app_index():
    """Redirect to customer app index."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/customer-app/index.html")


@app.get("/driver-app/")
async def driver_app_index():
    """Redirect to driver app index."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/driver-app/index.html")

# Mount static files
app.mount("/demo", StaticFiles(directory="demo-landing"), name="demo-landing")
app.mount("/customer-app", StaticFiles(directory="customer-app"), name="customer-app")
app.mount("/driver-app", StaticFiles(directory="driver-app"), name="driver-app")


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - redirect to demo landing page."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/demo/")


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "trucks": len(state_manager.trucks),
        "loads": len(state_manager.loads),
        "control_loop_running": state_manager.control_loop_running,
        "websocket_connections": ws_manager.connection_count
    }


@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint."""
    from fastapi.responses import FileResponse
    import os
    
    # Try to serve favicon from customer-app directory
    favicon_path = "customer-app/favicon.ico"
    if os.path.exists(favicon_path):
        return FileResponse(favicon_path)
    
    # Return 204 No Content if favicon doesn't exist
    from fastapi.responses import Response
    return Response(status_code=204)


# ============================================================================
# WebSocket Endpoint
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates.
    Clients connect here to receive truck location updates,
    control loop status changes, and decision notifications.
    """
    await ws_manager.connect(websocket)

    try:
        while True:
            # Wait for messages from client (ping/pong or commands)
            data = await websocket.receive_json()

            # Handle ping/pong for keepalive
            if data.get("type") == "ping":
                await ws_manager.send_personal_message(
                    {"type": "pong", "timestamp": data.get("timestamp")},
                    websocket
                )
            # Handle subscription requests
            elif data.get("type") == "subscribe":
                # Client wants to subscribe to specific events
                await ws_manager.send_personal_message(
                    {
                        "type": "subscribed",
                        "events": data.get("events", ["all"]),
                        "message": "Successfully subscribed to events"
                    },
                    websocket
                )
            # Echo back any other messages
            else:
                await ws_manager.send_personal_message(
                    {"type": "ack", "received": data},
                    websocket
                )

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


# ============================================================================
# Run with uvicorn
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
