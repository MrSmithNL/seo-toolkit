"""Rule-based format signal detection for keywords.

Detects patterns in keyword text ("how to", "best", "vs", "what is",
"near me", city names) and maps them to recommended content formats.
Provides a deterministic baseline for validation and fallback.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from src.research_engine.models.intent import ContentFormat, IntentType

# ---------------------------------------------------------------------------
# Signal patterns (order matters — first match wins)
# ---------------------------------------------------------------------------

_SIGNAL_PATTERNS: list[tuple[re.Pattern[str], ContentFormat, str]] = [
    (re.compile(r"\bhow\s+to\b", re.IGNORECASE), ContentFormat.HOW_TO_GUIDE, "how to"),
    (
        re.compile(r"\bhow\s+do\s+i\b", re.IGNORECASE),
        ContentFormat.HOW_TO_GUIDE,
        "how do i",
    ),
    (
        re.compile(r"\bwhat\s+is\b", re.IGNORECASE),
        ContentFormat.DEFINITION_EXPLAINER,
        "what is",
    ),
    (
        re.compile(r"\bwhat\s+are\b", re.IGNORECASE),
        ContentFormat.DEFINITION_EXPLAINER,
        "what are",
    ),
    (
        re.compile(r"\bcompared\s+to\b", re.IGNORECASE),
        ContentFormat.COMPARISON_ARTICLE,
        "compared to",
    ),
    (
        re.compile(r"\bversus\b", re.IGNORECASE),
        ContentFormat.COMPARISON_ARTICLE,
        "versus",
    ),
    (re.compile(r"\bvs\.?\b", re.IGNORECASE), ContentFormat.COMPARISON_ARTICLE, "vs"),
    (re.compile(r"\bbest\b", re.IGNORECASE), ContentFormat.LISTICLE, "best"),
    (re.compile(r"\btop\b", re.IGNORECASE), ContentFormat.LISTICLE, "top"),
    (
        re.compile(r"\bnear\s+me\b", re.IGNORECASE),
        ContentFormat.LOCATION_PAGE,
        "near me",
    ),
]

# Common city/country names for location detection
_LOCATION_PATTERN = re.compile(
    r"\b(?:Berlin|Hamburg|Munich|Frankfurt|Cologne|Düsseldorf|Stuttgart|"
    r"London|Manchester|Birmingham|Edinburgh|Dublin|"
    r"Amsterdam|Rotterdam|Brussels|Antwerp|"
    r"Paris|Lyon|Marseille|Madrid|Barcelona|"
    r"Istanbul|Ankara|Warsaw|Lisbon|Porto|"
    r"New York|Los Angeles|Chicago|Miami|"
    r"Germany|Deutschland|UK|England|Netherlands|"
    r"France|Spain|Turkey|Türkiye|Poland|Portugal)\b",
    re.IGNORECASE,
)

# Intent → default format mapping (when no signal detected)
_DEFAULT_FORMATS: dict[IntentType, ContentFormat] = {
    IntentType.INFORMATIONAL: ContentFormat.DEFINITION_EXPLAINER,
    IntentType.COMMERCIAL: ContentFormat.CATEGORY_PAGE,
    IntentType.TRANSACTIONAL: ContentFormat.PRODUCT_LANDING_PAGE,
    IntentType.NAVIGATIONAL: ContentFormat.BRAND_NAVIGATIONAL_PAGE,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class FormatSignalResult:
    """Result of format signal detection.

    Attributes:
        format: Recommended content format.
        signal: Detected signal string, or None if default was used.
    """

    format: ContentFormat
    signal: str | None


def detect_format_signal(keyword: str, intent: IntentType) -> FormatSignalResult:
    """Detect format signal in keyword text and recommend content format.

    Args:
        keyword: Keyword text to analyze.
        intent: The classified intent type.

    Returns:
        FormatSignalResult with recommended format and detected signal.
    """
    kw_lower = keyword.lower()

    # Check explicit signal patterns
    for pattern, fmt, signal_name in _SIGNAL_PATTERNS:
        if pattern.search(kw_lower):
            return FormatSignalResult(format=fmt, signal=signal_name)

    # Check for location + transactional intent
    if intent == IntentType.TRANSACTIONAL:
        loc_match = _LOCATION_PATTERN.search(keyword)
        if loc_match:
            return FormatSignalResult(
                format=ContentFormat.LOCATION_PAGE,
                signal=loc_match.group(0),
            )

    # Default based on intent
    default_format = _DEFAULT_FORMATS.get(intent, ContentFormat.DEFINITION_EXPLAINER)
    return FormatSignalResult(format=default_format, signal=None)
