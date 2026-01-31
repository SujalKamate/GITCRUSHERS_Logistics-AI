"""
FastAPI application entry point for the Logistics AI Dashboard.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from src.api.websocket import ws_manager
from src.api.routes import fleet_router, control_loop_router, decisions_router
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
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(fleet_router)
app.include_router(control_loop_router)
app.include_router(decisions_router)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint for health check."""
    return {
        "status": "healthy",
        "service": "Logistics AI Dashboard API",
        "version": "1.0.0"
    }


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
