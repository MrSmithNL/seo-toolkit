"""SERP Analysis domain models for F-004.

Pydantic v2 models matching the target TypeScript/Drizzle schema 1:1.
These are the single source of truth for SERP data structures.

TypeScript equivalent: modules/content-engine/research/schema/serp.ts
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.research_engine.models.keyword import SUPPORTED_COUNTRIES, SUPPORTED_LOCALES

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ContentType(StrEnum):
    """Content type classification for a SERP result."""

    BLOG = "blog"
    PRODUCT_PAGE = "product_page"
    CATEGORY_PAGE = "category_page"
    VIDEO = "video"
    TOOL = "tool"
    NEWS = "news"
    OTHER = "other"


class ApiSource(StrEnum):
    """Source of SERP data."""

    DATAFORSEO = "dataforseo"
    GOOGLE_SCRAPE = "google_scrape"
    MOCK = "mock"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_ss_id() -> str:
    """Generate a prefixed SERP snapshot ID."""
    return f"ss_{uuid.uuid4().hex[:12]}"


def _generate_sr_id() -> str:
    """Generate a prefixed SERP result ID."""
    return f"sr_{uuid.uuid4().hex[:12]}"


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(tz=UTC)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class SerpFeatures(BaseModel):
    """SERP feature flags for a keyword.

    All boolean fields default to False. PAA questions are capped at 5.

    TypeScript equivalent: SerpFeatures interface in design.md.
    """

    ai_overview: bool = False
    featured_snippet: bool = False
    people_also_ask: bool = False
    knowledge_panel: bool = False
    image_pack: bool = False
    video_carousel: bool = False
    local_pack: bool = False
    shopping_results: bool = False
    paa_questions: Annotated[list[str], Field(max_length=5)] = Field(
        default_factory=list,
    )


class SerpResult(BaseModel):
    """A single organic SERP result (child of SerpSnapshot).

    Maps to the `serp_result` table in the target Drizzle schema.
    Positions are 1-10 for top-10 organic results.
    """

    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(default_factory=_generate_sr_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    snapshot_id: str
    position: Annotated[int, Field(ge=1, le=10)]
    url: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    title: str | None = None
    meta_description: str | None = None
    estimated_word_count: Annotated[int | None, Field(ge=0)] = None
    content_type: ContentType | None = None
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @field_validator("url", mode="before")
    @classmethod
    def strip_url(cls, v: str) -> str:
        """Strip whitespace from URL."""
        if isinstance(v, str):
            return v.strip()
        return v


class SerpSnapshot(BaseModel):
    """Timestamped snapshot of SERP state for a keyword.

    Maps to the `serp_snapshot` table in the target Drizzle schema.
    Append-only: subsequent fetches create new records, never overwrite.

    TypeScript equivalent: serpSnapshot table in design.md.
    """

    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(default_factory=_generate_ss_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    keyword_id: str
    keyword_text: str = Field(min_length=1)
    language: str
    country: str
    fetched_at: datetime = Field(default_factory=_now_utc)
    api_source: ApiSource
    result_count: Annotated[int, Field(ge=0)] = 0
    no_organic_results: bool = False

    # SERP features (embedded object)
    serp_features: SerpFeatures = Field(default_factory=SerpFeatures)

    # Pipeline tracking
    pipeline_run_id: str | None = None
    cost_estimate_usd: str | None = None

    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        """Validate language is in the supported set."""
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
