"""
Request processing service for handling delivery requests.

This service processes incoming delivery requests using AI to:
1. Analyze the request requirements
2. Find optimal truck allocation
3. Estimate costs and timing
4. Create load assignments
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

import structlog
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

from src.models import (
    DeliveryRequest, RequestStatus, Load, Location, 
    LoadPriority, Truck, TruckStatus
)
from src.reasoning.grok_client import get_groq_client
from src.algorithms.load_assignment import LoadAssignmentEngine
from src.algorithms.route_optimizer import RouteOptimizer
from .state_manager import state_manager

logger = structlog.get_logger(__name__)


class RequestProcessor:
    """Service for processing delivery requests with AI assistance."""
    
    def __init__(self):
        self.groq_client = get_groq_client()
        self.assignment_engine = LoadAssignmentEngine()
        self.route_optimizer = RouteOptimizer()
        self.geocoder = Nominatim(user_agent="logistics-ai")
        
        # In-memory storage for requests (in production, use database)
        self.requests: Dict[str, DeliveryRequest] = {}
    
    async def submit_request(self, request_data: Dict[str, Any]) -> DeliveryRequest:
        """
        Submit a new delivery request for processing.
        
        Args:
            request_data: Dictionary containing request details
            
        Returns:
            DeliveryRequest: The created request (stays in PENDING status)
        """
        # Create request with unique ID
        request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        
        request = DeliveryRequest(
            id=request_id,
            **request_data
        )
        
        # Store request
        self.requests[request_id] = request
        
        logger.info("New delivery request submitted", 
                   request_id=request_id, 
                   customer=request.customer_name)
        
        # DO NOT process automatically - let dashboard trigger processing
        # This ensures requests stay visible in "pending" status
        
        return request
    
    async def _process_request(self, request: DeliveryRequest) -> None:
        """Process a delivery request through the AI pipeline."""
        try:
            request.status = RequestStatus.PROCESSING
            
            # Step 1: Geocode addresses
            await self._geocode_addresses(request)
            
            # Step 2: AI analysis of request
            await self._analyze_request_with_ai(request)
            
            # Step 3: Find optimal truck allocation
            await self._allocate_truck(request)
            
            # Step 4: Create load and update assignments
            await self._create_load_assignment(request)
            
            # Step 5: Calculate estimates
            await self._calculate_estimates(request)
            
            # Validate that truck allocation was successful
            if request.assigned_truck_id:
                request.status = RequestStatus.ASSIGNED
                request.processed_at = datetime.utcnow()
                
                logger.info("Request processing completed", 
                           request_id=request.id,
                           assigned_truck=request.assigned_truck_id)
            else:
                request.status = RequestStatus.FAILED
                logger.error("Request processing failed - no truck allocated", 
                            request_id=request.id)
            
        except Exception as e:
            logger.error("Request processing failed", 
                        request_id=request.id, 
                        error=str(e))
            request.status = RequestStatus.FAILED
    
    async def _geocode_addresses(self, request: DeliveryRequest) -> None:
        """Convert addresses to coordinates."""
        pickup_geocoded = False
        delivery_geocoded = False
        
        try:
            # Geocode pickup address
            if not request.pickup_location:
                pickup_loc = await asyncio.to_thread(
                    self.geocoder.geocode, request.pickup_address
                )
                if pickup_loc:
                    request.pickup_location = Location(
                        latitude=pickup_loc.latitude,
                        longitude=pickup_loc.longitude,
                        address=request.pickup_address
                    )
                    pickup_geocoded = True
            
            # Geocode delivery address
            if not request.delivery_location:
                delivery_loc = await asyncio.to_thread(
                    self.geocoder.geocode, request.delivery_address
                )
                if delivery_loc:
                    request.delivery_location = Location(
                        latitude=delivery_loc.latitude,
                        longitude=delivery_loc.longitude,
                        address=request.delivery_address
                    )
                    delivery_geocoded = True
            
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.warning("Geocoding failed, using fallback", 
                          request_id=request.id, error=str(e))
        except Exception as e:
            logger.warning("Geocoding error, using fallback", 
                          request_id=request.id, error=str(e))
        
        # Check if geocoded locations are outside service area (NYC region)
        # NYC region: roughly 40.4-41.0 latitude, -74.5 to -73.5 longitude
        def is_in_nyc_region(location: Location) -> bool:
            return (40.4 <= location.latitude <= 41.0 and 
                    -74.5 <= location.longitude <= -73.5)
        
        # If either location is outside NYC region, use NYC fallback for both
        if ((request.pickup_location and not is_in_nyc_region(request.pickup_location)) or
            (request.delivery_location and not is_in_nyc_region(request.delivery_location))):
            
            logger.info("Geocoded locations outside service area, using NYC fallback", 
                       request_id=request.id)
            
            request.pickup_location = Location(
                latitude=40.7128, longitude=-74.0060,
                address=request.pickup_address
            )
            request.delivery_location = Location(
                latitude=40.7589, longitude=-73.9851,
                address=request.delivery_address
            )
        
        # Smart fallback logic for failed geocoding
        elif not request.pickup_location and not request.delivery_location:
            # Both failed - use NYC coordinates (default service area)
            request.pickup_location = Location(
                latitude=40.7128, longitude=-74.0060,
                address=request.pickup_address
            )
            request.delivery_location = Location(
                latitude=40.7589, longitude=-73.9851,
                address=request.delivery_address
            )
            logger.info("Using NYC fallback for both locations", request_id=request.id)
            
        elif not request.pickup_location and request.delivery_location:
            # Pickup failed, delivery succeeded - use nearby pickup location
            request.pickup_location = Location(
                latitude=request.delivery_location.latitude + 0.01,  # ~1km offset
                longitude=request.delivery_location.longitude + 0.01,
                address=request.pickup_address
            )
            logger.info("Using nearby fallback for pickup location", request_id=request.id)
            
        elif request.pickup_location and not request.delivery_location:
            # Delivery failed, pickup succeeded - use nearby delivery location
            request.delivery_location = Location(
                latitude=request.pickup_location.latitude + 0.01,  # ~1km offset
                longitude=request.pickup_location.longitude + 0.01,
                address=request.delivery_address
            )
            logger.info("Using nearby fallback for delivery location", request_id=request.id)
        
        logger.info("Addresses geocoded", request_id=request.id)
    
    async def _analyze_request_with_ai(self, request: DeliveryRequest) -> None:
        """Use AI to analyze the request and provide insights."""
        if not self.groq_client.is_available:
            logger.info("AI not available, using rule-based analysis", 
                       request_id=request.id)
            request.ai_analysis = self._rule_based_analysis(request)
            return
        
        # Prepare context for AI
        context = self._prepare_ai_context(request)
        
        system_prompt = """
        You are an expert logistics AI assistant. Analyze delivery requests and provide:
        1. Risk assessment (low/medium/high)
        2. Recommended priority level
        3. Special handling requirements
        4. Estimated complexity score (1-10)
        5. Key considerations for truck allocation
        
        Respond in JSON format with these fields:
        - risk_level: string
        - recommended_priority: string  
        - special_requirements: array of strings
        - complexity_score: number
        - allocation_factors: array of strings
        - reasoning: string
        """
        
        try:
            response = self.groq_client.complete_json(
                prompt=f"Analyze this delivery request:\n{context}",
                system_prompt=system_prompt
            )
            
            if response.get("success") and response.get("parsed"):
                request.ai_analysis = response["parsed"]
                logger.info("AI analysis completed", request_id=request.id)
            else:
                request.ai_analysis = self._rule_based_analysis(request)
                
        except Exception as e:
            logger.warning("AI analysis failed, using fallback", 
                          request_id=request.id, error=str(e))
            request.ai_analysis = self._rule_based_analysis(request)
    
    def _prepare_ai_context(self, request: DeliveryRequest) -> str:
        """Prepare context string for AI analysis."""
        distance = "unknown"
        if request.pickup_location and request.delivery_location:
            distance = f"{request.pickup_location.distance_to(request.delivery_location):.1f}km"
        
        return f"""
        Customer: {request.customer_name}
        Description: {request.description}
        Weight: {request.weight_kg}kg
        Volume: {request.volume_m3 or 'not specified'}m³
        Priority: {request.priority}
        Distance: {distance}
        Pickup: {request.pickup_address}
        Delivery: {request.delivery_address}
        Deadline: {request.delivery_deadline or 'not specified'}
        Special Instructions: {request.special_instructions or 'none'}
        Fragile: {request.fragile}
        Temperature Controlled: {request.temperature_controlled}
        """
    
    def _rule_based_analysis(self, request: DeliveryRequest) -> Dict[str, Any]:
        """Fallback rule-based analysis when AI is unavailable."""
        # Simple rule-based logic
        risk_level = "low"
        complexity_score = 3
        
        if request.fragile or request.temperature_controlled:
            risk_level = "medium"
            complexity_score += 2
        
        if request.priority in [LoadPriority.URGENT, LoadPriority.CRITICAL]:
            risk_level = "high"
            complexity_score += 3
        
        if request.weight_kg > 5000:  # Heavy load
            complexity_score += 2
        
        return {
            "risk_level": risk_level,
            "recommended_priority": request.priority,
            "special_requirements": [
                req for req in [
                    "fragile_handling" if request.fragile else None,
                    "temperature_control" if request.temperature_controlled else None
                ] if req
            ],
            "complexity_score": min(complexity_score, 10),
            "allocation_factors": [
                "weight_capacity",
                "distance_optimization",
                "priority_matching"
            ],
            "reasoning": "Rule-based analysis (AI unavailable)"
        }
    
    async def _allocate_truck(self, request: DeliveryRequest) -> None:
        """Find the best truck for this request using AI-assisted allocation."""
        available_trucks = [
            truck for truck in state_manager.trucks 
            if truck.status in [TruckStatus.IDLE, TruckStatus.EN_ROUTE]
            and truck.capacity_kg >= request.weight_kg
        ]
        
        if not available_trucks:
            logger.warning("No available trucks found", 
                          request_id=request.id,
                          required_capacity=request.weight_kg)
            return
        
        logger.info("Found available trucks", 
                   request_id=request.id,
                   truck_count=len(available_trucks),
                   required_capacity=request.weight_kg)
        
        # Create temporary load for allocation algorithm
        temp_load = Load(
            id=f"TEMP-{request.id}",
            description=request.description,
            weight_kg=request.weight_kg,
            volume_m3=request.volume_m3,
            priority=request.priority,
            pickup_location=request.pickup_location,
            delivery_location=request.delivery_location,
            delivery_deadline=request.delivery_deadline
        )
        
        # Use assignment engine to find optimal allocation
        solution = self.assignment_engine.assign_loads_to_trucks(
            available_trucks, [temp_load]
        )
        
        if solution.assignments:
            assignment = solution.assignments[0]
            request.assigned_truck_id = assignment.truck_id
            
            # Get AI reasoning for the allocation
            await self._get_allocation_reasoning(request, assignment.truck_id)
            
            # Send WebSocket notification to the assigned truck
            await self._notify_truck_assignment(request, assignment.truck_id)
            
            logger.info("Truck allocated", 
                       request_id=request.id,
                       truck_id=assignment.truck_id,
                       cost=assignment.estimated_cost)
        else:
            logger.warning("Truck allocation failed - no valid assignments", 
                          request_id=request.id,
                          available_trucks=len(available_trucks),
                          unassigned_loads=solution.unassigned_loads)
    
    async def _get_allocation_reasoning(self, request: DeliveryRequest, truck_id: str) -> None:
        """Get AI explanation for truck allocation decision."""
        if not self.groq_client.is_available:
            request.allocation_reasoning = f"Allocated to truck {truck_id} based on capacity and availability"
            return
        
        truck = next((t for t in state_manager.trucks if t.id == truck_id), None)
        if not truck:
            return
        
        context = f"""
        Request: {request.description} ({request.weight_kg}kg, {request.priority} priority)
        Allocated Truck: {truck.name} (ID: {truck_id})
        Truck Status: {truck.status}
        Truck Capacity: {truck.capacity_kg}kg
        Current Location: {truck.current_location.address if truck.current_location else 'Unknown'}
        """
        
        try:
            response = self.groq_client.complete(
                prompt=f"Explain why this truck allocation is optimal:\n{context}",
                system_prompt="Provide a brief, clear explanation of why this truck is the best choice for this delivery request."
            )
            
            if response.get("success"):
                request.allocation_reasoning = response["content"]
            else:
                request.allocation_reasoning = f"Allocated to truck {truck_id} based on optimization algorithm"
                
        except Exception as e:
            logger.warning("Failed to get allocation reasoning", error=str(e))
            request.allocation_reasoning = f"Allocated to truck {truck_id} based on optimization algorithm"
    
    async def _notify_truck_assignment(self, request: DeliveryRequest, truck_id: str) -> None:
        """Send WebSocket notification to the assigned truck driver."""
        try:
            from src.api.websocket import ws_manager
            
            # Create notification message for the driver
            notification = {
                "type": "new_assignment",
                "truck_id": truck_id,
                "request_id": request.id,
                "customer_name": request.customer_name,
                "description": request.description,
                "weight_kg": request.weight_kg,
                "priority": request.priority,
                "pickup_address": request.pickup_address,
                "delivery_address": request.delivery_address,
                "estimated_cost": request.estimated_cost,
                "estimated_pickup_time": request.estimated_pickup_time.isoformat() if request.estimated_pickup_time else None,
                "special_instructions": request.special_instructions,
                "fragile": request.fragile,
                "temperature_controlled": request.temperature_controlled,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"New delivery assigned: {request.description} for {request.customer_name}"
            }
            
            # Broadcast to all connected clients (in a real app, you'd filter by truck_id)
            await ws_manager.broadcast(notification)
            
            logger.info("Truck assignment notification sent", 
                       request_id=request.id,
                       truck_id=truck_id)
                       
        except Exception as e:
            logger.warning("Failed to send truck assignment notification", 
                          request_id=request.id,
                          truck_id=truck_id,
                          error=str(e))
    
    async def _create_load_assignment(self, request: DeliveryRequest) -> None:
        """Create actual load and assign to truck."""
        if not request.assigned_truck_id or not request.pickup_location or not request.delivery_location:
            return
        
        # Create load ID
        load_id = f"LOAD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create load object
        load = Load(
            id=load_id,
            description=request.description,
            weight_kg=request.weight_kg,
            volume_m3=request.volume_m3,
            priority=request.priority,
            pickup_location=request.pickup_location,
            delivery_location=request.delivery_location,
            pickup_window_start=request.preferred_pickup_time,
            delivery_deadline=request.delivery_deadline,
            assigned_truck_id=request.assigned_truck_id
        )
        
        # Add to state manager
        state_manager.loads.append(load)
        request.assigned_load_id = load_id
        
        # Update truck status
        truck = next((t for t in state_manager.trucks if t.id == request.assigned_truck_id), None)
        if truck and truck.status == TruckStatus.IDLE:
            truck.status = TruckStatus.EN_ROUTE
            truck.current_load_id = load_id
        
        logger.info("Load created and assigned", 
                   request_id=request.id,
                   load_id=load_id)
    
    async def _calculate_estimates(self, request: DeliveryRequest) -> None:
        """Calculate cost and time estimates."""
        if not request.pickup_location or not request.delivery_location:
            return
        
        distance = request.pickup_location.distance_to(request.delivery_location)
        
        # Simple cost calculation (in production, use more sophisticated pricing)
        base_cost = 50.0  # Base fee
        distance_cost = distance * 2.5  # Per km
        weight_cost = request.weight_kg * 0.1  # Per kg
        
        priority_multiplier = {
            LoadPriority.LOW: 0.8,
            LoadPriority.NORMAL: 1.0,
            LoadPriority.HIGH: 1.3,
            LoadPriority.URGENT: 1.6,
            LoadPriority.CRITICAL: 2.0
        }
        
        request.estimated_cost = (base_cost + distance_cost + weight_cost) * priority_multiplier[request.priority]
        
        # Time estimates
        avg_speed = 45  # km/h average including stops
        travel_time_hours = distance / avg_speed
        
        # Add buffer time based on priority
        buffer_hours = {
            LoadPriority.LOW: 2.0,
            LoadPriority.NORMAL: 1.5,
            LoadPriority.HIGH: 1.0,
            LoadPriority.URGENT: 0.5,
            LoadPriority.CRITICAL: 0.25
        }
        
        total_time = travel_time_hours + buffer_hours[request.priority]
        
        now = datetime.utcnow()
        request.estimated_pickup_time = now + timedelta(hours=0.5)  # 30 min to reach pickup
        request.estimated_delivery_time = request.estimated_pickup_time + timedelta(hours=total_time)
    
    def get_request(self, request_id: str) -> Optional[DeliveryRequest]:
        """Get a request by ID."""
        return self.requests.get(request_id)
    
    def get_all_requests(self) -> List[DeliveryRequest]:
        """Get all requests."""
        return list(self.requests.values())
    
    def get_requests_by_status(self, status: RequestStatus) -> List[DeliveryRequest]:
        """Get requests by status."""
        return [req for req in self.requests.values() if req.status == status]
    
    async def process_request(self, request_id: str) -> bool:
        """
        Manually trigger processing of a specific request.
        
        Args:
            request_id: ID of the request to process
            
        Returns:
            bool: True if processing started successfully
        """
        request = self.get_request(request_id)
        if not request:
            return False
        
        if request.status != RequestStatus.PENDING:
            logger.warning("Request not in pending status", 
                          request_id=request_id, 
                          current_status=request.status)
            return False
        
        # Process the request
        asyncio.create_task(self._process_request(request))
        return True


# Global instance
request_processor = RequestProcessor()