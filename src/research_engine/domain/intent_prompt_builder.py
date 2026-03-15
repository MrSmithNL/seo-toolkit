"""Build LLM prompts for intent classification.

Loads the versioned prompt template from prompts/ directory and
injects the keyword list with proper escaping.
"""

from __future__ import annotations

import re
from pathlib import Path

_CONTROL_CHAR_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

_PROMPT_DIR = Path(__file__).parent.parent / "prompts"

_VALID_FORMATS = (
    "how-to-guide | definition-explainer | comparison-article"
    " | listicle | faq-page | product-landing-page"
    " | category-page | location-page | brand-navigational-page"
)

_JSON_SCHEMA = (
    '{\n  "classifications": [\n    {\n'
    '      "keyword": "the input keyword (echoed back)",\n'
    '      "intent": "informational | commercial | transactional'
    ' | navigational",\n'
    '      "confidence": "high | medium | low",\n'
    '      "rationale": "1-sentence explanation",\n'
    f'      "recommended_format": "{_VALID_FORMATS}",\n'
    '      "format_signal": "detected signal string or null"\n'
    "    }\n  ]\n}"
)


def _sanitize_keyword(keyword: str) -> str:
    """Strip control characters and normalize whitespace."""
    cleaned = _CONTROL_CHAR_RE.sub("", keyword)
    return " ".join(cleaned.split())


def build_intent_prompt(keywords: list[str]) -> str:
    """Build intent classification prompt from keyword list.

    Args:
        keywords: List of keyword terms to classify.

    Returns:
        Complete prompt string ready for LLM.
    """
    template = (_PROMPT_DIR / "intent-classification-v1.txt").read_text()

    keyword_lines = "\n".join(f'- "{_sanitize_keyword(kw)}"' for kw in keywords)

    return template.format(
        json_schema=_JSON_SCHEMA,
        keywords=keyword_lines if keywords else "(no keywords provided)",
    )
