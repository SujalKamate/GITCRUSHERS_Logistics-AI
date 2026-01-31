"""
WebSocket connection manager for real-time updates.
"""

import json
from datetime import datetime
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages WebSocket connections and broadcasts events to all connected clients.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict[str, Any], websocket: WebSocket):
        """Send a message to a specific client."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)

    async def broadcast(self, message: dict[str, Any]):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return

        # Ensure message has required fields
        if "timestamp" not in message:
            message["timestamp"] = datetime.utcnow().isoformat()

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error broadcasting to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

    async def broadcast_truck_location_update(
        self,
        truck_id: str,
        latitude: float,
        longitude: float,
        speed_kmh: float,
        heading: float
    ):
        """Broadcast a truck location update event."""
        await self.broadcast({
            "type": "truck_location_update",
            "data": {
                "truck_id": truck_id,
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                },
                "speed_kmh": speed_kmh,
                "heading": heading,
                "timestamp": datetime.utcnow().isoformat()
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "fleet_manager"
        })

    async def broadcast_control_loop_update(
        self,
        cycle_id: str,
        phase: str,
        progress_percent: float,
        issues_detected: int = 0,
        decisions_pending: int = 0
    ):
        """Broadcast a control loop status update."""
        await self.broadcast({
            "type": "control_loop_update",
            "data": {
                "cycle_id": cycle_id,
                "phase": phase,
                "progress_percent": progress_percent,
                "issues_detected": issues_detected,
                "decisions_pending": decisions_pending
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "control_loop"
        })

    async def broadcast_control_loop_phase_change(
        self,
        phase: str,
        previous_phase: str
    ):
        """Broadcast a control loop phase change event."""
        await self.broadcast({
            "type": "control_loop_phase_change",
            "data": {
                "current_phase": phase,
                "previous_phase": previous_phase
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "control_loop"
        })

    async def broadcast_decision_pending(
        self,
        decision_id: str,
        action_type: str,
        description: str,
        confidence: float,
        requires_approval: bool
    ):
        """Broadcast a new pending decision event."""
        await self.broadcast({
            "type": "decision_pending",
            "data": {
                "decision_id": decision_id,
                "action_type": action_type,
                "description": description,
                "confidence": confidence,
                "requires_approval": requires_approval
            },
            "timestamp": datetime.utcnow().isoformat(),
            "source": "decision_engine"
        })

    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)


# Global singleton instance
ws_manager = ConnectionManager()
