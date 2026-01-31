"""
Data models for the Agentic Logistics Control System.

This module defines all Pydantic models and LangGraph state schemas
used throughout the control loop.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ============================================================================
# Enums
# ============================================================================

class TruckStatus(str, Enum):
    """Status of a truck in the fleet."""
    IDLE = "idle"
    EN_ROUTE = "en_route"
    LOADING = "loading"
    UNLOADING = "unloading"
    MAINTENANCE = "maintenance"
    STUCK = "stuck"
    DELAYED = "delayed"


class TrafficLevel(str, Enum):
    """Traffic condition levels."""
    FREE_FLOW = "free_flow"
    LIGHT = "light"
    MODERATE = "moderate"
    HEAVY = "heavy"
    STANDSTILL = "standstill"


class LoadPriority(str, Enum):
    """Priority levels for loads."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class ActionType(str, Enum):
    """Types of actions the system can execute."""
    REROUTE = "reroute"
    REASSIGN = "reassign"
    DISPATCH = "dispatch"
    WAIT = "wait"
    NOTIFY = "notify"
    ESCALATE = "escalate"


class ControlLoopPhase(str, Enum):
    """Phases of the control loop."""
    OBSERVE = "observe"
    REASON = "reason"
    PLAN = "plan"
    DECIDE = "decide"
    ACT = "act"
    FEEDBACK = "feedback"


# ============================================================================
# Core Data Models
# ============================================================================

class Location(BaseModel):
    """Geographic location with coordinates."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    name: Optional[str] = None

    def distance_to(self, other: "Location") -> float:
        """Calculate approximate distance in km using Haversine formula."""
        from math import radians, sin, cos, sqrt, atan2

        R = 6371  # Earth's radius in km

        lat1, lon1 = radians(self.latitude), radians(self.longitude)
        lat2, lon2 = radians(other.latitude), radians(other.longitude)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))

        return R * c


class GPSReading(BaseModel):
    """GPS reading from a truck."""
    truck_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    location: Location
    speed_kmh: float = Field(ge=0)
    heading: float = Field(ge=0, le=360, description="Compass heading in degrees")
    accuracy_meters: float = Field(ge=0, default=10.0)


class Truck(BaseModel):
    """Truck entity in the fleet."""
    id: str
    name: str
    status: TruckStatus = TruckStatus.IDLE
    current_location: Optional[Location] = None
    current_load_id: Optional[str] = None
    driver_id: Optional[str] = None
    capacity_kg: float = Field(gt=0, default=10000)
    fuel_level_percent: float = Field(ge=0, le=100, default=100)
    last_gps_reading: Optional[GPSReading] = None

    # Performance metrics
    total_distance_km: float = Field(ge=0, default=0)
    total_deliveries: int = Field(ge=0, default=0)


class RoutePoint(BaseModel):
    """A point along a route."""
    location: Location
    sequence: int
    estimated_arrival: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    is_waypoint: bool = False
    is_destination: bool = False


class Route(BaseModel):
    """Route for a truck to follow."""
    id: str
    truck_id: str
    origin: Location
    destination: Location
    waypoints: list[RoutePoint] = Field(default_factory=list)

    # Estimates
    estimated_distance_km: float = Field(ge=0)
    estimated_duration_minutes: float = Field(ge=0)
    estimated_fuel_consumption_liters: float = Field(ge=0)

    # Actual tracking
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_distance_km: Optional[float] = None


class Load(BaseModel):
    """Load/cargo to be transported."""
    id: str
    description: str
    weight_kg: float = Field(gt=0)
    volume_m3: Optional[float] = Field(None, gt=0)
    priority: LoadPriority = LoadPriority.NORMAL

    # Locations
    pickup_location: Location
    delivery_location: Location

    # Timing
    pickup_window_start: Optional[datetime] = None
    pickup_window_end: Optional[datetime] = None
    delivery_deadline: Optional[datetime] = None

    # Assignment
    assigned_truck_id: Optional[str] = None
    assigned_route_id: Optional[str] = None

    # Status
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None


class TrafficCondition(BaseModel):
    """Traffic condition on a road segment."""
    segment_id: str
    level: TrafficLevel
    speed_kmh: float = Field(ge=0)
    delay_minutes: float = Field(ge=0, default=0)
    incident_description: Optional[str] = None
    affected_routes: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @property
    def delay_factor(self) -> float:
        """Calculate delay factor (1.0 = no delay, 2.0 = double time)."""
        factors = {
            TrafficLevel.FREE_FLOW: 1.0,
            TrafficLevel.LIGHT: 1.1,
            TrafficLevel.MODERATE: 1.3,
            TrafficLevel.HEAVY: 1.7,
            TrafficLevel.STANDSTILL: 3.0,
        }
        return factors.get(self.level, 1.5)


# ============================================================================
# Analysis and Reasoning Models
# ============================================================================

class Issue(BaseModel):
    """An issue detected by the reasoning system."""
    id: str
    type: str  # e.g., "delay", "capacity_mismatch", "traffic", "breakdown"
    severity: str  # "low", "medium", "high", "critical"
    description: str
    affected_truck_ids: list[str] = Field(default_factory=list)
    affected_load_ids: list[str] = Field(default_factory=list)
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ReasoningResult(BaseModel):
    """Result from the reasoning layer."""
    situation_summary: str
    issues: list[Issue] = Field(default_factory=list)
    risk_assessment: str
    recommendations: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
    reasoning_trace: list[str] = Field(default_factory=list)


# ============================================================================
# Planning Models
# ============================================================================

class Scenario(BaseModel):
    """A planning scenario generated by the simulation."""
    id: str
    name: str
    description: str
    actions: list[dict[str, Any]] = Field(default_factory=list)

    # Projected outcomes
    estimated_cost: float = Field(ge=0)
    estimated_time_minutes: float = Field(ge=0)
    estimated_fuel_liters: float = Field(ge=0)
    reliability_score: float = Field(ge=0, le=1)

    # Simulation details
    simulation_parameters: dict[str, Any] = Field(default_factory=dict)
    simulation_results: dict[str, Any] = Field(default_factory=dict)


class PlanningResult(BaseModel):
    """Result from the planning layer."""
    issue_id: Optional[str] = None
    scenarios: list[Scenario] = Field(default_factory=list)
    comparison_matrix: dict[str, dict[str, float]] = Field(default_factory=dict)
    recommended_scenario_id: Optional[str] = None


# ============================================================================
# Decision Models
# ============================================================================

class Decision(BaseModel):
    """A decision made by the decision layer."""
    id: str
    scenario_id: str
    action_type: ActionType
    parameters: dict[str, Any] = Field(default_factory=dict)

    # Evaluation
    score: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    rationale: str

    # Verification
    llm_verified: bool = False
    human_approved: bool = False

    # Timing
    decided_at: datetime = Field(default_factory=datetime.utcnow)


class DecisionResult(BaseModel):
    """Result from the decision layer."""
    selected_decision: Optional[Decision] = None
    alternatives: list[Decision] = Field(default_factory=list)
    requires_human_approval: bool = False
    decision_trace: list[str] = Field(default_factory=list)


# ============================================================================
# Action Models
# ============================================================================

class ActionResult(BaseModel):
    """Result from executing an action."""
    action_id: str
    decision_id: str
    success: bool
    message: str
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    details: dict[str, Any] = Field(default_factory=dict)
    rollback_possible: bool = False


class Notification(BaseModel):
    """A notification to send to stakeholders."""
    id: str
    recipient_type: str  # "driver", "dispatcher", "customer", "system"
    recipient_id: str
    subject: str
    message: str
    priority: str = "normal"
    sent_at: Optional[datetime] = None
    delivered: bool = False


# ============================================================================
# Feedback Models
# ============================================================================

class OutcomeMetrics(BaseModel):
    """Metrics from monitoring action outcomes."""
    decision_id: str
    predicted_time_minutes: float
    actual_time_minutes: Optional[float] = None
    predicted_cost: float
    actual_cost: Optional[float] = None
    success: Optional[bool] = None
    deviation_percent: Optional[float] = None


class LearningUpdate(BaseModel):
    """An update to system parameters based on feedback."""
    parameter_name: str
    old_value: float
    new_value: float
    reason: str
    applied_at: datetime = Field(default_factory=datetime.utcnow)


class FeedbackResult(BaseModel):
    """Result from the feedback layer."""
    outcomes: list[OutcomeMetrics] = Field(default_factory=list)
    learning_updates: list[LearningUpdate] = Field(default_factory=list)
    system_health: str
    recommendations: list[str] = Field(default_factory=list)


# ============================================================================
# LangGraph State Schema
# ============================================================================

class AgentState(TypedDict, total=False):
    """
    LangGraph state schema for the control loop.

    This state is passed between all nodes in the control loop graph.
    """
    # Current phase
    current_phase: ControlLoopPhase
    cycle_id: str

    # Fleet state
    trucks: list[dict]  # Serialized Truck objects
    routes: list[dict]  # Serialized Route objects
    loads: list[dict]   # Serialized Load objects
    traffic_conditions: list[dict]  # Serialized TrafficCondition objects

    # Observation data
    gps_readings: list[dict]
    observation_timestamp: str

    # Reasoning results
    reasoning_result: Optional[dict]
    current_issues: list[dict]

    # Planning results
    planning_result: Optional[dict]
    scenarios: list[dict]

    # Decision results
    decision_result: Optional[dict]
    selected_decision: Optional[dict]

    # Action results
    action_results: list[dict]
    notifications_sent: list[dict]

    # Feedback results
    feedback_result: Optional[dict]

    # Control flags
    continue_loop: bool
    requires_human_intervention: bool
    error_message: Optional[str]

    # Metrics
    cycle_start_time: str
    cycle_end_time: Optional[str]
    total_cycles: int


# ============================================================================
# System State (High-level wrapper)
# ============================================================================

class SystemState(BaseModel):
    """
    High-level system state combining all components.
    Used for checkpointing and serialization.
    """
    # Fleet
    trucks: list[Truck] = Field(default_factory=list)
    routes: list[Route] = Field(default_factory=list)
    loads: list[Load] = Field(default_factory=list)
    traffic_conditions: list[TrafficCondition] = Field(default_factory=list)

    # Current status
    active_issues: list[Issue] = Field(default_factory=list)
    pending_decisions: list[Decision] = Field(default_factory=list)

    # History
    recent_actions: list[ActionResult] = Field(default_factory=list)
    recent_outcomes: list[OutcomeMetrics] = Field(default_factory=list)

    # Metadata
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    total_cycles_completed: int = 0

    def to_agent_state(self) -> AgentState:
        """Convert to LangGraph AgentState."""
        return AgentState(
            trucks=[t.model_dump() for t in self.trucks],
            routes=[r.model_dump() for r in self.routes],
            loads=[l.model_dump() for l in self.loads],
            traffic_conditions=[tc.model_dump() for tc in self.traffic_conditions],
            current_issues=[i.model_dump() for i in self.active_issues],
            total_cycles=self.total_cycles_completed,
            continue_loop=True,
            requires_human_intervention=False,
        )
