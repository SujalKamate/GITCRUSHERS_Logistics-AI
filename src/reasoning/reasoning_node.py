"""
LangGraph reasoning node for the reasoning layer.

This node analyzes fleet data using Grok LLM to:
- Detect issues
- Assess risks
- Generate recommendations
"""
import json
import uuid
from datetime import datetime
from typing import Callable
import structlog

from src.models import (
    AgentState, ControlLoopPhase, Issue, ReasoningResult
)
from src.reasoning.grok_client import GroqClient, get_groq_client
from src.reasoning.prompts import PromptTemplates

logger = structlog.get_logger(__name__)


def create_reasoning_node(
    groq_client: GroqClient = None,
) -> Callable[[AgentState], AgentState]:
    """
    Create a reasoning node for the LangGraph control loop.

    Args:
        groq_client: Optional Groq client (uses default if not provided)

    Returns:
        A function that can be used as a LangGraph node
    """
    _client = groq_client or get_groq_client()

    def reasoning_node(state: AgentState) -> AgentState:
        """
        Reasoning node that analyzes fleet data with Grok LLM.

        This is the REASON phase of the control loop:
        OBSERVE -> [REASON] -> PLAN -> DECIDE -> ACT -> FEEDBACK

        Args:
            state: Current agent state with observation data

        Returns:
            Updated agent state with reasoning results
        """
        logger.info(
            "Starting reasoning phase",
            cycle_id=state.get("cycle_id"),
            trucks=len(state.get("trucks", [])),
            traffic=len(state.get("traffic_conditions", [])),
        )

        try:
            # Extract data from state
            trucks = state.get("trucks", [])
            traffic_conditions = state.get("traffic_conditions", [])
            loads = state.get("loads", [])
            gps_readings = state.get("gps_readings", [])

            # Perform situation assessment
            reasoning_result = _analyze_situation(
                _client, trucks, traffic_conditions, loads, gps_readings
            )

            # Detect issues for each truck with potential problems
            issues = reasoning_result.issues.copy()

            # Check for additional issues via per-truck analysis
            for truck in trucks:
                if truck.get("status") in ["en_route", "stuck", "delayed"]:
                    truck_issues = _analyze_truck(
                        _client, truck, loads, traffic_conditions
                    )
                    for issue in truck_issues:
                        # Avoid duplicates
                        if not any(i.id == issue.id for i in issues):
                            issues.append(issue)

            # Update reasoning result with all issues
            reasoning_result.issues = issues

            # Prioritize issues if multiple detected
            if len(issues) > 1:
                issues = _prioritize_issues(_client, issues, trucks, loads)
                reasoning_result.issues = issues

            # Update state
            updated_state: AgentState = {
                **state,
                "current_phase": ControlLoopPhase.REASON,
                "reasoning_result": reasoning_result.model_dump(),
                "current_issues": [i.model_dump() for i in reasoning_result.issues],
            }

            logger.info(
                "Reasoning phase completed",
                cycle_id=state.get("cycle_id"),
                issues_detected=len(reasoning_result.issues),
                confidence=reasoning_result.confidence,
            )

            return updated_state

        except Exception as e:
            logger.error(
                "Reasoning phase failed",
                cycle_id=state.get("cycle_id"),
                error=str(e),
            )

            # Create fallback reasoning result
            fallback_result = ReasoningResult(
                situation_summary=f"Reasoning failed: {str(e)}",
                issues=[],
                risk_assessment="Unable to assess - reasoning error",
                recommendations=["Manual review required"],
                confidence=0.0,
                reasoning_trace=[f"Error: {str(e)}"],
            )

            return {
                **state,
                "current_phase": ControlLoopPhase.REASON,
                "reasoning_result": fallback_result.model_dump(),
                "current_issues": [],
                "error_message": f"Reasoning failed: {str(e)}",
            }

    return reasoning_node


def _analyze_situation(
    client: GroqClient,
    trucks: list[dict],
    traffic: list[dict],
    loads: list[dict],
    gps_readings: list[dict],
) -> ReasoningResult:
    """Perform overall situation assessment."""
    # Format prompt
    prompt = PromptTemplates.format_situation_assessment(
        trucks=trucks,
        traffic=traffic,
        loads=loads,
        gps_readings=gps_readings,
    )

    # Get LLM analysis
    response = client.complete_json(
        prompt=prompt,
        system_prompt=PromptTemplates.SITUATION_ASSESSMENT_SYSTEM,
    )

    if not response.get("success") or not response.get("parsed"):
        # Return fallback result
        return _create_fallback_situation_analysis(trucks, traffic, loads)

    parsed = response["parsed"]

    # Convert to ReasoningResult
    issues = []
    for issue_data in parsed.get("issues", []):
        issue = Issue(
            id=issue_data.get("id", f"ISSUE-{uuid.uuid4().hex[:8].upper()}"),
            type=issue_data.get("type", "unknown"),
            severity=issue_data.get("severity", "medium"),
            description=issue_data.get("description", ""),
            affected_truck_ids=issue_data.get("affected_truck_ids", []),
            affected_load_ids=issue_data.get("affected_load_ids", []),
            metadata=issue_data.get("metadata", {}),
        )
        issues.append(issue)

    return ReasoningResult(
        situation_summary=parsed.get("situation_summary", "Analysis completed"),
        issues=issues,
        risk_assessment=parsed.get("risk_assessment", "Unknown"),
        recommendations=parsed.get("recommendations", []),
        confidence=parsed.get("confidence", 0.5),
        reasoning_trace=parsed.get("reasoning_trace", []),
    )


def _analyze_truck(
    client: GroqClient,
    truck: dict,
    loads: list[dict],
    traffic: list[dict],
) -> list[Issue]:
    """Analyze a specific truck for issues."""
    # Find truck's assigned load
    truck_load = None
    for load in loads:
        if load.get("assigned_truck_id") == truck.get("id"):
            truck_load = load
            break

    # Format prompt
    prompt = PromptTemplates.format_issue_detection(
        truck=truck,
        load=truck_load,
        route=None,  # Would come from routes
        traffic=traffic,
    )

    # Get LLM analysis
    response = client.complete_json(
        prompt=prompt,
        system_prompt=PromptTemplates.LOGISTICS_EXPERT_SYSTEM,
    )

    issues = []

    if response.get("success") and response.get("parsed"):
        parsed = response["parsed"]

        if parsed.get("has_issues"):
            for issue_data in parsed.get("issues", []):
                issue = Issue(
                    id=f"ISSUE-{truck.get('id')}-{uuid.uuid4().hex[:6].upper()}",
                    type=issue_data.get("type", "unknown"),
                    severity=issue_data.get("severity", "medium"),
                    description=issue_data.get("description", ""),
                    affected_truck_ids=[truck.get("id")],
                    affected_load_ids=[truck_load.get("id")] if truck_load else [],
                    metadata={
                        "recommended_action": issue_data.get("recommended_action"),
                        "eta_assessment": parsed.get("eta_assessment"),
                    },
                )
                issues.append(issue)

    return issues


def _prioritize_issues(
    client: GroqClient,
    issues: list[Issue],
    trucks: list[dict],
    loads: list[dict],
) -> list[Issue]:
    """Prioritize multiple issues."""
    # For now, simple prioritization by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}

    sorted_issues = sorted(
        issues,
        key=lambda i: severity_order.get(i.severity, 2)
    )

    # Add priority rank to metadata
    for rank, issue in enumerate(sorted_issues):
        issue.metadata["priority_rank"] = rank + 1

    return sorted_issues


def _create_fallback_situation_analysis(
    trucks: list[dict],
    traffic: list[dict],
    loads: list[dict],
) -> ReasoningResult:
    """Create a rule-based fallback analysis when LLM is unavailable."""
    issues = []

    # Check for stuck trucks
    for truck in trucks:
        if truck.get("status") == "stuck":
            issues.append(Issue(
                id=f"ISSUE-STUCK-{truck.get('id')}",
                type="stuck",
                severity="high",
                description=f"Truck {truck.get('id')} is stuck",
                affected_truck_ids=[truck.get("id")],
            ))

    # Check for heavy traffic
    heavy_segments = [tc for tc in traffic if tc.get("level") in ["heavy", "standstill"]]
    if len(heavy_segments) > 2:
        issues.append(Issue(
            id=f"ISSUE-TRAFFIC-{uuid.uuid4().hex[:6].upper()}",
            type="traffic",
            severity="medium",
            description=f"Heavy traffic on {len(heavy_segments)} segments",
        ))

    # Check for urgent loads
    urgent_loads = [l for l in loads if l.get("priority") in ["urgent", "critical"]]
    unassigned_urgent = [l for l in urgent_loads if not l.get("assigned_truck_id")]
    if unassigned_urgent:
        issues.append(Issue(
            id=f"ISSUE-LOAD-{uuid.uuid4().hex[:6].upper()}",
            type="capacity_mismatch",
            severity="high",
            description=f"{len(unassigned_urgent)} urgent loads without assigned trucks",
            affected_load_ids=[l.get("id") for l in unassigned_urgent],
        ))

    return ReasoningResult(
        situation_summary="Fallback analysis (LLM unavailable)",
        issues=issues,
        risk_assessment="Manual review recommended",
        recommendations=["Review stuck trucks", "Check traffic routes", "Assign urgent loads"],
        confidence=0.3,
        reasoning_trace=["Rule-based fallback analysis"],
    )
