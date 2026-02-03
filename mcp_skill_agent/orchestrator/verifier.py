import os
import re
import json
from typing import List, Dict, Tuple, Optional
from ..logger import get_logger

logger = get_logger("verifier")

class Verifier:
    """
    Controller Component: Validation Logic.
    Decouples "Checking" from "Doing".
    """
    def __init__(self, memory_manager):
        self.memory_manager = memory_manager

    @staticmethod
    def _smart_find(base_folder: str, filename: str, max_depth: int = 2) -> Optional[str]:
        """
        Searches for a file within subdirectories (up to max_depth).
        Returns the relative path from base_folder if found, else None.
        """
        for root, dirs, files in os.walk(base_folder):
            # Calculate current depth
            rel_path = os.path.relpath(root, base_folder)
            if rel_path == ".":
                depth = 0
            else:
                depth = rel_path.count(os.sep) + 1
            
            if depth > max_depth:
                dirs[:] = [] # Stop traversing deeper
                continue
                
            if filename in files:
                # Found it!
                full_path = os.path.join(root, filename)
                return os.path.relpath(full_path, base_folder)
        return None

    def verify_artifacts(self, current_response: str, expected_artifacts: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Physically verifies files on disk using session memory context.
        Returns: (verified_files, missing_expected, hallucinated_files)
        """
        active_folder = self.memory_manager.memory.project_root or self.memory_manager.memory.active_folder
        
        # 1. Parse Reported Files
        reported_files = []
        
        # A. Try JSON Extraction
        json_str = ""
        # Look for ```json block
        match = re.search(r"```json\s*(\{.*?\})\s*```", current_response, re.DOTALL)
        if match:
             json_str = match.group(1)
        else:
             # Look for raw JSON object
             match = re.search(r"(\{.*\})", current_response, re.DOTALL)
             if match:
                 json_str = match.group(1)
        
        if json_str:
            try:
                data = json.loads(json_str)
                # Flexible key access
                reported_files = data.get("created_files", []) or data.get("artifacts", [])
                if isinstance(reported_files, str): reported_files = [reported_files]
            except json.JSONDecodeError:
                logger.warning("Verifier failed to decode JSON from response.")
        
        # B. Fallback to Regex (Legacy/Hallucination)
        if not reported_files:
             reported_files = re.findall(r"CREATED_FILE:\s*(.*)", current_response)
             
        verified_files = []
        hallucinated_files = []
        
        # 2. Check Reported Files
        if reported_files:
            logger.info(f"Verifying {len(reported_files)} reported artifacts...")
            for f_path in reported_files:
                f_path = f_path.strip()
                # Sanitize: remove ./ prefix
                clean_path = f_path.lstrip("./").lstrip("/")
                abs_path = os.path.join(active_folder, clean_path)
                
                if os.path.exists(abs_path) and os.path.getsize(abs_path) > 0:
                    logger.info(f"  [OK] Verified: {f_path} ({os.path.getsize(abs_path)} bytes)")
                    verified_files.append(f_path)
                    # Log to Memory
                    self.memory_manager.register_artifact(str(self.memory_manager.memory.current_step_id), f_path)
                else:
                    # Smart Search for Reported File
                    found_rel = self._smart_find(active_folder, os.path.basename(clean_path))
                    if found_rel:
                         logger.info(f"  [OK] Verified (Smart Search): {found_rel} (was reported as {f_path})")
                         verified_files.append(found_rel)
                         # Log to Memory
                         self.memory_manager.register_artifact(str(self.memory_manager.memory.current_step_id), found_rel)
                    else:
                        logger.error(f"  [FAIL] Missing or Empty: {f_path}")
                        hallucinated_files.append(f_path)
        
        # 3. Check Expected Files (SOP Metadata)
        missing_expected = []
        for exp in expected_artifacts:
            # Sanitize
            clean_exp = exp.lstrip("./").lstrip("/")
            exp_path = os.path.join(active_folder, clean_exp)
            
            if os.path.exists(exp_path) and os.path.getsize(exp_path) > 0:
                logger.info(f"  [OK] Expected Artifact Found: {exp}")
            else:
                # Smart Search for Expected File
                found_rel = self._smart_find(active_folder, os.path.basename(clean_exp))
                if found_rel:
                    logger.info(f"  [OK] Expected Artifact Found (Smart Search): {found_rel}")
                else:
                    missing_expected.append(exp)
                    # Try to hint if it's a path mismatch (e.g. src/App.tsx expected, but no src folder)
                    logger.error(f"  [FAIL] Expected Artifact Missing: {exp}")
                
        return verified_files, missing_expected, hallucinated_files
