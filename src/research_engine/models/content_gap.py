"""Content Gap Identification domain models for F-006.

Pydantic v2 models matching the target TypeScript/Drizzle schema 1:1.
These are the single source of truth for content gap data structures.

TypeScript equivalent: modules/content-engine/research/schema/content-gap.ts
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class GapType(StrEnum):
    """Content gap classification type."""

    OWN_GAP = "own_gap"
    OWN_COVERAGE = "own_coverage"
    THIN_CONTENT = "thin_content"
    NEW_OPPORTUNITY = "new_opportunity"


class CoverageSource(StrEnum):
    """Source of coverage determination."""

    GSC = "gsc"
    SERP_FALLBACK = "serp_fallback"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_cg_id() -> str:
    """Generate a prefixed content gap ID."""
    return f"cg_{uuid.uuid4().hex[:12]}"


def _generate_cls_id() -> str:
    """Generate a prefixed cross-language summary ID."""
    return f"cls_{uuid.uuid4().hex[:12]}"


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(tz=UTC)


# ---------------------------------------------------------------------------
# Score Inputs (transparency / reproducibility)
# ---------------------------------------------------------------------------


class ScoreInputs(BaseModel):
    """Formula inputs stored alongside each score for reproducibility.

    TypeScript equivalent: score_inputs JSONB column in design.md.
    """

    volume: int
    volume_normalised: Annotated[float, Field(ge=0.0, le=1.0)]
    difficulty: int
    difficulty_inverse_normalised: Annotated[float, Field(ge=0.0, le=1.0)]
    gap_score: Annotated[float, Field(ge=0.0, le=1.0)]
    universal_gap_bonus: Annotated[float, Field(ge=0.0)] = 0.0


# ---------------------------------------------------------------------------
# Content Gap Record
# ---------------------------------------------------------------------------


class ContentGapRecord(BaseModel):
    """Content gap analysis record for a single keyword+language.

    Maps to the `content_gap` table in the target Drizzle schema.
    One record per keyword per language per campaign.

    TypeScript equivalent: contentGap table in design.md.
    """

    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(default_factory=_generate_cg_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    campaign_id: str = Field(min_length=1)
    keyword_id: str = Field(min_length=1)
    keyword_text: str = Field(min_length=1)
    language: str = Field(min_length=1)

    # Classification
    gap_type: GapType
    coverage_source: CoverageSource

    # Our coverage
    our_ranking_position: Annotated[int | None, Field(ge=1, le=50)] = None
    our_page_url: str | None = None
    our_word_count: Annotated[int | None, Field(ge=0)] = None
    gsc_impressions: Annotated[int | None, Field(ge=0)] = None

    # Competitor coverage
    competitor_best_position: Annotated[int | None, Field(ge=1)] = None
    competitor_best_url: str | None = None
    competitor_avg_word_count: Annotated[int | None, Field(ge=0)] = None
    competitor_avg_depth_score: Annotated[float | None, Field(ge=1.0, le=5.0)] = None
    competitors_analysed: Annotated[int, Field(ge=0)] = 0
    competitors_excluded: Annotated[int, Field(ge=0)] = 0

    # Thin content fields (populated when gap_type = "thin_content")
    word_count_gap: Annotated[int | None, Field(ge=0)] = None
    thin_content_rationale: str | None = None

    # Opportunity scoring
    opportunity_score: Annotated[float | None, Field(ge=0.0, le=1.0)] = None
    thin_content_priority_score: Annotated[float | None, Field(ge=0.0, le=1.0)] = None
    score_rationale: str | None = None
    score_inputs: ScoreInputs | None = None

    # Flags
    is_universal_gap: bool = False
    partial_data: bool = False
    partial_data_reason: str | None = None
    llm_assessed_fields: list[str] = Field(default_factory=list)

    # Pipeline tracking
    pipeline_run_id: str | None = None

    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @model_validator(mode="after")
    def validate_thin_content_constraints(self) -> ContentGapRecord:
        """Validate thin content business rules.

        - thin_content requires rank 11-50 (never top 10, never non-ranking)
        - thin_content requires our_page_url
        """
        if self.gap_type == GapType.THIN_CONTENT:
            if (
                self.our_ranking_position is not None
                and self.our_ranking_position <= 10
            ):
                msg = "thin_content cannot have ranking position <= 10"
                raise ValueError(msg)
            if self.our_ranking_position is None:
                msg = "thin_content requires a ranking position (11-50)"
                raise ValueError(msg)
            if self.our_page_url is None:
                msg = "thin_content requires our_page_url"
                raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_score_inputs_present(self) -> ContentGapRecord:
        """Ensure score_inputs is present when opportunity_score is set."""
        if self.opportunity_score is not None and self.score_inputs is None:
            msg = "score_inputs must be present when opportunity_score is set"
            raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# Cross-Language Summary
# ---------------------------------------------------------------------------


class CrossLanguageSummaryRecord(BaseModel):
    """Cross-language gap summary for a keyword.

    Maps to the `cross_language_summary` table in the target Drizzle schema.
    One record per keyword per campaign (aggregating across languages).

    TypeScript equivalent: crossLanguageSummary table in design.md.
    """

    id: str = Field(default_factory=_generate_cls_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    campaign_id: str = Field(min_length=1)
    keyword_id: str = Field(min_length=1)
    keyword_text: str = Field(min_length=1)

    languages_with_gap: list[str] = Field(default_factory=list)
    languages_with_coverage: list[str] = Field(default_factory=list)
    is_universal_gap: bool = False
    total_languages_analysed: Annotated[int, Field(ge=1)]

    pipeline_run_id: str | None = None
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @model_validator(mode="after")
    def validate_universal_gap(self) -> CrossLanguageSummaryRecord:
        """Universal gap must mean gap in all languages."""
        if (
            self.is_universal_gap
            and len(self.languages_with_gap) != self.total_languages_analysed
        ):
            msg = (
                "is_universal_gap=True but languages_with_gap count "
                f"({len(self.languages_with_gap)}) != "
                f"total_languages_analysed ({self.total_languages_analysed})"
            )
            raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# Input Types (consumed from upstream features)
# ---------------------------------------------------------------------------


class KeywordInput(BaseModel):
    """Keyword data consumed from F-001.

    Lightweight view containing only fields needed for gap analysis.
    """

    keyword_id: str
    keyword_text: str
    volume: int = 0
    difficulty: int = 0


class SerpEntry(BaseModel):
    """A single SERP result for a keyword, consumed from F-004.

    Used to determine competitor positions and user domain coverage.
    """

    url: str
    domain: str
    position: Annotated[int, Field(ge=1, le=50)]
    word_count: Annotated[int | None, Field(ge=0)] = None


class CompetitorEntry(BaseModel):
    """Competitor data consumed from F-005.

    Contains word count and quality scores for gap analysis comparison.
    """

    url: str
    domain: str
    position: Annotated[int, Field(ge=1)]
    word_count: Annotated[int | None, Field(ge=0)] = None
    depth_score: Annotated[int | None, Field(ge=1, le=5)] = None
    crawl_failed: bool = False
    llm_assessed_fields: list[str] = Field(default_factory=list)


class GscQueryData(BaseModel):
    """Google Search Console query data for user's site.

    Used as authoritative source of 'keywords we rank for'.
    """

    keyword_text: str
    impressions: Annotated[int, Field(ge=0)] = 0
    clicks: Annotated[int, Field(ge=0)] = 0
    position: Annotated[float | None, Field(ge=1.0)] = None
    page_url: str | None = None
