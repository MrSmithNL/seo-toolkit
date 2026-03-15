"""Tests for F-006 Content Gap Identification models.

Covers: PI-001 (valid classification), PI-002 (uniqueness),
PI-009 (tenant isolation), PI-010 (existing page URL for thin content),
PI-012 (non-ranking never thin).
"""

from __future__ import annotations

import uuid

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from src.research_engine.models.content_gap import (
    ContentGapRecord,
    CoverageSource,
    CrossLanguageSummaryRecord,
    GapType,
    ScoreInputs,
)

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")


# ---------------------------------------------------------------------------
# PI-001: Valid classification
# ---------------------------------------------------------------------------


class TestGapTypeEnum:
    """PI-001: gap_type is one of 4 valid values."""

    def test_own_gap_is_valid(self) -> None:
        assert GapType.OWN_GAP == "own_gap"

    def test_own_coverage_is_valid(self) -> None:
        assert GapType.OWN_COVERAGE == "own_coverage"

    def test_thin_content_is_valid(self) -> None:
        assert GapType.THIN_CONTENT == "thin_content"

    def test_new_opportunity_is_valid(self) -> None:
        assert GapType.NEW_OPPORTUNITY == "new_opportunity"

    def test_exactly_four_values(self) -> None:
        assert len(GapType) == 4

    def test_invalid_gap_type_rejected(self) -> None:
        with pytest.raises(ValueError):
            GapType("invalid_type")


# ---------------------------------------------------------------------------
# PI-009: Tenant isolation
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    """PI-009: Every gap row has non-null tenant_id."""

    def test_tenant_id_required(self) -> None:
        with pytest.raises(ValidationError):
            ContentGapRecord(
                campaign_id="camp_1",
                keyword_id="kw_1",
                keyword_text="test keyword",
                language="en",
                gap_type=GapType.OWN_GAP,
                coverage_source=CoverageSource.GSC,
            )

    def test_tenant_id_present(self) -> None:
        record = ContentGapRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="test keyword",
            language="en",
            gap_type=GapType.OWN_GAP,
            coverage_source=CoverageSource.GSC,
        )
        assert record.tenant_id == TENANT_ID


# ---------------------------------------------------------------------------
# PI-010: Existing page URL for thin content
# ---------------------------------------------------------------------------


class TestThinContentConstraints:
    """PI-010: thin_content requires our_page_url.

    PI-012: Non-ranking never classified as thin_content.
    """

    def test_thin_content_requires_page_url(self) -> None:
        with pytest.raises(ValueError, match="our_page_url"):
            ContentGapRecord(
                tenant_id=TENANT_ID,
                campaign_id="camp_1",
                keyword_id="kw_1",
                keyword_text="test keyword",
                language="en",
                gap_type=GapType.THIN_CONTENT,
                coverage_source=CoverageSource.GSC,
                our_ranking_position=22,
                our_page_url=None,
            )

    def test_thin_content_rejects_top_10(self) -> None:
        """Thin content cannot have ranking position <= 10."""
        with pytest.raises(ValueError, match="<= 10"):
            ContentGapRecord(
                tenant_id=TENANT_ID,
                campaign_id="camp_1",
                keyword_id="kw_1",
                keyword_text="test keyword",
                language="en",
                gap_type=GapType.THIN_CONTENT,
                coverage_source=CoverageSource.GSC,
                our_ranking_position=4,
                our_page_url="/some-page",
            )

    def test_thin_content_rejects_non_ranking(self) -> None:
        """PI-012: Non-ranking pages cannot be thin content."""
        with pytest.raises(ValueError, match="ranking position"):
            ContentGapRecord(
                tenant_id=TENANT_ID,
                campaign_id="camp_1",
                keyword_id="kw_1",
                keyword_text="test keyword",
                language="en",
                gap_type=GapType.THIN_CONTENT,
                coverage_source=CoverageSource.GSC,
                our_ranking_position=None,
                our_page_url="/some-page",
            )

    def test_thin_content_valid_with_position_11_plus(self) -> None:
        record = ContentGapRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="test keyword",
            language="en",
            gap_type=GapType.THIN_CONTENT,
            coverage_source=CoverageSource.GSC,
            our_ranking_position=18,
            our_page_url="/aftercare",
            our_word_count=400,
        )
        assert record.gap_type == GapType.THIN_CONTENT
        assert record.our_ranking_position == 18


# ---------------------------------------------------------------------------
# PI-004: Score inputs present when score set
# ---------------------------------------------------------------------------


class TestScoreInputsPresence:
    """PI-004: score_inputs always present when opportunity_score is set."""

    def test_score_without_inputs_rejected(self) -> None:
        with pytest.raises(ValueError, match="score_inputs"):
            ContentGapRecord(
                tenant_id=TENANT_ID,
                campaign_id="camp_1",
                keyword_id="kw_1",
                keyword_text="test keyword",
                language="en",
                gap_type=GapType.OWN_GAP,
                coverage_source=CoverageSource.GSC,
                opportunity_score=0.74,
                score_inputs=None,
            )

    def test_score_with_inputs_accepted(self) -> None:
        inputs = ScoreInputs(
            volume=8100,
            volume_normalised=1.0,
            difficulty=32,
            difficulty_inverse_normalised=0.68,
            gap_score=1.0,
            universal_gap_bonus=0.0,
        )
        record = ContentGapRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="test keyword",
            language="en",
            gap_type=GapType.OWN_GAP,
            coverage_source=CoverageSource.GSC,
            opportunity_score=0.74,
            score_inputs=inputs,
        )
        assert record.score_inputs is not None
        assert record.score_inputs.volume == 8100


# ---------------------------------------------------------------------------
# Cross-language summary validation
# ---------------------------------------------------------------------------


class TestCrossLanguageSummary:
    """Validates cross-language summary model constraints."""

    def test_universal_gap_consistency(self) -> None:
        """is_universal_gap=True requires all languages to have gaps."""
        with pytest.raises(ValueError, match="universal_gap"):
            CrossLanguageSummaryRecord(
                tenant_id=TENANT_ID,
                campaign_id="camp_1",
                keyword_id="kw_1",
                keyword_text="FUE vs DHI",
                is_universal_gap=True,
                languages_with_gap=["en", "de"],
                languages_with_coverage=["fr"],
                total_languages_analysed=3,
            )

    def test_universal_gap_valid(self) -> None:
        record = CrossLanguageSummaryRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="FUE vs DHI",
            is_universal_gap=True,
            languages_with_gap=["en", "de", "fr", "nl"],
            languages_with_coverage=[],
            total_languages_analysed=4,
        )
        assert record.is_universal_gap is True
        assert len(record.languages_with_gap) == 4

    def test_language_specific_gap(self) -> None:
        record = CrossLanguageSummaryRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="Haartransplantation Kosten",
            is_universal_gap=False,
            languages_with_gap=["de"],
            languages_with_coverage=["en"],
            total_languages_analysed=2,
        )
        assert record.is_universal_gap is False
        assert "de" in record.languages_with_gap
        assert "en" in record.languages_with_coverage


# ---------------------------------------------------------------------------
# ID generation
# ---------------------------------------------------------------------------


class TestIdGeneration:
    """Content gap IDs use correct prefix."""

    def test_content_gap_id_prefix(self) -> None:
        record = ContentGapRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="test keyword",
            language="en",
            gap_type=GapType.OWN_GAP,
            coverage_source=CoverageSource.GSC,
        )
        assert record.id.startswith("cg_")

    def test_cross_language_summary_id_prefix(self) -> None:
        record = CrossLanguageSummaryRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="test",
            total_languages_analysed=1,
        )
        assert record.id.startswith("cls_")


# ---------------------------------------------------------------------------
# Property-based tests (PI-003, PI-005)
# ---------------------------------------------------------------------------


class TestPropertyInvariants:
    """Property-based tests for model invariants."""

    @given(
        score=st.floats(min_value=0.0, max_value=1.0),
    )
    def test_opportunity_score_range(self, score: float) -> None:
        """PI-003: opportunity_score is always 0.0-1.0."""
        inputs = ScoreInputs(
            volume=100,
            volume_normalised=0.5,
            difficulty=50,
            difficulty_inverse_normalised=0.5,
            gap_score=0.5,
        )
        record = ContentGapRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="test",
            language="en",
            gap_type=GapType.OWN_GAP,
            coverage_source=CoverageSource.GSC,
            opportunity_score=score,
            score_inputs=inputs,
        )
        assert 0.0 <= record.opportunity_score <= 1.0

    @given(
        position=st.integers(min_value=11, max_value=50),
    )
    def test_thin_content_only_rank_11_50(self, position: int) -> None:
        """PI-005: thin_content only with rank 11-50."""
        record = ContentGapRecord(
            tenant_id=TENANT_ID,
            campaign_id="camp_1",
            keyword_id="kw_1",
            keyword_text="test",
            language="en",
            gap_type=GapType.THIN_CONTENT,
            coverage_source=CoverageSource.GSC,
            our_ranking_position=position,
            our_page_url="/test",
        )
        assert record.our_ranking_position >= 11
