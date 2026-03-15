"""Keyword domain models for the Research Engine.

Pydantic v2 models matching the target TypeScript/Drizzle schema 1:1.
These are the single source of truth for keyword data structures.
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

SUPPORTED_LOCALES = frozenset({"de", "fr", "nl", "es", "it", "pt", "pl", "tr", "en"})
SUPPORTED_COUNTRIES = frozenset(
    {"DE", "FR", "NL", "ES", "IT", "PT", "PL", "TR", "US", "GB"}
)


class KeywordSource(StrEnum):
    """Source of keyword discovery."""

    URL_EXTRACTION = "url_extraction"
    AUTOCOMPLETE = "autocomplete"
    MANUAL_SEED = "manual_seed"
    GAP_ANALYSIS = "gap_analysis"


class GapStatus(StrEnum):
    """Gap classification for a keyword."""

    OWN_KEYWORD = "own_keyword"
    COMPETITOR_GAP = "competitor_gap"
    NEW_OPPORTUNITY = "new_opportunity"


class DifficultySource(StrEnum):
    """Source of difficulty score."""

    HEURISTIC = "heuristic"
    DATAFOR_SEO = "datafor_seo"


class KeywordIntent(StrEnum):
    """Search intent classification."""

    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

_WHITESPACE_RE = re.compile(r"\s+")


def _generate_kw_id() -> str:
    """Generate a prefixed keyword ID."""
    return f"kw_{uuid.uuid4().hex[:12]}"


def _generate_km_id() -> str:
    """Generate a prefixed keyword metric ID."""
    return f"km_{uuid.uuid4().hex[:12]}"


def _generate_kg_id() -> str:
    """Generate a prefixed keyword gap ID."""
    return f"kg_{uuid.uuid4().hex[:12]}"


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(tz=UTC)


def _make_normalized_key(term: str) -> str:
    """Create a sorted-token dedup key from a term.

    Args:
        term: The keyword term to normalise.

    Returns:
        Lowercase, whitespace-collapsed, alphabetically sorted tokens.
    """
    cleaned = _WHITESPACE_RE.sub(" ", term.strip().lower())
    tokens = sorted(cleaned.split())
    return " ".join(tokens)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class Keyword(BaseModel):
    """Canonical keyword record (one per term per campaign).

    Maps to the `keyword` table in the target Drizzle schema.
    """

    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(default_factory=_generate_kw_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    campaign_id: str
    term: str = Field(min_length=1)
    normalized_key: str = ""
    source: KeywordSource
    source_url: str | None = None
    gap_status: GapStatus = GapStatus.NEW_OPPORTUNITY
    difficulty: Annotated[int | None, Field(ge=0, le=100)] = None
    difficulty_source: DifficultySource | None = None
    difficulty_rationale: str | None = None
    intent: KeywordIntent | None = None
    intent_confidence: str | None = None
    intent_rationale: str | None = None
    recommended_format: str | None = None
    format_signal: str | None = None
    classified_at: datetime | None = None
    cluster_id: str | None = None
    discovered_at: datetime = Field(default_factory=_now_utc)
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @field_validator("term", mode="before")
    @classmethod
    def strip_term(cls, v: str) -> str:
        """Strip whitespace and collapse multiple spaces."""
        if isinstance(v, str):
            return _WHITESPACE_RE.sub(" ", v.strip())
        return v

    @model_validator(mode="after")
    def compute_normalized_key(self) -> Keyword:
        """Compute normalized_key from the term after validation."""
        if not self.normalized_key and self.term:
            object.__setattr__(self, "normalized_key", _make_normalized_key(self.term))
        return self


class KeywordMetric(BaseModel):
    """Per-locale volume/CPC/trend data for a keyword.

    Maps to the `keyword_metric` table. One keyword can have multiple
    metric rows (one per locale).
    """

    id: str = Field(default_factory=_generate_km_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    keyword_id: str
    locale: str
    country: str
    volume: Annotated[int | None, Field(ge=0)] = None
    cpc: Annotated[float | None, Field(ge=0.0)] = None
    trend: list[int]
    data_source: str = "keywords_everywhere"
    fetched_at: datetime = Field(default_factory=_now_utc)
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @field_validator("locale")
    @classmethod
    def validate_locale(cls, v: str) -> str:
        """Validate locale is in the supported set."""
        if v not in SUPPORTED_LOCALES:
            msg = f"Unsupported locale: {v}. Must be one of {sorted(SUPPORTED_LOCALES)}"
            raise ValueError(msg)
        return v

    @field_validator("country")
    @classmethod
    def validate_country(cls, v: str) -> str:
        """Validate country is in the supported set."""
        if v not in SUPPORTED_COUNTRIES:
            msg = (
                f"Unsupported country: {v}. "
                f"Must be one of {sorted(SUPPORTED_COUNTRIES)}"
            )
            raise ValueError(msg)
        return v

    @field_validator("trend")
    @classmethod
    def validate_trend_length(cls, v: list[int]) -> list[int]:
        """Validate trend array has exactly 12 elements."""
        if len(v) != 12:
            msg = f"Trend must have exactly 12 elements (got {len(v)})"
            raise ValueError(msg)
        return v


class KeywordGap(BaseModel):
    """Competitor gap record for a keyword.

    Maps to the `keyword_gap` table. Tracks where competitors rank
    and we don't (or vice versa).
    """

    id: str = Field(default_factory=_generate_kg_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    campaign_id: str
    keyword_id: str
    competitor_domain: str = Field(min_length=1)
    competitor_url: str | None = None
    competitor_position: Annotated[int | None, Field(ge=1)] = None
    our_position: Annotated[int | None, Field(ge=1)] = None
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)
