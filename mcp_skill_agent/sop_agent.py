import json
import logging
from typing import List, Optional
from dataclasses import dataclass
from pydantic import BaseModel, Field

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

logger = logging.getLogger(__name__)

@dataclass
class SkillStep:
    id: int
    title: str
    content: str
    status: str = "pending"

# API Model for Structured Output (Internal use for validation)
class SOPOutput(BaseModel):
    steps: List[dict] = Field(description="List of step dictionaries with id, title, content")

    class Step(BaseModel):
        id: int
        title: str
        content: str
    
    steps: List[Step]

class SOPParserAgent:
    """
    An Agent responsible for reading raw skill manuals (Markdown) 
    and converting them into a structured List[SkillStep] JSON.
    Uses generate_str + manual parsing for small model compatibility.
    """
    def __init__(self, app: MCPApp):
        self.app = app

    async def parse(self, skill_content: str) -> List[SkillStep]:
        logger.info("SOPParserAgent: Parsing skill content...")

        instruction = """You are the SOP ANALYST.
Your goal is to convert an unstructured Instruction Manual (text/markdown) into a linear, sequential Execution Plan.

OUTPUT JSON ONLY.
JSON SCHEMA:
{
  "steps": [
    {
      "id": 1,
      "title": "Short verb-noun title",
      "content": "Detailed instructions..."
    }
  ]
}
"""
        # Trim content if too long for parsing context (naive truncation)
        context_content = skill_content[:10000] 

        # Assumes app context is already active in caller (Single Context Pattern)
        parser = Agent(name="SOPParser", instruction=instruction)
        async with parser:
            llm = await parser.attach_llm(OpenAIAugmentedLLM)
            # Use generate_str for robust parsing (avoiding strict schema freeze on small models)
            response_str = await llm.generate_str(f"Parse this SOP:\n\n{context_content}")
            
            try:
                 # Attempt to clean markdown fencing
                 clean_json = response_str.replace("```json", "").replace("```", "").strip()
                 data = json.loads(clean_json)
                 response = SOPOutput(**data)
            except Exception as e:
                logger.error(f"SOP Parse Error: {e} | Raw: {response_str}")
                return []
                
        steps = []
        for item in response.steps:
            steps.append(SkillStep(
                id=item.id,
                title=item.title,
                content=item.content,
                status="pending"
            ))
        
        if not steps:
            logger.warning("SOPParserAgent found no steps. Returning empty list.")
        
        return steps

# Simple State Wrapper for the runtime to use
class SOPController:
    def __init__(self, steps: List[SkillStep]):
        self.steps = steps
        self.current_index = 0
        
    def get_current_step(self) -> Optional[SkillStep]:
        if 0 <= self.current_index < len(self.steps):
            return self.steps[self.current_index]
        return None

    def advance_step(self):
        if 0 <= self.current_index < len(self.steps):
            self.steps[self.current_index].status = "done"
            self.current_index += 1
            if self.current_index < len(self.steps):
                self.steps[self.current_index].status = "active"

    def is_finished(self) -> bool:
        return self.current_index >= len(self.steps)

    def get_progress_summary(self) -> str:
        summary = []
        for step in self.steps:
            mark = "[x]" if step.status == "done" else "[ ]"
            if step == self.get_current_step():
                mark = "[>]" 
            summary.append(f"{mark} Step {step.id}: {step.title}")
        return "\n".join(summary)
    
    def build_prompt_context(self) -> str:
        current = self.get_current_step()
        if not current: return "ALL STEPS COMPLETED."
        return f"""SOP STATUS:
{self.get_progress_summary()}

ACTIVE STEP {current.id}: {current.title}
DETAILS:
{current.content}
"""
