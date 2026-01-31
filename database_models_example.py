"""
Example SQLAlchemy models for database implementation.
This shows what the database layer should look like.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, 
    ForeignKey, DECIMAL, ARRAY, JSON
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func

Base = declarative_base()


class TruckModel(Base):
    """SQLAlchemy model for trucks table."""
    __tablename__ = "trucks"

    id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    status = Column(String(20), nullable=False, default="idle")
    current_location_lat = Column(DECIMAL(10, 8))
    current_location_lng = Column(DECIMAL(11, 8))
    current_load_id = Column(String(50), ForeignKey("loads.id"))
    driver_id = Column(String(50))
    capacity_kg = Column(DECIMAL(10, 2), default=10000)
    fuel_level_percent = Column(DECIMAL(5, 2), default=100)
    total_distance_km = Column(DECIMAL(10, 2), default=0)
    total_deliveries = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    current_load = relationship("LoadModel", foreign_keys=[current_load_id])
    gps_readings = relationship("GPSReadingModel", back_populates="truck")
    routes = relationship("RouteModel", back_populates="truck")


class LoadModel(Base):
    """SQLAlchemy model for loads table."""
    __tablename__ = "loads"

    id = Column(String(50), primary_key=True)
    description = Column(Text, nullable=False)
    weight_kg = Column(DECIMAL(10, 2), nullable=False)
    volume_m3 = Column(DECIMAL(10, 3))
    priority = Column(String(20), default="normal")
    pickup_location_lat = Column(DECIMAL(10, 8), nullable=False)
    pickup_location_lng = Column(DECIMAL(11, 8), nullable=False)
    pickup_location_address = Column(Text)
    delivery_location_lat = Column(DECIMAL(10, 8), nullable=False)
    delivery_location_lng = Column(DECIMAL(11, 8), nullable=False)
    delivery_location_address = Column(Text)
    pickup_window_start = Column(DateTime)
    pickup_window_end = Column(DateTime)
    delivery_deadline = Column(DateTime)
    assigned_truck_id = Column(String(50), ForeignKey("trucks.id"))
    assigned_route_id = Column(String(50), ForeignKey("routes.id"))
    picked_up_at = Column(DateTime)
    delivered_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    assigned_truck = relationship("TruckModel", foreign_keys=[assigned_truck_id])
    assigned_route = relationship("RouteModel", foreign_keys=[assigned_route_id])


class RouteModel(Base):
    """SQLAlchemy model for routes table."""
    __tablename__ = "routes"

    id = Column(String(50), primary_key=True)
    truck_id = Column(String(50), ForeignKey("trucks.id"), nullable=False)
    origin_lat = Column(DECIMAL(10, 8), nullable=False)
    origin_lng = Column(DECIMAL(11, 8), nullable=False)
    destination_lat = Column(DECIMAL(10, 8), nullable=False)
    destination_lng = Column(DECIMAL(11, 8), nullable=False)
    estimated_distance_km = Column(DECIMAL(10, 2))
    estimated_duration_minutes = Column(Integer)
    estimated_fuel_consumption_liters = Column(DECIMAL(8, 2))
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    actual_distance_km = Column(DECIMAL(10, 2))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    truck = relationship("TruckModel", back_populates="routes")


class GPSReadingModel(Base):
    """SQLAlchemy model for GPS readings table."""
    __tablename__ = "gps_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    truck_id = Column(String(50), ForeignKey("trucks.id"), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    speed_kmh = Column(DECIMAL(6, 2), default=0)
    heading = Column(DECIMAL(5, 2), default=0)
    accuracy_meters = Column(DECIMAL(6, 2), default=10)

    # Relationships
    truck = relationship("TruckModel", back_populates="gps_readings")


class IssueModel(Base):
    """SQLAlchemy model for issues table."""
    __tablename__ = "issues"

    id = Column(String(50), primary_key=True)
    type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    description = Column(Text, nullable=False)
    affected_truck_ids = Column(ARRAY(String))  # PostgreSQL array
    affected_load_ids = Column(ARRAY(String))   # PostgreSQL array
    detected_at = Column(DateTime, default=func.now())
    resolved_at = Column(DateTime)
    issue_metadata = Column(JSON)  # JSON field for additional data


class DecisionModel(Base):
    """SQLAlchemy model for decisions table."""
    __tablename__ = "decisions"

    id = Column(String(50), primary_key=True)
    scenario_id = Column(String(50))
    action_type = Column(String(50), nullable=False)
    parameters = Column(JSON)
    score = Column(DECIMAL(3, 2))
    confidence = Column(DECIMAL(3, 2))
    rationale = Column(Text)
    llm_verified = Column(Boolean, default=False)
    human_approved = Column(Boolean, default=False)
    decided_at = Column(DateTime, default=func.now())
    executed_at = Column(DateTime)


class ControlLoopCycleModel(Base):
    """SQLAlchemy model for control loop cycles table."""
    __tablename__ = "control_loop_cycles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cycle_id = Column(String(50), nullable=False)
    phase = Column(String(20), nullable=False)
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    duration_ms = Column(Integer)
    issues_detected = Column(Integer, default=0)
    decisions_made = Column(Integer, default=0)
    success = Column(Boolean, default=True)
    error_message = Column(Text)


# Database Service Layer
class DatabaseService:
    """Service layer for database operations."""

    def __init__(self, session: Session):
        self.session = session

    # Truck operations
    def get_truck(self, truck_id: str) -> Optional[TruckModel]:
        """Get a truck by ID."""
        return self.session.query(TruckModel).filter(TruckModel.id == truck_id).first()

    def get_all_trucks(self) -> List[TruckModel]:
        """Get all trucks."""
        return self.session.query(TruckModel).all()

    def update_truck_location(self, truck_id: str, lat: float, lng: float) -> bool:
        """Update truck location."""
        truck = self.get_truck(truck_id)
        if truck:
            truck.current_location_lat = lat
            truck.current_location_lng = lng
            truck.updated_at = func.now()
            self.session.commit()
            return True
        return False

    def create_gps_reading(self, truck_id: str, lat: float, lng: float, 
                          speed: float, heading: float) -> GPSReadingModel:
        """Create a new GPS reading."""
        reading = GPSReadingModel(
            truck_id=truck_id,
            latitude=lat,
            longitude=lng,
            speed_kmh=speed,
            heading=heading
        )
        self.session.add(reading)
        self.session.commit()
        return reading

    # Load operations
    def get_pending_loads(self) -> List[LoadModel]:
        """Get loads without assigned trucks."""
        return self.session.query(LoadModel).filter(
            LoadModel.assigned_truck_id.is_(None)
        ).all()

    def assign_load_to_truck(self, load_id: str, truck_id: str) -> bool:
        """Assign a load to a truck."""
        load = self.session.query(LoadModel).filter(LoadModel.id == load_id).first()
        if load:
            load.assigned_truck_id = truck_id
            load.updated_at = func.now()
            self.session.commit()
            return True
        return False

    # Issue operations
    def create_issue(self, issue_data: dict) -> IssueModel:
        """Create a new issue."""
        issue = IssueModel(**issue_data)
        self.session.add(issue)
        self.session.commit()
        return issue

    def get_active_issues(self) -> List[IssueModel]:
        """Get unresolved issues."""
        return self.session.query(IssueModel).filter(
            IssueModel.resolved_at.is_(None)
        ).all()

    # Decision operations
    def create_decision(self, decision_data: dict) -> DecisionModel:
        """Create a new decision."""
        decision = DecisionModel(**decision_data)
        self.session.add(decision)
        self.session.commit()
        return decision

    def get_pending_decisions(self) -> List[DecisionModel]:
        """Get decisions awaiting human approval."""
        return self.session.query(DecisionModel).filter(
            DecisionModel.human_approved.is_(False),
            DecisionModel.executed_at.is_(None)
        ).all()

    # Analytics operations
    def get_fleet_summary(self) -> dict:
        """Get fleet summary statistics."""
        total_trucks = self.session.query(TruckModel).count()
        en_route = self.session.query(TruckModel).filter(
            TruckModel.status == "en_route"
        ).count()
        idle = self.session.query(TruckModel).filter(
            TruckModel.status == "idle"
        ).count()
        
        return {
            "total_trucks": total_trucks,
            "en_route": en_route,
            "idle": idle,
            "issues": self.session.query(IssueModel).filter(
                IssueModel.resolved_at.is_(None)
            ).count()
        }