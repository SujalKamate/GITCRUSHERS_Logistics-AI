"""
LangGraph decision node for the decision layer.
"""
from typing import Callable
import structlog

from src.models import AgentState, ControlLoopPhase, Scenario, DecisionResult
from src.decision.evaluator import DecisionEvaluator

logger = structlog.get_logger(__name__)


def create_decision_node(
    evaluator: DecisionEvaluator = None,
) -> Callable[[AgentState], AgentState]:
    """Create a decision node for the LangGraph control loop."""
    _evaluator = evaluator or DecisionEvaluator()

    def decision_node(state: AgentState) -> AgentState:
        """
        Decision node that evaluates and selects scenarios.

        OBSERVE -> REASON -> PLAN -> [DECIDE] -> ACT -> FEEDBACK
        """
        logger.info("Starting decision phase", cycle_id=state.get("cycle_id"))

        try:
            # Get scenarios from planning
            scenarios = [Scenario(**s) for s in state.get("scenarios", [])]
            planning_result = state.get("planning_result", {})
            comparison_matrix = planning_result.get("comparison_matrix", {})

            # Evaluate scenarios
            result = _evaluator.evaluate_scenarios(scenarios, comparison_matrix)

            # Update state
            updated_state: AgentState = {
                **state,
                "current_phase": ControlLoopPhase.DECIDE,
                "decision_result": result.model_dump(),
                "selected_decision": result.selected_decision.model_dump() if result.selected_decision else None,
                "requires_human_intervention": result.requires_human_approval,
            }

            logger.info(
                "Decision phase completed",
                selected=result.selected_decision.scenario_id if result.selected_decision else None,
                requires_human=result.requires_human_approval,
            )

            return updated_state

        except Exception as e:
            logger.error("Decision phase failed", error=str(e))
            return {
                **state,
                "current_phase": ControlLoopPhase.DECIDE,
                "decision_result": DecisionResult(decision_trace=[f"Error: {e}"]).model_dump(),
                "selected_decision": None,
                "error_message": f"Decision failed: {str(e)}",
            }

    return decision_node
