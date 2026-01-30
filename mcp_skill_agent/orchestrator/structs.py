from dataclasses import dataclass, field
from typing import List, Optional
import xml.etree.ElementTree as ET

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
<ProjectRoadmap>
{self.roadmap}
</ProjectRoadmap>
<ExpectedArtifacts>{", ".join(self.expectations)}</ExpectedArtifacts>
</CriticContext>
"""
        return xml_str.strip()
