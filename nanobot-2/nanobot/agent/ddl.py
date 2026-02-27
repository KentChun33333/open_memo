"""Autonomous DDL Optimizer and Symbolic Extractor for D-RAG."""

import collections
import logging
from typing import Dict, Any, Set

from nanobot.providers.base import LLMProvider
import json_repair

logger = logging.getLogger(__name__)


class AutonomousDDLManager:
    """Optimizes D-RAG dimensions based on Information Gain and frequency."""

    def __init__(self, threshold: float = 0.8):
        # Base set of dimensions that might be useful
        self.optimized_dimensions: Set[str] = {"project", "owner", "topic"}
        self.dimension_promotion_times: Dict[str, float] = {}
        self.threshold = threshold

    def analyze_batch(self, extracted_metadata_list: list[dict[str, Any]]) -> list[str]:
        """
        Analyze a batch of metadata dictionaries and return a list of newly promoted dimensions.
        """
        total_items = len(extracted_metadata_list)
        if total_items == 0:
            return []

        batch_counts = collections.defaultdict(int)

        for meta in extracted_metadata_list:
            for key in meta.keys():
                batch_counts[key] += 1

        import time
        promoted = []
        for key, count in batch_counts.items():
            frequency = count / total_items
            if frequency >= self.threshold and key not in self.optimized_dimensions:
                logger.info(f"PROMOTING DIMENSION: {key} (Freq: {frequency:.2f})")
                self.optimized_dimensions.add(key)
                self.dimension_promotion_times[key] = time.time()
                promoted.append(key)
                # In LanceDB, adding a column is a cheap, zero-copy metadata update,
                # which will be handled by the caller (MemoryStore).

        return promoted

    def filter_valid_dimensions(self, metadata: dict[str, Any]) -> dict[str, Any]:
        """Return only metadata key-values that are part of the optimized schema."""
        return {k: v for k, v in metadata.items() if k in self.optimized_dimensions}


class SymbolicExtractor:
    """Symbolic Analysis: Uses an LLM to map Natural Language to DDL Filters and metadata."""

    def __init__(self, provider: LLMProvider, model: str | None = None):
        self.provider = provider
        self.model = model

    async def extract_filters(self, query: str, active_dimensions: Set[str]) -> Dict[str, Any]:
        """
        Extract known dimensions from a user query to use as hard D-RAG filters.
        """
        if not active_dimensions:
            return {}

        dim_list = ", ".join(active_dimensions)
        system_prompt = f"""You are a Symbolic Extractor for a database.
Given a user query, extract values for the following known dimensions: {dim_list}
Return a JSON object where the keys are the matched dimensions and values are the extracted strings.
If a dimension is not mentioned in the query, do not include it.
Do not invent new dimensions. Respond ONLY with valid JSON."""

        try:
            response = await self.provider.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                model=self.model,
            )
            text = (response.content or "").strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            
            extracted = json_repair.loads(text)
            if isinstance(extracted, dict):
                # Ensure we only return keys in active_dimensions
                return {k: v for k, v in extracted.items() if k in active_dimensions}
            return {}
        except Exception as e:
            logger.error(f"Failed to extract symbolic filters: {e}")
            return {}

    async def extract_metadata(self, text: str) -> Dict[str, Any]:
        """
        Extract descriptive metadata tags from a block of text to be stored in memory.
        This allows the AutonomousDDLManager to track frequency of new tags.
        """
        system_prompt = """You are a Memory Tagging Agent.
Given a block of text, extract 3-5 high-value scalar metadata tags that describe the context (e.g., project, topic, owner, environment).
Return a JSON object where the keys are the tag names (lowercase, no spaces) and the values are the tag values.
Respond ONLY with valid JSON."""

        try:
            response = await self.provider.chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                model=self.model,
            )
            text = (response.content or "").strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[-1].rsplit("```", 1)[0].strip()
            
            extracted = json_repair.loads(text)
            if isinstance(extracted, dict):
                return extracted
            return {}
        except Exception as e:
            logger.error(f"Failed to extract metadata: {e}")
            return {}
