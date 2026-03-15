"""ContentBrief schema and domain models for F-007 Content Calendar.

Pydantic v2 models matching the target TypeScript/Zod schema 1:1.
This is the single source of truth for the E-001 → E-002 interface contract.

Changes to this schema require a new schema_version and an ADR.

TypeScript equivalent: contracts/content-brief.schema.ts
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SCHEMA_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class BriefStatus(StrEnum):
    """ContentBrief lifecycle status."""

    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    PUBLISHED = "published"


class SearchIntent(StrEnum):
    """Search intent classification (4-type taxonomy)."""

    INFORMATIONAL = "informational"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"
    COMMERCIAL = "commercial"


class ContentType(StrEnum):
    """Content format type for the brief."""

    BLOG_POST = "blog_post"
    COMPARISON = "comparison"
    HOW_TO = "how_to"
    FAQ = "faq"
    PRODUCT_PAGE = "product_page"
    LANDING_PAGE = "landing_page"


class GapType(StrEnum):
    """Content gap classification type."""

    OWN_GAP = "own_gap"
    THIN_CONTENT = "thin_content"
    NEW_OPPORTUNITY = "new_opportunity"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _generate_cb_id() -> str:
    """Generate a prefixed content brief ID."""
    return f"cb_{uuid.uuid4().hex[:12]}"


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(tz=UTC)


# ---------------------------------------------------------------------------
# ContentBrief Model
# ---------------------------------------------------------------------------


class ContentBrief(BaseModel):
    """Content brief — interface contract between E-001 and E-002.

    Version: 1.0.0
    Consumed by: E-002 Content Creation, E-003 Optimisation, E-005 Measurement.
    """

    model_config = ConfigDict(use_enum_values=False)

    # Identity
    id: str = Field(default_factory=_generate_cb_id)
    tenant_id: uuid.UUID
    created_at: datetime = Field(default_factory=_now_utc)
    schema_version: str = Field(default=SCHEMA_VERSION)
    status: BriefStatus = BriefStatus.PENDING_REVIEW

    # Target and strategy
    target_keyword: str = Field(min_length=1)
    target_language: str = Field(min_length=2, max_length=5)
    target_country: str = Field(min_length=2, max_length=2)
    supporting_keywords: list[str] = Field(default_factory=list)
    search_intent: SearchIntent
    topic_cluster: str | None = None
    content_type: ContentType

    # Research inputs
    keyword_volume: Annotated[int, Field(ge=0)]
    keyword_difficulty: Annotated[int, Field(ge=0, le=100)]
    opportunity_score: Annotated[float, Field(ge=0.0, le=1.0)]
    opportunity_score_rationale: str = Field(min_length=1)
    gap_type: GapType
    existing_page_url: str | None = None

    # Competitor benchmarks
    competitor_avg_word_count: Annotated[int, Field(ge=0)]
    competitor_depth_scores: list[int] = Field(default_factory=list)
    top_competitor_url: str | None = None
    competitor_schema_types: list[str] = Field(default_factory=list)
    competitors_have_faq: bool = False

    # Recommendations
    recommended_word_count: Annotated[int, Field(ge=1)]
    recommended_headings: list[str] = Field(default_factory=list)
    recommended_schema_types: list[str] = Field(default_factory=list)
    include_faq: bool = False
    suggested_publish_date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")

    # Human review
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    overridden_word_count: Annotated[int | None, Field(ge=1)] = None
    overridden_publish_date: str | None = None

    @model_validator(mode="after")
    def validate_schema_version(self) -> ContentBrief:
        """Ensure schema_version matches the current version."""
        if self.schema_version != SCHEMA_VERSION:
            msg = (
                f"ContentBrief schema mismatch: brief version {self.schema_version} "
                f"is incompatible with current version {SCHEMA_VERSION}. "
                "Regenerate this brief."
            )
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_thin_content_url(self) -> ContentBrief:
        """Thin content gap_type requires existing_page_url."""
        if self.gap_type == GapType.THIN_CONTENT and self.existing_page_url is None:
            msg = "thin_content gap_type requires existing_page_url to be set"
            raise ValueError(msg)
        return self

    @model_validator(mode="after")
    def validate_audit_fields_on_approval(self) -> ContentBrief:
        """Approved/rejected briefs must have reviewed_by and reviewed_at."""
        if self.status in (BriefStatus.APPROVED, BriefStatus.REJECTED):
            if self.reviewed_by is None:
                msg = f"reviewed_by is required when status is {self.status}"
                raise ValueError(msg)
            if self.reviewed_at is None:
                msg = f"reviewed_at is required when status is {self.status}"
                raise ValueError(msg)
        return self


# ---------------------------------------------------------------------------
# Approved Briefs File Wrapper
# ---------------------------------------------------------------------------


class ApprovedBriefsFile(BaseModel):
    """File-level wrapper for approved-briefs output.

    Contains schema_version at file root alongside the briefs array.
    """

    schema_version: str = Field(default=SCHEMA_VERSION)
    generated_at: datetime
    campaign_id: str
    briefs: list[ContentBrief] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_file_schema_version(self) -> ApprovedBriefsFile:
        """Ensure file schema_version matches current."""
        if self.schema_version != SCHEMA_VERSION:
            msg = (
                f"ApprovedBriefsFile schema mismatch: version {self.schema_version} "
                f"is incompatible with current version {SCHEMA_VERSION}."
            )
            raise ValueError(msg)
        return self
