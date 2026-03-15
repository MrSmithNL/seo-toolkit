"""Tests for ContentBrief Pydantic model and schema validation.

Covers: ATS-020, ATS-021, ATS-022, ATS-023, ATS-024,
        PI-001 through PI-007.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from src.research_engine.models.content_brief import (
    SCHEMA_VERSION,
    ApprovedBriefsFile,
    BriefStatus,
    ContentBrief,
    ContentType,
    GapType,
    SearchIntent,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _valid_brief(**overrides) -> dict:
    """Return a valid ContentBrief dict, overridable for specific tests."""
    base = {
        "id": f"cb_{uuid.uuid4().hex[:12]}",
        "tenant_id": uuid.UUID("12345678-1234-1234-1234-123456789abc"),
        "created_at": datetime.now(tz=UTC),
        "schema_version": SCHEMA_VERSION,
        "status": BriefStatus.PENDING_REVIEW,
        "target_keyword": "hair transplant cost",
        "target_language": "en",
        "target_country": "DE",
        "supporting_keywords": ["fue cost", "dhi cost"],
        "search_intent": SearchIntent.COMMERCIAL,
        "topic_cluster": "Hair Transplant Costs",
        "content_type": ContentType.COMPARISON,
        "keyword_volume": 8100,
        "keyword_difficulty": 32,
        "opportunity_score": 0.74,
        "opportunity_score_rationale": (
            "Score: 0.74 — High volume (8,100/mo),"
            " easy to rank (32/100), no competitor in top 5."
        ),
        "gap_type": GapType.OWN_GAP,
        "existing_page_url": None,
        "competitor_avg_word_count": 2400,
        "competitor_depth_scores": [3, 4, 3],
        "top_competitor_url": "https://example.com/hair-transplant-cost",
        "competitor_schema_types": ["Article", "FAQPage"],
        "competitors_have_faq": True,
        "recommended_word_count": 2600,
        "recommended_headings": [
            "What does a hair transplant cost?",
            "FUE vs DHI pricing",
        ],
        "recommended_schema_types": ["Article", "FAQPage"],
        "include_faq": True,
        "suggested_publish_date": "2026-03-16",
        "reviewed_by": None,
        "reviewed_at": None,
        "review_notes": None,
        "overridden_word_count": None,
        "overridden_publish_date": None,
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# ATS-020: Valid brief passes validation
# ---------------------------------------------------------------------------


class TestValidBrief:
    """ATS-020: Valid brief passes validation."""

    def test_valid_brief_passes(self) -> None:
        """A fully populated ContentBrief with correct types should validate."""
        brief = ContentBrief(**_valid_brief())
        assert brief.target_keyword == "hair transplant cost"
        assert brief.schema_version == SCHEMA_VERSION
        assert brief.status == BriefStatus.PENDING_REVIEW

    def test_id_is_prefixed(self) -> None:
        """Generated IDs should be prefixed with cb_."""
        brief = ContentBrief(**_valid_brief())
        assert brief.id.startswith("cb_")

    def test_nullable_fields_accept_none(self) -> None:
        """Nullable fields should accept None values."""
        brief = ContentBrief(
            **_valid_brief(
                topic_cluster=None,
                existing_page_url=None,
                top_competitor_url=None,
                reviewed_by=None,
                reviewed_at=None,
                review_notes=None,
                overridden_word_count=None,
                overridden_publish_date=None,
            )
        )
        assert brief.topic_cluster is None
        assert brief.reviewed_by is None


# ---------------------------------------------------------------------------
# ATS-021: Missing required field rejected
# ---------------------------------------------------------------------------


class TestMissingRequiredField:
    """ATS-021: Missing required field rejected."""

    def test_missing_target_keyword(self) -> None:
        """ContentBrief without target_keyword should fail validation."""
        data = _valid_brief()
        del data["target_keyword"]
        with pytest.raises(ValidationError, match="target_keyword"):
            ContentBrief(**data)

    def test_missing_search_intent(self) -> None:
        """ContentBrief without search_intent should fail validation."""
        data = _valid_brief()
        del data["search_intent"]
        with pytest.raises(ValidationError, match="search_intent"):
            ContentBrief(**data)

    def test_missing_opportunity_score(self) -> None:
        """ContentBrief without opportunity_score should fail validation."""
        data = _valid_brief()
        del data["opportunity_score"]
        with pytest.raises(ValidationError, match="opportunity_score"):
            ContentBrief(**data)


# ---------------------------------------------------------------------------
# ATS-022: Schema version mismatch rejected
# ---------------------------------------------------------------------------


class TestSchemaVersionMismatch:
    """ATS-022: Schema version mismatch rejected."""

    def test_wrong_schema_version(self) -> None:
        """A ContentBrief with wrong schema_version should be rejected."""
        with pytest.raises(ValidationError, match="schema mismatch"):
            ContentBrief(**_valid_brief(schema_version="0.9.0"))

    def test_correct_schema_version(self) -> None:
        """A ContentBrief with correct schema_version should pass."""
        brief = ContentBrief(**_valid_brief(schema_version=SCHEMA_VERSION))
        assert brief.schema_version == SCHEMA_VERSION


# ---------------------------------------------------------------------------
# ATS-023: Invalid enum value rejected
# ---------------------------------------------------------------------------


class TestInvalidEnumValue:
    """ATS-023: Invalid enum value rejected."""

    def test_invalid_content_type(self) -> None:
        """content_type='infographic' (not in enum) should fail."""
        with pytest.raises(ValidationError, match="content_type"):
            ContentBrief(**_valid_brief(content_type="infographic"))

    def test_invalid_search_intent(self) -> None:
        """search_intent='research' (not in enum) should fail."""
        with pytest.raises(ValidationError, match="search_intent"):
            ContentBrief(**_valid_brief(search_intent="research"))

    def test_invalid_status(self) -> None:
        """status='draft' (not in enum) should fail."""
        with pytest.raises(ValidationError, match="status"):
            ContentBrief(**_valid_brief(status="draft"))

    def test_invalid_gap_type(self) -> None:
        """gap_type='competitive_gap' (not in enum) should fail."""
        with pytest.raises(ValidationError, match="gap_type"):
            ContentBrief(**_valid_brief(gap_type="competitive_gap"))


# ---------------------------------------------------------------------------
# ATS-024: Approved-briefs file validated before writing
# ---------------------------------------------------------------------------


class TestApprovedBriefsFile:
    """ATS-024: Approved-briefs file validated before writing."""

    def test_valid_approved_briefs_file(self) -> None:
        """A valid ApprovedBriefsFile with schema_version should pass."""
        brief = ContentBrief(
            **_valid_brief(
                status=BriefStatus.APPROVED,
                reviewed_by="malcolm",
                reviewed_at=datetime.now(tz=UTC),
            )
        )
        file = ApprovedBriefsFile(
            schema_version=SCHEMA_VERSION,
            generated_at=datetime.now(tz=UTC),
            campaign_id="camp_001",
            briefs=[brief],
        )
        assert file.schema_version == SCHEMA_VERSION
        assert len(file.briefs) == 1

    def test_empty_briefs_array(self) -> None:
        """An empty briefs array should be valid."""
        file = ApprovedBriefsFile(
            schema_version=SCHEMA_VERSION,
            generated_at=datetime.now(tz=UTC),
            campaign_id="camp_001",
            briefs=[],
        )
        assert len(file.briefs) == 0

    def test_wrong_file_schema_version(self) -> None:
        """ApprovedBriefsFile with wrong schema_version should fail."""
        with pytest.raises(ValidationError, match="schema_version"):
            ApprovedBriefsFile(
                schema_version="0.5.0",
                generated_at=datetime.now(tz=UTC),
                campaign_id="camp_001",
                briefs=[],
            )


# ---------------------------------------------------------------------------
# PI-001: ContentBrief ID unique (UUID-based)
# ---------------------------------------------------------------------------


class TestIdUniqueness:
    """PI-001: ContentBrief ID unique."""

    def test_generated_ids_are_unique(self) -> None:
        """Two independently created briefs should have different IDs."""
        data1 = _valid_brief()
        data2 = _valid_brief()
        # Each call to _valid_brief() generates a new UUID
        assert data1["id"] != data2["id"]


# ---------------------------------------------------------------------------
# PI-003: Schema version pinned to "1.0.0"
# ---------------------------------------------------------------------------


class TestSchemaVersionPinned:
    """PI-003: Schema version pinned."""

    def test_schema_version_constant(self) -> None:
        """SCHEMA_VERSION should be '1.0.0'."""
        assert SCHEMA_VERSION == "1.0.0"


# ---------------------------------------------------------------------------
# PI-007: Opportunity score range 0.0 - 1.0
# ---------------------------------------------------------------------------


class TestOpportunityScoreRange:
    """PI-007: Opportunity score range."""

    def test_score_at_zero(self) -> None:
        """Score of 0.0 should be valid."""
        brief = ContentBrief(**_valid_brief(opportunity_score=0.0))
        assert brief.opportunity_score == 0.0

    def test_score_at_one(self) -> None:
        """Score of 1.0 should be valid."""
        brief = ContentBrief(**_valid_brief(opportunity_score=1.0))
        assert brief.opportunity_score == 1.0

    def test_score_above_one(self) -> None:
        """Score > 1.0 should fail validation."""
        with pytest.raises(ValidationError, match="opportunity_score"):
            ContentBrief(**_valid_brief(opportunity_score=1.5))

    def test_negative_score(self) -> None:
        """Negative score should fail validation."""
        with pytest.raises(ValidationError, match="opportunity_score"):
            ContentBrief(**_valid_brief(opportunity_score=-0.1))


# ---------------------------------------------------------------------------
# PI-008: Word count positive
# ---------------------------------------------------------------------------


class TestWordCountPositive:
    """PI-008: recommended_word_count > 0."""

    def test_zero_word_count(self) -> None:
        """Word count of 0 should fail."""
        with pytest.raises(ValidationError, match="recommended_word_count"):
            ContentBrief(**_valid_brief(recommended_word_count=0))

    def test_positive_word_count(self) -> None:
        """Word count of 100 should pass."""
        brief = ContentBrief(**_valid_brief(recommended_word_count=100))
        assert brief.recommended_word_count == 100


# ---------------------------------------------------------------------------
# PI-011: Rationale non-empty
# ---------------------------------------------------------------------------


class TestRationaleNonEmpty:
    """PI-011: opportunity_score_rationale is always non-empty."""

    def test_empty_rationale(self) -> None:
        """Empty rationale should fail."""
        with pytest.raises(ValidationError, match="opportunity_score_rationale"):
            ContentBrief(**_valid_brief(opportunity_score_rationale=""))


# ---------------------------------------------------------------------------
# PI-012: Thin content → existing_page_url non-null
# ---------------------------------------------------------------------------


class TestThinContentUrl:
    """PI-012: thin_content gap_type requires existing_page_url."""

    def test_thin_content_without_url(self) -> None:
        """thin_content with null existing_page_url should fail."""
        with pytest.raises(ValidationError, match="existing_page_url"):
            ContentBrief(
                **_valid_brief(
                    gap_type=GapType.THIN_CONTENT,
                    existing_page_url=None,
                )
            )

    def test_thin_content_with_url(self) -> None:
        """thin_content with a URL should pass."""
        brief = ContentBrief(
            **_valid_brief(
                gap_type=GapType.THIN_CONTENT,
                existing_page_url="https://example.com/page",
            )
        )
        assert brief.gap_type == GapType.THIN_CONTENT
        assert brief.existing_page_url == "https://example.com/page"

    def test_own_gap_without_url_is_fine(self) -> None:
        """own_gap with null existing_page_url should pass."""
        brief = ContentBrief(
            **_valid_brief(
                gap_type=GapType.OWN_GAP,
                existing_page_url=None,
            )
        )
        assert brief.existing_page_url is None


# ---------------------------------------------------------------------------
# PI-013: Tenant isolation (tenant_id non-null)
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    """PI-013: Every ContentBrief has a non-null tenant_id."""

    def test_missing_tenant_id(self) -> None:
        """Missing tenant_id should fail."""
        data = _valid_brief()
        del data["tenant_id"]
        with pytest.raises(ValidationError, match="tenant_id"):
            ContentBrief(**data)


# ---------------------------------------------------------------------------
# PI-014: Audit fields on approval
# ---------------------------------------------------------------------------


class TestAuditFieldsOnApproval:
    """PI-014: Approved/rejected records always have reviewed_by + reviewed_at."""

    def test_approved_without_reviewed_by(self) -> None:
        """Approved brief without reviewed_by should fail."""
        with pytest.raises(ValidationError, match="reviewed_by"):
            ContentBrief(
                **_valid_brief(
                    status=BriefStatus.APPROVED,
                    reviewed_by=None,
                    reviewed_at=datetime.now(tz=UTC),
                )
            )

    def test_approved_without_reviewed_at(self) -> None:
        """Approved brief without reviewed_at should fail."""
        with pytest.raises(ValidationError, match="reviewed_at"):
            ContentBrief(
                **_valid_brief(
                    status=BriefStatus.APPROVED,
                    reviewed_by="malcolm",
                    reviewed_at=None,
                )
            )

    def test_rejected_without_reviewed_by(self) -> None:
        """Rejected brief without reviewed_by should fail."""
        with pytest.raises(ValidationError, match="reviewed_by"):
            ContentBrief(
                **_valid_brief(
                    status=BriefStatus.REJECTED,
                    reviewed_by=None,
                    reviewed_at=datetime.now(tz=UTC),
                )
            )

    def test_approved_with_audit_fields(self) -> None:
        """Approved brief with both audit fields should pass."""
        brief = ContentBrief(
            **_valid_brief(
                status=BriefStatus.APPROVED,
                reviewed_by="malcolm",
                reviewed_at=datetime.now(tz=UTC),
            )
        )
        assert brief.reviewed_by == "malcolm"


# ---------------------------------------------------------------------------
# Property-based tests (Hypothesis)
# ---------------------------------------------------------------------------


class TestPropertyInvariants:
    """Property-based tests for ContentBrief schema invariants."""

    @given(score=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    def test_valid_score_always_passes(self, score: float) -> None:
        """PI-007: Any score in [0.0, 1.0] should produce a valid brief."""
        brief = ContentBrief(**_valid_brief(opportunity_score=score))
        assert 0.0 <= brief.opportunity_score <= 1.0

    @given(difficulty=st.integers(min_value=0, max_value=100))
    def test_valid_difficulty_always_passes(self, difficulty: int) -> None:
        """Any difficulty in [0, 100] should produce a valid brief."""
        brief = ContentBrief(**_valid_brief(keyword_difficulty=difficulty))
        assert 0 <= brief.keyword_difficulty <= 100

    @given(volume=st.integers(min_value=0, max_value=1_000_000))
    def test_valid_volume_always_passes(self, volume: int) -> None:
        """Any non-negative volume should produce a valid brief."""
        brief = ContentBrief(**_valid_brief(keyword_volume=volume))
        assert brief.keyword_volume >= 0

    @given(
        content_type=st.sampled_from(
            [
                "blog_post",
                "comparison",
                "how_to",
                "faq",
                "product_page",
                "landing_page",
            ]
        ),
        intent=st.sampled_from(
            [
                "informational",
                "transactional",
                "navigational",
                "commercial",
            ]
        ),
    )
    def test_valid_enums_always_pass(self, content_type: str, intent: str) -> None:
        """PI-005 + PI-006: Valid enum values should always produce a valid brief."""
        brief = ContentBrief(
            **_valid_brief(
                content_type=content_type,
                search_intent=intent,
            )
        )
        assert brief.content_type in ContentType
        assert brief.search_intent in SearchIntent
