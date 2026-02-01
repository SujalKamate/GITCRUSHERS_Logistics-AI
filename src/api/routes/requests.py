"""
API routes for delivery request management.
"""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel, Field

from src.models import DeliveryRequest, RequestStatus, LoadPriority
from src.api.services.request_processor import request_processor
from src.api.websocket import ws_manager

router = APIRouter(prefix="/api/requests", tags=["requests"])


# ============================================================================
# Request DTOs
# ============================================================================

class CreateRequestDTO(BaseModel):
    """DTO for creating a new delivery request."""
    customer_name: str = Field(..., min_length=1, max_length=100)
    customer_phone: Optional[str] = Field(None, max_length=20)
    customer_email: Optional[str] = Field(None, max_length=100)
    
    # Load details
    description: str = Field(..., min_length=1, max_length=500)
    weight_kg: float = Field(..., gt=0, le=50000, description="Weight in kilograms")
    volume_m3: Optional[float] = Field(None, gt=0, le=100, description="Volume in cubic meters")
    priority: LoadPriority = LoadPriority.NORMAL
    
    # Locations
    pickup_address: str = Field(..., min_length=5, max_length=200)
    delivery_address: str = Field(..., min_length=5, max_length=200)
    
    # Timing preferences
    preferred_pickup_time: Optional[datetime] = None
    delivery_deadline: Optional[datetime] = None
    
    # Special requirements
    special_instructions: Optional[str] = Field(None, max_length=1000)
    fragile: bool = False
    temperature_controlled: bool = False


class RequestResponseDTO(BaseModel):
    """DTO for request responses."""
    id: str
    customer_name: str
    description: str
    weight_kg: float
    priority: LoadPriority
    status: RequestStatus
    
    pickup_address: str
    delivery_address: str
    
    created_at: datetime
    processed_at: Optional[datetime] = None
    
    estimated_cost: Optional[float] = None
    estimated_pickup_time: Optional[datetime] = None
    estimated_delivery_time: Optional[datetime] = None
    
    assigned_truck_id: Optional[str] = None
    assigned_load_id: Optional[str] = None
    
    ai_analysis: Optional[dict] = None
    allocation_reasoning: Optional[str] = None


class RequestSummaryDTO(BaseModel):
    """DTO for request summary statistics."""
    total_requests: int
    pending_requests: int
    processing_requests: int
    assigned_requests: int
    completed_requests: int
    failed_requests: int
    
    avg_processing_time_minutes: Optional[float] = None
    total_estimated_revenue: float = 0.0


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/", response_model=RequestResponseDTO)
async def create_request(
    request_data: CreateRequestDTO,
    background_tasks: BackgroundTasks
) -> RequestResponseDTO:
    """
    Create a new delivery request.
    
    The request will be processed asynchronously by AI to:
    - Analyze requirements and risks
    - Find optimal truck allocation
    - Calculate cost and time estimates
    """
    try:
        # Submit request for processing
        request = await request_processor.submit_request(request_data.model_dump())
        
        # Notify WebSocket clients
        background_tasks.add_task(
            ws_manager.broadcast,
            {
                "type": "new_request",
                "request_id": request.id,
                "customer": request.customer_name,
                "status": request.status
            }
        )
        
        return RequestResponseDTO(**request.model_dump())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create request: {str(e)}")


@router.get("/", response_model=List[RequestResponseDTO])
async def get_requests(
    status: Optional[RequestStatus] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
) -> List[RequestResponseDTO]:
    """
    Get delivery requests with optional filtering.
    
    Args:
        status: Filter by request status
        limit: Maximum number of requests to return
        offset: Number of requests to skip
    """
    try:
        if status:
            requests = request_processor.get_requests_by_status(status)
        else:
            requests = request_processor.get_all_requests()
        
        # Apply pagination
        paginated_requests = requests[offset:offset + limit]
        
        return [RequestResponseDTO(**req.model_dump()) for req in paginated_requests]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get requests: {str(e)}")


@router.get("/summary", response_model=RequestSummaryDTO)
async def get_request_summary() -> RequestSummaryDTO:
    """Get summary statistics for all requests."""
    try:
        all_requests = request_processor.get_all_requests()
        
        # Count by status
        status_counts = {}
        total_revenue = 0.0
        processing_times = []
        
        for req in all_requests:
            status_counts[req.status] = status_counts.get(req.status, 0) + 1
            
            if req.estimated_cost:
                total_revenue += req.estimated_cost
            
            if req.processed_at and req.created_at:
                processing_time = (req.processed_at - req.created_at).total_seconds() / 60
                processing_times.append(processing_time)
        
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else None
        
        return RequestSummaryDTO(
            total_requests=len(all_requests),
            pending_requests=status_counts.get(RequestStatus.PENDING, 0),
            processing_requests=status_counts.get(RequestStatus.PROCESSING, 0),
            assigned_requests=status_counts.get(RequestStatus.ASSIGNED, 0),
            completed_requests=status_counts.get(RequestStatus.DELIVERED, 0),
            failed_requests=status_counts.get(RequestStatus.FAILED, 0),
            avg_processing_time_minutes=avg_processing_time,
            total_estimated_revenue=total_revenue
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")


@router.get("/{request_id}", response_model=RequestResponseDTO)
async def get_request(request_id: str) -> RequestResponseDTO:
    """Get a specific request by ID."""
    request = request_processor.get_request(request_id)
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    return RequestResponseDTO(**request.model_dump())


@router.put("/{request_id}/cancel")
async def cancel_request(
    request_id: str,
    background_tasks: BackgroundTasks
) -> dict:
    """Cancel a pending or processing request."""
    request = request_processor.get_request(request_id)
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    if request.status not in [RequestStatus.PENDING, RequestStatus.PROCESSING]:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel request with status: {request.status}"
        )
    
    # Update status
    request.status = RequestStatus.CANCELLED
    
    # Notify WebSocket clients
    background_tasks.add_task(
        ws_manager.broadcast,
        {
            "type": "request_cancelled",
            "request_id": request_id,
            "customer": request.customer_name
        }
    )
    
    return {"message": "Request cancelled successfully"}


@router.get("/{request_id}/tracking")
async def get_request_tracking(request_id: str) -> dict:
    """Get real-time tracking information for a request."""
    request = request_processor.get_request(request_id)
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    tracking_info = {
        "request_id": request_id,
        "status": request.status,
        "customer_name": request.customer_name,
        "description": request.description,
        "created_at": request.created_at,
        "estimated_pickup_time": request.estimated_pickup_time,
        "estimated_delivery_time": request.estimated_delivery_time,
        "assigned_truck_id": request.assigned_truck_id,
        "current_location": None,
        "progress_percentage": 0
    }
    
    # Add truck location if assigned
    if request.assigned_truck_id:
        from src.api.services.state_manager import state_manager
        truck = next((t for t in state_manager.trucks if t.id == request.assigned_truck_id), None)
        if truck and truck.current_location:
            tracking_info["current_location"] = {
                "latitude": truck.current_location.latitude,
                "longitude": truck.current_location.longitude,
                "address": truck.current_location.address
            }
            
            # Calculate rough progress percentage
            if request.pickup_location and request.delivery_location:
                total_distance = request.pickup_location.distance_to(request.delivery_location)
                if total_distance > 0:
                    current_to_delivery = truck.current_location.distance_to(request.delivery_location)
                    progress = max(0, min(100, (1 - current_to_delivery / total_distance) * 100))
                    tracking_info["progress_percentage"] = round(progress, 1)
    
    return tracking_info