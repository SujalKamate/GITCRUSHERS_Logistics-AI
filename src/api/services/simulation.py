"""
Simulation service for the Logistics AI Dashboard.
Generates demo data and simulates real-time updates.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Optional
from src.models import (
    Truck, Route, Load, TrafficCondition, Location, GPSReading, RoutePoint,
    Decision, TruckStatus, TrafficLevel, LoadPriority, ActionType, ControlLoopPhase
)
from .state_manager import state_manager


# NYC area coordinates for simulation
NYC_LOCATIONS = [
    {"name": "Times Square", "lat": 40.7580, "lng": -73.9855},
    {"name": "Chelsea Market", "lat": 40.7424, "lng": -74.0061},
    {"name": "Brooklyn Bridge", "lat": 40.7061, "lng": -73.9969},
    {"name": "Central Park", "lat": 40.7829, "lng": -73.9654},
    {"name": "Empire State", "lat": 40.7484, "lng": -73.9857},
    {"name": "JFK Airport", "lat": 40.6413, "lng": -73.7781},
    {"name": "LaGuardia", "lat": 40.7769, "lng": -73.8740},
    {"name": "Newark NJ", "lat": 40.6895, "lng": -74.1745},
    {"name": "Bronx Terminal", "lat": 40.8268, "lng": -73.9260},
    {"name": "Staten Island", "lat": 40.5795, "lng": -74.1502},
    {"name": "Hoboken NJ", "lat": 40.7440, "lng": -74.0324},
    {"name": "Queens Depot", "lat": 40.7282, "lng": -73.7949},
]

TRUCK_NAMES = [
    "Alpha Express", "Beta Logistics", "Gamma Transport", "Delta Freight",
    "Echo Shipping", "Foxtrot Cargo", "Golf Haulers", "Hotel Transit",
    "India Movers", "Juliet Fleet", "Kilo Trucking", "Lima Lines"
]


class SimulationService:
    """Service for generating and updating simulation data."""

    def __init__(self):
        self._update_task: Optional[asyncio.Task] = None
        self._decision_task: Optional[asyncio.Task] = None

    def generate_initial_data(self, num_trucks: int = 10):
        """Generate initial fleet data."""
        state_manager.reset()

        # Generate trucks
        statuses = [
            TruckStatus.EN_ROUTE, TruckStatus.EN_ROUTE, TruckStatus.EN_ROUTE,
            TruckStatus.EN_ROUTE, TruckStatus.LOADING, TruckStatus.UNLOADING,
            TruckStatus.IDLE, TruckStatus.IDLE, TruckStatus.DELAYED, TruckStatus.STUCK
        ]

        for i in range(min(num_trucks, len(TRUCK_NAMES))):
            loc_data = random.choice(NYC_LOCATIONS)
            location = Location(
                latitude=loc_data["lat"] + random.uniform(-0.01, 0.01),
                longitude=loc_data["lng"] + random.uniform(-0.01, 0.01),
                address=f"{loc_data['name']}, New York, NY",
                name=loc_data["name"]
            )

            status = statuses[i % len(statuses)]
            truck = Truck(
                id=f"TRK-{i+1:03d}",
                name=TRUCK_NAMES[i],
                status=status,
                current_location=location,
                driver_id=f"DRV-{i+1:03d}",
                capacity_kg=random.choice([10000, 12000, 15000, 18000, 20000]),
                fuel_level_percent=random.uniform(20, 100),
                current_load_id=f"LOAD-{i+1:03d}" if status in [TruckStatus.EN_ROUTE, TruckStatus.DELAYED] else None,
                last_gps_reading=GPSReading(
                    truck_id=f"TRK-{i+1:03d}",
                    timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 10)),
                    location=location,
                    speed_kmh=random.uniform(0, 65) if status == TruckStatus.EN_ROUTE else 0,
                    heading=random.uniform(0, 360),
                    accuracy_meters=random.uniform(3, 15)
                ),
                total_distance_km=random.uniform(5000, 25000),
                total_deliveries=random.randint(30, 150)
            )
            state_manager.trucks.append(truck)

        # Generate loads
        for i in range(15):
            pickup = random.choice(NYC_LOCATIONS)
            delivery = random.choice([l for l in NYC_LOCATIONS if l != pickup])

            load = Load(
                id=f"LOAD-{i+1:03d}",
                description=f"Cargo shipment #{i+1:03d}",
                weight_kg=random.uniform(500, 8000),
                volume_m3=random.uniform(5, 50),
                priority=random.choice(list(LoadPriority)),
                pickup_location=Location(
                    latitude=pickup["lat"],
                    longitude=pickup["lng"],
                    address=f"{pickup['name']}, New York, NY"
                ),
                delivery_location=Location(
                    latitude=delivery["lat"],
                    longitude=delivery["lng"],
                    address=f"{delivery['name']}, New York, NY"
                ),
                pickup_window_start=datetime.utcnow() + timedelta(hours=random.randint(0, 4)),
                pickup_window_end=datetime.utcnow() + timedelta(hours=random.randint(5, 8)),
                delivery_deadline=datetime.utcnow() + timedelta(hours=random.randint(12, 48)),
                assigned_truck_id=f"TRK-{i+1:03d}" if i < 5 else None
            )
            state_manager.loads.append(load)

        # Generate traffic conditions
        traffic_segments = [
            ("I-95 North", TrafficLevel.HEAVY),
            ("I-495 West", TrafficLevel.MODERATE),
            ("Route 1 South", TrafficLevel.LIGHT),
            ("Holland Tunnel", TrafficLevel.STANDSTILL),
            ("Lincoln Tunnel", TrafficLevel.HEAVY),
            ("GW Bridge", TrafficLevel.MODERATE),
        ]

        for segment_name, level in traffic_segments:
            traffic = TrafficCondition(
                segment_id=segment_name.lower().replace(" ", "-"),
                level=level,
                speed_kmh=random.uniform(5, 80),
                delay_minutes=random.uniform(0, 30),
                incident_description="Heavy traffic due to construction" if level == TrafficLevel.HEAVY else None,
                affected_routes=[f"ROUTE-{random.randint(1,5):03d}"],
                timestamp=datetime.utcnow()
            )
            state_manager.traffic_conditions.append(traffic)

        # Initialize control loop state
        state_manager.total_cycles = random.randint(1000, 2000)
        state_manager.cycle_durations = [random.uniform(800, 1200) for _ in range(50)]

    async def start_background_updates(self, websocket_broadcast=None):
        """Start background tasks for simulation updates."""
        self._update_task = asyncio.create_task(
            self._position_update_loop(websocket_broadcast)
        )
        self._decision_task = asyncio.create_task(
            self._decision_generation_loop(websocket_broadcast)
        )

    async def stop_background_updates(self):
        """Stop background update tasks."""
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass

        if self._decision_task:
            self._decision_task.cancel()
            try:
                await self._decision_task
            except asyncio.CancelledError:
                pass

    async def _position_update_loop(self, broadcast=None):
        """Update truck positions periodically."""
        while True:
            try:
                await asyncio.sleep(5)  # Update every 5 seconds

                for truck in state_manager.trucks:
                    if truck.status == TruckStatus.EN_ROUTE and truck.current_location:
                        # Small random movement
                        lat_change = random.uniform(-0.002, 0.002)
                        lng_change = random.uniform(-0.002, 0.002)

                        truck.current_location.latitude += lat_change
                        truck.current_location.longitude += lng_change

                        truck.last_gps_reading = GPSReading(
                            truck_id=truck.id,
                            timestamp=datetime.utcnow(),
                            location=truck.current_location,
                            speed_kmh=random.uniform(30, 70),
                            heading=random.uniform(0, 360),
                            accuracy_meters=random.uniform(3, 10)
                        )

                        # Broadcast update via WebSocket
                        if broadcast:
                            await broadcast({
                                "type": "truck_location_update",
                                "data": {
                                    "truck_id": truck.id,
                                    "location": {
                                        "latitude": truck.current_location.latitude,
                                        "longitude": truck.current_location.longitude
                                    },
                                    "speed_kmh": truck.last_gps_reading.speed_kmh,
                                    "heading": truck.last_gps_reading.heading,
                                    "timestamp": truck.last_gps_reading.timestamp.isoformat()
                                },
                                "timestamp": datetime.utcnow().isoformat(),
                                "source": "fleet_manager"
                            })

                # Update control loop phase if running
                if state_manager.control_loop_running:
                    state_manager.advance_phase()
                    state_manager.record_cycle_duration(random.uniform(800, 1200))

                    if broadcast:
                        await broadcast({
                            "type": "control_loop_update",
                            "data": {
                                "cycle_id": state_manager.cycle_id,
                                "phase": state_manager.current_phase.value,
                                "progress_percent": (list(ControlLoopPhase).index(state_manager.current_phase) + 1) / len(ControlLoopPhase) * 100,
                                "issues_detected": len([t for t in state_manager.trucks if t.status in [TruckStatus.STUCK, TruckStatus.DELAYED]]),
                                "decisions_pending": len(state_manager.pending_decisions)
                            },
                            "timestamp": datetime.utcnow().isoformat(),
                            "source": "control_loop"
                        })

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in position update loop: {e}")
                await asyncio.sleep(1)

    async def _decision_generation_loop(self, broadcast=None):
        """Generate sample decisions periodically."""
        decision_counter = 0

        while True:
            try:
                await asyncio.sleep(random.uniform(8, 15))  # Random interval

                if not state_manager.control_loop_running:
                    continue

                decision_counter += 1
                action_type = random.choice(list(ActionType))
                truck = random.choice(state_manager.trucks) if state_manager.trucks else None

                decision = Decision(
                    id=f"DEC-{int(datetime.utcnow().timestamp())}-{decision_counter}",
                    scenario_id=f"SCN-{decision_counter:03d}",
                    action_type=action_type,
                    parameters={
                        "truck_id": truck.id if truck else None,
                        "reason": random.choice([
                            "Traffic optimization",
                            "Fuel efficiency",
                            "Load balancing",
                            "Schedule adjustment",
                            "Route improvement"
                        ])
                    },
                    score=random.uniform(0.7, 0.99),
                    confidence=random.uniform(0.75, 0.98),
                    rationale=f"AI detected opportunity for {action_type.value} optimization",
                    llm_verified=random.choice([True, True, False]),
                    decided_at=datetime.utcnow()
                )

                # Auto-approve high confidence decisions
                if decision.confidence > 0.9 and decision.llm_verified:
                    decision.human_approved = True
                    state_manager.approved_decisions.append(decision)
                else:
                    state_manager.add_pending_decision(decision)

                if broadcast:
                    await broadcast({
                        "type": "decision_pending",
                        "data": {
                            "decision_id": decision.id,
                            "action_type": decision.action_type.value,
                            "description": decision.rationale,
                            "confidence": decision.confidence,
                            "requires_approval": not decision.human_approved,
                            "auto_execute_in_seconds": 30 if decision.llm_verified else None
                        },
                        "timestamp": datetime.utcnow().isoformat(),
                        "source": "decision_engine"
                    })

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in decision generation loop: {e}")
                await asyncio.sleep(1)


# Global singleton instance
simulation_service = SimulationService()
