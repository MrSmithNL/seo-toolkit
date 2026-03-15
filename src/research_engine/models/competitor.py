"""Competitor Content Analysis domain models for F-005.

Pydantic v2 models matching the target TypeScript/Drizzle schema 1:1.
These are the single source of truth for competitor analysis data structures.

TypeScript equivalent: modules/content-engine/research/schema/competitor.ts
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CrawlStatus(StrEnum):
    """Crawl outcome status."""

    SUCCESS = "success"
    CRAWL_FAILED = "crawl_failed"
    ROBOTS_BLOCKED = "robots_blocked"
    JS_RENDERED = "js_rendered"


class QualityAssessmentStatus(StrEnum):
    """Quality assessment outcome status."""

    COMPLETED = "completed"
    SKIPPED = "skipped"
    FAILED = "failed"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_cs_id() -> str:
    """Generate a prefixed competitor snapshot ID."""
    return f"cs_{uuid.uuid4().hex[:12]}"


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(tz=UTC)


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class QualityProfile(BaseModel):
    """LLM-assessed quality profile for a competitor page.

    All fields are tagged as LLM-assessed for auditability.
    TypeScript equivalent: QualityProfile interface in design.md.
    """

    depth_score: Annotated[int, Field(ge=1, le=5)]
    topics_covered: list[str] = Field(default_factory=list)
    has_original_data: bool = False
    has_author_credentials: bool = False
    eeat_signals: list[str] = Field(default_factory=list)
    quality_rationale: str = Field(min_length=1)

    # Mark all fields as LLM-assessed
    llm_assessed_fields: list[str] = Field(
        default_factory=lambda: [
            "depth_score",
            "topics_covered",
            "has_original_data",
            "has_author_credentials",
            "eeat_signals",
            "quality_rationale",
        ],
    )


class CompetitorSnapshot(BaseModel):
    """Timestamped snapshot of a competitor page analysis.

    Maps to the `competitor_snapshot` table in the target Drizzle schema.
    Append-only: subsequent crawls create new records, never overwrite.

    TypeScript equivalent: competitorSnapshot table in design.md.
    """

    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(default_factory=_generate_cs_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    keyword_id: str = Field(min_length=1)
    serp_snapshot_id: str = Field(min_length=1)
    url: str = Field(min_length=1)
    domain: str = Field(min_length=1)
    serp_position: Annotated[int, Field(ge=1, le=10)]

    # Structural extraction (US-001)
    crawl_status: CrawlStatus
    http_status_code: int | None = None
    word_count: Annotated[int | None, Field(ge=0)] = None
    h1_text: str | None = None
    h2_count: Annotated[int | None, Field(ge=0)] = None
    h3_count: Annotated[int | None, Field(ge=0)] = None
    h2_texts: list[str] = Field(default_factory=list)
    schema_types: list[str] = Field(default_factory=list)
    has_faq_section: bool = False
    internal_link_count: Annotated[int | None, Field(ge=0)] = None
    external_link_count: Annotated[int | None, Field(ge=0)] = None
    image_count: Annotated[int | None, Field(ge=0)] = None
    is_thin_content: bool = False

    # Quality assessment (US-002)
    quality_assessment_status: QualityAssessmentStatus | None = None
    depth_score: Annotated[int | None, Field(ge=1, le=5)] = None
    topics_covered: list[str] = Field(default_factory=list)
    has_original_data: bool | None = None
    has_author_credentials: bool | None = None
    eeat_signals: list[str] = Field(default_factory=list)
    quality_rationale: str | None = None
    llm_assessed_fields: list[str] = Field(default_factory=list)

    # Change detection (US-003)
    raw_html_hash: str | None = None
    content_changed: bool = False

    # Metadata
    crawled_at: datetime = Field(default_factory=_now_utc)
    llm_tokens_used: int | None = None
    pipeline_run_id: str | None = None

    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @field_validator("url", mode="before")
    @classmethod
    def strip_url(cls, v: str) -> str:
        """Strip whitespace from URL."""
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("h2_texts", mode="after")
    @classmethod
    def validate_h2_texts_match_count(cls, v: list[str], info: object) -> list[str]:
        """Validate h2_texts length matches h2_count when both set."""
        # Validation only fires during full model construction
        # h2_count may not yet be available during partial construction
        return v


class CompetitorBenchmark(BaseModel):
    """Lightweight view for F-006 gap analysis consumption.

    TypeScript equivalent: CompetitorBenchmark interface in design.md.
    """

    url: str
    domain: str
    serp_position: int
    word_count: int | None = None
    depth_score: int | None = None
    h2_texts: list[str] = Field(default_factory=list)
    schema_types: list[str] = Field(default_factory=list)
    has_faq_section: bool = False
    topics_covered: list[str] = Field(default_factory=list)
