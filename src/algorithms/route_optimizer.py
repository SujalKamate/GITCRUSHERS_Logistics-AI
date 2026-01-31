"""
Route optimization algorithms for logistics planning.
"""
import math
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from src.models import Location, Truck, Load, TrafficCondition


@dataclass
class RouteSegment:
    """A segment of a route between two points."""
    start: Location
    end: Location
    distance_km: float
    estimated_time_minutes: float
    traffic_factor: float = 1.0


@dataclass
class OptimizedRoute:
    """An optimized route with cost and time estimates."""
    segments: List[RouteSegment]
    total_distance_km: float
    total_time_minutes: float
    total_cost: float
    fuel_consumption_liters: float
    confidence_score: float


class RouteOptimizer:
    """
    Route optimization engine using multiple algorithms.
    
    Implements:
    - Nearest neighbor heuristic
    - 2-opt improvement
    - Traffic-aware routing
    - Multi-objective optimization (time, cost, fuel)
    """
    
    def __init__(self):
        self.fuel_rate_base = 0.3  # L/km base consumption
        self.fuel_price = 1.50  # $/L
        self.driver_rate = 25.0  # $/hour
        self.vehicle_rate = 10.0  # $/hour
        
    def optimize_route(
        self,
        truck: Truck,
        loads: List[Load],
        traffic_conditions: List[TrafficCondition] = None,
        optimization_goal: str = "balanced"  # "time", "cost", "fuel", "balanced"
    ) -> OptimizedRoute:
        """
        Optimize route for a truck with multiple loads.
        
        Args:
            truck: The truck to optimize for
            loads: List of loads to deliver
            traffic_conditions: Current traffic conditions
            optimization_goal: Primary optimization objective
            
        Returns:
            Optimized route with segments and estimates
        """
        if not loads:
            return self._empty_route()
            
        # Create list of all locations (pickup and delivery)
        locations = []
        location_types = []  # 'pickup' or 'delivery'
        load_mapping = {}  # location index -> load
        
        start_location = truck.current_location
        if not start_location:
            start_location = loads[0].pickup_location
            
        # Add all pickup and delivery locations
        for i, load in enumerate(loads):
            # Pickup location
            locations.append(load.pickup_location)
            location_types.append('pickup')
            load_mapping[len(locations) - 1] = (load, 'pickup')
            
            # Delivery location
            locations.append(load.delivery_location)
            location_types.append('delivery')
            load_mapping[len(locations) - 1] = (load, 'delivery')
        
        # Calculate distance matrix
        distance_matrix = self._calculate_distance_matrix([start_location] + locations)
        
        # Apply traffic factors
        if traffic_conditions:
            distance_matrix = self._apply_traffic_factors(distance_matrix, traffic_conditions)
        
        # Find optimal sequence using nearest neighbor + 2-opt
        if len(locations) <= 2:
            # Simple case: direct route
            sequence = list(range(len(locations)))
        else:
            sequence = self._nearest_neighbor_tsp(distance_matrix[1:, 1:])  # Exclude start location
        
        # Improve with 2-opt
        if len(sequence) > 3:
            sequence = self._two_opt_improve(sequence, distance_matrix[1:, 1:])
        
        # Ensure pickup before delivery constraint
        sequence = self._enforce_pickup_delivery_order(sequence, loads, location_types)
        
        # Build route segments
        segments = []
        current_location = start_location
        current_idx = 0  # Start location index
        
        total_distance = 0
        total_time = 0
        
        for next_idx in sequence:
            next_location = locations[next_idx]
            
            # Calculate segment
            distance = distance_matrix[current_idx][next_idx + 1]  # +1 for start location offset
            traffic_factor = self._get_traffic_factor(current_location, next_location, traffic_conditions)
            base_speed = 60.0  # km/h
            time_minutes = (distance / (base_speed / traffic_factor)) * 60
            
            segment = RouteSegment(
                start=current_location,
                end=next_location,
                distance_km=distance,
                estimated_time_minutes=time_minutes,
                traffic_factor=traffic_factor
            )
            segments.append(segment)
            
            total_distance += distance
            total_time += time_minutes
            current_location = next_location
            current_idx = next_idx + 1
        
        # Calculate costs
        fuel_consumption = self._calculate_fuel_consumption(total_distance, truck, loads)
        fuel_cost = fuel_consumption * self.fuel_price
        time_cost = (total_time / 60) * (self.driver_rate + self.vehicle_rate)
        total_cost = fuel_cost + time_cost
        
        # Calculate confidence score
        confidence = self._calculate_confidence_score(segments, traffic_conditions)
        
        return OptimizedRoute(
            segments=segments,
            total_distance_km=round(total_distance, 2),
            total_time_minutes=round(total_time, 1),
            total_cost=round(total_cost, 2),
            fuel_consumption_liters=round(fuel_consumption, 2),
            confidence_score=confidence
        )
    
    def find_best_truck_for_load(
        self,
        load: Load,
        available_trucks: List[Truck],
        traffic_conditions: List[TrafficCondition] = None
    ) -> Tuple[Optional[Truck], float]:
        """
        Find the best truck for a specific load.
        
        Returns:
            Tuple of (best_truck, estimated_cost)
        """
        if not available_trucks:
            return None, float('inf')
        
        best_truck = None
        best_score = float('inf')
        
        for truck in available_trucks:
            # Check capacity
            if truck.capacity_kg < load.weight_kg:
                continue
                
            # Calculate score based on multiple factors
            score = self._calculate_truck_load_score(truck, load, traffic_conditions)
            
            if score < best_score:
                best_score = score
                best_truck = truck
        
        return best_truck, best_score
    
    def _calculate_distance_matrix(self, locations: List[Location]) -> List[List[float]]:
        """Calculate distance matrix between all locations."""
        n = len(locations)
        matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    matrix[i][j] = locations[i].distance_to(locations[j])
        
        return matrix
    
    def _apply_traffic_factors(
        self,
        distance_matrix: List[List[float]],
        traffic_conditions: List[TrafficCondition]
    ) -> List[List[float]]:
        """Apply traffic factors to distance matrix (converting to time-based costs)."""
        # For simplicity, apply average traffic factor
        if not traffic_conditions:
            return distance_matrix
        
        avg_factor = sum(tc.delay_factor for tc in traffic_conditions) / len(traffic_conditions)
        
        # Convert distances to time costs with traffic
        n = len(distance_matrix)
        time_matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    distance = distance_matrix[i][j]
                    time_hours = (distance / 60.0) * avg_factor  # 60 km/h base speed
                    time_matrix[i][j] = time_hours * 60  # Convert to minutes
        
        return time_matrix
    
    def _nearest_neighbor_tsp(self, distance_matrix: List[List[float]]) -> List[int]:
        """Solve TSP using nearest neighbor heuristic."""
        n = len(distance_matrix)
        if n == 0:
            return []
        
        unvisited = set(range(1, n))  # Start from location 0
        current = 0
        tour = [current]
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            tour.append(nearest)
            unvisited.remove(nearest)
            current = nearest
        
        return tour[1:]  # Remove starting location
    
    def _two_opt_improve(self, tour: List[int], distance_matrix: List[List[float]]) -> List[int]:
        """Improve tour using 2-opt algorithm."""
        def tour_distance(t):
            dist = 0
            for i in range(len(t)):
                j = (i + 1) % len(t)
                dist += distance_matrix[t[i]][t[j]]
            return dist
        
        best_tour = tour[:]
        best_distance = tour_distance(best_tour)
        improved = True
        
        while improved:
            improved = False
            for i in range(len(tour)):
                for j in range(i + 2, len(tour)):
                    # Try 2-opt swap
                    new_tour = tour[:i] + tour[i:j+1][::-1] + tour[j+1:]
                    new_distance = tour_distance(new_tour)
                    
                    if new_distance < best_distance:
                        best_tour = new_tour
                        best_distance = new_distance
                        tour = new_tour
                        improved = True
        
        return best_tour
    
    def _enforce_pickup_delivery_order(
        self,
        sequence: List[int],
        loads: List[Load],
        location_types: List[str]
    ) -> List[int]:
        """Ensure pickup happens before delivery for each load."""
        # Simple constraint enforcement - in production, use more sophisticated algorithm
        corrected_sequence = []
        
        for load_idx, load in enumerate(loads):
            pickup_idx = load_idx * 2  # Even indices are pickups
            delivery_idx = load_idx * 2 + 1  # Odd indices are deliveries
            
            # Find positions in sequence
            pickup_pos = sequence.index(pickup_idx) if pickup_idx in sequence else -1
            delivery_pos = sequence.index(delivery_idx) if delivery_idx in sequence else -1
            
            if pickup_pos >= 0 and delivery_pos >= 0:
                if pickup_pos < delivery_pos:
                    # Correct order
                    if pickup_idx not in corrected_sequence:
                        corrected_sequence.append(pickup_idx)
                    if delivery_idx not in corrected_sequence:
                        corrected_sequence.append(delivery_idx)
                else:
                    # Wrong order - fix it
                    if pickup_idx not in corrected_sequence:
                        corrected_sequence.append(pickup_idx)
                    if delivery_idx not in corrected_sequence:
                        corrected_sequence.append(delivery_idx)
        
        # Add any missing locations
        for idx in sequence:
            if idx not in corrected_sequence:
                corrected_sequence.append(idx)
        
        return corrected_sequence
    
    def _get_traffic_factor(
        self,
        start: Location,
        end: Location,
        traffic_conditions: List[TrafficCondition]
    ) -> float:
        """Get traffic factor for a route segment."""
        if not traffic_conditions:
            return 1.0
        
        # Simple implementation - use average traffic factor
        factors = [tc.delay_factor for tc in traffic_conditions]
        return sum(factors) / len(factors) if factors else 1.0
    
    def _calculate_fuel_consumption(
        self,
        distance_km: float,
        truck: Truck,
        loads: List[Load]
    ) -> float:
        """Calculate fuel consumption for the route."""
        base_rate = self.fuel_rate_base
        
        # Adjust for total load weight
        total_weight = sum(load.weight_kg for load in loads)
        weight_factor = 0.00002  # Additional L/km per kg
        
        effective_rate = base_rate + (weight_factor * total_weight)
        return distance_km * effective_rate
    
    def _calculate_confidence_score(
        self,
        segments: List[RouteSegment],
        traffic_conditions: List[TrafficCondition]
    ) -> float:
        """Calculate confidence score for the route."""
        base_confidence = 0.9
        
        # Reduce confidence based on traffic uncertainty
        if traffic_conditions:
            heavy_traffic_count = sum(1 for tc in traffic_conditions if tc.delay_factor > 1.5)
            traffic_penalty = heavy_traffic_count * 0.1
            base_confidence -= traffic_penalty
        
        # Reduce confidence for long routes
        total_distance = sum(s.distance_km for s in segments)
        if total_distance > 200:  # Long routes are less predictable
            distance_penalty = (total_distance - 200) / 1000 * 0.1
            base_confidence -= distance_penalty
        
        return max(0.3, min(1.0, base_confidence))
    
    def _calculate_truck_load_score(
        self,
        truck: Truck,
        load: Load,
        traffic_conditions: List[TrafficCondition]
    ) -> float:
        """Calculate score for assigning a load to a truck (lower is better)."""
        if not truck.current_location:
            return float('inf')
        
        # Distance to pickup
        distance_to_pickup = truck.current_location.distance_to(load.pickup_location)
        
        # Distance from pickup to delivery
        delivery_distance = load.pickup_location.distance_to(load.delivery_location)
        
        # Time factors
        traffic_factor = 1.0
        if traffic_conditions:
            traffic_factor = sum(tc.delay_factor for tc in traffic_conditions) / len(traffic_conditions)
        
        # Calculate total time
        total_distance = distance_to_pickup + delivery_distance
        total_time_hours = (total_distance / 60.0) * traffic_factor
        
        # Calculate costs
        fuel_cost = total_distance * self.fuel_rate_base * self.fuel_price
        time_cost = total_time_hours * (self.driver_rate + self.vehicle_rate)
        
        # Priority factor (urgent loads get lower scores)
        priority_factor = {
            'low': 1.0,
            'normal': 0.9,
            'high': 0.7,
            'urgent': 0.5,
            'critical': 0.3
        }.get(load.priority.value, 1.0)
        
        # Fuel level factor (low fuel gets higher scores)
        fuel_factor = 1.0 if truck.fuel_level_percent > 30 else 1.5
        
        total_score = (fuel_cost + time_cost) * priority_factor * fuel_factor
        
        return total_score
    
    def _empty_route(self) -> OptimizedRoute:
        """Return empty route."""
        return OptimizedRoute(
            segments=[],
            total_distance_km=0.0,
            total_time_minutes=0.0,
            total_cost=0.0,
            fuel_consumption_liters=0.0,
            confidence_score=1.0
        )