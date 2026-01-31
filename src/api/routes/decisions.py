"""
Decision management API routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.api.services.state_manager import state_manager
from src.api.websocket import ws_manager

router = APIRouter(prefix="/api/decisions", tags=["decisions"])


# ============================================================================
# Request/Response Models
# ============================================================================

class ApproveDecisionRequest(BaseModel):
    decision_id: str
    approved: bool
    reason: Optional[str] = None
    modifications: Optional[dict] = None


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/pending")
async def get_pending_decisions():
    """
    Get all pending decisions awaiting approval or execution.
    """
    return state_manager.get_pending_decisions_response()


@router.post("/approve")
async def approve_decision(request: ApproveDecisionRequest):
    """
    Approve or reject a pending decision.
    """
    decision = state_manager.approve_decision(
        request.decision_id,
        approved=request.approved
    )

    if not decision:
        raise HTTPException(
            status_code=404,
            detail=f"Decision {request.decision_id} not found in pending decisions"
        )

    # Broadcast the decision update
    event_type = "decision_approved" if request.approved else "decision_rejected"
    await ws_manager.broadcast({
        "type": event_type,
        "data": {
            "decision_id": decision.id,
            "action_type": decision.action_type.value,
            "approved": request.approved,
            "reason": request.reason,
            "confidence": decision.confidence
        },
        "source": "decision_engine"
    })

    return {
        "success": True,
        "message": f"Decision {request.decision_id} {'approved' if request.approved else 'rejected'}",
        "decision": decision.model_dump()
    }


@router.get("/history")
async def get_decision_history(page: int = 1, limit: int = 50):
    """
    Get historical decisions with outcomes.
    """
    all_decisions = state_manager.approved_decisions + state_manager.rejected_decisions
    all_decisions.sort(key=lambda d: d.decided_at, reverse=True)

    start = (page - 1) * limit
    end = start + limit
    page_decisions = all_decisions[start:end]

    # Calculate success rate
    total = len(all_decisions)
    approved = len(state_manager.approved_decisions)
    success_rate = (approved / total * 100) if total > 0 else 0

    # Calculate average confidence
    avg_confidence = 0
    if all_decisions:
        avg_confidence = sum(d.confidence for d in all_decisions) / len(all_decisions)

    return {
        "decisions": [
            {
                **d.model_dump(),
                "outcome": {"success": d.human_approved},
                "effectiveness_score": d.score if d.human_approved else 0
            }
            for d in page_decisions
        ],
        "total": total,
        "success_rate": success_rate,
        "average_confidence": avg_confidence,
        "page": page,
        "per_page": limit
    }
