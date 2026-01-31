"""
Enhanced simulation service with real algorithms.
"""

import asyncio
import uuid
import random
from datetime import datetime, timedelta
from typing import Optional, Callable, List
import structlog

from src.models import (
    Truck, Route, Load, TrafficCondition, GPSReading, Location,
    TruckStatus, LoadPriority, TrafficLevel
)
from src.api.services.state_manager import state_manager
from src.algorithms.route_optimizer import RouteOptimizer
from src.algorithms.load_assignment import LoadAssignmentEngine

logger = structlog.get_logger(__name__)


class EnhancedSimulationService:
    """
    Enhanced simulation service with real optimization algorithms.
    """

    def __init__(self):
        self.route_optimizer = RouteOptimizer()
        self.load_assignment_engine = LoadAssignmentEngine()
        self._background_task: Optional[asyncio.Task] = None
        self._broadcast_callback: Optional[Callable] = None
        self._running = False

    def generate_initial_data(self, num_trucks: int = 10, num_loads: int = 15):
        """Generate initial fleet data with realistic scenarios."""
        logger.info("Generating enhanced initial data", trucks=num_trucks, loads=num_loads)

        # Clear existing data
        state_manager.reset()

        # Generate trucks with realistic locations (NYC area)
        trucks = self._generate_realistic_trucks(num_trucks)
        state_manager.trucks = trucks

        # Generate loads with realistic pickup/delivery locations
        loads = self._generate_realistic_loads(num_loads)
        state_manager.loads = loads

        # Generate traffic conditions
        traffic_conditions = self._generate_realistic_traffic()
        state_manager.traffic_conditions = traffic_conditions

        # Perform initial load assignments using our algorithm
        self._perform_initial_assignments()

        # Generate initial routes for assigned loads
        self._generate_initial_routes()

        logger.info(
            "Enhanced initial data generated",
            trucks=len(trucks),
            loads=len(loads),
            traffic_segments=len(traffic_conditions),
            assigned_loads=len([l for l in loads if l.assigned_truck_id])
        )

    def _generate_realistic_trucks(self, count: int) -> List[Truck]:
        """Generate trucks with realistic NYC-area locations."""
        trucks = []
        
        # NYC area coordinates
        nyc_locations = [
            (40.7128, -74.0060),  # Manhattan
            (40.6782, -73.9442),  # Brooklyn
            (40.7282, -73.7949),  # Queens
            (40.8176, -73.7781),  # Bronx
            (40.5795, -74.1502),  # Staten Island
            (40.7589, -73.9851),  # Times Square
            (40.6892, -74.0445),  # Jersey City
            (40.7505, -73.9934),  # Midtown
        ]

        truck_names = [
            "Alpha Express", "Beta Logistics", "Gamma Freight", "Delta Cargo",
            "Epsilon Transport", "Zeta Delivery", "Eta Hauling", "Theta Shipping",
            "Iota Express", "Kappa Freight", "Lambda Cargo", "Mu Transport"
        ]

        for i in range(count):
            lat, lng = random.choice(nyc_locations)
            # Add some random variation
            lat += random.uniform(-0.05, 0.05)
            lng += random.uniform(-0.05, 0.05)

            status = random.choices(
                [TruckStatus.IDLE, TruckStatus.EN_ROUTE, TruckStatus.LOADING],
                weights=[0.4, 0.5, 0.1]
            )[0]

            truck = Truck(
                id=f"TRK-{i+1:03d}",
                name=truck_names[i % len(truck_names)] + f" {i+1}",
                status=status,
                current_location=Location(latitude=lat, longitude=lng),
                driver_id=f"DRV-{i+1:03d}",
                capacity_kg=random.choice([10000, 12000, 15000, 18000, 20000]),
                fuel_level_percent=random.uniform(30, 95),
                total_distance_km=random.uniform(1000, 50000),
                total_deliveries=random.randint(10, 500)
            )
            trucks.append(truck)

        return trucks

    def _generate_realistic_loads(self, count: int) -> List[Load]:
        """Generate loads with realistic pickup/delivery scenarios."""
        loads = []
        
        # Common pickup locations (warehouses, distribution centers)
        pickup_locations = [
            (40.6892, -74.0445, "Newark Distribution Center"),
            (40.7282, -73.7949, "Queens Warehouse"),
            (40.8176, -73.7781, "Bronx Logistics Hub"),
            (40.5795, -74.1502, "Staten Island Port"),
            (40.7128, -74.0060, "Manhattan Depot")
        ]

        # Common delivery locations (stores, offices, residential)
        delivery_locations = [
            (40.7589, -73.9851, "Times Square Store"),
            (40.7505, -73.9934, "Midtown Office"),
            (40.6782, -73.9442, "Brooklyn Heights"),
            (40.7614, -73.9776, "Upper East Side"),
            (40.7831, -73.9712, "Upper West Side"),
            (40.7282, -73.7949, "Flushing Meadows"),
            (40.8448, -73.8648, "Riverdale"),
            (40.5795, -74.1502, "St. George Terminal")
        ]

        load_descriptions = [
            "Electronics shipment", "Medical supplies", "Office furniture",
            "Retail merchandise", "Food delivery", "Construction materials",
            "Pharmaceutical products", "Automotive parts", "Textiles",
            "Industrial equipment", "Consumer goods", "Fresh produce"
        ]

        for i in range(count):
            pickup_lat, pickup_lng, pickup_name = random.choice(pickup_locations)
            delivery_lat, delivery_lng, delivery_name = random.choice(delivery_locations)
            
            # Add variation to locations
            pickup_lat += random.uniform(-0.01, 0.01)
            pickup_lng += random.uniform(-0.01, 0.01)
            delivery_lat += random.uniform(-0.01, 0.01)
            delivery_lng += random.uniform(-0.01, 0.01)

            priority = random.choices(
                list(LoadPriority),
                weights=[0.2, 0.5, 0.2, 0.08, 0.02]  # Most normal, few critical
            )[0]

            # Set delivery deadline based on priority
            now = datetime.utcnow()
            if priority == LoadPriority.CRITICAL:
                deadline = now + timedelta(hours=random.uniform(2, 6))
            elif priority == LoadPriority.URGENT:
                deadline = now + timedelta(hours=random.uniform(4, 12))
            elif priority == LoadPriority.HIGH:
                deadline = now + timedelta(hours=random.uniform(8, 24))
            else:
                deadline = now + timedelta(days=random.uniform(1, 3))

            load = Load(
                id=f"LOAD-{i+1:03d}",
                description=random.choice(load_descriptions),
                weight_kg=random.uniform(500, 8000),
                volume_m3=random.uniform(1, 15),
                priority=priority,
                pickup_location=Location(
                    latitude=pickup_lat, 
                    longitude=pickup_lng,
                    name=pickup_name
                ),
                delivery_location=Location(
                    latitude=delivery_lat, 
                    longitude=delivery_lng,
                    name=delivery_name
                ),
                delivery_deadline=deadline
            )
            loads.append(load)

        return loads

    def _generate_realistic_traffic(self) -> List[TrafficCondition]:
        """Generate realistic traffic conditions for NYC area."""
        traffic_conditions = []
        
        # Major NYC routes with typical traffic patterns
        routes = [
            ("I-95-North", TrafficLevel.HEAVY, 35),
            ("I-95-South", TrafficLevel.MODERATE, 45),
            ("FDR-Drive", TrafficLevel.HEAVY, 25),
            ("West-Side-Highway", TrafficLevel.MODERATE, 40),
            ("Brooklyn-Bridge", TrafficLevel.STANDSTILL, 15),
            ("Manhattan-Bridge", TrafficLevel.HEAVY, 20),
            ("Williamsburg-Bridge", TrafficLevel.MODERATE, 35),
            ("Queens-Midtown-Tunnel", TrafficLevel.HEAVY, 30),
            ("Lincoln-Tunnel", TrafficLevel.STANDSTILL, 10),
            ("Holland-Tunnel", TrafficLevel.HEAVY, 25),
            ("BQE-Brooklyn", TrafficLevel.MODERATE, 40),
            ("LIE-Queens", TrafficLevel.HEAVY, 30)
        ]

        for route_name, level, speed in routes:
            # Add some randomness to current conditions
            current_level = random.choices(
                [TrafficLevel.FREE_FLOW, TrafficLevel.LIGHT, TrafficLevel.MODERATE, 
                 TrafficLevel.HEAVY, TrafficLevel.STANDSTILL],
                weights=[0.1, 0.2, 0.3, 0.3, 0.1]
            )[0]
            
            current_speed = speed + random.uniform(-10, 10)
            current_speed = max(5, current_speed)  # Minimum 5 km/h

            delay_minutes = {
                TrafficLevel.FREE_FLOW: 0,
                TrafficLevel.LIGHT: random.uniform(5, 10),
                TrafficLevel.MODERATE: random.uniform(10, 20),
                TrafficLevel.HEAVY: random.uniform(20, 40),
                TrafficLevel.STANDSTILL: random.uniform(40, 90)
            }[current_level]

            # Add incidents for some segments
            incident = None
            if random.random() < 0.2:  # 20% chance of incident
                incidents = [
                    "Construction work", "Accident reported", "Lane closure",
                    "Disabled vehicle", "Police activity", "Road maintenance"
                ]
                incident = random.choice(incidents)

            traffic_condition = TrafficCondition(
                segment_id=route_name,
                level=current_level,
                speed_kmh=current_speed,
                delay_minutes=delay_minutes,
                incident_description=incident
            )
            traffic_conditions.append(traffic_condition)

        return traffic_conditions

    def _perform_initial_assignments(self):
        """Perform initial load assignments using our algorithm."""
        available_trucks = [t for t in state_manager.trucks if t.status == TruckStatus.IDLE]
        unassigned_loads = [l for l in state_manager.loads if not l.assigned_truck_id]

        if not available_trucks or not unassigned_loads:
            return

        # Use our load assignment engine
        solution = self.load_assignment_engine.assign_loads_to_trucks(
            available_trucks, unassigned_loads, strategy="priority_first"
        )

        # Apply assignments
        for assignment in solution.assignments:
            # Find and update the load
            for load in state_manager.loads:
                if load.id == assignment.load_id:
                    load.assigned_truck_id = assignment.truck_id
                    break
            
            # Update truck status
            for truck in state_manager.trucks:
                if truck.id == assignment.truck_id:
                    truck.status = TruckStatus.EN_ROUTE
                    truck.current_load_id = assignment.load_id
                    break

        logger.info(
            "Initial assignments completed",
            assignments=len(solution.assignments),
            unassigned=len(solution.unassigned_loads),
            utilization=f"{solution.utilization_rate:.1%}"
        )

    def _generate_initial_routes(self):
        """Generate optimized routes for trucks with assigned loads."""
        for truck in state_manager.trucks:
            if truck.current_load_id and truck.status == TruckStatus.EN_ROUTE:
                # Find the assigned load
                assigned_load = next(
                    (l for l in state_manager.loads if l.id == truck.current_load_id), 
                    None
                )
                
                if assigned_load and truck.current_location:
                    # Generate optimized route
                    optimized_route = self.route_optimizer.optimize_route(
                        truck, [assigned_load], state_manager.traffic_conditions
                    )
                    
                    # Create route object
                    route = Route(
                        id=f"ROUTE-{truck.id}-{datetime.utcnow().strftime('%H%M%S')}",
                        truck_id=truck.id,
                        origin=truck.current_location,
                        destination=assigned_load.delivery_location,
                        estimated_distance_km=optimized_route.total_distance_km,
                        estimated_duration_minutes=optimized_route.total_time_minutes,
                        estimated_fuel_consumption_liters=optimized_route.fuel_consumption_liters,
                        started_at=datetime.utcnow()
                    )
                    state_manager.routes.append(route)

    async def start_background_updates(self, broadcast_callback: Callable = None):
        """Start background simulation updates."""
        if self._running:
            return

        self._running = True
        self._broadcast_callback = broadcast_callback
        self._background_task = asyncio.create_task(self._simulation_loop())
        logger.info("Enhanced background simulation started")

    async def stop_background_updates(self):
        """Stop background simulation updates."""
        self._running = False
        if self._background_task:
            self._background_task.cancel()
            try:
                await self._background_task
            except asyncio.CancelledError:
                pass
        logger.info("Enhanced background simulation stopped")

    async def _simulation_loop(self):
        """Main simulation loop with realistic updates."""
        try:
            while self._running:
                # Update truck positions and status
                self._update_truck_positions()
                
                # Update traffic conditions
                self._update_traffic_conditions()
                
                # Check for completed deliveries
                self._check_delivery_completions()
                
                # Generate new loads occasionally
                if random.random() < 0.1:  # 10% chance per cycle
                    self._generate_new_load()
                
                # Broadcast updates
                if self._broadcast_callback:
                    await self._broadcast_fleet_update()
                
                # Wait before next update
                await asyncio.sleep(5)  # Update every 5 seconds
                
        except asyncio.CancelledError:
            logger.info("Simulation loop cancelled")
        except Exception as e:
            logger.error("Simulation loop error", error=str(e))

    def _update_truck_positions(self):
        """Update truck positions based on their routes."""
        for truck in state_manager.trucks:
            if truck.status == TruckStatus.EN_ROUTE and truck.current_location:
                # Find truck's route
                route = next(
                    (r for r in state_manager.routes if r.truck_id == truck.id and not r.completed_at),
                    None
                )
                
                if route:
                    # Simulate movement towards destination
                    self._simulate_truck_movement(truck, route)

    def _simulate_truck_movement(self, truck: Truck, route: Route):
        """Simulate realistic truck movement."""
        if not truck.current_location:
            return

        # Calculate movement based on time elapsed and traffic
        time_elapsed = (datetime.utcnow() - route.started_at).total_seconds() / 3600  # hours
        
        # Get traffic factor for current area
        traffic_factor = self._get_current_traffic_factor(truck.current_location)
        effective_speed = 50.0 / traffic_factor  # Base speed 50 km/h
        
        # Calculate distance that should have been traveled
        distance_traveled = effective_speed * time_elapsed
        
        # Move truck towards destination
        if distance_traveled < route.estimated_distance_km:
            # Calculate new position (simplified linear interpolation)
            progress = distance_traveled / route.estimated_distance_km
            
            start_lat = route.origin.latitude
            start_lng = route.origin.longitude
            end_lat = route.destination.latitude
            end_lng = route.destination.longitude
            
            new_lat = start_lat + (end_lat - start_lat) * progress
            new_lng = start_lng + (end_lng - start_lng) * progress
            
            truck.current_location = Location(latitude=new_lat, longitude=new_lng)
            
            # Update fuel level
            fuel_consumed = distance_traveled * 0.3  # L/km
            fuel_percent_consumed = (fuel_consumed / 200) * 100  # Assume 200L tank
            truck.fuel_level_percent = max(0, truck.fuel_level_percent - fuel_percent_consumed)
            
            # Create GPS reading
            gps_reading = GPSReading(
                truck_id=truck.id,
                location=truck.current_location,
                speed_kmh=effective_speed + random.uniform(-5, 5),
                heading=self._calculate_heading(route.origin, route.destination)
            )
            state_manager.gps_readings.append(gps_reading)
            
            # Keep only recent GPS readings
            state_manager.gps_readings = state_manager.gps_readings[-100:]

    def _get_current_traffic_factor(self, location: Location) -> float:
        """Get traffic factor for current location."""
        # Simple implementation - use average traffic factor
        if state_manager.traffic_conditions:
            factors = [tc.delay_factor for tc in state_manager.traffic_conditions]
            return sum(factors) / len(factors)
        return 1.0

    def _calculate_heading(self, start: Location, end: Location) -> float:
        """Calculate compass heading from start to end location."""
        import math
        
        lat1, lng1 = math.radians(start.latitude), math.radians(start.longitude)
        lat2, lng2 = math.radians(end.latitude), math.radians(end.longitude)
        
        dlng = lng2 - lng1
        
        y = math.sin(dlng) * math.cos(lat2)
        x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(dlng)
        
        heading = math.atan2(y, x)
        heading = math.degrees(heading)
        heading = (heading + 360) % 360
        
        return heading

    def _update_traffic_conditions(self):
        """Update traffic conditions with realistic changes."""
        for traffic in state_manager.traffic_conditions:
            # Randomly change traffic levels
            if random.random() < 0.05:  # 5% chance per update
                levels = list(TrafficLevel)
                current_idx = levels.index(traffic.level)
                
                # Bias towards adjacent levels
                if current_idx > 0 and random.random() < 0.5:
                    traffic.level = levels[current_idx - 1]
                elif current_idx < len(levels) - 1 and random.random() < 0.5:
                    traffic.level = levels[current_idx + 1]
                
                # Update speed accordingly
                speed_ranges = {
                    TrafficLevel.FREE_FLOW: (60, 80),
                    TrafficLevel.LIGHT: (45, 60),
                    TrafficLevel.MODERATE: (30, 45),
                    TrafficLevel.HEAVY: (15, 30),
                    TrafficLevel.STANDSTILL: (0, 15)
                }
                min_speed, max_speed = speed_ranges[traffic.level]
                traffic.speed_kmh = random.uniform(min_speed, max_speed)

    def _check_delivery_completions(self):
        """Check for completed deliveries and update status."""
        for truck in state_manager.trucks:
            if truck.status == TruckStatus.EN_ROUTE and truck.current_load_id:
                # Find the route
                route = next(
                    (r for r in state_manager.routes if r.truck_id == truck.id and not r.completed_at),
                    None
                )
                
                if route and truck.current_location:
                    # Check if truck reached destination
                    distance_to_dest = truck.current_location.distance_to(route.destination)
                    
                    if distance_to_dest < 0.5:  # Within 500m of destination
                        # Complete the delivery
                        self._complete_delivery(truck, route)

    def _complete_delivery(self, truck: Truck, route: Route):
        """Complete a delivery and update all related objects."""
        # Update route
        route.completed_at = datetime.utcnow()
        route.actual_distance_km = route.estimated_distance_km  # Simplified
        
        # Update load
        for load in state_manager.loads:
            if load.id == truck.current_load_id:
                load.delivered_at = datetime.utcnow()
                break
        
        # Update truck
        truck.status = TruckStatus.IDLE
        truck.current_load_id = None
        truck.total_deliveries += 1
        truck.total_distance_km += route.estimated_distance_km
        
        logger.info(
            "Delivery completed",
            truck_id=truck.id,
            load_id=truck.current_load_id,
            distance=route.estimated_distance_km
        )

    def _generate_new_load(self):
        """Generate a new load during simulation."""
        new_loads = self._generate_realistic_loads(1)
        if new_loads:
            state_manager.loads.extend(new_loads)
            logger.info("New load generated", load_id=new_loads[0].id)

    async def _broadcast_fleet_update(self):
        """Broadcast fleet updates via WebSocket."""
        if not self._broadcast_callback:
            return

        # Prepare update data
        update_data = {
            "type": "fleet_update",
            "data": {
                "trucks": [t.model_dump() for t in state_manager.trucks],
                "loads": [l.model_dump() for l in state_manager.loads],
                "traffic_conditions": [tc.model_dump() for tc in state_manager.traffic_conditions],
                "active_routes": [r.model_dump() for r in state_manager.routes if not r.completed_at],
                "timestamp": datetime.utcnow().isoformat()
            },
            "source": "enhanced_simulation"
        }

        try:
            await self._broadcast_callback(update_data)
        except Exception as e:
            logger.error("Failed to broadcast update", error=str(e))


# Global instance
enhanced_simulation_service = EnhancedSimulationService()