"""
Data collectors for the perception layer.

These collectors gather data from various sources:
- GPS data from trucks
- Traffic conditions from APIs
- Load manifests from systems
"""
import asyncio
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Optional
import structlog

from src.models import (
    GPSReading, Location, Truck, TruckStatus,
    TrafficCondition, TrafficLevel, Load, LoadPriority
)

logger = structlog.get_logger(__name__)


class BaseCollector(ABC):
    """Base class for all data collectors."""

    def __init__(self, name: str):
        self.name = name
        self.last_collection: Optional[datetime] = None
        self.collection_count = 0

    @abstractmethod
    async def collect(self) -> list[Any]:
        """Collect data from the source."""
        pass

    def _update_stats(self):
        """Update collection statistics."""
        self.last_collection = datetime.utcnow()
        self.collection_count += 1


class GPSCollector(BaseCollector):
    """
    Collects GPS readings from truck fleet.

    In production, this would connect to:
    - Fleet management APIs
    - IoT device endpoints
    - Telematics providers
    """

    def __init__(self, trucks: list[Truck] = None, simulate: bool = True):
        super().__init__("GPSCollector")
        self.trucks = trucks or []
        self.simulate = simulate
        # Simulated movement parameters
        self._last_positions: dict[str, Location] = {}

    async def collect(self) -> list[GPSReading]:
        """Collect GPS readings for all trucks."""
        if self.simulate:
            readings = await self._simulate_gps_readings()
        else:
            readings = await self._fetch_real_gps_data()

        self._update_stats()
        logger.info(
            "GPS data collected",
            collector=self.name,
            readings=len(readings),
            trucks=len(self.trucks)
        )
        return readings

    async def _simulate_gps_readings(self) -> list[GPSReading]:
        """Generate simulated GPS readings for testing."""
        readings = []

        for truck in self.trucks:
            # Get or initialize last position
            if truck.id not in self._last_positions:
                if truck.current_location:
                    self._last_positions[truck.id] = truck.current_location
                else:
                    # Default to NYC area
                    self._last_positions[truck.id] = Location(
                        latitude=40.7128 + random.uniform(-0.1, 0.1),
                        longitude=-74.0060 + random.uniform(-0.1, 0.1)
                    )

            last_pos = self._last_positions[truck.id]

            # Simulate movement based on status
            if truck.status == TruckStatus.EN_ROUTE:
                # Moving truck - add some movement
                speed = random.uniform(30, 80)  # km/h
                heading = random.uniform(0, 360)

                # Calculate new position (simplified)
                # ~0.01 degree ≈ 1.1 km at mid-latitudes
                movement = (speed / 3600) * 30 / 111  # 30 second movement in degrees
                new_lat = last_pos.latitude + movement * random.uniform(-1, 1)
                new_lng = last_pos.longitude + movement * random.uniform(-1, 1)

                new_location = Location(
                    latitude=max(-90, min(90, new_lat)),
                    longitude=max(-180, min(180, new_lng))
                )
            else:
                # Stationary truck
                speed = 0
                heading = 0
                new_location = last_pos

            self._last_positions[truck.id] = new_location

            reading = GPSReading(
                truck_id=truck.id,
                timestamp=datetime.utcnow(),
                location=new_location,
                speed_kmh=speed,
                heading=heading,
                accuracy_meters=random.uniform(3, 15)
            )
            readings.append(reading)

            # Small delay to simulate async collection
            await asyncio.sleep(0.01)

        return readings

    async def _fetch_real_gps_data(self) -> list[GPSReading]:
        """Fetch real GPS data from fleet API."""
        # Placeholder for real API integration
        raise NotImplementedError("Real GPS API integration not implemented")

    def set_trucks(self, trucks: list[Truck]):
        """Update the list of trucks to monitor."""
        self.trucks = trucks


class TrafficCollector(BaseCollector):
    """
    Collects traffic condition data.

    In production, this would connect to:
    - Google Maps Traffic API
    - HERE Traffic API
    - Local DOT feeds
    """

    def __init__(self, route_segments: list[str] = None, simulate: bool = True):
        super().__init__("TrafficCollector")
        self.route_segments = route_segments or []
        self.simulate = simulate
        # Simulate traffic patterns
        self._incident_probability = 0.1

    async def collect(self) -> list[TrafficCondition]:
        """Collect traffic conditions for monitored segments."""
        if self.simulate:
            conditions = await self._simulate_traffic_conditions()
        else:
            conditions = await self._fetch_real_traffic_data()

        self._update_stats()
        logger.info(
            "Traffic data collected",
            collector=self.name,
            segments=len(conditions),
            incidents=sum(1 for c in conditions if c.incident_description)
        )
        return conditions

    async def _simulate_traffic_conditions(self) -> list[TrafficCondition]:
        """Generate simulated traffic conditions."""
        conditions = []

        # Default segments if none provided
        segments = self.route_segments or [
            "SEG-I95-NB-1", "SEG-I95-NB-2", "SEG-I95-SB-1",
            "SEG-9A-NB-1", "SEG-9A-SB-1",
            "SEG-LOCAL-1", "SEG-LOCAL-2"
        ]

        for segment_id in segments:
            # Simulate traffic level
            level_weights = {
                TrafficLevel.FREE_FLOW: 0.3,
                TrafficLevel.LIGHT: 0.3,
                TrafficLevel.MODERATE: 0.25,
                TrafficLevel.HEAVY: 0.12,
                TrafficLevel.STANDSTILL: 0.03,
            }

            level = random.choices(
                list(level_weights.keys()),
                weights=list(level_weights.values())
            )[0]

            # Calculate speed based on level
            base_speed = 65  # km/h
            speed_factors = {
                TrafficLevel.FREE_FLOW: 1.0,
                TrafficLevel.LIGHT: 0.85,
                TrafficLevel.MODERATE: 0.65,
                TrafficLevel.HEAVY: 0.4,
                TrafficLevel.STANDSTILL: 0.1,
            }
            speed = base_speed * speed_factors[level]

            # Calculate delay
            delay = 0
            if level in [TrafficLevel.HEAVY, TrafficLevel.STANDSTILL]:
                delay = random.uniform(5, 30)

            # Simulate incidents
            incident = None
            if random.random() < self._incident_probability:
                incidents = [
                    "Vehicle breakdown on shoulder",
                    "Multi-vehicle accident, lane blocked",
                    "Road construction",
                    "Emergency vehicle activity",
                    "Weather-related slowdown",
                ]
                incident = random.choice(incidents)
                level = TrafficLevel.HEAVY
                delay = random.uniform(10, 45)

            condition = TrafficCondition(
                segment_id=segment_id,
                level=level,
                speed_kmh=speed,
                delay_minutes=delay,
                incident_description=incident,
                timestamp=datetime.utcnow()
            )
            conditions.append(condition)

        return conditions

    async def _fetch_real_traffic_data(self) -> list[TrafficCondition]:
        """Fetch real traffic data from API."""
        raise NotImplementedError("Real Traffic API integration not implemented")

    def set_route_segments(self, segments: list[str]):
        """Update the list of route segments to monitor."""
        self.route_segments = segments


class LoadCollector(BaseCollector):
    """
    Collects load/shipment manifest data.

    In production, this would connect to:
    - Warehouse Management System (WMS)
    - Order Management System (OMS)
    - Customer APIs
    """

    def __init__(self, simulate: bool = True):
        super().__init__("LoadCollector")
        self.simulate = simulate
        self._load_counter = 0

    async def collect(self) -> list[Load]:
        """Collect current load manifests."""
        if self.simulate:
            loads = await self._simulate_loads()
        else:
            loads = await self._fetch_real_load_data()

        self._update_stats()
        logger.info(
            "Load data collected",
            collector=self.name,
            loads=len(loads),
            urgent=sum(1 for l in loads if l.priority in [LoadPriority.URGENT, LoadPriority.CRITICAL])
        )
        return loads

    async def _simulate_loads(self) -> list[Load]:
        """Generate simulated load data."""
        loads = []

        # Generate 3-8 loads
        num_loads = random.randint(3, 8)

        for i in range(num_loads):
            self._load_counter += 1
            load_id = f"LOAD-{datetime.utcnow().strftime('%Y%m%d')}-{self._load_counter:04d}"

            # Random locations in NYC area
            pickup = Location(
                latitude=40.7128 + random.uniform(-0.15, 0.15),
                longitude=-74.0060 + random.uniform(-0.15, 0.15),
                name=f"Warehouse {random.choice(['A', 'B', 'C', 'D'])}"
            )

            delivery = Location(
                latitude=40.7128 + random.uniform(-0.2, 0.2),
                longitude=-74.0060 + random.uniform(-0.2, 0.2),
                name=f"Customer {random.randint(100, 999)}"
            )

            # Random priority with weights
            priority = random.choices(
                [LoadPriority.LOW, LoadPriority.NORMAL, LoadPriority.HIGH,
                 LoadPriority.URGENT, LoadPriority.CRITICAL],
                weights=[0.1, 0.5, 0.25, 0.1, 0.05]
            )[0]

            # Deadline based on priority
            hours_map = {
                LoadPriority.CRITICAL: 2,
                LoadPriority.URGENT: 4,
                LoadPriority.HIGH: 8,
                LoadPriority.NORMAL: 24,
                LoadPriority.LOW: 48,
            }
            deadline = datetime.utcnow() + timedelta(hours=hours_map[priority])

            load = Load(
                id=load_id,
                description=random.choice([
                    "General merchandise",
                    "Electronics - fragile",
                    "Food products - temperature controlled",
                    "Industrial equipment",
                    "Medical supplies",
                    "Retail inventory",
                ]),
                weight_kg=random.uniform(500, 8000),
                volume_m3=random.uniform(2, 25),
                priority=priority,
                pickup_location=pickup,
                delivery_location=delivery,
                pickup_window_start=datetime.utcnow(),
                pickup_window_end=datetime.utcnow() + timedelta(hours=2),
                delivery_deadline=deadline,
            )
            loads.append(load)

        return loads

    async def _fetch_real_load_data(self) -> list[Load]:
        """Fetch real load data from WMS/OMS."""
        raise NotImplementedError("Real Load API integration not implemented")


class AggregatedCollector:
    """Aggregates data from all collectors into a unified observation."""

    def __init__(
        self,
        gps_collector: GPSCollector,
        traffic_collector: TrafficCollector,
        load_collector: LoadCollector
    ):
        self.gps_collector = gps_collector
        self.traffic_collector = traffic_collector
        self.load_collector = load_collector

    async def collect_all(self) -> dict[str, Any]:
        """Collect data from all sources concurrently."""
        # Run all collectors in parallel
        gps_task = asyncio.create_task(self.gps_collector.collect())
        traffic_task = asyncio.create_task(self.traffic_collector.collect())
        load_task = asyncio.create_task(self.load_collector.collect())

        gps_readings, traffic_conditions, loads = await asyncio.gather(
            gps_task, traffic_task, load_task
        )

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "gps_readings": gps_readings,
            "traffic_conditions": traffic_conditions,
            "loads": loads,
            "collection_stats": {
                "gps_count": len(gps_readings),
                "traffic_segments": len(traffic_conditions),
                "active_loads": len(loads),
            }
        }
