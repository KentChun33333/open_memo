import structlog
import uuid
import sys
from datetime import datetime
from typing import Optional, Any, Dict, List

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(sys.stderr),
)

class TelemetryManager:
    """
    Centralized Telemetry Manager using structlog.
    Logs structured JSON events for Thought, Action, Observation, and State Changes.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TelemetryManager, cls).__new__(cls)
            cls._instance.logger = structlog.get_logger()
            cls._instance.session_id = str(uuid.uuid4())
        return cls._instance

    def log_event(self, 
                  event_type: str, 
                  step_id: Optional[int] = None, 
                  agent_name: str = "orchestrator", 
                  details: Optional[Dict[str, Any]] = None):
        """
        Logs a structured event.
        
        Args:
            event_type: THOUGHT, ACTION, OBSERVATION, STATE_CHANGE
            step_id: Current SOP step ID
            agent_name: Name of the active agent/component
            details: Payload dictionary
        """
        if details is None:
            details = {}
            
        self.logger.msg(
            event=event_type,
            session_id=self.session_id,
            step_id=step_id,
            agent_name=agent_name,
            **details
        )
    
    def get_session_id(self) -> str:
        return self.session_id
