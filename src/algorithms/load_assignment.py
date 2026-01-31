"""
Load assignment algorithms for optimal truck-load matching.
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import heapq

from src.models import Truck, Load, Location, TruckStatus, LoadPriority
from src.algorithms.route_optimizer import RouteOptimizer


@dataclass
class Assignment:
    """A truck-load assignment with cost and timing."""
    truck_id: str
    load_id: str
    estimated_cost: float
    estimated_time_minutes: float
    pickup_eta: datetime
    delivery_eta: datetime
    confidence_score: float
    priority_score: float


@dataclass
class AssignmentSolution:
    """Complete assignment solution."""
    assignments: List[Assignment]
    total_cost: float
    unassigned_loads: List[str]
    utilization_rate: float
    on_time_probability: float


class LoadAssignmentEngine:
    """
    Advanced load assignment engine using multiple optimization strategies.
    
    Implements:
    - Hungarian algorithm for optimal assignment
    - Priority-based assignment for urgent loads
    - Capacity and time window constraints
    - Multi-objective optimization
    """
    
    def __init__(self):
        self.route_optimizer = RouteOptimizer()
        
    def assign_loads_to_trucks(
        self,
        trucks: List[Truck],
        loads: List[Load],
        strategy: str = "optimal"  # "optimal", "greedy", "priority_first"
    ) -> AssignmentSolution:
        """
        Assign loads to trucks using specified strategy.
        
        Args:
            trucks: Available trucks
            loads: Loads to assign
            strategy: Assignment strategy
            
        Returns:
            Complete assignment solution
        """
        # Filter available trucks
        available_trucks = [
            t for t in trucks 
            if t.status in [TruckStatus.IDLE, TruckStatus.EN_ROUTE] 
            and t.current_location is not None
        ]
        
        # Filter unassigned loads
        unassigned_loads = [l for l in loads if not l.assigned_truck_id]
        
        if not available_trucks or not unassigned_loads:
            return AssignmentSolution(
                assignments=[],
                total_cost=0.0,
                unassigned_loads=[l.id for l in unassigned_loads],
                utilization_rate=0.0,
                on_time_probability=1.0
            )
        
        if strategy == "optimal":
            return self._optimal_assignment(available_trucks, unassigned_loads)
        elif strategy == "greedy":
            return self._greedy_assignment(available_trucks, unassigned_loads)
        elif strategy == "priority_first":
            return self._priority_first_assignment(available_trucks, unassigned_loads)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _optimal_assignment(
        self,
        trucks: List[Truck],
        loads: List[Load]
    ) -> AssignmentSolution:
        """
        Optimal assignment using Hungarian algorithm approach.
        """
        # Build cost matrix
        cost_matrix = self._build_cost_matrix(trucks, loads)
        
        # Solve assignment problem
        assignments = []
        total_cost = 0.0
        assigned_loads = set()
        assigned_trucks = set()
        
        # Simple greedy approximation of Hungarian algorithm
        # In production, use scipy.optimize.linear_sum_assignment
        truck_load_pairs = []
        
        for i, truck in enumerate(trucks):
            for j, load in enumerate(loads):
                cost = cost_matrix[i][j]
                if cost < float('inf'):
                    heapq.heappush(truck_load_pairs, (cost, i, j, truck, load))
        
        while truck_load_pairs and len(assigned_loads) < len(loads):
            cost, truck_idx, load_idx, truck, load = heapq.heappop(truck_load_pairs)
            
            if truck.id not in assigned_trucks and load.id not in assigned_loads:
                # Check constraints
                if self._check_assignment_constraints(truck, load):
                    assignment = self._create_assignment(truck, load, cost)
                    assignments.append(assignment)
                    total_cost += cost
                    assigned_loads.add(load.id)
                    assigned_trucks.add(truck.id)
        
        unassigned = [l.id for l in loads if l.id not in assigned_loads]
        utilization = len(assigned_trucks) / len(trucks) if trucks else 0.0
        on_time_prob = self._calculate_on_time_probability(assignments)
        
        return AssignmentSolution(
            assignments=assignments,
            total_cost=total_cost,
            unassigned_loads=unassigned,
            utilization_rate=utilization,
            on_time_probability=on_time_prob
        )
    
    def _greedy_assignment(
        self,
        trucks: List[Truck],
        loads: List[Load]
    ) -> AssignmentSolution:
        """
        Greedy assignment - assign each load to the best available truck.
        """
        assignments = []
        total_cost = 0.0
        available_trucks = trucks[:]
        
        # Sort loads by priority and deadline
        sorted_loads = sorted(loads, key=lambda l: (
            self._priority_to_numeric(l.priority),
            l.delivery_deadline or datetime.max
        ))
        
        for load in sorted_loads:
            best_truck = None
            best_cost = float('inf')
            
            for truck in available_trucks:
                if self._check_assignment_constraints(truck, load):
                    cost = self._calculate_assignment_cost(truck, load)
                    if cost < best_cost:
                        best_cost = cost
                        best_truck = truck
            
            if best_truck:
                assignment = self._create_assignment(best_truck, load, best_cost)
                assignments.append(assignment)
                total_cost += best_cost
                available_trucks.remove(best_truck)
        
        unassigned = [l.id for l in loads if not any(a.load_id == l.id for a in assignments)]
        utilization = (len(trucks) - len(available_trucks)) / len(trucks) if trucks else 0.0
        on_time_prob = self._calculate_on_time_probability(assignments)
        
        return AssignmentSolution(
            assignments=assignments,
            total_cost=total_cost,
            unassigned_loads=unassigned,
            utilization_rate=utilization,
            on_time_probability=on_time_prob
        )
    
    def _priority_first_assignment(
        self,
        trucks: List[Truck],
        loads: List[Load]
    ) -> AssignmentSolution:
        """
        Priority-first assignment - handle urgent loads first.
        """
        # Separate loads by priority
        critical_loads = [l for l in loads if l.priority in [LoadPriority.CRITICAL, LoadPriority.URGENT]]
        normal_loads = [l for l in loads if l.priority not in [LoadPriority.CRITICAL, LoadPriority.URGENT]]
        
        assignments = []
        total_cost = 0.0
        available_trucks = trucks[:]
        
        # Assign critical loads first
        for load in sorted(critical_loads, key=lambda l: l.delivery_deadline or datetime.max):
            best_truck, cost = self.route_optimizer.find_best_truck_for_load(load, available_trucks)
            if best_truck:
                assignment = self._create_assignment(best_truck, load, cost)
                assignments.append(assignment)
                total_cost += cost
                available_trucks.remove(best_truck)
        
        # Assign remaining loads
        for load in normal_loads:
            best_truck, cost = self.route_optimizer.find_best_truck_for_load(load, available_trucks)
            if best_truck:
                assignment = self._create_assignment(best_truck, load, cost)
                assignments.append(assignment)
                total_cost += cost
                available_trucks.remove(best_truck)
        
        unassigned = [l.id for l in loads if not any(a.load_id == l.id for a in assignments)]
        utilization = (len(trucks) - len(available_trucks)) / len(trucks) if trucks else 0.0
        on_time_prob = self._calculate_on_time_probability(assignments)
        
        return AssignmentSolution(
            assignments=assignments,
            total_cost=total_cost,
            unassigned_loads=unassigned,
            utilization_rate=utilization,
            on_time_probability=on_time_prob
        )
    
    def _build_cost_matrix(self, trucks: List[Truck], loads: List[Load]) -> List[List[float]]:
        """Build cost matrix for assignment problem."""
        matrix = []
        
        for truck in trucks:
            truck_costs = []
            for load in loads:
                if self._check_assignment_constraints(truck, load):
                    cost = self._calculate_assignment_cost(truck, load)
                else:
                    cost = float('inf')
                truck_costs.append(cost)
            matrix.append(truck_costs)
        
        return matrix
    
    def _check_assignment_constraints(self, truck: Truck, load: Load) -> bool:
        """Check if truck can handle the load."""
        # Capacity constraint
        if truck.capacity_kg < load.weight_kg:
            return False
        
        # Fuel constraint (rough estimate)
        if truck.current_location:
            distance_to_pickup = truck.current_location.distance_to(load.pickup_location)
            delivery_distance = load.pickup_location.distance_to(load.delivery_location)
            total_distance = distance_to_pickup + delivery_distance
            
            fuel_needed = total_distance * 0.3  # L/km
            fuel_available = 200 * (truck.fuel_level_percent / 100)  # Assume 200L tank
            
            if fuel_needed > fuel_available * 0.8:  # Keep 20% buffer
                return False
        
        # Time window constraint (if specified)
        if load.delivery_deadline:
            estimated_time = self._estimate_delivery_time(truck, load)
            if estimated_time > load.delivery_deadline:
                return False
        
        return True
    
    def _calculate_assignment_cost(self, truck: Truck, load: Load) -> float:
        """Calculate cost of assigning load to truck."""
        if not truck.current_location:
            return float('inf')
        
        # Distance costs
        distance_to_pickup = truck.current_location.distance_to(load.pickup_location)
        delivery_distance = load.pickup_location.distance_to(load.delivery_location)
        total_distance = distance_to_pickup + delivery_distance
        
        # Time costs
        avg_speed = 50.0  # km/h
        total_time_hours = total_distance / avg_speed
        
        # Fuel costs
        fuel_consumption = total_distance * 0.3  # L/km
        fuel_cost = fuel_consumption * 1.50  # $/L
        
        # Time costs
        time_cost = total_time_hours * (25.0 + 10.0)  # Driver + vehicle costs
        
        # Priority adjustment
        priority_multiplier = {
            LoadPriority.LOW: 1.2,
            LoadPriority.NORMAL: 1.0,
            LoadPriority.HIGH: 0.8,
            LoadPriority.URGENT: 0.6,
            LoadPriority.CRITICAL: 0.4
        }.get(load.priority, 1.0)
        
        base_cost = fuel_cost + time_cost
        return base_cost * priority_multiplier
    
    def _create_assignment(self, truck: Truck, load: Load, cost: float) -> Assignment:
        """Create assignment object with timing estimates."""
        now = datetime.utcnow()
        
        # Estimate pickup time
        if truck.current_location:
            distance_to_pickup = truck.current_location.distance_to(load.pickup_location)
            pickup_time_hours = distance_to_pickup / 50.0  # 50 km/h avg speed
            pickup_eta = now + timedelta(hours=pickup_time_hours)
        else:
            pickup_eta = now + timedelta(hours=1)  # Default estimate
        
        # Estimate delivery time
        delivery_distance = load.pickup_location.distance_to(load.delivery_location)
        delivery_time_hours = delivery_distance / 50.0
        delivery_eta = pickup_eta + timedelta(hours=delivery_time_hours)
        
        # Calculate total time
        total_time_minutes = (delivery_eta - now).total_seconds() / 60
        
        # Calculate scores
        confidence = self._calculate_assignment_confidence(truck, load)
        priority_score = self._priority_to_numeric(load.priority)
        
        return Assignment(
            truck_id=truck.id,
            load_id=load.id,
            estimated_cost=cost,
            estimated_time_minutes=total_time_minutes,
            pickup_eta=pickup_eta,
            delivery_eta=delivery_eta,
            confidence_score=confidence,
            priority_score=priority_score
        )
    
    def _estimate_delivery_time(self, truck: Truck, load: Load) -> datetime:
        """Estimate when delivery will be completed."""
        now = datetime.utcnow()
        
        if not truck.current_location:
            return now + timedelta(hours=4)  # Default estimate
        
        distance_to_pickup = truck.current_location.distance_to(load.pickup_location)
        delivery_distance = load.pickup_location.distance_to(load.delivery_location)
        total_distance = distance_to_pickup + delivery_distance
        
        # Estimate time with traffic buffer
        avg_speed = 45.0  # km/h (conservative with traffic)
        total_hours = total_distance / avg_speed
        
        return now + timedelta(hours=total_hours)
    
    def _calculate_assignment_confidence(self, truck: Truck, load: Load) -> float:
        """Calculate confidence score for assignment."""
        base_confidence = 0.8
        
        # Fuel level factor
        if truck.fuel_level_percent < 30:
            base_confidence -= 0.2
        elif truck.fuel_level_percent > 70:
            base_confidence += 0.1
        
        # Distance factor
        if truck.current_location:
            distance = truck.current_location.distance_to(load.pickup_location)
            if distance > 100:  # Long distance reduces confidence
                base_confidence -= 0.1
        
        # Priority factor
        if load.priority in [LoadPriority.CRITICAL, LoadPriority.URGENT]:
            base_confidence += 0.1  # More attention for urgent loads
        
        return max(0.3, min(1.0, base_confidence))
    
    def _priority_to_numeric(self, priority: LoadPriority) -> float:
        """Convert priority to numeric score (higher = more urgent)."""
        return {
            LoadPriority.LOW: 1.0,
            LoadPriority.NORMAL: 2.0,
            LoadPriority.HIGH: 3.0,
            LoadPriority.URGENT: 4.0,
            LoadPriority.CRITICAL: 5.0
        }.get(priority, 2.0)
    
    def _calculate_on_time_probability(self, assignments: List[Assignment]) -> float:
        """Calculate probability that all assignments will be on time."""
        if not assignments:
            return 1.0
        
        # Simple model: average of individual confidence scores
        confidences = [a.confidence_score for a in assignments]
        return sum(confidences) / len(confidences)
    
    def optimize_existing_assignments(
        self,
        trucks: List[Truck],
        loads: List[Load]
    ) -> List[Tuple[str, str]]:  # List of (truck_id, load_id) reassignments
        """
        Optimize existing assignments by suggesting reassignments.
        
        Returns:
            List of suggested reassignments
        """
        reassignments = []
        
        # Find trucks with loads
        loaded_trucks = [t for t in trucks if t.current_load_id]
        idle_trucks = [t for t in trucks if t.status == TruckStatus.IDLE]
        
        if not loaded_trucks or not idle_trucks:
            return reassignments
        
        # Check if any reassignments would be beneficial
        for loaded_truck in loaded_trucks:
            current_load = next((l for l in loads if l.id == loaded_truck.current_load_id), None)
            if not current_load:
                continue
            
            current_cost = self._calculate_assignment_cost(loaded_truck, current_load)
            
            # Check if any idle truck could do it better
            for idle_truck in idle_trucks:
                if self._check_assignment_constraints(idle_truck, current_load):
                    idle_cost = self._calculate_assignment_cost(idle_truck, current_load)
                    
                    # If idle truck is significantly better (>20% cost reduction)
                    if idle_cost < current_cost * 0.8:
                        reassignments.append((idle_truck.id, current_load.id))
                        break
        
        return reassignments