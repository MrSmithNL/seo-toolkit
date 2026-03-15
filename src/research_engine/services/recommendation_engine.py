"""RecommendationEngine — LLM-powered recommendations grounded in competitor data.

Per ADR-F007-003: LLM used for headings, content_type, schema_types.
Scoring comes from F-006 (deterministic). This separation is deliberate.

Fallback: if LLM fails after 2 retries, use competitor headings directly.

TypeScript equivalent:
  modules/content-engine/research/services/recommendation-engine.ts
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from src.research_engine.models.content_brief import ContentType, SearchIntent

if TYPE_CHECKING:
    from src.research_engine.ports.llm_gateway import LlmGateway

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent.parent / "prompts" / "content-calendar"


@dataclass(frozen=True)
class Recommendation:
    """LLM recommendation output."""

    content_type: ContentType
    recommended_headings: list[str]
    recommended_schema_types: list[str]
    source: str = "llm_recommended"  # or "extracted from competitor — LLM unavailable"


# ---------------------------------------------------------------------------
# Content type inference from intent
# ---------------------------------------------------------------------------

_INTENT_TYPE_MAP: dict[SearchIntent, ContentType] = {
    SearchIntent.INFORMATIONAL: ContentType.HOW_TO,
    SearchIntent.COMMERCIAL: ContentType.COMPARISON,
    SearchIntent.TRANSACTIONAL: ContentType.PRODUCT_PAGE,
    SearchIntent.NAVIGATIONAL: ContentType.LANDING_PAGE,
}


def _infer_content_type_from_intent(intent: SearchIntent) -> ContentType:
    """Default content type based on search intent."""
    return _INTENT_TYPE_MAP.get(intent, ContentType.BLOG_POST)


# ---------------------------------------------------------------------------
# Prompt builder
# ---------------------------------------------------------------------------


def _build_prompt(
    keyword: str,
    intent: SearchIntent,
    competitor_headings: list[list[str]],
    competitor_schema_types: list[str],
) -> str:
    """Build the LLM prompt for recommendations."""
    prompt_file = PROMPTS_DIR / "v1.txt"
    template = prompt_file.read_text() if prompt_file.exists() else _DEFAULT_PROMPT

    # Format competitor headings
    headings_text = ""
    for i, h_list in enumerate(competitor_headings, 1):
        headings_text += f"\nCompetitor {i}: {', '.join(h_list)}"

    return template.format(
        keyword=keyword,
        intent=intent.value,
        competitor_headings=headings_text,
        competitor_schemas=", ".join(competitor_schema_types) or "None detected",
        content_types=", ".join(ct.value for ct in ContentType),
    )


_DEFAULT_PROMPT = (
    "You are an SEO content strategist. "
    "Analyse the following keyword and competitor data, "
    "then recommend:\n"
    "1. The best content_type for this keyword\n"
    "2. 4-8 recommended H2 headings\n"
    "3. Schema markup types to implement\n"
    "\n"
    "Keyword: {keyword}\n"
    "Search Intent: {intent}\n"
    "\n"
    "Competitor H2 headings:{competitor_headings}\n"
    "\n"
    "Competitor schema types: {competitor_schemas}\n"
    "\n"
    "Available content_types: {content_types}\n"
    "\n"
    "Respond in JSON only:\n"
    '{{"content_type": "...", '
    '"recommended_headings": ["..."], '
    '"recommended_schema_types": ["..."]}}'
)


# ---------------------------------------------------------------------------
# Response parser
# ---------------------------------------------------------------------------


def _parse_llm_response(response: str, intent: SearchIntent) -> Recommendation:
    """Parse structured JSON from LLM response."""
    # Extract JSON from response (handle markdown code blocks)
    text = response.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()

    data = json.loads(text)

    ct_str = data.get("content_type", "")
    try:
        content_type = ContentType(ct_str)
    except ValueError:
        content_type = _infer_content_type_from_intent(intent)

    headings = data.get("recommended_headings", [])
    if not isinstance(headings, list):
        headings = []
    headings = [str(h) for h in headings if h]

    schema_types = data.get("recommended_schema_types", [])
    if not isinstance(schema_types, list):
        schema_types = []
    schema_types = [str(s) for s in schema_types if s]

    return Recommendation(
        content_type=content_type,
        recommended_headings=headings,
        recommended_schema_types=schema_types,
        source="llm_recommended",
    )


# ---------------------------------------------------------------------------
# Fallback: extract from competitor data
# ---------------------------------------------------------------------------


def _build_fallback_recommendation(
    intent: SearchIntent,
    competitor_headings: list[list[str]],
    competitor_schema_types: list[str],
) -> Recommendation:
    """Build recommendation from competitor data when LLM is unavailable."""
    # Use the longest competitor heading list
    best_headings: list[str] = []
    for h_list in competitor_headings:
        if len(h_list) > len(best_headings):
            best_headings = h_list

    return Recommendation(
        content_type=_infer_content_type_from_intent(intent),
        recommended_headings=best_headings,
        recommended_schema_types=list(set(competitor_schema_types)),
        source="extracted from competitor — LLM unavailable",
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_recommendations(
    *,
    keyword: str,
    intent: SearchIntent,
    competitor_headings: list[list[str]],
    competitor_schema_types: list[str],
    llm: LlmGateway | None = None,
    max_retries: int = 2,
    topic_cluster: str | None = None,
) -> Recommendation:
    """Get content recommendations for a keyword.

    Args:
        keyword: Target keyword.
        intent: Search intent from F-003.
        competitor_headings: List of H2 heading lists from F-005 competitors.
        competitor_schema_types: Schema types from competitors.
        llm: LLM gateway (None = use fallback).
        max_retries: Max LLM retries before fallback.
        topic_cluster: Optional cluster name for context.

    Returns:
        Recommendation with content_type, headings, schema_types.
    """
    if llm is None:
        logger.info("No LLM provided, using competitor fallback for: %s", keyword)
        return _build_fallback_recommendation(
            intent, competitor_headings, competitor_schema_types
        )

    prompt = _build_prompt(
        keyword, intent, competitor_headings, competitor_schema_types
    )

    for attempt in range(max_retries + 1):
        try:
            response = llm.complete(prompt)
            return _parse_llm_response(response, intent)
        except Exception:
            logger.warning(
                "LLM call failed for '%s' (attempt %d/%d)",
                keyword,
                attempt + 1,
                max_retries + 1,
                exc_info=True,
            )

    # All retries exhausted — fallback
    logger.warning(
        "LLM unavailable after %d attempts for '%s', using competitor fallback",
        max_retries + 1,
        keyword,
    )
    return _build_fallback_recommendation(
        intent, competitor_headings, competitor_schema_types
    )
