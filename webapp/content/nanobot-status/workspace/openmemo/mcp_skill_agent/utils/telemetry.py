"""
Unified Telemetry & Logging Module.

Provides centralized structured logging via structlog.
All logging goes through TelemetryManager for consistent JSON output.

Usage:
    from ..utils.telemetry import get_telemetry
    
    logger = get_telemetry("orchestrator")
    logger.info("Planning complete", step_count=5)
    logger.warning("Missing artifact", file="output.txt")
    logger.error("Step failed", step_id=3, reason="timeout")
"""

import structlog
import uuid
import sys
from datetime import datetime
from typing import Optional, Any, Dict

# Configure structlog
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(sys.stderr),
)


class TelemetryManager:
    """
    Centralized Telemetry Manager using structlog.
    
    Provides both:
    - Structured event logging (log_event)
    - Logger-like convenience methods (info, warning, error, debug, critical)
    
    Singleton pattern ensures consistent session tracking.
    """
    _instance = None
    _named_loggers: Dict[str, 'TelemetryManager'] = {}

    def __new__(cls, component: str = "default"):
        # Return cached named logger if exists
        if component in cls._named_loggers:
            return cls._named_loggers[component]
        
        # Create base instance if not exists
        if cls._instance is None:
            cls._instance = super(TelemetryManager, cls).__new__(cls)
            cls._instance._base_logger = structlog.get_logger()
            cls._instance.session_id = str(uuid.uuid4())
        
        # Create new named logger binding
        instance = object.__new__(cls)
        instance._logger = cls._instance._base_logger.bind(component=component)
        instance.session_id = cls._instance.session_id
        instance.component = component
        cls._named_loggers[component] = instance
        
        return instance

    # =========================================================================
    # Structured Event Logging (Original API)
    # =========================================================================
    
    def log_event(self, 
                  event_type: str, 
                  step_id: Optional[int] = None, 
                  agent_name: Optional[str] = None,
                  details: Optional[Dict[str, Any]] = None):
        """
        Logs a structured event.
        
        Args:
            event_type: THOUGHT, ACTION, OBSERVATION, STATE_CHANGE, etc.
            step_id: Current SOP step ID
            agent_name: Name of the active agent/component
            details: Payload dictionary
        """
        if details is None:
            details = {}
        
        self._logger.msg(
            event_type,
            session_id=self.session_id,
            step_id=step_id,
            agent_name=agent_name or self.component,
            **details
        )

    # =========================================================================
    # Logger-like Convenience Methods
    # =========================================================================
    
    def debug(self, message: str, **kwargs):
        """Log debug level message."""
        self._logger.debug(message, session_id=self.session_id, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info level message."""
        self._logger.info(message, session_id=self.session_id, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning level message."""
        self._logger.warning(message, session_id=self.session_id, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """Log error level message."""
        if exc_info:
            import traceback
            kwargs["traceback"] = traceback.format_exc()
        self._logger.error(message, session_id=self.session_id, **kwargs)
    
    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """Log critical level message."""
        if exc_info:
            import traceback
            kwargs["traceback"] = traceback.format_exc()
        self._logger.critical(message, session_id=self.session_id, **kwargs)

    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_session_id(self) -> str:
        return self.session_id


def get_telemetry(component: str = "default") -> TelemetryManager:
    """
    Factory function to get a named TelemetryManager.
    
    Usage:
        logger = get_telemetry("orchestrator")
        logger.info("Starting execution")
    """
    return TelemetryManager(component)
