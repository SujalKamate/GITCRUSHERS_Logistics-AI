"""
Decision evaluator for multi-criteria scenario evaluation.
"""
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
import structlog

from src.models import Scenario, Decision, ActionType, DecisionResult
from config.settings import settings

logger = structlog.get_logger(__name__)


class DecisionEvaluator:
    """
    Evaluates and selects the best scenario based on multiple criteria.

    Criteria:
    - Cost efficiency
    - Time optimization
    - Reliability
    - Fuel efficiency
    """

    def __init__(
        self,
        confidence_threshold: float = None,
        weights: Dict[str, float] = None,
    ):
        self.confidence_threshold = confidence_threshold or settings.DECISION_CONFIDENCE_THRESHOLD
        self.weights = weights or {
            "cost": 0.25,
            "time": 0.35,
            "reliability": 0.30,
            "fuel": 0.10,
        }

    def evaluate_scenarios(
        self,
        scenarios: List[Scenario],
        comparison_matrix: Dict[str, Dict[str, float]] = None,
    ) -> DecisionResult:
        """
        Evaluate scenarios and select the best one.

        Args:
            scenarios: List of scenarios to evaluate
            comparison_matrix: Pre-computed comparison scores

        Returns:
            DecisionResult with selected decision and alternatives
        """
        if not scenarios:
            return DecisionResult(
                selected_decision=None,
                alternatives=[],
                requires_human_approval=True,
                decision_trace=["No scenarios to evaluate"],
            )

        decisions = []
        traces = []

        for scenario in scenarios:
            # Get or compute scores
            if comparison_matrix and scenario.id in comparison_matrix:
                scores = comparison_matrix[scenario.id]
            else:
                scores = self._compute_scores(scenario)

            # Calculate weighted score
            weighted_score = (
                self.weights["cost"] * scores.get("cost_score", 0.5) +
                self.weights["time"] * scores.get("time_score", 0.5) +
                self.weights["reliability"] * scores.get("reliability", scenario.reliability_score) +
                self.weights["fuel"] * scores.get("fuel_score", 0.5)
            )

            # Determine action type
            action_type = self._determine_action_type(scenario)

            # Create decision
            decision = Decision(
                id=f"DEC-{scenario.id}",
                scenario_id=scenario.id,
                action_type=action_type,
                parameters={"actions": scenario.actions},
                score=round(weighted_score, 3),
                confidence=round(weighted_score * scenario.reliability_score, 3),
                rationale=f"Selected {scenario.name}: score={weighted_score:.3f}, reliability={scenario.reliability_score}",
            )
            decisions.append(decision)
            traces.append(f"Evaluated {scenario.name}: score={weighted_score:.3f}")

        # Sort by score
        decisions.sort(key=lambda d: d.score, reverse=True)

        # Select best decision
        best = decisions[0] if decisions else None
        alternatives = decisions[1:] if len(decisions) > 1 else []

        # Check if human approval needed
        requires_human = False
        if best:
            if best.confidence < self.confidence_threshold:
                requires_human = True
                traces.append(f"Confidence {best.confidence:.2f} below threshold {self.confidence_threshold}")

            # Check for high-impact actions
            if best.action_type in [ActionType.REASSIGN, ActionType.ESCALATE]:
                if best.confidence < 0.85:
                    requires_human = True
                    traces.append(f"High-impact action requires verification")

        traces.append(f"Selected: {best.scenario_id if best else 'None'}")
        traces.append(f"Requires human approval: {requires_human}")

        return DecisionResult(
            selected_decision=best,
            alternatives=alternatives,
            requires_human_approval=requires_human,
            decision_trace=traces,
        )

    def _compute_scores(self, scenario: Scenario) -> Dict[str, float]:
        """Compute normalized scores for a scenario."""
        # Simple normalization (in production, use actual ranges)
        cost_score = 1 / (1 + scenario.estimated_cost / 100)
        time_score = 1 / (1 + scenario.estimated_time_minutes / 60)
        fuel_score = 1 / (1 + scenario.estimated_fuel_liters / 10)

        return {
            "cost_score": cost_score,
            "time_score": time_score,
            "fuel_score": fuel_score,
            "reliability": scenario.reliability_score,
            "overall": (cost_score + time_score + fuel_score + scenario.reliability_score) / 4,
        }

    def _determine_action_type(self, scenario: Scenario) -> ActionType:
        """Determine primary action type from scenario."""
        if not scenario.actions:
            return ActionType.WAIT

        first_action = scenario.actions[0]
        action_type_str = first_action.get("type", "wait")

        try:
            return ActionType(action_type_str)
        except ValueError:
            return ActionType.WAIT
