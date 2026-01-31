"""
Data preprocessor for the perception layer.

Validates, cleans, and transforms raw data into normalized formats
ready for the reasoning layer.
"""
from datetime import datetime, timedelta
from typing import Any, Optional
import structlog

from src.models import (
    GPSReading, Location, Truck, TruckStatus,
    TrafficCondition, TrafficLevel, Load, Route
)

logger = structlog.get_logger(__name__)


class DataPreprocessor:
    """
    Preprocesses and validates collected data.

    Responsibilities:
    - Validate data integrity
    - Handle missing data
    - Normalize formats
    - Detect anomalies
    - Merge data sources
    """

    def __init__(self):
        self.validation_errors: list[dict] = []
        self.anomalies_detected: list[dict] = []
        self._gps_history: dict[str, list[GPSReading]] = {}
        self._max_history_length = 100

    def preprocess_gps_readings(
        self,
        readings: list[GPSReading],
        trucks: list[Truck]
    ) -> tuple[list[GPSReading], list[Truck]]:
        """
        Preprocess GPS readings and update truck positions.

        Args:
            readings: Raw GPS readings
            trucks: Current truck states

        Returns:
            Tuple of (validated readings, updated trucks)
        """
        validated_readings = []
        truck_map = {t.id: t for t in trucks}

        for reading in readings:
            # Validate reading
            if not self._validate_gps_reading(reading):
                continue

            # Check for anomalies
            if reading.truck_id in self._gps_history:
                self._detect_gps_anomalies(reading)

            # Store in history
            if reading.truck_id not in self._gps_history:
                self._gps_history[reading.truck_id] = []
            self._gps_history[reading.truck_id].append(reading)
            if len(self._gps_history[reading.truck_id]) > self._max_history_length:
                self._gps_history[reading.truck_id].pop(0)

            validated_readings.append(reading)

            # Update truck with latest reading
            if reading.truck_id in truck_map:
                truck = truck_map[reading.truck_id]
                truck.current_location = reading.location
                truck.last_gps_reading = reading

                # Infer status from speed if en_route
                if truck.status == TruckStatus.EN_ROUTE:
                    if reading.speed_kmh < 5:
                        # Possibly stuck
                        history = self._gps_history.get(reading.truck_id, [])
                        if len(history) >= 5:
                            recent_speeds = [r.speed_kmh for r in history[-5:]]
                            if all(s < 5 for s in recent_speeds):
                                truck.status = TruckStatus.STUCK
                                self.anomalies_detected.append({
                                    "type": "truck_stuck",
                                    "truck_id": reading.truck_id,
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "details": "Truck stationary for extended period"
                                })

        updated_trucks = list(truck_map.values())
        logger.info(
            "GPS readings preprocessed",
            total=len(readings),
            validated=len(validated_readings),
            errors=len(self.validation_errors)
        )

        return validated_readings, updated_trucks

    def _validate_gps_reading(self, reading: GPSReading) -> bool:
        """Validate a single GPS reading."""
        errors = []

        # Check coordinates
        if not (-90 <= reading.location.latitude <= 90):
            errors.append(f"Invalid latitude: {reading.location.latitude}")
        if not (-180 <= reading.location.longitude <= 180):
            errors.append(f"Invalid longitude: {reading.location.longitude}")

        # Check speed
        if reading.speed_kmh < 0:
            errors.append(f"Negative speed: {reading.speed_kmh}")
        if reading.speed_kmh > 200:  # Unrealistic for trucks
            errors.append(f"Unrealistic speed: {reading.speed_kmh}")

        # Check timestamp
        if reading.timestamp > datetime.utcnow() + timedelta(minutes=5):
            errors.append("Future timestamp detected")

        if errors:
            self.validation_errors.append({
                "truck_id": reading.truck_id,
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            })
            return False

        return True

    def _detect_gps_anomalies(self, reading: GPSReading) -> None:
        """Detect anomalies in GPS data by comparing with history."""
        history = self._gps_history.get(reading.truck_id, [])
        if not history:
            return

        last_reading = history[-1]

        # Check for teleportation (impossible distance in time)
        time_diff = (reading.timestamp - last_reading.timestamp).total_seconds()
        if time_diff > 0:
            distance = last_reading.location.distance_to(reading.location)
            implied_speed = (distance / time_diff) * 3600  # km/h

            if implied_speed > 200:  # Impossible speed
                self.anomalies_detected.append({
                    "type": "teleportation",
                    "truck_id": reading.truck_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "details": f"Implied speed {implied_speed:.0f} km/h",
                    "distance_km": distance,
                    "time_seconds": time_diff
                })

        # Check for sudden speed changes
        speed_change = abs(reading.speed_kmh - last_reading.speed_kmh)
        if speed_change > 50 and time_diff < 5:  # 50 km/h change in <5 seconds
            self.anomalies_detected.append({
                "type": "sudden_speed_change",
                "truck_id": reading.truck_id,
                "timestamp": datetime.utcnow().isoformat(),
                "details": f"Speed change of {speed_change:.0f} km/h in {time_diff:.1f}s"
            })

    def preprocess_traffic_conditions(
        self,
        conditions: list[TrafficCondition],
        routes: list[Route]
    ) -> list[TrafficCondition]:
        """
        Preprocess traffic conditions and link to routes.

        Args:
            conditions: Raw traffic conditions
            routes: Active routes

        Returns:
            Validated and enriched traffic conditions
        """
        validated_conditions = []
        route_segments = self._extract_route_segments(routes)

        for condition in conditions:
            # Validate condition
            if not self._validate_traffic_condition(condition):
                continue

            # Link to affected routes
            affected = []
            for route in routes:
                if condition.segment_id in route_segments.get(route.id, []):
                    affected.append(route.id)
            condition.affected_routes = affected

            validated_conditions.append(condition)

        # Detect traffic anomalies
        self._detect_traffic_anomalies(validated_conditions)

        logger.info(
            "Traffic conditions preprocessed",
            total=len(conditions),
            validated=len(validated_conditions),
            with_incidents=sum(1 for c in validated_conditions if c.incident_description)
        )

        return validated_conditions

    def _validate_traffic_condition(self, condition: TrafficCondition) -> bool:
        """Validate a traffic condition."""
        errors = []

        if condition.speed_kmh < 0:
            errors.append(f"Negative speed: {condition.speed_kmh}")

        if condition.delay_minutes < 0:
            errors.append(f"Negative delay: {condition.delay_minutes}")

        if errors:
            self.validation_errors.append({
                "segment_id": condition.segment_id,
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            })
            return False

        return True

    def _extract_route_segments(self, routes: list[Route]) -> dict[str, list[str]]:
        """Extract segment IDs from routes (placeholder for route-segment mapping)."""
        # In production, this would use actual route-segment mapping
        # For now, return empty mapping
        return {}

    def _detect_traffic_anomalies(self, conditions: list[TrafficCondition]) -> None:
        """Detect anomalies in traffic data."""
        # Check for multiple standstill conditions (possible major incident)
        standstill_count = sum(
            1 for c in conditions if c.level == TrafficLevel.STANDSTILL
        )
        if standstill_count >= 3:
            self.anomalies_detected.append({
                "type": "major_traffic_event",
                "timestamp": datetime.utcnow().isoformat(),
                "details": f"{standstill_count} segments at standstill",
                "affected_segments": [
                    c.segment_id for c in conditions
                    if c.level == TrafficLevel.STANDSTILL
                ]
            })

    def preprocess_loads(self, loads: list[Load]) -> list[Load]:
        """
        Preprocess load manifests.

        Args:
            loads: Raw load data

        Returns:
            Validated and enriched loads
        """
        validated_loads = []

        for load in loads:
            if not self._validate_load(load):
                continue

            # Check for deadline issues
            if load.delivery_deadline:
                time_to_deadline = (load.delivery_deadline - datetime.utcnow()).total_seconds() / 3600
                if time_to_deadline < 1:
                    self.anomalies_detected.append({
                        "type": "imminent_deadline",
                        "load_id": load.id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": f"Deadline in {time_to_deadline:.1f} hours",
                        "priority": load.priority.value
                    })

            validated_loads.append(load)

        logger.info(
            "Loads preprocessed",
            total=len(loads),
            validated=len(validated_loads)
        )

        return validated_loads

    def _validate_load(self, load: Load) -> bool:
        """Validate a load."""
        errors = []

        if load.weight_kg <= 0:
            errors.append(f"Invalid weight: {load.weight_kg}")

        if load.volume_m3 is not None and load.volume_m3 <= 0:
            errors.append(f"Invalid volume: {load.volume_m3}")

        if errors:
            self.validation_errors.append({
                "load_id": load.id,
                "errors": errors,
                "timestamp": datetime.utcnow().isoformat()
            })
            return False

        return True

    def get_preprocessing_summary(self) -> dict[str, Any]:
        """Get summary of preprocessing results."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "validation_errors": len(self.validation_errors),
            "anomalies_detected": len(self.anomalies_detected),
            "recent_errors": self.validation_errors[-10:],
            "recent_anomalies": self.anomalies_detected[-10:],
        }

    def clear_history(self) -> None:
        """Clear preprocessing history and caches."""
        self._gps_history.clear()
        self.validation_errors.clear()
        self.anomalies_detected.clear()
