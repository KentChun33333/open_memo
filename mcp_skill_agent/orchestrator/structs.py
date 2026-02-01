from dataclasses import dataclass, field
from typing import List, Optional
import xml.etree.ElementTree as ET

@dataclass
class WorkerHandover:
    """
    Structured Context passed to the Worker Agent.
    """
    task_input: str
    active_folder: str
    roadmap: str
    session_context: str
    tool_definitions: str = ""
    expectations: List[str] = field(default_factory=list)

    def to_xml(self) -> str:
        """Serializes the handover context to XML for the Worker."""
        return f"""
<WorkerContext>
<TaskInput>{self.task_input}</TaskInput>
<ActiveFolder>{self.active_folder}</ActiveFolder>
<ProjectRoadmap>
{self.roadmap}
</ProjectRoadmap>
<SessionContext>
{self.session_context}
</SessionContext>
<ToolDefinitions>
{self.tool_definitions}
</ToolDefinitions>
<ExpectedArtifacts>{", ".join(self.expectations)}</ExpectedArtifacts>
</WorkerContext>
""".strip()

@dataclass
class StepHandover:
    """
    Structured Output from the Worker Agent (Step Execution).
    """
    success: bool
    output: str
    feedback: str = ""

@dataclass
class CriticHandover:
    """
    Structured Context passed to the Technical Critic.
    """
    step_id: str
    step_title: str
    worker_output: str
    active_folder: str
    roadmap: str
    global_context: str = "" # New field
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
        add_section("GlobalContext", self.global_context) # Added
        add_section("ProjectRoadmap", self.roadmap)
        add_section("ExpectedArtifacts", ", ".join(self.expectations))

        # Pretty print logic hack for XML (ElementTree doesn't pretty print by default in old python)
        # Using simple string formatting for robustness
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
class SkillStep:
    """
    Structured SOP Step (The Plan).
    Acts as the contract between SOPAgent (Planner) and StepExecutor.
    """
    id: int
    title: str
    task_instruction: str = "" # Generated instruction for this task (Narrative Plan)
    task_query: str = ""       # Detail action required considering user query (Contextualized Action)
    content: str = ""          # Legacy content/context (Optional)
    references: List[str] = field(default_factory=list)
    expected_artifacts: List[str] = field(default_factory=list)
    skill_raw_context: str = "" # The raw SKILL.md content (Full Context)
    status: str = "pending"
    allow_rollback: bool = False

