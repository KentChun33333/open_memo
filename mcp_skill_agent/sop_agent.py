import json
import logging
import asyncio
from typing import List, Optional, Union, Dict
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

logger = logging.getLogger(__name__)

@dataclass
class SkillStep:
    id: int
    title: str
    content: str = ""
    references: List[str] = field(default_factory=list)
    expected_artifacts: List[str] = field(default_factory=list)
    status: str = "pending"
    allow_rollback: bool = False
    

class SOPAgent:
    def __init__(self, app: MCPApp):
        self.app = app
        self.steps: List[SkillStep] = []
        self.current_index = 0
        self.skill_context = ""
        self.resources_info = ""

    async def initialize(self, skill_content: str, resources_info: str = ""):
        """
        Refactored Initialization: Chunk-and-Tag Strategy.
        1. Identify Steps (LLM)
        2. Chunk Content (Rule)
        3. Tag Chunks (LLM)
        4. Aggregate
        """
        self.skill_context = skill_content
        self.resources_info = resources_info
        logger.info("SOPAgent: Initializing Chunk-and-Tag Parsing...")

        # 1. Identify Steps
        # 1. Identify Steps & Expectations
        step_data = await self._identify_steps(skill_content)
        if not step_data:
            logger.warning("No steps identified. Falling back to single step.")
            self.steps = [SkillStep(id=1, title="Execute Skill", content=skill_content)]
            return

        # Initialize Steps
        # Initialize Steps (Rich Metadata)
        # Handle backward compatibility if _identify_steps returns plain strings (though we updated it)
        try:
             self.steps = []
             for i, s_data in enumerate(step_data):
                  if isinstance(s_data, str):
                       self.steps.append(SkillStep(id=i+1, title=s_data))
                  else:
                       title = s_data.get("title", f"Step {i+1}")
                       artifacts = s_data.get("expected_files", [])
                       self.steps.append(SkillStep(id=i+1, title=title, expected_artifacts=artifacts))
        except Exception:
             # Fallback
             self.steps = [SkillStep(id=i+1, title=t) for i, t in enumerate(step_data)]
        
        # 2. Chunk Content
        chunks = self._split_by_paragraphs(skill_content)
        
        # 3. Tag Chunks
        # Extract titles for tagging prompt
        titles_only = [s.title for s in self.steps]
        tagged_map = await self._tag_chunks(chunks, titles_only)
        
        # 4. Aggregate Content & References
        for i, step in enumerate(self.steps):
            # Get chunks for this step (1-based ID)
            step_chunks = tagged_map.get(step.id, [])
            
            # Concatenate content
            step.content = "\n\n".join(step_chunks)
            
            # [Optimization] We could ask LLM to identify references per step here, 
            # or just append general resources info to every step context. 
            # User asked for "reference... provide path". 
            # Let's simple append the RESOURCES INFO to the bottom of the content 
            # so the subagent can choose. 
            # Or better, we can assume the chunks contain the reference text if the manual works that way.
            # Let's add a "RESOURCES" section if available.
            
            if not step.content.strip():
                 step.content = "(No content found for this step in manual.)"
        
        self.current_index = 0
        logger.info(f"SOPAgent: Parsed {len(self.steps)} steps.")

    async def _identify_steps(self, content: str) -> List[Dict]:
        """Ask LLM to list high-level steps with expected artifacts."""
        prompt = f"""You are a PLANNER.
Analyze the Technical Manual. 
Break it down into Execution Steps.
For each step, identify ANY file/artifact that MUST exist after completion.

MANUAL:
{content[:15000]}...

OUTPUT JSON ONLY:
{{
  "steps": [
    {{ "title": "Initialize Repository", "expected_files": ["package.json"] }},
    {{ "title": "Create User Component", "expected_files": ["src/components/User.tsx"] }}
  ]
}}
"""
        agent = Agent(name="StepIdent", instruction="Extract steps and artifacts as JSON.")
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            try:
                resp = await llm.generate_str(prompt)
                import json
                json_str = resp.strip().replace("```json", "").replace("```", "")
                data = json.loads(json_str)
                return data.get("steps", [])
            except Exception as e:
                logger.error(f"Step ID failed: {e}")
                return []

    def _split_by_paragraphs(self, content: str) -> List[str]:
        """Split by double newline."""
        # Normalize newlines
        content = content.replace("\r\n", "\n")
        # Split by empty lines
        chunks = [c.strip() for c in content.split("\n\n") if c.strip()]
        return chunks

    async def _tag_chunks(self, chunks: List[str], step_titles: List[str]) -> Dict[int, List[str]]:
        """
        Ask LLM to assign each chunk to a Step ID.
        Returns: { step_id: [chunk_text, ...] }
        """
        # We process in batches to avoid huge context, but ideally we want global context.
        # Let's try to do it effectively: index chunks and ask for a map.
        
        # Prepare Step Map for Prompt
        steps_str = "\n".join([f"{i+1}. {t}" for i, t in enumerate(step_titles)])
        
        # We'll map chunks to steps. 
        # Output: { chunk_index: step_id }
        
        # Prepare Chunks with Indices
        chunk_text_block = ""
        for i, c in enumerate(chunks):
            preview = c[:100].replace("\n", " ")
            chunk_text_block += f"[{i}] {preview}...\n"
            
        prompt = f"""You are a CONTENT SORTER.
Map each Text Chunk to the most relevant Step ID.

STEPS:
{steps_str}

TEXT CHUNKS:
{chunk_text_block}

TASK: Return a JSON mapping of Chunk Index -> Step ID.
If a chunk is irrelevant (preamble), map to 0.
If a chunk applies to multiple, pick the FIRST relevant one.

OUTPUT JSON ONLY:
{{
  "mapping": {{
    "0": 1,
    "1": 1,
    "2": 2
  }}
}}
"""
        agent = Agent(name="ChunkTagger", instruction="Map chunks to steps.")
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            try:
                resp = await llm.generate_str(prompt)
                import json
                json_str = resp.strip().replace("```json", "").replace("```", "")
                data = json.loads(json_str)
                mapping = data.get("mapping", {})
                
                # Reconstruct
                result = {}
                for idx_str, step_id in mapping.items():
                    idx = int(idx_str)
                    if 0 <= idx < len(chunks) and step_id > 0:
                        if step_id not in result: result[step_id] = []
                        result[step_id].append(chunks[idx])
                
                # Handle unmapped chunks? (Maybe preamble)
                return result
                
            except Exception as e:
                logger.error(f"Tagging failed: {e}")
                # Fallback: All to Step 1
                return {1: chunks}

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

    def detect_context_switch(self, step: SkillStep) -> Dict[str, Union[bool, str]]:
        """
        Defensive Check: Analyze step to predict if it will change the filesystem root.
        Focuses on: 'run_skill_script', 'mkdir', 'create project', 'cd'.
        """
        content_lower = step.content.lower() + " " + step.title.lower()
        
        # 1. Script Execution (High Probability of Init)
        if "run_skill_script" in content_lower:
            return {"detected": True, "reason": "Detected 'run_skill_script' execution."}
            
        # 2. Key Phrases
        triggers = [
            "mkdir", 
            "create project", 
            "new project", 
            "initialize", 
            "cd "
        ]
        
        for trigger in triggers:
            if trigger in content_lower:
                return {"detected": True, "reason": f"Detected keyword '{trigger}'."}
                
        return {"detected": False, "reason": ""}
