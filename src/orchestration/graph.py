"""
LangGraph StateGraph implementation for the control loop.

Implements the complete control loop:
OBSERVE -> REASON -> PLAN -> DECIDE -> ACT -> FEEDBACK -> (loop)
"""
import uuid
from datetime import datetime
from typing import Any, Dict, Literal
import structlog

from langgraph.graph import StateGraph, END

from src.models import AgentState, ControlLoopPhase, Truck
from src.perception.observation_node import create_observation_node
from src.reasoning.reasoning_node import create_reasoning_node
from src.planning.planning_node import create_planning_node
from src.decision.decision_node import create_decision_node

logger = structlog.get_logger(__name__)


def create_action_node():
    """Create action execution node."""
    def action_node(state: AgentState) -> AgentState:
        """Execute decided actions."""
        logger.info("Starting action phase", cycle_id=state.get("cycle_id"))

        decision = state.get("selected_decision")
        action_results = []

        if decision:
            # Simulate action execution
            action_results.append({
                "action_id": f"ACT-{uuid.uuid4().hex[:8]}",
                "decision_id": decision.get("id"),
                "success": True,
                "message": f"Executed {decision.get('action_type')}",
                "executed_at": datetime.utcnow().isoformat(),
            })

        return {
            **state,
            "current_phase": ControlLoopPhase.ACT,
            "action_results": action_results,
        }

    return action_node


def create_feedback_node():
    """Create feedback/learning node."""
    def feedback_node(state: AgentState) -> AgentState:
        """Monitor outcomes and learn."""
        logger.info("Starting feedback phase", cycle_id=state.get("cycle_id"))

        feedback_result = {
            "outcomes": [],
            "learning_updates": [],
            "system_health": "healthy",
            "recommendations": [],
        }

        # Analyze action results
        for action in state.get("action_results", []):
            if action.get("success"):
                feedback_result["outcomes"].append({
                    "action_id": action.get("action_id"),
                    "success": True,
                })

        return {
            **state,
            "current_phase": ControlLoopPhase.FEEDBACK,
            "feedback_result": feedback_result,
            "cycle_end_time": datetime.utcnow().isoformat(),
            "total_cycles": state.get("total_cycles", 0) + 1,
        }

    return feedback_node


def should_continue(state: AgentState) -> Literal["continue", "stop", "human"]:
    """Determine if control loop should continue."""
    if state.get("error_message"):
        return "stop"

    if state.get("requires_human_intervention"):
        return "human"

    if not state.get("continue_loop", True):
        return "stop"

    # Check if issues were resolved
    if not state.get("current_issues"):
        return "stop"

    return "continue"


def create_control_loop_graph() -> StateGraph:
    """
    Create the complete LangGraph control loop.

    Returns:
        Compiled StateGraph
    """
    # Create nodes
    observe_node = create_observation_node()
    reason_node = create_reasoning_node()
    plan_node = create_planning_node()
    decide_node = create_decision_node()
    action_node = create_action_node()
    feedback_node = create_feedback_node()

    # Build graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("observe", observe_node)
    graph.add_node("reason", reason_node)
    graph.add_node("plan", plan_node)
    graph.add_node("decide", decide_node)
    graph.add_node("act", action_node)
    graph.add_node("feedback", feedback_node)

    # Add edges (linear flow)
    graph.add_edge("observe", "reason")
    graph.add_edge("reason", "plan")
    graph.add_edge("plan", "decide")
    graph.add_edge("decide", "act")
    graph.add_edge("act", "feedback")

    # Conditional edge from feedback
    graph.add_conditional_edges(
        "feedback",
        should_continue,
        {
            "continue": "observe",
            "stop": END,
            "human": END,
        }
    )

    # Set entry point
    graph.set_entry_point("observe")

    logger.info("Control loop graph created")

    return graph.compile()


def run_control_loop(
    initial_trucks: list[Truck] = None,
    max_cycles: int = 1,
) -> AgentState:
    """
    Run the control loop.

    Args:
        initial_trucks: Initial fleet state
        max_cycles: Maximum cycles to run

    Returns:
        Final state
    """
    # Create initial state
    state: AgentState = {
        "current_phase": ControlLoopPhase.OBSERVE,
        "cycle_id": str(uuid.uuid4()),
        "trucks": [t.model_dump() for t in (initial_trucks or [])],
        "routes": [],
        "loads": [],
        "traffic_conditions": [],
        "gps_readings": [],
        "observation_timestamp": "",
        "reasoning_result": None,
        "current_issues": [],
        "planning_result": None,
        "scenarios": [],
        "decision_result": None,
        "selected_decision": None,
        "action_results": [],
        "notifications_sent": [],
        "feedback_result": None,
        "continue_loop": max_cycles > 1,
        "requires_human_intervention": False,
        "error_message": None,
        "cycle_start_time": datetime.utcnow().isoformat(),
        "cycle_end_time": None,
        "total_cycles": 0,
    }

    # Create and run graph
    graph = create_control_loop_graph()

    logger.info("Starting control loop", max_cycles=max_cycles)

    # Run the graph
    result = graph.invoke(state)

    logger.info(
        "Control loop completed",
        total_cycles=result.get("total_cycles"),
        final_phase=result.get("current_phase"),
    )

    return result
