"""
Orchestrator State Machine - Explicit state transitions for clearer flow control.

This module provides an explicit state enum for the orchestrator, making
state transitions visible and easier to debug/monitor.
"""

from enum import Enum, auto
from typing import Optional, Any
from dataclasses import dataclass, field
from datetime import datetime


class OrchestratorState(Enum):
    """
    Explicit states for the orchestrator lifecycle.
    
    State Machine Flow:
        INITIALIZING → DISCOVERY → PLANNING → EXECUTING ⇄ VERIFYING ⇄ CRITIQUING
                                           ↓
                                    SELF_HEALING
                                           ↓
                                     (back to EXECUTING or FAILED)
                                           ↓
                                    COMPLETE or FAILED
    """
    # Initialization States
    INITIALIZING = auto()
    DISCOVERY = auto()
    
    # Planning States
    PLANNING = auto()
    
    # Execution States
    EXECUTING = auto()
    VERIFYING = auto()
    CRITIQUING = auto()
    
    # Recovery States
    SELF_HEALING = auto()
    
    # Terminal States
    COMPLETE = auto()
    FAILED = auto()
    
    @property
    def is_terminal(self) -> bool:
        """Check if this is a terminal state."""
        return self in (OrchestratorState.COMPLETE, OrchestratorState.FAILED)
    
    @property
    def is_recovery(self) -> bool:
        """Check if this is a recovery state."""
        return self == OrchestratorState.SELF_HEALING
    
    @property
    def phase(self) -> str:
        """Get the high-level phase for this state."""
        phase_map = {
            OrchestratorState.INITIALIZING: "INIT",
            OrchestratorState.DISCOVERY: "INIT",
            OrchestratorState.PLANNING: "PLAN",
            OrchestratorState.EXECUTING: "EXEC",
            OrchestratorState.VERIFYING: "EXEC",
            OrchestratorState.CRITIQUING: "EXEC",
            OrchestratorState.SELF_HEALING: "RECOVERY",
            OrchestratorState.COMPLETE: "DONE",
            OrchestratorState.FAILED: "DONE",
        }
        return phase_map.get(self, "UNKNOWN")


@dataclass
class StateTransition:
    """Record of a state transition for audit/telemetry."""
    from_state: OrchestratorState
    to_state: OrchestratorState
    timestamp: datetime = field(default_factory=datetime.now)
    step_id: Optional[int] = None
    reason: str = ""
    
    def to_dict(self) -> dict:
        return {
            "from": self.from_state.name,
            "to": self.to_state.name,
            "timestamp": self.timestamp.isoformat(),
            "step_id": self.step_id,
            "reason": self.reason,
        }


class StateManager:
    """
    Manages orchestrator state transitions with validation and history.
    
    Usage:
        state_manager = StateManager()
        state_manager.transition_to(OrchestratorState.DISCOVERY, reason="Starting skill discovery")
    """
    
    # Valid state transitions
    VALID_TRANSITIONS = {
        OrchestratorState.INITIALIZING: [OrchestratorState.DISCOVERY, OrchestratorState.FAILED],
        OrchestratorState.DISCOVERY: [OrchestratorState.PLANNING, OrchestratorState.FAILED],
        OrchestratorState.PLANNING: [OrchestratorState.EXECUTING, OrchestratorState.FAILED],
        OrchestratorState.EXECUTING: [
            OrchestratorState.VERIFYING,
            OrchestratorState.SELF_HEALING,
            OrchestratorState.COMPLETE,
            OrchestratorState.FAILED,
        ],
        OrchestratorState.VERIFYING: [
            OrchestratorState.CRITIQUING,
            OrchestratorState.EXECUTING,
            OrchestratorState.FAILED,
        ],
        OrchestratorState.CRITIQUING: [
            OrchestratorState.EXECUTING,
            OrchestratorState.COMPLETE,
            OrchestratorState.FAILED,
        ],
        OrchestratorState.SELF_HEALING: [
            OrchestratorState.EXECUTING,
            OrchestratorState.FAILED,
        ],
        # Terminal states have no outgoing transitions
        OrchestratorState.COMPLETE: [],
        OrchestratorState.FAILED: [],
    }
    
    def __init__(self, initial_state: OrchestratorState = OrchestratorState.INITIALIZING):
        self._current_state = initial_state
        self._history: list[StateTransition] = []
    
    @property
    def current_state(self) -> OrchestratorState:
        return self._current_state
    
    @property
    def history(self) -> list[StateTransition]:
        return self._history.copy()
    
    def can_transition_to(self, target: OrchestratorState) -> bool:
        """Check if a transition to the target state is valid."""
        valid_targets = self.VALID_TRANSITIONS.get(self._current_state, [])
        return target in valid_targets
    
    def transition_to(
        self, 
        target: OrchestratorState, 
        step_id: Optional[int] = None,
        reason: str = ""
    ) -> StateTransition:
        """
        Transition to a new state.
        
        Raises:
            InvalidStateTransitionError: If the transition is not valid.
        """
        if not self.can_transition_to(target):
            from .errors import InvalidStateTransitionError
            raise InvalidStateTransitionError(
                from_state=self._current_state,
                to_state=target,
                valid_targets=self.VALID_TRANSITIONS.get(self._current_state, [])
            )
        
        transition = StateTransition(
            from_state=self._current_state,
            to_state=target,
            step_id=step_id,
            reason=reason,
        )
        
        self._history.append(transition)
        self._current_state = target
        
        return transition
    
    def get_execution_summary(self) -> dict:
        """Get a summary of the execution history."""
        return {
            "current_state": self._current_state.name,
            "total_transitions": len(self._history),
            "phases_visited": list(set(t.to_state.phase for t in self._history)),
            "recovery_count": sum(1 for t in self._history if t.to_state.is_recovery),
            "history": [t.to_dict() for t in self._history[-5:]],  # Last 5 transitions
        }
