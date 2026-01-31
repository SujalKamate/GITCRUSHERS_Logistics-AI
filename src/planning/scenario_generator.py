"""
Scenario generator for planning layer.

Generates and evaluates alternative action scenarios for issues.
"""
import uuid
from typing import Any, Dict, List, Optional
import structlog

from src.models import (
    Truck, Route, Load, TrafficCondition, TruckStatus,
    Location, Issue, Scenario, ActionType
)
from src.planning.simulation_engine import SimulationEngine

logger = structlog.get_logger(__name__)


class ScenarioGenerator:
    """
    Generates alternative scenarios for resolving logistics issues.

    For each issue type, generates appropriate scenarios:
    - Stuck truck: wait, reroute, reassign
    - Traffic delay: wait, reroute
    - Capacity mismatch: reassign, dispatch
    - etc.
    """

    def __init__(self, simulation_engine: SimulationEngine = None):
        """Initialize the scenario generator."""
        self.sim_engine = simulation_engine or SimulationEngine()
        logger.info("Scenario generator initialized")

    def generate_scenarios(
        self,
        issue: Issue,
        trucks: List[Truck],
        loads: List[Load],
        traffic_conditions: List[TrafficCondition],
        routes: List[Route] = None,
        max_scenarios: int = 5,
    ) -> List[Scenario]:
        """
        Generate scenarios for resolving an issue.

        Args:
            issue: The issue to resolve
            trucks: Available trucks
            loads: Active loads
            traffic_conditions: Current traffic
            routes: Active routes
            max_scenarios: Maximum scenarios to generate

        Returns:
            List of generated scenarios
        """
        scenarios = []

        # Get affected truck and load
        affected_truck = self._get_affected_truck(issue, trucks)
        affected_load = self._get_affected_load(issue, loads)

        # Generate scenarios based on issue type
        if issue.type == "stuck":
            scenarios.extend(self._generate_stuck_truck_scenarios(
                issue, affected_truck, affected_load, trucks, traffic_conditions
            ))
        elif issue.type == "delay":
            scenarios.extend(self._generate_delay_scenarios(
                issue, affected_truck, affected_load, traffic_conditions
            ))
        elif issue.type == "traffic":
            scenarios.extend(self._generate_traffic_scenarios(
                issue, affected_truck, traffic_conditions
            ))
        elif issue.type == "capacity_mismatch":
            scenarios.extend(self._generate_capacity_scenarios(
                issue, trucks, loads
            ))
        else:
            # Generic scenarios
            scenarios.extend(self._generate_generic_scenarios(
                issue, affected_truck, affected_load, trucks
            ))

        # Limit number of scenarios
        scenarios = scenarios[:max_scenarios]

        # Evaluate and rank scenarios
        scenarios = self._rank_scenarios(scenarios)

        logger.info(
            "Scenarios generated",
            issue_id=issue.id,
            issue_type=issue.type,
            count=len(scenarios)
        )

        return scenarios

    def _get_affected_truck(self, issue: Issue, trucks: List[Truck]) -> Optional[Truck]:
        """Get the truck affected by the issue."""
        if issue.affected_truck_ids:
            truck_id = issue.affected_truck_ids[0]
            for truck in trucks:
                if truck.id == truck_id:
                    return truck
        return None

    def _get_affected_load(self, issue: Issue, loads: List[Load]) -> Optional[Load]:
        """Get the load affected by the issue."""
        if issue.affected_load_ids:
            load_id = issue.affected_load_ids[0]
            for load in loads:
                if load.id == load_id:
                    return load
        return None

    def _generate_stuck_truck_scenarios(
        self,
        issue: Issue,
        truck: Optional[Truck],
        load: Optional[Load],
        trucks: List[Truck],
        traffic: List[TrafficCondition],
    ) -> List[Scenario]:
        """Generate scenarios for a stuck truck."""
        scenarios = []

        # Scenario 1: Wait for traffic to clear
        wait_sim = self.sim_engine.simulate_wait(30, truck)  # 30 min wait
        scenarios.append(Scenario(
            id=f"SCEN-{issue.id}-WAIT",
            name="Wait for Conditions to Improve",
            description="Wait 30 minutes for traffic to clear, then continue on current route",
            actions=[{"type": ActionType.WAIT.value, "duration_minutes": 30}],
            estimated_cost=wait_sim['wait_cost'] + 50,  # Plus resumed travel
            estimated_time_minutes=30 + 45,  # Wait plus travel
            estimated_fuel_liters=2.0,
            reliability_score=0.7,
            simulation_parameters={"wait_time": 30},
            simulation_results=wait_sim,
        ))

        # Scenario 2: Reroute if truck location known
        if truck and truck.current_location:
            # Simulate alternate route (simplified - would use actual routing in production)
            destination = load.delivery_location if load else Location(
                latitude=truck.current_location.latitude + 0.1,
                longitude=truck.current_location.longitude + 0.1
            )

            alt_routes = [
                {"name": "Route 9A North", "distance_km": 25, "traffic_factor": 1.1},
                {"name": "Local Roads", "distance_km": 30, "traffic_factor": 1.2},
            ]

            reroute_sims = self.sim_engine.simulate_reroute(
                truck=truck,
                current_location=truck.current_location,
                destination=destination,
                original_route_traffic=traffic,
                alternate_routes=alt_routes,
            )

            for i, alt_sim in enumerate(reroute_sims[1:], 1):  # Skip current route
                scenarios.append(Scenario(
                    id=f"SCEN-{issue.id}-REROUTE-{i}",
                    name=f"Reroute via {alt_sim['route_name']}",
                    description=f"Take alternate route: {alt_sim['route_name']}",
                    actions=[{
                        "type": ActionType.REROUTE.value,
                        "new_route": alt_sim['route_name'],
                        "truck_id": truck.id,
                    }],
                    estimated_cost=alt_sim['total_cost'],
                    estimated_time_minutes=alt_sim['time_minutes'],
                    estimated_fuel_liters=alt_sim['fuel_liters'],
                    reliability_score=0.85,
                    simulation_parameters={"route": alt_sim['route_name']},
                    simulation_results=alt_sim,
                ))

        # Scenario 3: Reassign to another truck
        available_trucks = [
            t for t in trucks
            if t.id != (truck.id if truck else None)
            and t.status in [TruckStatus.IDLE, TruckStatus.EN_ROUTE]
        ]

        if available_trucks and load and truck:
            best_truck = available_trucks[0]  # Simplified selection
            reassign_sim = self.sim_engine.simulate_reassignment(
                original_truck=truck,
                new_truck=best_truck,
                load=load,
            )

            scenarios.append(Scenario(
                id=f"SCEN-{issue.id}-REASSIGN",
                name=f"Reassign to {best_truck.id}",
                description=f"Transfer load to {best_truck.name} ({best_truck.id})",
                actions=[
                    {"type": ActionType.REASSIGN.value,
                     "from_truck": truck.id,
                     "to_truck": best_truck.id,
                     "load_id": load.id},
                    {"type": ActionType.DISPATCH.value, "truck_id": best_truck.id},
                ],
                estimated_cost=reassign_sim['total_cost'],
                estimated_time_minutes=reassign_sim['total_time_minutes'],
                estimated_fuel_liters=reassign_sim['new_truck_distance_km'] * 0.3,
                reliability_score=0.9,
                simulation_parameters={"new_truck": best_truck.id},
                simulation_results=reassign_sim,
            ))

        return scenarios

    def _generate_delay_scenarios(
        self,
        issue: Issue,
        truck: Optional[Truck],
        load: Optional[Load],
        traffic: List[TrafficCondition],
    ) -> List[Scenario]:
        """Generate scenarios for a delay issue."""
        scenarios = []

        # Scenario 1: Continue and notify
        scenarios.append(Scenario(
            id=f"SCEN-{issue.id}-CONTINUE",
            name="Continue and Notify Customer",
            description="Continue on current route and send customer delay notification",
            actions=[
                {"type": ActionType.NOTIFY.value, "recipient": "customer",
                 "message": "Delivery delayed due to traffic"},
            ],
            estimated_cost=10,  # Just notification cost
            estimated_time_minutes=60,
            estimated_fuel_liters=3.0,
            reliability_score=0.6,
        ))

        # Scenario 2: Wait for peak to pass
        scenarios.append(Scenario(
            id=f"SCEN-{issue.id}-WAIT",
            name="Wait for Traffic Peak to Pass",
            description="Pull over and wait 45 minutes for rush hour to end",
            actions=[{"type": ActionType.WAIT.value, "duration_minutes": 45}],
            estimated_cost=45,
            estimated_time_minutes=75,
            estimated_fuel_liters=2.5,
            reliability_score=0.75,
        ))

        return scenarios

    def _generate_traffic_scenarios(
        self,
        issue: Issue,
        truck: Optional[Truck],
        traffic: List[TrafficCondition],
    ) -> List[Scenario]:
        """Generate scenarios for traffic issues."""
        return self._generate_delay_scenarios(issue, truck, None, traffic)

    def _generate_capacity_scenarios(
        self,
        issue: Issue,
        trucks: List[Truck],
        loads: List[Load],
    ) -> List[Scenario]:
        """Generate scenarios for capacity mismatch."""
        scenarios = []

        # Find unassigned loads
        unassigned_loads = [
            l for l in loads
            if l.id in issue.affected_load_ids or not l.assigned_truck_id
        ]

        # Find available trucks
        available_trucks = [
            t for t in trucks
            if t.status == TruckStatus.IDLE
        ]

        if available_trucks and unassigned_loads:
            # Dispatch available truck
            truck = available_trucks[0]
            load = unassigned_loads[0]

            scenarios.append(Scenario(
                id=f"SCEN-{issue.id}-DISPATCH",
                name=f"Dispatch {truck.id} for {load.id}",
                description=f"Dispatch idle truck {truck.name} to pick up {load.description}",
                actions=[
                    {"type": ActionType.DISPATCH.value, "truck_id": truck.id, "load_id": load.id},
                ],
                estimated_cost=150,
                estimated_time_minutes=90,
                estimated_fuel_liters=8.0,
                reliability_score=0.95,
            ))

        # Escalate if no trucks available
        if not available_trucks:
            scenarios.append(Scenario(
                id=f"SCEN-{issue.id}-ESCALATE",
                name="Escalate to Dispatch Manager",
                description="No trucks available - escalate for external carrier or priority adjustment",
                actions=[
                    {"type": ActionType.ESCALATE.value, "reason": "No trucks available"},
                ],
                estimated_cost=0,
                estimated_time_minutes=15,
                estimated_fuel_liters=0,
                reliability_score=0.8,
            ))

        return scenarios

    def _generate_generic_scenarios(
        self,
        issue: Issue,
        truck: Optional[Truck],
        load: Optional[Load],
        trucks: List[Truck],
    ) -> List[Scenario]:
        """Generate generic scenarios for unknown issue types."""
        scenarios = []

        # Wait and observe
        scenarios.append(Scenario(
            id=f"SCEN-{issue.id}-OBSERVE",
            name="Monitor and Reassess",
            description="Continue monitoring for 15 minutes and reassess situation",
            actions=[
                {"type": ActionType.WAIT.value, "duration_minutes": 15},
            ],
            estimated_cost=20,
            estimated_time_minutes=15,
            estimated_fuel_liters=0,
            reliability_score=0.5,
        ))

        # Escalate
        scenarios.append(Scenario(
            id=f"SCEN-{issue.id}-ESCALATE",
            name="Escalate to Human Operator",
            description="Request human review and decision",
            actions=[
                {"type": ActionType.ESCALATE.value, "issue_id": issue.id},
            ],
            estimated_cost=0,
            estimated_time_minutes=30,
            estimated_fuel_liters=0,
            reliability_score=0.9,
        ))

        return scenarios

    def _rank_scenarios(self, scenarios: List[Scenario]) -> List[Scenario]:
        """Rank scenarios by overall score."""

        def score_scenario(s: Scenario) -> float:
            # Weighted scoring
            time_score = 1 / (1 + s.estimated_time_minutes / 60)  # Prefer faster
            cost_score = 1 / (1 + s.estimated_cost / 100)  # Prefer cheaper
            reliability = s.reliability_score

            return 0.3 * time_score + 0.2 * cost_score + 0.5 * reliability

        return sorted(scenarios, key=score_scenario, reverse=True)
