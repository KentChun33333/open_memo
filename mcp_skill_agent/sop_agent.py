import json
import logging
import asyncio
from typing import List, Optional, Union, Dict
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

# Import from structs
from .orchestrator.structs import SkillStep

logger = logging.getLogger(__name__)

class SOPAgent:
    def __init__(self):
        self.steps: List[SkillStep] = []
        self.current_index = 0

    async def initialize(self, skill_content: str, resources_info: str = "", task_input: str = ""):
        """
        Refactored Initialization: Stateless & Linear.
        1. Identify Steps (LLM) with Rich Metadata
        2. Instantiate SkillStep objects
        """
        logger.info("SOPAgent: Initializing Linear Parsing...")

        # 1. Identify Steps & Expectations (Rich Metadata)
        step_data = await self._identify_steps(skill_content, resources_info, task_input)
        if not step_data:
            logger.warning("No steps identified. Falling back to single step.")
            self.steps = [SkillStep(id=1, title="Execute Skill", content=skill_content, skill_raw_context=skill_content)]
            return

        # 2. Initialize Steps (Rich Metadata)
        try:
             self.steps = []
             for i, s_data in enumerate(step_data):
                  if isinstance(s_data, str):
                       self.steps.append(SkillStep(id=i+1, title=s_data, skill_raw_context=skill_content))
                  else:
                       title = s_data.get("title", f"Step {i+1}")
                       # Fallback support for various key names
                       artifacts = s_data.get("expected_files", []) or s_data.get("expected_artifacts", [])
                       narrative = s_data.get("task_instruction", "")
                       action = s_data.get("task_query", "")
                       refs = s_data.get("references", [])
                       
                       # Use narrative as default content if available
                       content = narrative if narrative else "(See Task Instruction)"

                       self.steps.append(SkillStep(
                           id=i+1, 
                           title=title, 
                           expected_artifacts=artifacts,
                           task_instruction=narrative,
                           task_query=action,
                           references=refs,
                           skill_raw_context=skill_content, # Pass full context
                           content=content
                        ))
        except Exception as e:
             logger.error(f"Failed to parse step data: {e}")
             # Fallback
             self.steps = [SkillStep(id=i+1, title=str(d), skill_raw_context=skill_content) for i, d in enumerate(step_data)]
        
        self.current_index = 0
        logger.info(f"SOPAgent: Parsed {len(self.steps)} steps.")

    async def _identify_steps(self, content: str, resources: str, query: str) -> List[Dict]:
        """Ask LLM to list high-level steps with rich metadata."""
        prompt = f"""You are a STRATEGIC PLANNER.
Analyze the Technical Manual and the User's Query.
Break the workflow down into Linear Execution Steps.

USER QUERY: "{query}"

AVAILABLE RESOURCES:
{resources}

MANUAL:
{content[:15000]}...

CRITICAL INSTRUCTION:
For each step, generate:
1. title: Concise title.
2. task_instruction: High-level narrative of what to do (the 'Plan').
3. task_query: Specific, actionable detailed instruction for the Subagent to execute now (contextualized to the User's Query).
4. expected_artifacts: List of files created/modified.
5. references: List of relevant files/docs from Resource list.

OUTPUT JSON ONLY:
{{
  "steps": [
    {{
      "title": "Initialize Repository",
      "task_instruction": "Set up the project structure using the init script.",
      "task_query": "Run `init-artifact.sh` to scaffold the project for a 'Waitlist Page'.",
      "expected_artifacts": ["package.json", "vite.config.ts"],
      "references": ["scripts/init-artifact.sh"]
    }}
  ]
}}
"""
        agent = Agent(name="StepIdent", instruction="Extract steps as JSON.")
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            try:
                resp = await llm.generate_str(prompt)
                import json
                import re
                
                # Robust extraction
                json_str = resp.strip()
                match = re.search(r"```json\s*(\{.*?\})\s*```", resp, re.DOTALL)
                if match: json_str = match.group(1)
                elif re.search(r"(\{.*\})", resp, re.DOTALL):
                     json_str = re.search(r"(\{.*\})", resp, re.DOTALL).group(1)
                
                data = json.loads(json_str)
                return data.get("steps", [])
            except Exception as e:
                logger.error(f"Step ID failed: {e}")
                return []


    # --- Runtime Control ---

    def get_current_step(self) -> Optional[SkillStep]:
        if 0 <= self.current_index < len(self.steps):
            return self.steps[self.current_index]
        return None

    def mark_step_done(self):
        current = self.get_current_step()
        if current:
            current.status = "done"
            logger.info(f"SOPAgent: Finished Step {current.id}")
            self.current_index += 1
            
            nxt = self.get_current_step()
            if nxt: nxt.status = "active"

    def is_finished(self) -> bool:
        return self.current_index >= len(self.steps)

    def get_progress_summary(self) -> str:
        """Text summary for Prompt Context"""
        summary = ["Task List:"]
        for step in self.steps:
            mark = "[x]" if step.status == "done" else "[ ]"
            if step == self.get_current_step(): mark = "[/]"
            summary.append(f"{mark} {step.title}")
        return "\n".join(summary)

    # Context Switch Logic Removed
