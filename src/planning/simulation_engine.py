"""
Simulation engine for logistics planning using SymPy models.

Provides simulation capabilities for:
- Route simulation with traffic
- Fleet movement simulation
- Scenario outcome prediction
"""
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
import structlog

from src.models import (
    Truck, Route, Load, TrafficCondition, TruckStatus,
    Location, Scenario
)
from src.planning.sympy_models import SymbolicModels

logger = structlog.get_logger(__name__)


class SimulationEngine:
    """
    Simulation engine for logistics scenarios.

    Uses SymPy symbolic models for calculations and provides
    simulation of truck movements, routes, and logistics operations.
    """

    def __init__(self):
        """Initialize the simulation engine."""
        self.models = SymbolicModels()

        # Simulation parameters
        self.default_speed_kmh = 60.0
        self.default_fuel_rate = 0.3  # L/km
        self.fuel_price = 1.50  # $/L
        self.driver_rate = 25.0  # $/hour
        self.vehicle_rate = 10.0  # $/hour

        logger.info("Simulation engine initialized")

    def simulate_route(
        self,
        origin: Location,
        destination: Location,
        traffic_conditions: List[TrafficCondition] = None,
        truck: Truck = None,
        load: Load = None,
    ) -> Dict[str, Any]:
        """
        Simulate traveling a route with given conditions.

        Args:
            origin: Starting location
            destination: End location
            traffic_conditions: Traffic affecting the route
            truck: Truck to simulate (optional)
            load: Load being carried (optional)

        Returns:
            Simulation results dictionary
        """
        # Calculate base distance
        distance_km = origin.distance_to(destination)

        # Determine effective speed considering traffic
        base_speed = self.default_speed_kmh
        traffic_factor = 1.0

        if traffic_conditions:
            # Average traffic factor from conditions
            factors = [tc.delay_factor for tc in traffic_conditions]
            if factors:
                traffic_factor = sum(factors) / len(factors)

        effective_speed = base_speed / traffic_factor

        # Calculate time
        time_hours = distance_km / effective_speed
        time_minutes = time_hours * 60

        # Calculate fuel consumption
        fuel_rate = self.default_fuel_rate
        if load:
            # Adjust for load weight
            weight_factor = 0.00002  # Additional L/km per kg
            fuel_rate += weight_factor * load.weight_kg

        fuel_liters = fuel_rate * distance_km

        # Calculate cost
        fuel_cost = fuel_liters * self.fuel_price
        time_cost = time_hours * (self.driver_rate + self.vehicle_rate)
        total_cost = fuel_cost + time_cost

        # Check fuel sufficiency
        fuel_sufficient = True
        if truck:
            # Assume full tank is 200L and fuel_level_percent indicates remaining
            tank_capacity = 200
            available_fuel = tank_capacity * (truck.fuel_level_percent / 100)
            fuel_sufficient = available_fuel >= fuel_liters

        return {
            'distance_km': round(distance_km, 2),
            'effective_speed_kmh': round(effective_speed, 2),
            'traffic_factor': round(traffic_factor, 2),
            'time_hours': round(time_hours, 3),
            'time_minutes': round(time_minutes, 1),
            'fuel_liters': round(fuel_liters, 2),
            'fuel_cost': round(fuel_cost, 2),
            'time_cost': round(time_cost, 2),
            'total_cost': round(total_cost, 2),
            'fuel_sufficient': fuel_sufficient,
            'origin': origin.model_dump(),
            'destination': destination.model_dump(),
        }

    def simulate_reroute(
        self,
        truck: Truck,
        current_location: Location,
        destination: Location,
        original_route_traffic: List[TrafficCondition],
        alternate_routes: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Simulate rerouting options for a truck.

        Args:
            truck: Truck to reroute
            current_location: Current position
            destination: Target destination
            original_route_traffic: Traffic on original route
            alternate_routes: List of alternate route options

        Returns:
            List of route simulation results with comparisons
        """
        results = []

        # Simulate current route continuation
        current_sim = self.simulate_route(
            origin=current_location,
            destination=destination,
            traffic_conditions=original_route_traffic,
            truck=truck,
        )
        current_sim['route_name'] = 'Current Route'
        current_sim['is_current'] = True
        results.append(current_sim)

        # Simulate alternate routes
        for alt_route in alternate_routes:
            # Create traffic conditions for alternate route
            alt_traffic = []
            if 'traffic_factor' in alt_route:
                # Create synthetic traffic condition
                alt_traffic = [
                    TrafficCondition(
                        segment_id=f"ALT-{alt_route.get('name', 'Unknown')}",
                        level='moderate',
                        speed_kmh=self.default_speed_kmh / alt_route['traffic_factor'],
                    )
                ]

            alt_dest = alt_route.get('via_point', destination)
            if isinstance(alt_dest, dict):
                alt_dest = Location(**alt_dest)

            # Adjust distance if specified
            effective_origin = current_location
            if alt_route.get('distance_km'):
                # Use provided distance directly
                alt_sim = {
                    'distance_km': alt_route['distance_km'],
                    'traffic_factor': alt_route.get('traffic_factor', 1.0),
                }
                effective_speed = self.default_speed_kmh / alt_sim['traffic_factor']
                time_hours = alt_sim['distance_km'] / effective_speed
                fuel_liters = self.default_fuel_rate * alt_sim['distance_km']

                alt_sim.update({
                    'effective_speed_kmh': round(effective_speed, 2),
                    'time_hours': round(time_hours, 3),
                    'time_minutes': round(time_hours * 60, 1),
                    'fuel_liters': round(fuel_liters, 2),
                    'fuel_cost': round(fuel_liters * self.fuel_price, 2),
                    'time_cost': round(time_hours * (self.driver_rate + self.vehicle_rate), 2),
                    'total_cost': round(
                        fuel_liters * self.fuel_price +
                        time_hours * (self.driver_rate + self.vehicle_rate), 2
                    ),
                    'fuel_sufficient': True,
                })
            else:
                alt_sim = self.simulate_route(
                    origin=effective_origin,
                    destination=destination,
                    traffic_conditions=alt_traffic,
                    truck=truck,
                )

            alt_sim['route_name'] = alt_route.get('name', 'Alternate Route')
            alt_sim['is_current'] = False

            # Compare with current
            alt_sim['time_savings_minutes'] = round(
                current_sim['time_minutes'] - alt_sim['time_minutes'], 1
            )
            alt_sim['cost_difference'] = round(
                alt_sim['total_cost'] - current_sim['total_cost'], 2
            )

            results.append(alt_sim)

        return results

    def simulate_reassignment(
        self,
        original_truck: Truck,
        new_truck: Truck,
        load: Load,
        pickup_location: Location = None,
    ) -> Dict[str, Any]:
        """
        Simulate reassigning a load from one truck to another.

        Args:
            original_truck: Currently assigned truck
            new_truck: Truck to reassign to
            load: Load to reassign
            pickup_location: Where the handoff occurs (defaults to original truck location)

        Returns:
            Reassignment simulation results
        """
        if pickup_location is None:
            pickup_location = original_truck.current_location

        # Time for new truck to reach pickup
        new_truck_to_pickup = self.simulate_route(
            origin=new_truck.current_location,
            destination=pickup_location,
            truck=new_truck,
        )

        # Time for new truck to complete delivery
        new_truck_to_delivery = self.simulate_route(
            origin=pickup_location,
            destination=load.delivery_location,
            truck=new_truck,
            load=load,
        )

        # Handoff time (loading/unloading)
        handoff_time_minutes = 15  # Fixed estimate

        # Total time
        total_time_minutes = (
            new_truck_to_pickup['time_minutes'] +
            handoff_time_minutes +
            new_truck_to_delivery['time_minutes']
        )

        # Total cost
        total_cost = (
            new_truck_to_pickup['total_cost'] +
            new_truck_to_delivery['total_cost'] +
            (handoff_time_minutes / 60) * self.driver_rate  # Handoff labor
        )

        return {
            'original_truck_id': original_truck.id,
            'new_truck_id': new_truck.id,
            'load_id': load.id,
            'pickup_time_minutes': round(new_truck_to_pickup['time_minutes'], 1),
            'handoff_time_minutes': handoff_time_minutes,
            'delivery_time_minutes': round(new_truck_to_delivery['time_minutes'], 1),
            'total_time_minutes': round(total_time_minutes, 1),
            'total_cost': round(total_cost, 2),
            'new_truck_distance_km': round(
                new_truck_to_pickup['distance_km'] + new_truck_to_delivery['distance_km'], 2
            ),
        }

    def simulate_wait(
        self,
        wait_time_minutes: float,
        truck: Truck = None,
    ) -> Dict[str, Any]:
        """
        Simulate waiting for conditions to improve.

        Args:
            wait_time_minutes: Time to wait
            truck: Truck that will wait

        Returns:
            Wait simulation results
        """
        wait_hours = wait_time_minutes / 60

        # Cost of waiting (driver time, opportunity cost)
        wait_cost = wait_hours * self.driver_rate

        return {
            'wait_time_minutes': wait_time_minutes,
            'wait_cost': round(wait_cost, 2),
            'fuel_consumed': 0,  # Assuming engine off
            'opportunity_cost': round(wait_cost * 0.5, 2),  # Estimate
            'truck_id': truck.id if truck else None,
        }

    def predict_eta(
        self,
        truck: Truck,
        destination: Location,
        traffic_conditions: List[TrafficCondition] = None,
    ) -> Dict[str, Any]:
        """
        Predict estimated time of arrival.

        Args:
            truck: Truck to predict for
            destination: Target destination
            traffic_conditions: Current traffic

        Returns:
            ETA prediction with confidence
        """
        if not truck.current_location:
            return {
                'eta': None,
                'confidence': 0,
                'error': 'Truck location unknown'
            }

        simulation = self.simulate_route(
            origin=truck.current_location,
            destination=destination,
            traffic_conditions=traffic_conditions,
            truck=truck,
        )

        eta = datetime.utcnow() + timedelta(minutes=simulation['time_minutes'])

        # Confidence based on traffic factor variability
        base_confidence = 0.9
        if traffic_conditions:
            # Lower confidence with heavy traffic
            traffic_penalty = (simulation['traffic_factor'] - 1) * 0.1
            confidence = max(0.5, base_confidence - traffic_penalty)
        else:
            confidence = base_confidence * 0.8  # Lower without traffic data

        return {
            'eta': eta.isoformat(),
            'eta_minutes_from_now': round(simulation['time_minutes'], 1),
            'confidence': round(confidence, 2),
            'traffic_factor': simulation['traffic_factor'],
            'distance_remaining_km': simulation['distance_km'],
        }

    def compare_scenarios(
        self,
        scenarios: List[Scenario]
    ) -> Dict[str, Dict[str, float]]:
        """
        Compare multiple scenarios on key metrics.

        Args:
            scenarios: List of scenarios to compare

        Returns:
            Comparison matrix
        """
        comparison = {}

        # Find ranges for normalization
        costs = [s.estimated_cost for s in scenarios]
        times = [s.estimated_time_minutes for s in scenarios]
        fuels = [s.estimated_fuel_liters for s in scenarios]

        min_cost, max_cost = min(costs), max(costs)
        min_time, max_time = min(times), max(times)
        min_fuel, max_fuel = min(fuels), max(fuels)

        for scenario in scenarios:
            # Normalize scores (lower is better for cost/time/fuel)
            cost_range = max_cost - min_cost if max_cost != min_cost else 1
            time_range = max_time - min_time if max_time != min_time else 1
            fuel_range = max_fuel - min_fuel if max_fuel != min_fuel else 1

            cost_score = 1 - (scenario.estimated_cost - min_cost) / cost_range
            time_score = 1 - (scenario.estimated_time_minutes - min_time) / time_range
            fuel_score = 1 - (scenario.estimated_fuel_liters - min_fuel) / fuel_range

            # Weighted overall score
            overall = (
                0.3 * cost_score +
                0.4 * time_score +
                0.2 * fuel_score +
                0.1 * scenario.reliability_score
            )

            comparison[scenario.id] = {
                'cost_score': round(cost_score, 3),
                'time_score': round(time_score, 3),
                'fuel_score': round(fuel_score, 3),
                'reliability': scenario.reliability_score,
                'overall': round(overall, 3),
            }

        return comparison
