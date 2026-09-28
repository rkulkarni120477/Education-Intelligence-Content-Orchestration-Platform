"""
Service for tracking real-time agent execution status.

Maintains in-memory state of currently executing agents so the frontend can display them in the Agent Box.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import threading

execution_state_lock = threading.Lock()

_current_execution: Dict[str, Any] = {
    "agent_name": None,
    "execution_id": None,
    "progress": 0,
    "is_executing": False,
    "started_at": None,
}


def start_agent_execution(agent_name: str, execution_id: str) -> None:
    """Mark an agent as starting execution."""
    with execution_state_lock:
        _current_execution.update({
            "agent_name": agent_name,
            "execution_id": execution_id,
            "progress": 0,
            "is_executing": True,
            "started_at": datetime.utcnow().isoformat(),
        })


def update_agent_progress(progress: float) -> None:
    """Update the progress of the currently executing agent (0-100)."""
    with execution_state_lock:
        if _current_execution["is_executing"]:
            _current_execution["progress"] = min(max(progress, 0), 100)


def complete_agent_execution() -> None:
    """Mark the current agent execution as complete."""
    with execution_state_lock:
        _current_execution.update({
            "agent_name": None,
            "execution_id": None,
            "progress": 0,
            "is_executing": False,
            "started_at": None,
        })


def get_agent_execution_status() -> Dict[str, Any]:
    """Get the current agent execution status."""
    with execution_state_lock:
        return _current_execution.copy()
