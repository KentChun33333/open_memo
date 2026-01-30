import os
import re
import json
from typing import List, Dict, Tuple
from logger import get_logger

logger = get_logger("verifier")

class Verifier:
    """
    Controller Component: Validation Logic.
    Decouples "Checking" from "Doing".
    """
    
    @staticmethod
    def verify_artifacts(active_folder: str, current_response: str, expected_artifacts: List[str]) -> Tuple[List[str], List[str], List[str]]:
        """
        Physically verifies files on disk.
        Returns: (verified_files, missing_expected, hallucinated_files)
        """
        # 1. Parse Reported Files
        reported_files = re.findall(r"CREATED_FILE:\s*(.*)", current_response)
        verified_files = []
        hallucinated_files = []
        
        # 2. Check Reported Files
        if reported_files:
            logger.info(f"Verifying {len(reported_files)} reported artifacts...")
            for f_path in reported_files:
                f_path = f_path.strip()
                abs_path = os.path.join(active_folder, f_path)
                
                if os.path.exists(abs_path) and os.path.getsize(abs_path) > 0:
                    logger.info(f"  [OK] Verified: {f_path} ({os.path.getsize(abs_path)} bytes)")
                    verified_files.append(f_path)
                else:
                    logger.error(f"  [FAIL] Missing or Empty: {f_path}")
                    hallucinated_files.append(f_path)
        
        # 3. Check Expected Files (SOP Metadata)
        missing_expected = []
        for exp in expected_artifacts:
            exp_path = os.path.join(active_folder, exp)
            if not os.path.exists(exp_path) or os.path.getsize(exp_path) == 0:
                missing_expected.append(exp)
                logger.error(f"  [FAIL] Expected Artifact Missing: {exp}")
            else:
                logger.info(f"  [OK] Expected Artifact Found: {exp}")
                
        return verified_files, missing_expected, hallucinated_files
