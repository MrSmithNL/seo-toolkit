"""Parse and validate LLM responses for intent classification.

Validates completeness (every input keyword in output), enum values,
rationale presence, and detects duplicates/invented keywords.
"""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field

from src.research_engine.models.intent import (
    ContentFormat,
    IntentConfidence,
    IntentType,
)
from src.research_engine.models.result import Err, Ok, Result

# ---------------------------------------------------------------------------
# Response models (LLM output schema)
# ---------------------------------------------------------------------------

_VALID_INTENTS = {t.value for t in IntentType}
_VALID_CONFIDENCES = {c.value for c in IntentConfidence}
_VALID_FORMATS = {f.value for f in ContentFormat}


class IntentClassificationItem(BaseModel):
    """A single classification from the LLM response."""

    keyword: str
    intent: str
    confidence: str
    rationale: str
    recommended_format: str
    format_signal: str | None = None


class IntentClassificationLLMResponse(BaseModel):
    """Structured response from the classification LLM call."""

    classifications: list[IntentClassificationItem] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

_MARKDOWN_FENCE_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)


def _strip_markdown_fences(raw: str) -> str:
    """Remove markdown code fences from LLM output."""
    match = _MARKDOWN_FENCE_RE.search(raw)
    if match:
        return match.group(1)
    return raw


def parse_intent_response(  # noqa: C901
    raw_json: str,
    input_keywords: list[str],
) -> Result[IntentClassificationLLMResponse, str]:
    """Parse and validate the LLM intent classification response.

    Validates:
    - Valid JSON structure
    - Every input keyword appears exactly once
    - No invented keywords
    - Valid enum values for intent, confidence, format
    - Non-empty rationale
    - No duplicate keywords

    Args:
        raw_json: Raw JSON string from LLM.
        input_keywords: Original input keywords for completeness check.

    Returns:
        Ok(response) on success, Err(message) on validation failure.
    """
    cleaned = _strip_markdown_fences(raw_json.strip())

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return Err(f"Failed to parse JSON: {exc}")

    if not isinstance(data, dict) or "classifications" not in data:
        return Err("Response missing 'classifications' key")

    try:
        response = IntentClassificationLLMResponse.model_validate(data)
    except Exception as exc:  # noqa: BLE001
        return Err(f"Invalid response structure: {exc}")

    # Validate each classification
    for cls in response.classifications:
        if cls.intent not in _VALID_INTENTS:
            return Err(
                f"Invalid intent '{cls.intent}' for keyword '{cls.keyword}'. "
                f"Must be one of: {sorted(_VALID_INTENTS)}"
            )
        if cls.confidence not in _VALID_CONFIDENCES:
            return Err(
                f"Invalid confidence '{cls.confidence}' for keyword '{cls.keyword}'. "
                f"Must be one of: {sorted(_VALID_CONFIDENCES)}"
            )
        if cls.recommended_format not in _VALID_FORMATS:
            return Err(
                f"Invalid format '{cls.recommended_format}' "
                f"for keyword '{cls.keyword}'. "
                f"Must be one of: {sorted(_VALID_FORMATS)}"
            )
        if not cls.rationale.strip():
            return Err(f"Empty rationale for keyword '{cls.keyword}'")

    # Check for duplicates
    seen: set[str] = set()
    for cls in response.classifications:
        kw_lower = cls.keyword.lower()
        if kw_lower in seen:
            return Err(f"Duplicate keyword in output: '{cls.keyword}'")
        seen.add(kw_lower)

    # Check completeness
    input_lower = {kw.lower() for kw in input_keywords}
    output_lower = {cls.keyword.lower() for cls in response.classifications}

    missing = input_lower - output_lower
    if missing:
        return Err(f"Missing keywords from output: {sorted(missing)}")

    invented = output_lower - input_lower
    if invented:
        return Err(f"Invented keywords in output: {sorted(invented)}")

    return Ok(response)
