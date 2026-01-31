"""
Prompt templates for the reasoning layer.

These templates are optimized for logistics domain reasoning with Grok LLM.
"""
from typing import Any
from string import Template


class PromptTemplates:
    """
    Collection of prompt templates for logistics reasoning.

    Each template is designed to elicit structured, actionable analysis
    from the LLM for specific reasoning tasks.
    """

    # System prompts
    LOGISTICS_EXPERT_SYSTEM = """You are an expert logistics analyst and fleet management specialist.
Your role is to analyze real-time fleet data and provide actionable insights.

Key responsibilities:
1. Identify operational issues (delays, stuck trucks, capacity mismatches)
2. Assess risks to delivery schedules
3. Recommend corrective actions
4. Prioritize issues by business impact

Always provide structured, data-driven analysis with clear reasoning traces.
When uncertain, indicate confidence levels and suggest information needed."""

    SITUATION_ASSESSMENT_SYSTEM = """You are a logistics situation analyst.
Analyze the provided fleet state and identify any issues requiring attention.

Focus on:
- Delivery timeline risks
- Traffic impacts
- Resource utilization
- Capacity constraints

Provide analysis in structured JSON format."""

    # Analysis prompts
    SITUATION_ASSESSMENT = Template("""
Analyze the current fleet situation and identify any issues.

## Fleet State
- Active Trucks: $truck_count
- En-Route: $en_route_count
- Idle: $idle_count
- Stuck/Delayed: $problem_count

## Traffic Conditions
- Heavy Traffic Segments: $heavy_traffic_count
- Incidents Reported: $incident_count

## Loads
- Active Loads: $load_count
- Urgent/Critical: $urgent_count
- At-Risk Deliveries: $at_risk_count

## Recent GPS Data
$gps_summary

## Traffic Details
$traffic_summary

Provide your analysis in the following JSON format:
{
    "situation_summary": "Brief overview of current operations",
    "issues": [
        {
            "id": "ISSUE-XXX",
            "type": "delay|capacity_mismatch|traffic|breakdown|other",
            "severity": "low|medium|high|critical",
            "description": "Detailed description",
            "affected_truck_ids": ["TRK-XXX"],
            "affected_load_ids": ["LOAD-XXX"],
            "metadata": {}
        }
    ],
    "risk_assessment": "Overall risk assessment",
    "recommendations": ["Recommendation 1", "Recommendation 2"],
    "confidence": 0.0-1.0,
    "reasoning_trace": ["Step 1 of analysis", "Step 2 of analysis"]
}
""")

    ISSUE_DETECTION = Template("""
Analyze the following truck data to detect potential issues.

## Truck: $truck_id ($truck_name)
- Status: $status
- Current Location: ($latitude, $longitude)
- Speed: $speed km/h
- Heading: $heading°
- Fuel Level: $fuel_level%

## Assigned Load
$load_info

## Route Information
$route_info

## Recent Speed History
$speed_history

## Traffic on Route
$traffic_info

Identify any issues with this truck. Consider:
1. Is the truck stuck (low speed for extended time)?
2. Is the delivery at risk of being late?
3. Are there traffic issues affecting the route?
4. Is fuel level sufficient?

Respond with JSON:
{
    "truck_id": "$truck_id",
    "has_issues": true/false,
    "issues": [
        {
            "type": "stuck|delay|traffic|fuel|route|other",
            "severity": "low|medium|high|critical",
            "description": "Description",
            "recommended_action": "Suggested action"
        }
    ],
    "eta_assessment": "On-time|At-risk|Late",
    "confidence": 0.0-1.0
}
""")

    TRAFFIC_IMPACT_ANALYSIS = Template("""
Analyze the impact of current traffic conditions on fleet operations.

## Traffic Conditions
$traffic_conditions

## Affected Routes
$affected_routes

## Trucks on Affected Routes
$affected_trucks

For each affected truck, assess:
1. Expected additional delay
2. Alternative route options
3. Impact on delivery deadlines
4. Priority for intervention

Respond with JSON:
{
    "overall_impact": "minimal|moderate|significant|severe",
    "affected_deliveries": $affected_delivery_count,
    "truck_impacts": [
        {
            "truck_id": "TRK-XXX",
            "current_delay_minutes": 0,
            "expected_additional_delay": 0,
            "delivery_at_risk": true/false,
            "recommended_action": "wait|reroute|reassign"
        }
    ],
    "recommendations": ["Recommendation 1"],
    "confidence": 0.0-1.0
}
""")

    RISK_EVALUATION = Template("""
Evaluate delivery risks for the following loads.

## Loads at Risk
$loads_at_risk

## Current Fleet State
$fleet_state

## Traffic Conditions
$traffic_conditions

For each load, assess:
1. Probability of on-time delivery
2. Key risk factors
3. Mitigation options
4. Business impact if late

Respond with JSON:
{
    "risk_summary": "Overall risk assessment",
    "load_risks": [
        {
            "load_id": "LOAD-XXX",
            "on_time_probability": 0.0-1.0,
            "risk_factors": ["Factor 1", "Factor 2"],
            "mitigation_options": ["Option 1"],
            "business_impact": "low|medium|high|critical"
        }
    ],
    "prioritized_actions": ["Most urgent action first"],
    "confidence": 0.0-1.0
}
""")

    MULTI_ISSUE_PRIORITIZATION = Template("""
Prioritize the following issues for action.

## Detected Issues
$issues_list

## Fleet Resources
- Available Trucks: $available_trucks
- Drivers on Duty: $drivers_on_duty

## Business Priorities
- Critical Loads: $critical_loads
- SLA Commitments: $sla_commitments

Prioritize issues considering:
1. Customer impact
2. SLA risk
3. Resource availability
4. Cascading effects
5. Cost of delay vs. cost of action

Respond with JSON:
{
    "prioritized_issues": [
        {
            "issue_id": "ISSUE-XXX",
            "priority_rank": 1,
            "urgency": "immediate|high|medium|low",
            "rationale": "Why this priority",
            "recommended_response_time_minutes": 0
        }
    ],
    "resource_allocation": {
        "trucks_to_reassign": [],
        "routes_to_modify": []
    },
    "confidence": 0.0-1.0
}
""")

    # Verification prompts
    DECISION_VERIFICATION = Template("""
Verify the proposed decision for handling a logistics issue.

## Issue
$issue_description

## Proposed Decision
- Action Type: $action_type
- Parameters: $action_parameters
- Expected Outcome: $expected_outcome
- Estimated Cost: $estimated_cost
- Estimated Time Impact: $time_impact

## Alternative Options Considered
$alternatives

## Current Context
$context

Verify this decision by evaluating:
1. Is the action appropriate for the issue?
2. Are the expected outcomes realistic?
3. Are there any risks or side effects?
4. Is this the optimal choice among alternatives?

Respond with JSON:
{
    "verification_passed": true/false,
    "confidence": 0.0-1.0,
    "concerns": ["Any concerns about the decision"],
    "suggestions": ["Any suggested modifications"],
    "risk_factors": ["Identified risks"],
    "approval_recommendation": "approve|modify|reject",
    "rationale": "Explanation of verification result"
}
""")

    # Explanation generation
    GENERATE_EXPLANATION = Template("""
Generate a clear explanation for the following logistics decision.

## Decision
- Action: $action_type
- For Issue: $issue_description
- Affected: $affected_entities

## Analysis Summary
$analysis_summary

## Why This Decision
$decision_rationale

Generate explanations for different audiences:
1. Driver (simple, actionable instructions)
2. Dispatcher (technical details, coordination needs)
3. Customer (impact on their delivery, reassurance)

Respond with JSON:
{
    "driver_explanation": "Clear instructions for the driver",
    "dispatcher_explanation": "Technical explanation for dispatcher",
    "customer_explanation": "Customer-friendly update",
    "key_points": ["Main point 1", "Main point 2"],
    "expected_resolution": "What will happen next"
}
""")

    @classmethod
    def format_situation_assessment(
        cls,
        trucks: list[dict],
        traffic: list[dict],
        loads: list[dict],
        gps_readings: list[dict],
    ) -> str:
        """Format the situation assessment prompt with actual data."""
        # Calculate statistics
        truck_count = len(trucks)
        en_route_count = sum(1 for t in trucks if t.get('status') == 'en_route')
        idle_count = sum(1 for t in trucks if t.get('status') == 'idle')
        problem_count = sum(1 for t in trucks if t.get('status') in ['stuck', 'delayed'])

        heavy_traffic_count = sum(1 for tc in traffic if tc.get('level') in ['heavy', 'standstill'])
        incident_count = sum(1 for tc in traffic if tc.get('incident_description'))

        load_count = len(loads)
        urgent_count = sum(1 for l in loads if l.get('priority') in ['urgent', 'critical'])

        # Calculate at-risk deliveries (simplified)
        at_risk_count = 0
        for load in loads:
            if load.get('priority') in ['urgent', 'critical', 'high']:
                at_risk_count += 1

        # Format GPS summary
        gps_summary = "Recent positions:\n"
        for reading in gps_readings[:5]:
            gps_summary += f"- {reading.get('truck_id')}: ({reading.get('location', {}).get('latitude', 0):.4f}, {reading.get('location', {}).get('longitude', 0):.4f}) @ {reading.get('speed_kmh', 0):.1f} km/h\n"

        # Format traffic summary
        traffic_summary = "Traffic conditions:\n"
        for tc in traffic:
            if tc.get('level') in ['heavy', 'standstill'] or tc.get('incident_description'):
                traffic_summary += f"- {tc.get('segment_id')}: {tc.get('level')} - {tc.get('incident_description', 'No incident')}\n"

        return cls.SITUATION_ASSESSMENT.substitute(
            truck_count=truck_count,
            en_route_count=en_route_count,
            idle_count=idle_count,
            problem_count=problem_count,
            heavy_traffic_count=heavy_traffic_count,
            incident_count=incident_count,
            load_count=load_count,
            urgent_count=urgent_count,
            at_risk_count=at_risk_count,
            gps_summary=gps_summary,
            traffic_summary=traffic_summary,
        )

    @classmethod
    def format_issue_detection(cls, truck: dict, load: dict = None, route: dict = None, traffic: list[dict] = None, speed_history: list[float] = None) -> str:
        """Format the issue detection prompt for a specific truck."""
        location = truck.get('current_location', {})

        load_info = "No assigned load"
        if load:
            load_info = f"""
- Load ID: {load.get('id')}
- Description: {load.get('description')}
- Priority: {load.get('priority')}
- Deadline: {load.get('delivery_deadline')}
"""

        route_info = "No active route"
        if route:
            route_info = f"""
- Route ID: {route.get('id')}
- Distance: {route.get('estimated_distance_km', 0):.1f} km
- Duration: {route.get('estimated_duration_minutes', 0):.0f} min
"""

        speed_hist = "No history available"
        if speed_history:
            speed_hist = ", ".join([f"{s:.1f}" for s in speed_history[-10:]])

        traffic_info = "No traffic data for route"
        if traffic:
            traffic_info = "\n".join([
                f"- {tc.get('segment_id')}: {tc.get('level')} ({tc.get('speed_kmh', 0):.0f} km/h)"
                for tc in traffic
            ])

        return cls.ISSUE_DETECTION.substitute(
            truck_id=truck.get('id'),
            truck_name=truck.get('name'),
            status=truck.get('status'),
            latitude=location.get('latitude', 0),
            longitude=location.get('longitude', 0),
            speed=truck.get('last_gps_reading', {}).get('speed_kmh', 0),
            heading=truck.get('last_gps_reading', {}).get('heading', 0),
            fuel_level=truck.get('fuel_level_percent', 0),
            load_info=load_info,
            route_info=route_info,
            speed_history=speed_hist,
            traffic_info=traffic_info,
        )
