import re
import asyncio
from enum import Enum
from typing import List, Optional
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from ..logger import get_logger
from ..prompt import ROUTER_PERSONA_INSTRUCTION, ROUTER_EVALUATION_INSTRUCTION

logger = get_logger("router")

class RouterDecision(Enum):
    CONTINUE = "CONTINUE"
    SUCCESS = "SUCCESS"
    INTERVENTION_TECH_LEAD = "INTERVENTION_TECH_LEAD"
    INTERVENTION_SWITCH_FRONTEND = "INTERVENTION_SWITCH_FRONTEND"

class EvaluationRouter:
    """
    Smart Router Agent.
    Uses an LLM to make high-level control flow decisions.
    """
    def __init__(self):
        self.agent = Agent(name="Router", instruction="You are a control flow manager.")

    async def select_persona(self, step_title: str, skill_name: str, content: str) -> str:
        """
        Decides which persona should handle the task.
        """
        # Truncate content for token efficiency
        content_snippet = content[:500] if content else ""
        
        prompt = ROUTER_PERSONA_INSTRUCTION.format(
            step_title=step_title,
            skill_name=skill_name,
            content_snippet=content_snippet
        )

        try:
            async with self.agent:
                llm = await self.agent.attach_llm(OpenAIAugmentedLLM)
                response = await llm.generate_str(prompt)
                
                decision = response.strip().replace('"', '').replace("'", "")
                
                # Validation
                valid_personas = ["DEFAULT", "FRONTEND_SPECIALIST", "TECH_LEAD"]
                if decision not in valid_personas:
                    logger.warning(f"Router: Invalid persona '{decision}'. Defaulting.")
                    return "DEFAULT"
                
                logger.info(f"Router: Selected Persona -> {decision}")
                return decision
        except Exception as e:
            logger.error(f"Router Persona Selection Failed: {e}")
            return "DEFAULT"

    async def evaluate(self, recent_output: str, history: List[List[str]], cycle: int, success_signal: bool, task_title: str = "") -> RouterDecision:
        """
        Determines the next state based on LLM analysis of the execution.
        """
        if success_signal:
            return RouterDecision.SUCCESS
            
        # Optimization: Only call LLM if error keywords exist OR cycle count is high
        # We start with basic heuristics to save latency, then escalate to LLM if needed?
        # User requested "keyword approach is too rigid causing errors". 
        # So we should rely more on LLM, but maybe purely on LLM is slow.
        # Compromise: Always call LLM but keep prompt short.
        
        # Tool History formatting
        tool_history_str = str(history[-3:]) if len(history) >= 3 else str(history)

        prompt = ROUTER_EVALUATION_INSTRUCTION.format(
            cycle=cycle,
            task_title=task_title,
            recent_output=recent_output[-2000:], # Context window management
            tool_history=tool_history_str
        )

        try:
            async with self.agent:
                llm = await self.agent.attach_llm(OpenAIAugmentedLLM)
                response = await llm.generate_str(prompt)
                
                decision_str = response.strip().replace('"', '').replace("'", "")
                
                # Map string to Enum
                try:
                    # check for substring match if LLM is chatty
                    if "INTERVENTION_SWITCH_FRONTEND" in decision_str:
                        return RouterDecision.INTERVENTION_SWITCH_FRONTEND
                    if "INTERVENTION_TECH_LEAD" in decision_str:
                         return RouterDecision.INTERVENTION_TECH_LEAD
                    if "SUCCESS" in decision_str:
                         return RouterDecision.SUCCESS
                    
                    # Default
                    return RouterDecision.CONTINUE
                except ValueError:
                    logger.warning(f"Router: Unknown decision '{decision_str}'. Continuing.")
                    return RouterDecision.CONTINUE

        except Exception as e:
            logger.error(f"Router Evaluation Failed: {e}")
            return RouterDecision.CONTINUE
