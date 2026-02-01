"""
API route modules for the Logistics AI Dashboard.
"""

from .fleet import router as fleet_router
from .control_loop import router as control_loop_router
from .decisions import router as decisions_router
from .requests import router as requests_router

__all__ = ["fleet_router", "control_loop_router", "decisions_router", "requests_router"]
