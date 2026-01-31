"""
Control loop API routes.
"""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from src.api.services.state_manager import state_manager
from src.api.services.simulation import simulation_service
from src.api.websocket import ws_manager

router = APIRouter(prefix="/api/control-loop", tags=["control-loop"])


# ============================================================================
# Request/Response Models
# ============================================================================

class StartControlLoopRequest(BaseModel):
    max_cycles: Optional[int] = None
    cycle_interval_seconds: Optional[int] = 5
    auto_approve_decisions: Optional[bool] = True


class StopControlLoopRequest(BaseModel):
    reason: Optional[str] = None
    immediate: Optional[bool] = False


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/status")
async def get_control_loop_status():
    """
    Get current control loop status including running state, phase, and metrics.
    """
    return state_manager.get_control_loop_status()


@router.post("/start")
async def start_control_loop(request: StartControlLoopRequest = None):
    """
    Start the control loop background task.
    """
    if state_manager.control_loop_running:
        return {
            "success": False,
            "message": "Control loop is already running",
            "status": state_manager.get_control_loop_status()
        }

    state_manager.start_control_loop()

    # Start background simulation updates with WebSocket broadcasting
    await simulation_service.start_background_updates(ws_manager.broadcast)

    # Broadcast the start event
    await ws_manager.broadcast({
        "type": "control_loop_update",
        "data": {
            "cycle_id": state_manager.cycle_id,
            "phase": state_manager.current_phase.value,
            "progress_percent": 0,
            "issues_detected": 0,
            "decisions_pending": len(state_manager.pending_decisions),
            "event": "started"
        },
        "source": "control_loop"
    })

    return {
        "success": True,
        "message": "Control loop started successfully",
        "status": state_manager.get_control_loop_status()
    }


@router.post("/stop")
async def stop_control_loop(request: StopControlLoopRequest = None):
    """
    Stop the running control loop.
    """
    if not state_manager.control_loop_running:
        return {
            "success": False,
            "message": "Control loop is not running",
            "status": state_manager.get_control_loop_status()
        }

    # Stop background updates
    await simulation_service.stop_background_updates()

    state_manager.stop_control_loop()

    # Broadcast the stop event
    await ws_manager.broadcast({
        "type": "control_loop_update",
        "data": {
            "cycle_id": state_manager.cycle_id,
            "phase": state_manager.current_phase.value,
            "progress_percent": 0,
            "issues_detected": 0,
            "decisions_pending": len(state_manager.pending_decisions),
            "event": "stopped",
            "reason": request.reason if request else None
        },
        "source": "control_loop"
    })

    return {
        "success": True,
        "message": "Control loop stopped successfully",
        "reason": request.reason if request else None,
        "status": state_manager.get_control_loop_status()
    }


@router.get("/history")
async def get_control_loop_history(page: int = 1, limit: int = 50):
    """
    Get control loop execution history.
    """
    # For now, return recent cycle information
    return {
        "cycles": [
            {
                "cycle_id": f"CYCLE-{state_manager.total_cycles - i}",
                "completed_at": None,
                "duration_ms": state_manager.cycle_durations[-(i+1)] if i < len(state_manager.cycle_durations) else 1000,
                "decisions_made": 0,
                "issues_resolved": 0
            }
            for i in range(min(limit, len(state_manager.cycle_durations)))
        ],
        "total": state_manager.total_cycles,
        "page": page,
        "per_page": limit
    }
