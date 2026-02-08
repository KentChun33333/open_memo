import os
import re
import json
from typing import Optional, List, Dict
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

from ..utils.telemetry import get_telemetry, TelemetryManager
from ..prompt import ATOMIC_PLANNER_INSTRUCTION, ATOMIC_REPLANNER_INSTRUCTION
from .structs import AtomicPlannerInput, AtomicPlannerOutput, SkillStep
from .completion_checker import CompletionCriteria

logger = get_telemetry("atomic_planner")

class AtomicPlanner:
    def __init__(self):
        pass

    async def plan(self, input_data: AtomicPlannerInput) -> AtomicPlannerOutput:
        """
        Refactored Initialization: Stateless & Linear.
        1. Identify Steps (LLM) with Rich Metadata
        2. Instantiate SkillStep objects
        3. Return Output DTO
        """
        logger.info("AtomicPlanner: Initializing Linear Parsing...")
        
        # 0. Telemetry & Cache Check
        tm = TelemetryManager()
        tm.log_event(event_type="PLANNING_START", agent_name="AtomicPlanner", details={"query": input_data.query})

        # 1. Identify Steps & Expectations (Rich Metadata)
        raw_output = await self._identify_steps(input_data)
        step_data = raw_output.get("steps", [])
        reasoning = raw_output.get("reasoning", "No reasoning provided.")
        
        steps = []
        
        if not step_data:
            logger.warning("No steps identified. Falling back to single step.")
            steps = [SkillStep(id=1, title="Execute Skill", content=input_data.skill_content, skill_raw_context=input_data.skill_content)]
            output = AtomicPlannerOutput(steps=steps, reasoning=reasoning)
            return output

        # 2. Initialize Steps (Rich Metadata)
        try:
            for i, s_data in enumerate(step_data):
                if isinstance(s_data, str):
                    step = SkillStep(id=i+1, title=s_data, skill_raw_context=input_data.skill_content)
                    # Validate and synthesize
                    step = self._validate_step(step)
                    steps.append(step)
                else:
                    title = s_data.get("title", f"Step {i+1}")
                    # Fallback support for various key names
                    artifacts = s_data.get("expected_files", []) or s_data.get("expected_artifacts", [])
                    narrative = s_data.get("task_instruction", "")
                    action = s_data.get("task_query", "")
                    refs = s_data.get("references", [])
                    
                    # Use narrative as default content if available
                    content = narrative if narrative else "(See Task Instruction)"

                    step = SkillStep(
                        id=i+1, 
                        title=title, 
                        expected_artifacts=artifacts,
                        task_instruction=narrative,
                        task_query=action,
                        references=refs,
                        skill_raw_context=input_data.skill_content, # Pass full context
                        content=content
                    )
                    # Validate and synthesize
                    step = self._validate_step(step)
                    steps.append(step)
        except Exception as e:
            logger.error(f"Failed to parse step data: {e}")
            # Fallback
            steps = [SkillStep(id=i+1, title=str(d), skill_raw_context=input_data.skill_content) for i, d in enumerate(step_data)]
        
        logger.info(f"AtomicPlanner: Parsed {len(steps)} steps.")
        
        # Derive completion criteria from the plan
        completion_criteria = self._derive_completion_criteria(steps)
        
        final_output = AtomicPlannerOutput(
            steps=steps, 
            reasoning=reasoning,
            completion_criteria=completion_criteria
        )

        # Telemetry: Log the full plan
        tm.log_event(
            event_type="PLANNING_COMPLETE", 
            agent_name="AtomicPlanner", 
            details={
                "step_count": len(steps), 
                "reasoning": reasoning,
                "steps": [s.title for s in steps],
                "completion_artifacts": completion_criteria.required_artifacts
            }
        )
                
        return final_output

    async def replan(self, current_plan: AtomicPlannerOutput, failed_step: SkillStep, failure_reason: str, skill_content: str) -> AtomicPlannerOutput:
        """
        Self-Healing Mode: Generates a rescue plan.
        """
        logger.info(f"AtomicPlanner: RE-PLANNING due to failure in '{failed_step.title}'...")
        
        # 0. Telemetry
        tm = TelemetryManager()
        tm.log_event(
            event_type="REPLAN_START", 
            agent_name="AtomicPlanner", 
            details={
                "failed_step": failed_step.title, 
                "reason": failure_reason
            }
        )
        
        # 1. Ask LLM for Rescue Plan
        prompt = ATOMIC_REPLANNER_INSTRUCTION.format(
            query="Original Goal (Implied)", # We might need to persist original query or retrieve it.
            failed_step=failed_step.title,
            failure_reason=failure_reason,
            content=skill_content
        )
        
        agent = Agent(name="AtomicRepanner", instruction="Generate Recovery Plan.")
        
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            try:
                resp = await llm.generate_str(prompt)
                
                # ... reuse extraction logic ... or extract to helper
                json_str = resp.strip()
                match = re.search(r"```json\s*(\{.*?\})\s*```", resp, re.DOTALL)
                if match: json_str = match.group(1)
                elif re.search(r"(\{.*\})", resp, re.DOTALL):
                     json_str = re.search(r"(\{.*\})", resp, re.DOTALL).group(1)
                
                data = json.loads(json_str)
                step_data = data.get("steps", [])
                reasoning = data.get("reasoning", "Recovery Plan")
                
                # 2. Parse New Steps
                new_steps = []
                for i, s_data in enumerate(step_data):
                        # ... simplified parsing (assuming replan prompt is strict) ...
                        title = s_data.get("title", f"Recovery Step {i+1}")
                        narrative = s_data.get("task_instruction", "")
                        action = s_data.get("task_query", "")
                        
                        new_steps.append(SkillStep(
                           id=failed_step.id + 1 + i, # Re-index properly later?
                           title=title, 
                           expected_artifacts=s_data.get("expected_artifacts", []),
                           task_instruction=narrative,
                           task_query=action,
                           references=s_data.get("references", []),
                           skill_raw_context=skill_content,
                           content=narrative
                        ))
                
                logger.info(f"AtomicPlanner: Generated {len(new_steps)} rescue steps.")
                
                tm.log_event(
                    event_type="REPLAN_COMPLETE", 
                    agent_name="AtomicPlanner", 
                    details={"new_step_count": len(new_steps), "reasoning": reasoning}
                )
                
                return AtomicPlannerOutput(steps=new_steps, reasoning=reasoning)

            except Exception as e:
                logger.error(f"Replanning failed: {e}")
                return AtomicPlannerOutput(steps=[], reasoning="Replanning Failed")

    async def _identify_steps(self, input_data: AtomicPlannerInput) -> Dict:
        """Ask LLM to list high-level steps with rich metadata."""
        prompt = ATOMIC_PLANNER_INSTRUCTION.format(
            query=input_data.query,
            content=input_data.skill_content,
            resources=input_data.resources
        )
        agent = Agent(name="AtomicPlanner", instruction="Extract steps as JSON.")
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            try:
                resp = await llm.generate_str(prompt)
                
                # DEBUG: Log the raw LLM response
                logger.info(f"[DEBUG] Raw LLM response length: {len(resp)} chars")
                logger.info(f"[DEBUG] Raw LLM response (first 500 chars):\n{resp[:500]}")
                
                # Robust extraction
                json_str = resp.strip()
                match = re.search(r"```json\s*(\{.*?\})\s*```", resp, re.DOTALL)
                if match: 
                    json_str = match.group(1)
                    logger.info("[DEBUG] Extracted JSON from ```json``` block")
                elif re.search(r"(\{.*\})", resp, re.DOTALL):
                    json_str = re.search(r"(\{.*\})", resp, re.DOTALL).group(1)
                    logger.info("[DEBUG] Extracted JSON from raw braces")
                else:
                    logger.warning("[DEBUG] No JSON structure found in response!")
                
                data = json.loads(json_str)
                logger.info(f"[DEBUG] Parsed JSON keys: {list(data.keys())}")
                logger.info(f"[DEBUG] Steps count: {len(data.get('steps', []))}")
                return data
            except Exception as e:
                logger.error(f"Step ID failed: {e}")
                logger.error(f"[DEBUG] Failed json_str (first 500): {json_str[:500] if json_str else 'None'}")
                return {}

    def _derive_completion_criteria(self, steps: List[SkillStep]) -> CompletionCriteria:
        """
        Derive completion criteria from the plan's steps.
        
        Strategy:
        1. Collect all expected_artifacts from ALL steps (not just final)
        2. Prioritize the final step's artifacts as primary completion check
        3. Add default success signals
        
        Args:
            steps: List of SkillStep objects from the plan
            
        Returns:
            CompletionCriteria with required_artifacts and success_signals
        """
        if not steps:
            return CompletionCriteria()
        
        # Collect final step artifacts (primary completion check)
        final_step = steps[-1]
        final_artifacts = list(getattr(final_step, "expected_artifacts", []))
        
        # Also collect ALL artifacts from all steps for comprehensive check
        all_artifacts = []
        for step in steps:
            step_artifacts = getattr(step, "expected_artifacts", [])
            all_artifacts.extend(step_artifacts)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_all = []
        for a in all_artifacts:
            if a not in seen:
                seen.add(a)
                unique_all.append(a)
        
        # Use final step artifacts as primary (for early exit)
        # If no final artifacts, use all collected artifacts
        required = final_artifacts if final_artifacts else unique_all
        
        # Default success signals
        signals = [
            "MISSION_COMPLETE",
            "TASK_DONE",
            "BUNDLE_SUCCESS",
            "[STEP_COMPLETE]"
        ]
        
        criteria = CompletionCriteria(
            required_artifacts=required,
            success_signals=signals,
            completion_message=f"Plan has {len(steps)} steps, final: {getattr(final_step, 'title', 'N/A')}"
        )
        
        logger.info(f"Derived completion criteria: {len(required)} artifacts, {len(signals)} signals")
        return criteria

