import os
import re
import logging
from typing import Dict, List, Any, Union

logger = logging.getLogger(__name__)

class Validator:
    """
    Defensive Layer for the Industrial Agent.
    Responsibilities:
    1. Pre-Execution: Predict Context Switches.
    2. Execution: Detect 'Auto-Write' failures (Code without Tool Calls).
    3. Post-Execution: Verify Artifacts (Existence, Size).
    """

    def detect_context_switch(self, step_title: str, step_instruction: str) -> Dict[str, Union[bool, str]]:
        """
        Analyzes step to predict if it will change the filesystem root.
        Targeting: 'run_skill_script', 'mkdir', 'create project', 'init'.
        """
        content_lower = (step_title + " " + step_instruction).lower()
        
        # 1. Script Execution
        if "run_skill_script" in content_lower:
             return {"detected": True, "reason": "Detected 'run_skill_script' execution."}

        # 2. Key Phrases
        triggers = ["mkdir", "create project", "new project", "initialize", "cd "]
        for trigger in triggers:
            if trigger in content_lower:
                 return {"detected": True, "reason": f"Detected keyword '{trigger}'."}
        
        return {"detected": False, "reason": ""}

    def detect_missed_writes(self, response: str) -> List[str]:
        """
        DeepCode Pattern: Detects when Agent claims to write a file (FILE: path) 
        but likely didn't call the tool (checked by caller).
        Returns list of paths detected.
        """
        # Look for the FILE: pattern
        if "FILE:" in response:
            return re.findall(r"FILE:\s*([^\s\n]+)", response)
        return []

    def verify_step_artifacts(self, expected_artifacts: List[str], active_folder: str) -> Dict[str, Any]:
        """
        Verifies that expected artifacts exist on disk.
        Returns: { 'success': bool, 'missing': List[str], 'found': List[str] }
        """
        missing = []
        found = []
        
        for art in expected_artifacts:
            # Resolve path
            path = os.path.join(active_folder, art)
            if os.path.exists(path) and os.path.getsize(path) > 0:
                found.append(art)
            else:
                missing.append(art)
        
        return {
            "success": len(missing) == 0,
            "missing": missing,
            "found": found
        }
