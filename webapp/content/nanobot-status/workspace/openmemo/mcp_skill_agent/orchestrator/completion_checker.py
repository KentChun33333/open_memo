"""
Completion Checker - General-purpose task completion detection.

This module provides a declarative way to define and check task completion
criteria, enabling early exit from the orchestrator loop when work is done.
"""

import os
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Tuple, Optional, Any
from ..utils.telemetry import get_telemetry

logger = get_telemetry("completion_checker")


@dataclass
class CompletionCriteria:
    """
    Declarative completion conditions.
    
    Supports multiple signal types for flexible completion detection:
    - required_artifacts: Files that must exist for completion
    - success_signals: Memory signals indicating success
    - command_checks: Shell commands that return 0 on success
    """
    required_artifacts: List[str] = field(default_factory=list)
    success_signals: List[str] = field(default_factory=list)
    command_checks: List[str] = field(default_factory=list)
    
    # Optional: custom completion message
    completion_message: str = ""
    
    def is_empty(self) -> bool:
        """Check if criteria is empty (no conditions defined)."""
        return (
            not self.required_artifacts and 
            not self.success_signals and 
            not self.command_checks
        )
    
    def to_dict(self) -> dict:
        """Serialize for logging/debugging."""
        return {
            "required_artifacts": self.required_artifacts,
            "success_signals": self.success_signals,
            "command_checks": self.command_checks,
        }


class CompletionChecker:
    """
    General-purpose task completion detector.
    
    Checks multiple signals to determine if a task is already complete,
    enabling early exit from the orchestrator loop.
    
    Usage:
        checker = CompletionChecker(memory_manager, workspace_root)
        is_done, reason = checker.is_complete(criteria)
        if is_done:
            logger.info(f"Task complete: {reason}")
            return
    """
    
    def __init__(self, memory_manager: Any, workspace_root: str):
        """
        Initialize the completion checker.
        
        Args:
            memory_manager: SessionMemoryManager instance for signal checking
            workspace_root: Root directory for resolving relative paths
        """
        self.memory = memory_manager
        self.workspace = Path(workspace_root).resolve()
    
    def is_complete(self, criteria: CompletionCriteria) -> Tuple[bool, str]:
        """
        Check if task is complete based on criteria.
        
        Returns:
            Tuple of (is_complete, reason_string)
        """
        if criteria.is_empty():
            return False, "No completion criteria defined"
        
        # 1. Check required artifacts exist
        artifact_result = self._check_artifacts(criteria.required_artifacts)
        if artifact_result[0]:
            return artifact_result
        
        # 2. Check success signals in memory
        signal_result = self._check_signals(criteria.success_signals)
        if signal_result[0]:
            return signal_result
        
        # 3. Run command checks
        command_result = self._check_commands(criteria.command_checks)
        if command_result[0]:
            return command_result
        
        return False, "Completion criteria not met"
    
    def _check_artifacts(self, artifacts: List[str]) -> Tuple[bool, str]:
        """Check if required artifacts exist."""
        if not artifacts:
            return False, ""
        
        for artifact in artifacts:
            path = self._resolve_path(artifact)
            if path.exists():
                logger.info(f"Completion artifact found: {path}")
                return True, f"Artifact exists: {artifact}"
        
        return False, ""
    
    def _check_signals(self, signals: List[str]) -> Tuple[bool, str]:
        """Check for success signals in memory."""
        if not signals:
            return False, ""
        
        # Check in memory's agent_feedback_history or tool_history
        try:
            # Check tool history for success markers
            for entry in getattr(self.memory.memory, "tool_history", []):
                tool_result = entry.get("result", "")
                for signal in signals:
                    if signal.upper() in str(tool_result).upper():
                        logger.info(f"Success signal found: {signal}")
                        return True, f"Signal detected: {signal}"
            
            # Check registered artifacts
            registered = getattr(self.memory.memory, "artifacts", {})
            if registered:
                # If we have artifacts registered, check if any match our signals
                for signal in signals:
                    if signal in str(registered):
                        return True, f"Artifact signal: {signal}"
                        
        except Exception as e:
            logger.debug(f"Signal check error: {e}")
        
        return False, ""
    
    def _check_commands(self, commands: List[str]) -> Tuple[bool, str]:
        """Run command checks (e.g., 'test -f file.html')."""
        if not commands:
            return False, ""
        
        for cmd in commands:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=str(self.workspace),
                    capture_output=True,
                    timeout=5
                )
                if result.returncode == 0:
                    logger.info(f"Command check passed: {cmd}")
                    return True, f"Check passed: {cmd}"
            except subprocess.TimeoutExpired:
                logger.warning(f"Command check timed out: {cmd}")
            except Exception as e:
                logger.debug(f"Command check error: {e}")
        
        return False, ""
    
    def _resolve_path(self, artifact: str) -> Path:
        """Resolve artifact path relative to workspace."""
        path = Path(artifact)
        if path.is_absolute():
            return path
        return self.workspace / artifact


def derive_completion_criteria(
    steps: List[Any],
    default_signals: Optional[List[str]] = None
) -> CompletionCriteria:
    """
    Auto-derive completion criteria from plan steps.
    
    Strategy:
    1. Use the LAST step's expected_artifacts as required_artifacts
    2. Add default success signals
    
    Args:
        steps: List of SkillStep objects from the plan
        default_signals: Optional override for success signals
    
    Returns:
        CompletionCriteria instance
    """
    if not steps:
        return CompletionCriteria()
    
    # Get final step's expected artifacts
    final_step = steps[-1]
    final_artifacts = getattr(final_step, "expected_artifacts", [])
    
    # Default success signals
    signals = default_signals or [
        "MISSION_COMPLETE",
        "TASK_DONE", 
        "STEP_COMPLETE",
        "BUNDLE_SUCCESS"
    ]
    
    return CompletionCriteria(
        required_artifacts=list(final_artifacts),
        success_signals=signals,
        completion_message=f"Derived from step {getattr(final_step, 'id', 'N/A')}: {getattr(final_step, 'title', '')}"
    )
