"""
LangGraph observation node for the perception layer.

This node is the entry point of the control loop, responsible for:
- Collecting data from all sources
- Preprocessing and validating data
- Updating the agent state with observations
"""
from datetime import datetime
from typing import Any, Callable
import structlog

from src.models import (
    AgentState, ControlLoopPhase, Truck, Route, TruckStatus, Location
)
from src.perception.collectors import (
    GPSCollector, TrafficCollector, LoadCollector, AggregatedCollector
)
from src.perception.preprocessor import DataPreprocessor

logger = structlog.get_logger(__name__)


def create_observation_node(
    gps_collector: GPSCollector = None,
    traffic_collector: TrafficCollector = None,
    load_collector: LoadCollector = None,
    preprocessor: DataPreprocessor = None,
) -> Callable[[AgentState], AgentState]:
    """
    Create an observation node for the LangGraph control loop.

    Args:
        gps_collector: GPS data collector (optional, created if not provided)
        traffic_collector: Traffic data collector (optional)
        load_collector: Load data collector (optional)
        preprocessor: Data preprocessor (optional)

    Returns:
        A function that can be used as a LangGraph node
    """
    # Initialize components with defaults if not provided
    _gps_collector = gps_collector or GPSCollector(simulate=True)
    _traffic_collector = traffic_collector or TrafficCollector(simulate=True)
    _load_collector = load_collector or LoadCollector(simulate=True)
    _preprocessor = preprocessor or DataPreprocessor()

    async def observation_node(state: AgentState) -> AgentState:
        """
        Observation node that collects and preprocesses data.

        This is the OBSERVE phase of the control loop:
        OBSERVE -> REASON -> PLAN -> DECIDE -> ACT -> FEEDBACK

        Args:
            state: Current agent state

        Returns:
            Updated agent state with observations
        """
        logger.info(
            "Starting observation phase",
            cycle_id=state.get("cycle_id"),
            total_cycles=state.get("total_cycles", 0)
        )

        try:
            # Reconstruct trucks from state
            trucks = [
                Truck(**t) for t in state.get("trucks", [])
            ]

            # Update collector with current trucks
            _gps_collector.set_trucks(trucks)

            # Reconstruct routes for traffic correlation
            routes = [
                Route(**r) for r in state.get("routes", [])
            ]

            # Collect all data concurrently
            aggregated = AggregatedCollector(
                _gps_collector, _traffic_collector, _load_collector
            )

            import asyncio
            collection_result = await aggregated.collect_all()

            # Preprocess GPS readings
            gps_readings, updated_trucks = _preprocessor.preprocess_gps_readings(
                collection_result["gps_readings"],
                trucks
            )

            # Preprocess traffic conditions
            traffic_conditions = _preprocessor.preprocess_traffic_conditions(
                collection_result["traffic_conditions"],
                routes
            )

            # Preprocess loads
            loads = _preprocessor.preprocess_loads(
                collection_result["loads"]
            )

            # Get preprocessing summary
            preprocessing_summary = _preprocessor.get_preprocessing_summary()

            # Update state
            updated_state: AgentState = {
                **state,
                "current_phase": ControlLoopPhase.OBSERVE,
                "observation_timestamp": datetime.utcnow().isoformat(),
                "trucks": [t.model_dump() for t in updated_trucks],
                "gps_readings": [r.model_dump() for r in gps_readings],
                "traffic_conditions": [tc.model_dump() for tc in traffic_conditions],
                "loads": [l.model_dump() for l in loads],
                "error_message": None,
            }

            # Add anomalies to issues if any critical ones detected
            if preprocessing_summary["anomalies_detected"] > 0:
                logger.warning(
                    "Anomalies detected during observation",
                    count=preprocessing_summary["anomalies_detected"],
                    anomalies=preprocessing_summary["recent_anomalies"]
                )

            logger.info(
                "Observation phase completed",
                cycle_id=state.get("cycle_id"),
                trucks=len(updated_trucks),
                gps_readings=len(gps_readings),
                traffic_conditions=len(traffic_conditions),
                loads=len(loads),
                anomalies=preprocessing_summary["anomalies_detected"]
            )

            return updated_state

        except Exception as e:
            logger.error(
                "Observation phase failed",
                cycle_id=state.get("cycle_id"),
                error=str(e)
            )
            return {
                **state,
                "current_phase": ControlLoopPhase.OBSERVE,
                "error_message": f"Observation failed: {str(e)}",
                "continue_loop": False,
            }

    # Return sync wrapper for LangGraph compatibility
    def sync_observation_node(state: AgentState) -> AgentState:
        """Synchronous wrapper for the observation node."""
        import asyncio
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(observation_node(state))

    return sync_observation_node


def create_sample_fleet() -> list[Truck]:
    """Create a sample fleet for testing."""
    return [
        Truck(
            id="TRK-001",
            name="Alpha Hauler",
            status=TruckStatus.EN_ROUTE,
            current_location=Location(latitude=40.7128, longitude=-74.0060),
            driver_id="DRV-001",
            capacity_kg=15000,
            fuel_level_percent=75.0,
        ),
        Truck(
            id="TRK-002",
            name="Beta Carrier",
            status=TruckStatus.EN_ROUTE,
            current_location=Location(latitude=40.7580, longitude=-73.9855),
            driver_id="DRV-002",
            capacity_kg=12000,
            fuel_level_percent=60.0,
        ),
        Truck(
            id="TRK-003",
            name="Gamma Transport",
            status=TruckStatus.IDLE,
            current_location=Location(latitude=40.6892, longitude=-74.0445),
            driver_id="DRV-003",
            capacity_kg=10000,
            fuel_level_percent=90.0,
        ),
        Truck(
            id="TRK-004",
            name="Delta Freight",
            status=TruckStatus.LOADING,
            current_location=Location(latitude=40.7282, longitude=-73.7949),
            driver_id="DRV-004",
            capacity_kg=18000,
            fuel_level_percent=45.0,
        ),
        Truck(
            id="TRK-005",
            name="Epsilon Mover",
            status=TruckStatus.EN_ROUTE,
            current_location=Location(latitude=40.7614, longitude=-73.9776),
            driver_id="DRV-005",
            capacity_kg=14000,
            fuel_level_percent=55.0,
        ),
    ]
