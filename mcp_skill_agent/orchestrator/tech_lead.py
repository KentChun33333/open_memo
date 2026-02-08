import json
from typing import List, Dict, Optional
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from ..utils.telemetry import get_telemetry
from .structs import TechLeadOutput, StepExecutorInput, SkillStep, TechLeadInput

logger = get_telemetry("tech_lead")

TECH_LEAD_INSTRUCTION = """You are a SENIOR TECHNICAL LEAD (The "Active Debugger").
Your Junior Engineer (The Worker) is STUCK or failing.
Your goal is to unblock them with SPECIFIC, TECHNICAL advice.

CONTEXT:
{context_xml}

ERROR LOG / RECENT OUTPUT:
{error_log}

PROTOCOL:
1. ANALYZE the error log against the Task Input and Roadmap.
2. DIAGNOSE the root cause (e.g., "Build failed because of absolute path /vite.svg", "Missing dependency 'parcel'").
3. ADVISE specific corrective actions.
   - Do NOT say "Check the logs".
   - Say "Edit src/App.tsx and change '/vite.svg' to './vite.svg'".
   - Or "Run `npm install parcel`".
4. SEVERITY: "info" (minor suggestion), "warning" (potential blocker), "critical" (show-stopper).

OUTPUT JSON ONLY:
{{
  "diagnosis": "Brief explanation of what went wrong",
  "advice": "Specific instructions for the Worker to fix it",
  "severity": "warning"
}}
"""

class TechLead:
    def __init__(self):
        self.agent = Agent(name="TechLead", instruction="Debugger")

    async def advise(self, 
                     step: SkillStep, 
                     handover: StepExecutorInput, 
                     error_log: str) -> TechLeadOutput:
        """
        Analyzes the situation and returns advice.
        """
        logger.info(f"TechLead triggered for Step {step.id}")
        
        # Prepare Context
        context_xml = handover.to_xml()
        
        # Prepare Input DTO (Implicit usage for prompt formatting)
        input_dto = TechLeadInput(context_xml=context_xml, error_log=error_log[:5000])

        prompt = TECH_LEAD_INSTRUCTION.format(
            context_xml=input_dto.context_xml,
            error_log=input_dto.error_log
        )

        async with self.agent:
            llm = await self.agent.attach_llm(OpenAIAugmentedLLM)
            try:
                response = await llm.generate_str(prompt)
                
                # Parse JSON
                import re
                json_str = response.strip()
                match = re.search(r"```json\s*(\{.*?\})\s*```", response, re.DOTALL)
                if match: 
                    json_str = match.group(1)
                elif re.search(r"(\{.*\})", response, re.DOTALL):
                     json_str = re.search(r"(\{.*\})", response, re.DOTALL).group(1)
                
                data = json.loads(json_str)
                return TechLeadOutput(
                    diagnosis=data.get("diagnosis", "Unknown Issue"),
                    advice=data.get("advice", "Review the error logs and retry."),
                    severity=data.get("severity", "warning")
                )
            except Exception as e:
                logger.error(f"TechLead failed to generate advice: {e}")
                return TechLeadOutput(
                    diagnosis="Tech Lead Generation Failed",
                    advice="I attempted to analyze the error but failed. Please review the logs manually.",
                    severity="warning"
                )
