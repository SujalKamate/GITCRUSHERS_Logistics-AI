"""
State management service for the Logistics AI Dashboard.
Singleton class that manages in-memory system state.
"""

import asyncio
from datetime import datetime
from typing import Optional
from src.models import (
    Truck, Route, Load, TrafficCondition, Decision,
    TruckStatus, ControlLoopPhase, ActionType
)


class StateManager:
    """
    Singleton class managing system state.
    Tracks trucks, routes, loads, traffic, decisions, and control loop state.
    """

    _instance: Optional["StateManager"] = None

    def __new__(cls) -> "StateManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Fleet state
        self.trucks: list[Truck] = []
        self.routes: list[Route] = []
        self.loads: list[Load] = []
        self.traffic_conditions: list[TrafficCondition] = []

        # Decision state
        self.pending_decisions: list[Decision] = []
        self.approved_decisions: list[Decision] = []
        self.rejected_decisions: list[Decision] = []

        # Control loop state
        self.control_loop_running: bool = False
        self.current_phase: ControlLoopPhase = ControlLoopPhase.OBSERVE
        self.total_cycles: int = 0
        self.cycle_id: str = ""
        self.loop_start_time: Optional[datetime] = None
        self.last_cycle_duration_ms: float = 0
        self.cycle_durations: list[float] = []

        # Background task reference
        self._loop_task: Optional[asyncio.Task] = None

        self._initialized = True

    def reset(self):
        """Reset state to initial values."""
        self.trucks = []
        self.routes = []
        self.loads = []
        self.traffic_conditions = []
        self.pending_decisions = []
        self.approved_decisions = []
        self.rejected_decisions = []
        self.control_loop_running = False
        self.current_phase = ControlLoopPhase.OBSERVE
        self.total_cycles = 0
        self.cycle_id = ""
        self.loop_start_time = None
        self.last_cycle_duration_ms = 0
        self.cycle_durations = []

    # =========================================================================
    # Fleet Management
    # =========================================================================

    def get_truck(self, truck_id: str) -> Optional[Truck]:
        """Get a truck by ID."""
        for truck in self.trucks:
            if truck.id == truck_id:
                return truck
        return None

    def update_truck(self, truck_id: str, **updates) -> Optional[Truck]:
        """Update a truck's properties."""
        truck = self.get_truck(truck_id)
        if truck:
            for key, value in updates.items():
                if hasattr(truck, key):
                    setattr(truck, key, value)
        return truck

    def get_fleet_summary(self) -> dict:
        """Get summary statistics for the fleet."""
        total = len(self.trucks)
        en_route = sum(1 for t in self.trucks if t.status == TruckStatus.EN_ROUTE)
        loading = sum(1 for t in self.trucks if t.status == TruckStatus.LOADING)
        unloading = sum(1 for t in self.trucks if t.status == TruckStatus.UNLOADING)
        idle = sum(1 for t in self.trucks if t.status == TruckStatus.IDLE)
        maintenance = sum(1 for t in self.trucks if t.status == TruckStatus.MAINTENANCE)
        stuck = sum(1 for t in self.trucks if t.status == TruckStatus.STUCK)
        delayed = sum(1 for t in self.trucks if t.status == TruckStatus.DELAYED)

        # Calculate loads summary
        total_loads = len(self.loads)
        pending_loads = sum(1 for l in self.loads if l.assigned_truck_id is None)
        in_transit = sum(1 for l in self.loads if l.picked_up_at and not l.delivered_at)
        delivered = sum(1 for l in self.loads if l.delivered_at)

        return {
            "total_trucks": total,
            "active_trucks": en_route + loading + unloading,
            "idle_trucks": idle,
            "trucks_with_issues": stuck + delayed,
            "total_loads": total_loads,
            "pending_loads": pending_loads,
            "in_transit_loads": in_transit,
            "delivered_loads": delivered,
        }

    # =========================================================================
    # Control Loop Management
    # =========================================================================

    def get_control_loop_status(self) -> dict:
        """Get current control loop status."""
        uptime_seconds = 0
        if self.loop_start_time:
            uptime_seconds = (datetime.utcnow() - self.loop_start_time).total_seconds()

        avg_duration = 0
        if self.cycle_durations:
            avg_duration = sum(self.cycle_durations) / len(self.cycle_durations)

        cycles_per_minute = 0
        if avg_duration > 0:
            cycles_per_minute = 60000 / avg_duration

        return {
            "current_state": {
                "current_phase": self.current_phase.value,
                "cycle_id": self.cycle_id,
                "total_cycles": self.total_cycles,
                "continue_loop": self.control_loop_running,
                "requires_human_intervention": len(self.pending_decisions) > 0,
            },
            "is_running": self.control_loop_running,
            "last_cycle_duration_ms": self.last_cycle_duration_ms,
            "average_cycle_duration_ms": avg_duration,
            "cycles_per_minute": cycles_per_minute,
            "uptime_seconds": uptime_seconds,
        }

    def start_control_loop(self):
        """Mark control loop as started."""
        self.control_loop_running = True
        self.loop_start_time = datetime.utcnow()
        self.cycle_id = f"CYCLE-{int(datetime.utcnow().timestamp())}"

    def stop_control_loop(self):
        """Mark control loop as stopped."""
        self.control_loop_running = False

    def advance_phase(self):
        """Advance to the next phase in the control loop."""
        phases = list(ControlLoopPhase)
        current_idx = phases.index(self.current_phase)
        next_idx = (current_idx + 1) % len(phases)
        self.current_phase = phases[next_idx]

        # If we completed a full cycle
        if next_idx == 0:
            self.total_cycles += 1
            self.cycle_id = f"CYCLE-{int(datetime.utcnow().timestamp())}"

    def record_cycle_duration(self, duration_ms: float):
        """Record a cycle duration."""
        self.last_cycle_duration_ms = duration_ms
        self.cycle_durations.append(duration_ms)
        # Keep only last 100 durations
        if len(self.cycle_durations) > 100:
            self.cycle_durations = self.cycle_durations[-100:]

    # =========================================================================
    # Decision Management
    # =========================================================================

    def add_pending_decision(self, decision: Decision):
        """Add a decision to pending list."""
        self.pending_decisions.append(decision)

    def approve_decision(self, decision_id: str, approved: bool = True) -> Optional[Decision]:
        """Approve or reject a pending decision."""
        for i, decision in enumerate(self.pending_decisions):
            if decision.id == decision_id:
                decision.human_approved = approved
                self.pending_decisions.pop(i)
                if approved:
                    self.approved_decisions.append(decision)
                else:
                    self.rejected_decisions.append(decision)
                return decision
        return None

    def get_pending_decisions_response(self) -> dict:
        """Get pending decisions response."""
        return {
            "decisions": [d.model_dump() for d in self.pending_decisions],
            "requires_human_approval": [
                d.model_dump() for d in self.pending_decisions
                if not d.llm_verified
            ],
            "auto_approved": [d.model_dump() for d in self.approved_decisions[-10:]],
            "rejected": [d.model_dump() for d in self.rejected_decisions[-10:]],
        }


# Global singleton instance
state_manager = StateManager()
