"""
Orchestrator Error Taxonomy - Structured error classification for better debugging.

This module provides a hierarchy of error types for the orchestrator,
enabling precise error handling, recovery decisions, and better telemetry.
"""

from enum import Enum, auto
from typing import Optional, Any, List
from dataclasses import dataclass, field


class ErrorSeverity(Enum):
    """Severity levels for errors."""
    INFO = auto()       # Minor issue, non-blocking
    WARNING = auto()    # Potential problem, may need attention
    ERROR = auto()      # Recoverable error
    CRITICAL = auto()   # Fatal error, requires intervention


class ErrorCategory(Enum):
    """High-level error categories for classification."""
    # Infrastructure Errors
    NETWORK = auto()
    LLM_API = auto()
    MCP_SERVER = auto()
    FILE_SYSTEM = auto()
    
    # Planning Errors
    SKILL_NOT_FOUND = auto()
    INVALID_PLAN = auto()
    MISSING_CONTEXT = auto()
    
    # Execution Errors
    STEP_FAILED = auto()
    TOOL_ERROR = auto()
    TIMEOUT = auto()
    
    # Validation Errors
    ARTIFACT_MISSING = auto()
    ARTIFACT_INVALID = auto()
    VERIFICATION_FAILED = auto()
    CRITIC_REJECTED = auto()
    
    # State Errors
    INVALID_TRANSITION = auto()
    STATE_CORRUPTION = auto()
    
    # Unknown
    UNKNOWN = auto()


@dataclass
class OrchestratorError(Exception):
    """Base error class for all orchestrator errors."""
    message: str
    category: ErrorCategory = ErrorCategory.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.ERROR
    step_id: Optional[int] = None
    context: dict = field(default_factory=dict)
    recoverable: bool = True
    
    def __str__(self) -> str:
        return f"[{self.category.name}] {self.message}"
    
    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "category": self.category.name,
            "severity": self.severity.name,
            "step_id": self.step_id,
            "recoverable": self.recoverable,
            "context": self.context,
        }


# =============================================================================
# Specific Error Types
# =============================================================================

@dataclass
class SkillNotFoundError(OrchestratorError):
    """Raised when no matching skill is discovered."""
    query: str = ""
    
    def __post_init__(self):
        self.category = ErrorCategory.SKILL_NOT_FOUND
        self.severity = ErrorSeverity.CRITICAL
        self.recoverable = False
        self.message = f"No skill found for query: {self.query}"


@dataclass
class PlanningError(OrchestratorError):
    """Raised when planning fails."""
    reason: str = ""
    
    def __post_init__(self):
        self.category = ErrorCategory.INVALID_PLAN
        self.severity = ErrorSeverity.ERROR
        self.message = f"Planning failed: {self.reason}"


@dataclass
class StepExecutionError(OrchestratorError):
    """Raised when a step fails to execute."""
    step_title: str = ""
    attempt: int = 0
    
    def __post_init__(self):
        self.category = ErrorCategory.STEP_FAILED
        self.severity = ErrorSeverity.ERROR
        self.message = f"Step '{self.step_title}' failed on attempt {self.attempt}"


@dataclass
class ArtifactError(OrchestratorError):
    """Raised when artifact validation fails."""
    missing_files: List[str] = field(default_factory=list)
    hallucinated_files: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        self.category = ErrorCategory.ARTIFACT_MISSING
        self.severity = ErrorSeverity.WARNING
        if self.missing_files:
            self.message = f"Missing artifacts: {self.missing_files}"
        elif self.hallucinated_files:
            self.category = ErrorCategory.ARTIFACT_INVALID
            self.message = f"Hallucinated artifacts: {self.hallucinated_files}"


@dataclass
class CriticRejectionError(OrchestratorError):
    """Raised when the critic agent rejects work."""
    feedback: str = ""
    
    def __post_init__(self):
        self.category = ErrorCategory.CRITIC_REJECTED
        self.severity = ErrorSeverity.WARNING
        self.message = f"Critic rejected: {self.feedback[:100]}..."


@dataclass
class InvalidStateTransitionError(OrchestratorError):
    """Raised when an invalid state transition is attempted."""
    from_state: Any = None
    to_state: Any = None
    valid_targets: List[Any] = field(default_factory=list)
    
    def __post_init__(self):
        self.category = ErrorCategory.INVALID_TRANSITION
        self.severity = ErrorSeverity.CRITICAL
        self.recoverable = False
        valid_names = [s.name for s in self.valid_targets]
        self.message = (
            f"Invalid state transition: {self.from_state.name} → {self.to_state.name}. "
            f"Valid targets: {valid_names}"
        )


@dataclass
class SelfHealingFailedError(OrchestratorError):
    """Raised when self-healing/replanning fails."""
    original_error: str = ""
    
    def __post_init__(self):
        self.category = ErrorCategory.INVALID_PLAN
        self.severity = ErrorSeverity.CRITICAL
        self.recoverable = False
        self.message = f"Self-healing failed. Original error: {self.original_error}"


@dataclass
class LLMError(OrchestratorError):
    """Raised when LLM API call fails."""
    model: str = ""
    error_type: str = ""
    
    def __post_init__(self):
        self.category = ErrorCategory.LLM_API
        self.severity = ErrorSeverity.ERROR
        self.message = f"LLM error ({self.model}): {self.error_type}"


@dataclass  
class MCPServerError(OrchestratorError):
    """Raised when MCP server communication fails."""
    server_name: str = ""
    tool_name: str = ""
    
    def __post_init__(self):
        self.category = ErrorCategory.MCP_SERVER
        self.severity = ErrorSeverity.ERROR
        self.message = f"MCP server '{self.server_name}' error on tool '{self.tool_name}'"


# =============================================================================
# Error Utilities
# =============================================================================

def classify_error(exception: Exception) -> OrchestratorError:
    """
    Classify a generic exception into an OrchestratorError.
    
    Useful for wrapping unexpected errors with proper classification.
    """
    if isinstance(exception, OrchestratorError):
        return exception
    
    error_str = str(exception).lower()
    
    # Pattern matching for common errors
    if "connection" in error_str or "network" in error_str or "timeout" in error_str:
        return OrchestratorError(
            message=str(exception),
            category=ErrorCategory.NETWORK,
            severity=ErrorSeverity.ERROR,
            recoverable=True,
        )
    elif "json" in error_str or "parse" in error_str:
        return OrchestratorError(
            message=str(exception),
            category=ErrorCategory.INVALID_PLAN,
            severity=ErrorSeverity.WARNING,
            recoverable=True,
        )
    elif "file" in error_str or "path" in error_str or "permission" in error_str:
        return OrchestratorError(
            message=str(exception),
            category=ErrorCategory.FILE_SYSTEM,
            severity=ErrorSeverity.ERROR,
            recoverable=True,
        )
    else:
        return OrchestratorError(
            message=str(exception),
            category=ErrorCategory.UNKNOWN,
            severity=ErrorSeverity.ERROR,
            recoverable=True,
        )


def is_recoverable(error: Exception) -> bool:
    """Check if an error can be recovered from."""
    if isinstance(error, OrchestratorError):
        return error.recoverable
    return True  # Default to recoverable for unknown errors
