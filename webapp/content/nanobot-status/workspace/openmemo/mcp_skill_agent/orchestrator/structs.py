from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, TYPE_CHECKING
import xml.etree.ElementTree as ET
import os
import logging

logger = logging.getLogger(__name__)

# Avoid circular import
if TYPE_CHECKING:
    from .completion_checker import CompletionCriteria

@dataclass
class SkillContextDTO:
    """
    Rich Context for a Skill Discovery Phase.
    Contains everything needed to plan and execute a skill.
    """
    skill_name: str
    raw_content: str          # The full SKILL.md
    references: List[str]     # Paths to resources
    roadmap: str              # Directory structure of the skill (internal)
    tool_definitions: str     # Available tools

@dataclass
class StepExecutorInput:
    """
    Structured Context passed to the Worker Agent (StepExecutor).
    """
    task_input: str
    active_folder: str
    roadmap: str
    session_context: str
    session_context: str
    expectations: List[str] = field(default_factory=list)
    clipboard: str = "" # New: Persisted file content
    step_content: str = "" # New: Moved from User Prompt
    sop_context: str = ""  # New: Moved from User Prompt
    skill_context: str = "" # New: Full SKILL.md Manual

    alerts: List[str] = field(default_factory=list) # New: Structured Side-Channels (Warnings/Feedback)

    def to_system_protocol_view(self) -> str:
        """Returns the Static System Context (Skill Manual)."""
        return f"<SkillManual>\n{self.skill_context}\n</SkillManual>"

    def to_user_status_view(self, template: str, step_id: int, step_title: str) -> str:
        """Returns the Dynamic User Context using the provided template."""
        # Format Alerts
        alerts_str = ""
        if self.alerts:
             alerts_str = "\n".join([f"- {a}" for a in self.alerts])

        return template.format(
            task_input=self.task_input,
            sop_context=self.sop_context,
            roadmap=self.roadmap,
            clipboard=self.clipboard,
            alerts=alerts_str,
            step_id=step_id,
            step_title=step_title
        )

@dataclass
class StepExecutorOutput:
    """
    Structured Output from the Worker Agent (Step Execution).
    """
    success: bool
    output: str
    feedback: str = ""

@dataclass
class CriticInput:
    """
    Structured Context passed to the Technical Critic.
    """
    step_id: str
    step_title: str
    worker_output: str
    active_folder: str
    roadmap: str
    global_context: str = "" 
    expectations: List[str] = field(default_factory=list)

    def to_xml(self) -> str:
        """Serializes the handover context to XML for the LLM."""
        root = ET.Element("CriticContext")
        
        ET.SubElement(root, "StepID").text = str(self.step_id)
        ET.SubElement(root, "StepTitle").text = self.step_title
        ET.SubElement(root, "ActiveFolder").text = self.active_folder
        
        # Helper to safely add CDATA-like sections (text)
        def add_section(tag, text):
            elem = ET.SubElement(root, tag)
            elem.text = text if text else "(None)"

        add_section("WorkerOutput", self.worker_output)
        add_section("GlobalContext", self.global_context) 
        add_section("ProjectRoadmap", self.roadmap)
        add_section("ExpectedArtifacts", ", ".join(self.expectations))

        # Pretty print logic hack for XML 
        xml_str = f"""
<CriticContext>
<StepID>{self.step_id}</StepID>
<StepTitle>{self.step_title}</StepTitle>
<ActiveFolder>{self.active_folder}</ActiveFolder>
<WorkerOutput>
{self.worker_output}
</WorkerOutput>
<GlobalContext>
{self.global_context}
</GlobalContext>
<ProjectRoadmap>
{self.roadmap}
</ProjectRoadmap>
<ExpectedArtifacts>{", ".join(self.expectations)}</ExpectedArtifacts>
</CriticContext>
"""
        return xml_str.strip()

@dataclass
class CriticOutput:
    """
    Output from the Technical Critic.
    """
    decision: str # APPROVED / REJECTED
    feedback: str

@dataclass
class SkillStep:
    """
    Structured SOP Step (The Plan).
    Acts as the contract between AtomicPlanner and StepExecutor.
    """
    id: int
    title: str
    task_instruction: str = "" 
    task_query: str = ""       
    content: str = ""          
    references: List[str] = field(default_factory=list)
    expected_artifacts: List[str] = field(default_factory=list)
    skill_raw_context: str = "" 
    status: str = "pending"
    allow_rollback: bool = False

@dataclass
class TechLeadInput:
    """
    Input for the Tech Lead Agent.
    """
    context_xml: str
    error_log: str

@dataclass
class TechLeadOutput:
    """
    Structured Advice from the Tech Lead Agent (Active Debugging).
    """
    diagnosis: str
    advice: str
    severity: str = "warning" # info, warning, critical
    
    def to_prompt_format(self) -> str:
        """Formats the advice for injection into the Worker's prompt."""
        icon = "ℹ️"
        if self.severity == "warning": icon = "⚠️"
        if self.severity == "critical": icon = "🚨"
        
        return f"""
{icon} **TECH LEAD INTERVENTION**
**Diagnosis**: {self.diagnosis}
**Advice**: {self.advice}
"""

@dataclass
class AtomicPlannerInput:
    """
    Input for AtomicPlanner Phase.
    """
    query: str
    skill_content: str
    resources: str # Joined string of resources

@dataclass
class AtomicPlannerOutput:
    """
    Output from AtomicPlanner Phase (The Plan).
    """
    steps: List[SkillStep]
    reasoning: str = ""  # Explanation of the plan logic
    completion_criteria: Optional['CompletionCriteria'] = None  # Auto-derived or custom

@dataclass
class SessionMemory:
    workspace_root: str
    cwd_rel: str = "." # Stores relative path from workspace_root
    project_root: str = "" # Absolute path to current project root (if any)
    artifacts: Dict[str, List[str]] = field(default_factory=dict)

    # directory_tree removed (redundant)
    env_vars: Dict[str, str] = field(default_factory=dict)     # New: Environment Variables
    step_outputs: Dict[int, str] = field(default_factory=dict) # New: Step Outputs
    tool_history: List[Dict[str, Any]] = field(default_factory=list) # New: Tool Execution History
    clipboard: Dict[str, str] = field(default_factory=dict) # New: Cross-step file cache
    plan: List[Dict[str, Any]] = field(default_factory=list) # New: Persisted Execution Plan
    agent_feedback_history: List[Dict[str, Any]] = field(default_factory=list) # New: Generic Feedback History
    current_step_id: int = 0
    current_step_id: int = 0

    @property
    def active_folder(self) -> str:
        """Dynamic property to get absolute active folder path."""
        return os.path.abspath(os.path.join(self.workspace_root, self.cwd_rel))

    @active_folder.setter
    def active_folder(self, value: str):
        """
        Setter to update cwd_rel from an absolute or relative path.
        Validates that the path stays within workspace_root.
        """
        if os.path.isabs(value):
            abs_path = os.path.abspath(value)
        else:
            abs_path = os.path.abspath(os.path.join(self.workspace_root, value))
        
        # Validate: path must be within workspace_root
        workspace_resolved = os.path.abspath(self.workspace_root)
        if not abs_path.startswith(workspace_resolved):
            logger.warning(
                f"SessionMemory: Blocked attempt to set active_folder outside workspace. "
                f"Requested: {abs_path}, Workspace: {workspace_resolved}"
            )
            return  # Silently reject - don't update
        
        # Update cwd_rel
        self.cwd_rel = os.path.relpath(abs_path, self.workspace_root)
