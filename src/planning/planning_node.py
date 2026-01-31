"""
LangGraph planning node for the planning layer.

This node generates and evaluates alternative scenarios for issues.
"""
from typing import Callable
import structlog

from src.models import (
    AgentState, ControlLoopPhase, Truck, Load,
    TrafficCondition, Issue, PlanningResult
)
from src.planning.simulation_engine import SimulationEngine
from src.planning.scenario_generator import ScenarioGenerator

logger = structlog.get_logger(__name__)


def create_planning_node(
    simulation_engine: SimulationEngine = None,
    scenario_generator: ScenarioGenerator = None,
) -> Callable[[AgentState], AgentState]:
    """
    Create a planning node for the LangGraph control loop.

    Args:
        simulation_engine: Optional simulation engine
        scenario_generator: Optional scenario generator

    Returns:
        A function that can be used as a LangGraph node
    """
    _sim_engine = simulation_engine or SimulationEngine()
    _scenario_gen = scenario_generator or ScenarioGenerator(_sim_engine)

    def planning_node(state: AgentState) -> AgentState:
        """
        Planning node that generates scenarios for issues.

        This is the PLAN phase of the control loop:
        OBSERVE -> REASON -> [PLAN] -> DECIDE -> ACT -> FEEDBACK

        Args:
            state: Current agent state with reasoning results

        Returns:
            Updated agent state with planning results
        """
        logger.info(
            "Starting planning phase",
            cycle_id=state.get("cycle_id"),
            issues=len(state.get("current_issues", [])),
        )

        try:
            # Extract data from state
            trucks = [Truck(**t) for t in state.get("trucks", [])]
            loads = [Load(**l) for l in state.get("loads", [])]
            traffic = [TrafficCondition(**tc) for tc in state.get("traffic_conditions", [])]
            issues = [Issue(**i) for i in state.get("current_issues", [])]

            all_scenarios = []
            planning_results = []

            # Generate scenarios for each issue
            for issue in issues:
                scenarios = _scenario_gen.generate_scenarios(
                    issue=issue,
                    trucks=trucks,
                    loads=loads,
                    traffic_conditions=traffic,
                )

                if scenarios:
                    # Compare scenarios
                    comparison = _sim_engine.compare_scenarios(scenarios)

                    # Find recommended scenario
                    recommended_id = None
                    best_score = 0
                    for sid, scores in comparison.items():
                        if scores['overall'] > best_score:
                            best_score = scores['overall']
                            recommended_id = sid

                    planning_result = PlanningResult(
                        issue_id=issue.id,
                        scenarios=scenarios,
                        comparison_matrix=comparison,
                        recommended_scenario_id=recommended_id,
                    )
                    planning_results.append(planning_result)
                    all_scenarios.extend(scenarios)

            # Combine all planning results
            combined_comparison = {}
            for pr in planning_results:
                combined_comparison.update(pr.comparison_matrix)

            # Find overall recommended scenario
            overall_recommended = None
            best_overall = 0
            for sid, scores in combined_comparison.items():
                if scores['overall'] > best_overall:
                    best_overall = scores['overall']
                    overall_recommended = sid

            final_planning_result = PlanningResult(
                issue_id=issues[0].id if issues else None,
                scenarios=all_scenarios,
                comparison_matrix=combined_comparison,
                recommended_scenario_id=overall_recommended,
            )

            # Update state
            updated_state: AgentState = {
                **state,
                "current_phase": ControlLoopPhase.PLAN,
                "planning_result": final_planning_result.model_dump(),
                "scenarios": [s.model_dump() for s in all_scenarios],
            }

            logger.info(
                "Planning phase completed",
                cycle_id=state.get("cycle_id"),
                scenarios_generated=len(all_scenarios),
                recommended=overall_recommended,
            )

            return updated_state

        except Exception as e:
            logger.error(
                "Planning phase failed",
                cycle_id=state.get("cycle_id"),
                error=str(e),
            )

            # Return state with error
            return {
                **state,
                "current_phase": ControlLoopPhase.PLAN,
                "planning_result": PlanningResult(
                    scenarios=[],
                    comparison_matrix={},
                ).model_dump(),
                "scenarios": [],
                "error_message": f"Planning failed: {str(e)}",
            }

    return planning_node
