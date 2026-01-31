"""
Fleet management API routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.models import Location, TruckStatus
from src.api.services.state_manager import state_manager

router = APIRouter(prefix="/api/fleet", tags=["fleet"])


# ============================================================================
# Request/Response Models
# ============================================================================

class LocationUpdate(BaseModel):
    latitude: float
    longitude: float


class TruckUpdateRequest(BaseModel):
    status: Optional[str] = None
    location: Optional[LocationUpdate] = None
    fuel_level_percent: Optional[float] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/status")
async def get_fleet_status():
    """
    Get full fleet status including trucks, routes, loads, and summary.
    """
    summary = state_manager.get_fleet_summary()

    return {
        "trucks": [t.model_dump() for t in state_manager.trucks],
        "active_routes": [r.model_dump() for r in state_manager.routes],
        "pending_loads": [l.model_dump() for l in state_manager.loads if not l.assigned_truck_id],
        "traffic_conditions": [tc.model_dump() for tc in state_manager.traffic_conditions],
        "summary": summary
    }


@router.get("/trucks")
async def get_trucks():
    """
    Get list of all trucks.
    """
    return {
        "trucks": [t.model_dump() for t in state_manager.trucks],
        "total": len(state_manager.trucks)
    }


@router.get("/trucks/{truck_id}")
async def get_truck(truck_id: str):
    """
    Get a single truck by ID.
    """
    truck = state_manager.get_truck(truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail=f"Truck {truck_id} not found")

    return truck.model_dump()


@router.patch("/trucks/{truck_id}")
async def update_truck(truck_id: str, update: TruckUpdateRequest):
    """
    Update a truck's status, location, or fuel level.
    """
    truck = state_manager.get_truck(truck_id)
    if not truck:
        raise HTTPException(status_code=404, detail=f"Truck {truck_id} not found")

    updates = {}

    if update.status:
        try:
            updates["status"] = TruckStatus(update.status)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status: {update.status}"
            )

    if update.location:
        updates["current_location"] = Location(
            latitude=update.location.latitude,
            longitude=update.location.longitude
        )

    if update.fuel_level_percent is not None:
        if not 0 <= update.fuel_level_percent <= 100:
            raise HTTPException(
                status_code=400,
                detail="Fuel level must be between 0 and 100"
            )
        updates["fuel_level_percent"] = update.fuel_level_percent

    updated_truck = state_manager.update_truck(truck_id, **updates)
    return updated_truck.model_dump()


@router.get("/routes")
async def get_routes():
    """
    Get list of all active routes.
    """
    return {
        "routes": [r.model_dump() for r in state_manager.routes],
        "total": len(state_manager.routes)
    }


@router.get("/loads")
async def get_loads():
    """
    Get list of all loads.
    """
    return {
        "loads": [l.model_dump() for l in state_manager.loads],
        "total": len(state_manager.loads)
    }


@router.get("/traffic")
async def get_traffic_conditions():
    """
    Get current traffic conditions.
    """
    return {
        "traffic_conditions": [tc.model_dump() for tc in state_manager.traffic_conditions],
        "total": len(state_manager.traffic_conditions)
    }
