"""
Database service layer replacing the in-memory StateManager.
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from src.models import (
    Truck, Route, Load, TrafficCondition, Issue, Decision,
    TruckStatus, ControlLoopPhase, ActionType
)
from database_models_example import (
    TruckModel, RouteModel, LoadModel, GPSReadingModel,
    IssueModel, DecisionModel, ControlLoopCycleModel
)


class DatabaseService:
    """
    Database service layer for persistent storage.
    Replaces the in-memory StateManager with actual database operations.
    """

    def __init__(self, session: Session):
        self.session = session

    # =========================================================================
    # Fleet Management
    # =========================================================================

    def get_all_trucks(self) -> List[Truck]:
        """Get all trucks from database."""
        truck_models = self.session.query(TruckModel).all()
        return [self._truck_model_to_pydantic(tm) for tm in truck_models]

    def get_truck(self, truck_id: str) -> Optional[Truck]:
        """Get a truck by ID."""
        truck_model = self.session.query(TruckModel).filter(TruckModel.id == truck_id).first()
        if truck_model:
            return self._truck_model_to_pydantic(truck_model)
        return None

    def create_truck(self, truck: Truck) -> Truck:
        """Create a new truck."""
        truck_model = TruckModel(
            id=truck.id,
            name=truck.name,
            status=truck.status.value,
            current_location_lat=truck.current_location.latitude if truck.current_location else None,
            current_location_lng=truck.current_location.longitude if truck.current_location else None,
            driver_id=truck.driver_id,
            capacity_kg=truck.capacity_kg,
            fuel_level_percent=truck.fuel_level_percent,
            total_distance_km=truck.total_distance_km,
            total_deliveries=truck.total_deliveries,
        )
        self.session.add(truck_model)
        self.session.commit()
        return self._truck_model_to_pydantic(truck_model)

    def update_truck(self, truck_id: str, **updates) -> Optional[Truck]:
        """Update a truck's properties."""
        truck_model = self.session.query(TruckModel).filter(TruckModel.id == truck_id).first()
        if not truck_model:
            return None

        for key, value in updates.items():
            if key == 'status' and hasattr(value, 'value'):
                setattr(truck_model, key, value.value)
            elif key == 'current_location' and value:
                truck_model.current_location_lat = value.latitude
                truck_model.current_location_lng = value.longitude
            elif hasattr(truck_model, key):
                setattr(truck_model, key, value)

        truck_model.updated_at = datetime.utcnow()
        self.session.commit()
        return self._truck_model_to_pydantic(truck_model)

    def create_gps_reading(self, truck_id: str, lat: float, lng: float, 
                          speed: float, heading: float) -> None:
        """Create a new GPS reading and update truck location."""
        # Create GPS reading
        reading = GPSReadingModel(
            truck_id=truck_id,
            latitude=lat,
            longitude=lng,
            speed_kmh=speed,
            heading=heading
        )
        self.session.add(reading)

        # Update truck location
        truck = self.session.query(TruckModel).filter(TruckModel.id == truck_id).first()
        if truck:
            truck.current_location_lat = lat
            truck.current_location_lng = lng
            truck.updated_at = datetime.utcnow()

        self.session.commit()

    # =========================================================================
    # Load Management
    # =========================================================================

    def get_all_loads(self) -> List[Load]:
        """Get all loads from database."""
        load_models = self.session.query(LoadModel).all()
        return [self._load_model_to_pydantic(lm) for lm in load_models]

    def get_pending_loads(self) -> List[Load]:
        """Get loads without assigned trucks."""
        load_models = self.session.query(LoadModel).filter(
            LoadModel.assigned_truck_id.is_(None)
        ).all()
        return [self._load_model_to_pydantic(lm) for lm in load_models]

    def assign_load_to_truck(self, load_id: str, truck_id: str) -> bool:
        """Assign a load to a truck."""
        load_model = self.session.query(LoadModel).filter(LoadModel.id == load_id).first()
        if load_model:
            load_model.assigned_truck_id = truck_id
            load_model.updated_at = datetime.utcnow()
            self.session.commit()
            return True
        return False

    def create_load(self, load: Load) -> Load:
        """Create a new load."""
        load_model = LoadModel(
            id=load.id,
            description=load.description,
            weight_kg=load.weight_kg,
            volume_m3=load.volume_m3,
            priority=load.priority.value,
            pickup_location_lat=load.pickup_location.latitude,
            pickup_location_lng=load.pickup_location.longitude,
            delivery_location_lat=load.delivery_location.latitude,
            delivery_location_lng=load.delivery_location.longitude,
            pickup_window_start=load.pickup_window_start,
            pickup_window_end=load.pickup_window_end,
            delivery_deadline=load.delivery_deadline,
            assigned_truck_id=load.assigned_truck_id,
        )
        self.session.add(load_model)
        self.session.commit()
        return self._load_model_to_pydantic(load_model)

    # =========================================================================
    # Issue Management
    # =========================================================================

    def create_issue(self, issue: Issue) -> Issue:
        """Create a new issue."""
        issue_model = IssueModel(
            id=issue.id,
            type=issue.type,
            severity=issue.severity,
            description=issue.description,
            affected_truck_ids=issue.affected_truck_ids,
            affected_load_ids=issue.affected_load_ids,
            metadata=issue.metadata,
        )
        self.session.add(issue_model)
        self.session.commit()
        return self._issue_model_to_pydantic(issue_model)

    def get_active_issues(self) -> List[Issue]:
        """Get unresolved issues."""
        issue_models = self.session.query(IssueModel).filter(
            IssueModel.resolved_at.is_(None)
        ).all()
        return [self._issue_model_to_pydantic(im) for im in issue_models]

    def resolve_issue(self, issue_id: str) -> bool:
        """Mark an issue as resolved."""
        issue_model = self.session.query(IssueModel).filter(IssueModel.id == issue_id).first()
        if issue_model:
            issue_model.resolved_at = datetime.utcnow()
            self.session.commit()
            return True
        return False

    # =========================================================================
    # Decision Management
    # =========================================================================

    def create_decision(self, decision: Decision) -> Decision:
        """Create a new decision."""
        decision_model = DecisionModel(
            id=decision.id,
            scenario_id=decision.scenario_id,
            action_type=decision.action_type.value,
            parameters=decision.parameters,
            score=decision.score,
            confidence=decision.confidence,
            rationale=decision.rationale,
            llm_verified=decision.llm_verified,
            human_approved=decision.human_approved,
        )
        self.session.add(decision_model)
        self.session.commit()
        return self._decision_model_to_pydantic(decision_model)

    def get_pending_decisions(self) -> List[Decision]:
        """Get decisions awaiting human approval."""
        decision_models = self.session.query(DecisionModel).filter(
            DecisionModel.human_approved.is_(False),
            DecisionModel.executed_at.is_(None)
        ).all()
        return [self._decision_model_to_pydantic(dm) for dm in decision_models]

    def approve_decision(self, decision_id: str, approved: bool = True) -> Optional[Decision]:
        """Approve or reject a decision."""
        decision_model = self.session.query(DecisionModel).filter(
            DecisionModel.id == decision_id
        ).first()
        if decision_model:
            decision_model.human_approved = approved
            self.session.commit()
            return self._decision_model_to_pydantic(decision_model)
        return None

    # =========================================================================
    # Analytics and Reporting
    # =========================================================================

    def get_fleet_summary(self) -> dict:
        """Get fleet summary statistics."""
        total_trucks = self.session.query(TruckModel).count()
        
        en_route = self.session.query(TruckModel).filter(
            TruckModel.status == TruckStatus.EN_ROUTE.value
        ).count()
        
        idle = self.session.query(TruckModel).filter(
            TruckModel.status == TruckStatus.IDLE.value
        ).count()
        
        loading = self.session.query(TruckModel).filter(
            TruckModel.status == TruckStatus.LOADING.value
        ).count()
        
        issues = self.session.query(IssueModel).filter(
            IssueModel.resolved_at.is_(None)
        ).count()

        total_loads = self.session.query(LoadModel).count()
        pending_loads = self.session.query(LoadModel).filter(
            LoadModel.assigned_truck_id.is_(None)
        ).count()
        
        in_transit = self.session.query(LoadModel).filter(
            and_(LoadModel.picked_up_at.isnot(None), LoadModel.delivered_at.is_(None))
        ).count()
        
        delivered = self.session.query(LoadModel).filter(
            LoadModel.delivered_at.isnot(None)
        ).count()

        return {
            "total_trucks": total_trucks,
            "active_trucks": en_route + loading,
            "idle_trucks": idle,
            "trucks_with_issues": issues,
            "total_loads": total_loads,
            "pending_loads": pending_loads,
            "in_transit_loads": in_transit,
            "delivered_loads": delivered,
        }

    # =========================================================================
    # Control Loop Management
    # =========================================================================

    def record_control_loop_cycle(self, cycle_id: str, phase: ControlLoopPhase, 
                                 duration_ms: int, issues_detected: int, 
                                 decisions_made: int, success: bool = True,
                                 error_message: str = None) -> None:
        """Record a control loop cycle."""
        cycle = ControlLoopCycleModel(
            cycle_id=cycle_id,
            phase=phase.value,
            duration_ms=duration_ms,
            issues_detected=issues_detected,
            decisions_made=decisions_made,
            success=success,
            error_message=error_message,
            completed_at=datetime.utcnow()
        )
        self.session.add(cycle)
        self.session.commit()

    # =========================================================================
    # Model Conversion Helpers
    # =========================================================================

    def _truck_model_to_pydantic(self, truck_model: TruckModel) -> Truck:
        """Convert SQLAlchemy model to Pydantic model."""
        from src.models import Location
        
        location = None
        if truck_model.current_location_lat and truck_model.current_location_lng:
            location = Location(
                latitude=truck_model.current_location_lat,
                longitude=truck_model.current_location_lng
            )

        return Truck(
            id=truck_model.id,
            name=truck_model.name,
            status=TruckStatus(truck_model.status),
            current_location=location,
            current_load_id=truck_model.current_load_id,
            driver_id=truck_model.driver_id,
            capacity_kg=truck_model.capacity_kg,
            fuel_level_percent=truck_model.fuel_level_percent,
            total_distance_km=truck_model.total_distance_km,
            total_deliveries=truck_model.total_deliveries,
        )

    def _load_model_to_pydantic(self, load_model: LoadModel) -> Load:
        """Convert load model to Pydantic."""
        from src.models import Location, LoadPriority
        
        pickup_location = Location(
            latitude=load_model.pickup_location_lat,
            longitude=load_model.pickup_location_lng
        )
        
        delivery_location = Location(
            latitude=load_model.delivery_location_lat,
            longitude=load_model.delivery_location_lng
        )

        return Load(
            id=load_model.id,
            description=load_model.description,
            weight_kg=load_model.weight_kg,
            volume_m3=load_model.volume_m3,
            priority=LoadPriority(load_model.priority),
            pickup_location=pickup_location,
            delivery_location=delivery_location,
            pickup_window_start=load_model.pickup_window_start,
            pickup_window_end=load_model.pickup_window_end,
            delivery_deadline=load_model.delivery_deadline,
            assigned_truck_id=load_model.assigned_truck_id,
            assigned_route_id=load_model.assigned_route_id,
            picked_up_at=load_model.picked_up_at,
            delivered_at=load_model.delivered_at,
        )

    def _issue_model_to_pydantic(self, issue_model: IssueModel) -> Issue:
        """Convert issue model to Pydantic."""
        return Issue(
            id=issue_model.id,
            type=issue_model.type,
            severity=issue_model.severity,
            description=issue_model.description,
            affected_truck_ids=issue_model.affected_truck_ids or [],
            affected_load_ids=issue_model.affected_load_ids or [],
            detected_at=issue_model.detected_at,
            metadata=issue_model.metadata or {},
        )

    def _decision_model_to_pydantic(self, decision_model: DecisionModel) -> Decision:
        """Convert decision model to Pydantic."""
        return Decision(
            id=decision_model.id,
            scenario_id=decision_model.scenario_id,
            action_type=ActionType(decision_model.action_type),
            parameters=decision_model.parameters or {},
            score=decision_model.score,
            confidence=decision_model.confidence,
            rationale=decision_model.rationale,
            llm_verified=decision_model.llm_verified,
            human_approved=decision_model.human_approved,
            decided_at=decision_model.decided_at,
        )