import os
import json
import hashlib
from typing import Optional, Dict
from dataclasses import asdict
from .structs import AtomicPlannerOutput, SkillStep

class PlanCache:
    """
    Simple JSON file-based cache for Atomic Plans.
    """
    def __init__(self, cache_dir: str):
        self.cache_dir = os.path.join(cache_dir, ".cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_file = os.path.join(self.cache_dir, "plan_cache.json")
        self._memory_cache: Dict[str, dict] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self._memory_cache = json.load(f)
            except Exception:
                self._memory_cache = {}

    def _save(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self._memory_cache, f, indent=2)
        except Exception:
            pass

    def _generate_key(self, query: str, skill_content: str) -> str:
        raw = f"{query}::{skill_content}"
        return hashlib.md5(raw.encode()).hexdigest()

    def get(self, query: str, skill_content: str) -> Optional[AtomicPlannerOutput]:
        key = self._generate_key(query, skill_content)
        data = self._memory_cache.get(key)
        if not data:
            return None
        
        # Reconstruct DTO
        try:
            steps = [SkillStep(**s) for s in data.get("steps", [])]
            return AtomicPlannerOutput(steps=steps, reasoning=data.get("reasoning", ""))
        except Exception:
            return None

    def set(self, query: str, skill_content: str, plan: AtomicPlannerOutput):
        key = self._generate_key(query, skill_content)
        
        # Serialize DTO
        serialized_steps = [asdict(s) for s in plan.steps]
        
        self._memory_cache[key] = {
            "steps": serialized_steps,
            "reasoning": plan.reasoning
        }
        self._save()
