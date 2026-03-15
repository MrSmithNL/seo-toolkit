"""SERP Feature Detector — normalizes feature flags from any data source.

Post-processing step per ADR-F004-003. Each adapter provides raw feature
data; this detector produces a consistent boolean-flag SerpFeatures object.

TypeScript equivalent: modules/content-engine/research/services/serp-feature-detector.ts
"""

from __future__ import annotations

import logging
from typing import Any

from src.research_engine.models.serp import SerpFeatures

logger = logging.getLogger(__name__)

# Feature flag keys we expect from any source
_BOOLEAN_FIELDS = (
    "ai_overview",
    "featured_snippet",
    "people_also_ask",
    "knowledge_panel",
    "image_pack",
    "video_carousel",
    "local_pack",
    "shopping_results",
)

_MAX_PAA_QUESTIONS = 5


class SerpFeatureDetector:
    """Normalizes SERP feature flags from any data source.

    Accepts a raw dict of feature flags (from DataForSEO, Google scraper,
    or any other source) and produces a canonical SerpFeatures object.
    All boolean fields are coerced to bool. PAA questions are capped at 5.
    """

    @staticmethod
    def normalize(raw: dict[str, Any]) -> SerpFeatures:
        """Normalize raw feature data into canonical SerpFeatures.

        Args:
            raw: Dict of feature flags from any SERP data source.
                Keys should match SerpFeatures field names.
                Values can be any truthy/falsy type — they are coerced to bool.

        Returns:
            Canonical SerpFeatures with all fields set.
        """
        flags: dict[str, Any] = {}
        for field_name in _BOOLEAN_FIELDS:
            value = raw.get(field_name)
            flags[field_name] = bool(value) if value is not None else False

        # PAA questions — truncate to 5 max
        paa_raw = raw.get("paa_questions", [])
        if isinstance(paa_raw, list):
            paa_questions = [str(q) for q in paa_raw[:_MAX_PAA_QUESTIONS]]
        else:
            paa_questions = []

        flags["paa_questions"] = paa_questions
        return SerpFeatures(**flags)

    @staticmethod
    def get_warnings(features: SerpFeatures) -> list[str]:
        """Generate warning flags for notable SERP features.

        Args:
            features: Canonical SerpFeatures object.

        Returns:
            List of warning flag strings.
        """
        warnings: list[str] = []
        if features.ai_overview:
            warnings.append("ai_overview_detected")
            logger.info("AI Overview detected — keyword may have reduced organic CTR")
        return warnings
