"""Tests for F-006 CrossLanguageSummariser.

Covers: ATS-016, ATS-017, ATS-018, ATS-019.
"""

from __future__ import annotations

import uuid

from src.research_engine.models.content_gap import (
    ContentGapRecord,
    CoverageSource,
    GapType,
)
from src.research_engine.services.cross_language_summariser import (
    summarise_cross_language,
)

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN_ID = "camp_1"


def _make_gap_record(
    keyword_id: str,
    keyword_text: str,
    language: str,
    gap_type: GapType,
) -> ContentGapRecord:
    """Helper to create a gap record for testing."""
    return ContentGapRecord(
        tenant_id=TENANT_ID,
        campaign_id=CAMPAIGN_ID,
        keyword_id=keyword_id,
        keyword_text=keyword_text,
        language=language,
        gap_type=gap_type,
        coverage_source=CoverageSource.GSC,
    )


# ---------------------------------------------------------------------------
# ATS-016: Universal gap across all languages
# ---------------------------------------------------------------------------


class TestUniversalGap:
    """ATS-016: Keyword missing in all languages → universal gap."""

    def test_universal_gap_four_languages(self) -> None:
        records = [
            _make_gap_record("kw_1", "FUE vs DHI", "en", GapType.OWN_GAP),
            _make_gap_record("kw_1", "FUE vs DHI", "de", GapType.OWN_GAP),
            _make_gap_record("kw_1", "FUE vs DHI", "fr", GapType.OWN_GAP),
            _make_gap_record("kw_1", "FUE vs DHI", "nl", GapType.OWN_GAP),
        ]

        result = summarise_cross_language(
            gap_records=records,
            languages=["en", "de", "fr", "nl"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        assert len(result.summaries) == 1
        summary = result.summaries[0]
        assert summary.is_universal_gap is True
        assert len(summary.languages_with_gap) == 4
        assert len(summary.languages_with_coverage) == 0
        assert "kw_1" in result.universal_gap_keyword_ids

    def test_new_opportunity_counts_as_gap(self) -> None:
        """new_opportunity is also a gap (no coverage)."""
        records = [
            _make_gap_record("kw_1", "scalp massage", "en", GapType.NEW_OPPORTUNITY),
            _make_gap_record("kw_1", "scalp massage", "de", GapType.NEW_OPPORTUNITY),
        ]

        result = summarise_cross_language(
            gap_records=records,
            languages=["en", "de"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        assert result.summaries[0].is_universal_gap is True
        assert "kw_1" in result.universal_gap_keyword_ids


# ---------------------------------------------------------------------------
# ATS-017: Language-specific gap
# ---------------------------------------------------------------------------


class TestLanguageSpecificGap:
    """ATS-017: Keyword is gap in DE only, covered in EN."""

    def test_language_specific_gap(self) -> None:
        records = [
            _make_gap_record(
                "kw_2", "Haartransplantation Kosten", "de", GapType.OWN_GAP
            ),
            _make_gap_record(
                "kw_2", "Haartransplantation Kosten", "en", GapType.OWN_COVERAGE
            ),
        ]

        result = summarise_cross_language(
            gap_records=records,
            languages=["en", "de"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        assert len(result.summaries) == 1
        summary = result.summaries[0]
        assert summary.is_universal_gap is False
        assert "de" in summary.languages_with_gap
        assert "en" in summary.languages_with_coverage
        assert "kw_2" not in result.universal_gap_keyword_ids


# ---------------------------------------------------------------------------
# ATS-018: Already covered in all languages
# ---------------------------------------------------------------------------


class TestAllCovered:
    """ATS-018: No gap in any language → no summary record."""

    def test_all_covered_no_summary(self) -> None:
        records = [
            _make_gap_record(
                "kw_3", "hair transplant surgery", "en", GapType.OWN_COVERAGE
            ),
            _make_gap_record(
                "kw_3", "hair transplant surgery", "de", GapType.OWN_COVERAGE
            ),
            _make_gap_record(
                "kw_3", "hair transplant surgery", "fr", GapType.OWN_COVERAGE
            ),
        ]

        result = summarise_cross_language(
            gap_records=records,
            languages=["en", "de", "fr"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        # No summary for keywords with full coverage
        assert len(result.summaries) == 0
        assert len(result.universal_gap_keyword_ids) == 0


# ---------------------------------------------------------------------------
# ATS-019: Per-language independent matrices
# ---------------------------------------------------------------------------


class TestIndependentMatrices:
    """ATS-019: Multiple keywords, mixed gap patterns."""

    def test_mixed_keywords_across_languages(self) -> None:
        records = [
            # kw_1: universal gap
            _make_gap_record("kw_1", "FUE vs DHI", "en", GapType.OWN_GAP),
            _make_gap_record("kw_1", "FUE vs DHI", "de", GapType.OWN_GAP),
            # kw_2: language-specific gap (DE only)
            _make_gap_record("kw_2", "Kosten", "de", GapType.OWN_GAP),
            _make_gap_record("kw_2", "Kosten", "en", GapType.OWN_COVERAGE),
            # kw_3: fully covered
            _make_gap_record("kw_3", "transplant", "en", GapType.OWN_COVERAGE),
            _make_gap_record("kw_3", "transplant", "de", GapType.OWN_COVERAGE),
        ]

        result = summarise_cross_language(
            gap_records=records,
            languages=["en", "de"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        # kw_1 (universal) + kw_2 (language-specific) = 2 summaries
        assert len(result.summaries) == 2
        assert len(result.universal_gap_keyword_ids) == 1
        assert "kw_1" in result.universal_gap_keyword_ids

    def test_missing_language_record_treated_as_gap(self) -> None:
        """If a keyword has no record for a language, that's a gap."""
        records = [
            _make_gap_record("kw_1", "FUE vs DHI", "en", GapType.OWN_COVERAGE),
            # No DE record at all
        ]

        result = summarise_cross_language(
            gap_records=records,
            languages=["en", "de"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        assert len(result.summaries) == 1
        summary = result.summaries[0]
        assert "de" in summary.languages_with_gap
        assert "en" in summary.languages_with_coverage


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge case handling."""

    def test_single_language_universal_gap(self) -> None:
        """Universal gap with only 1 language analysed."""
        records = [
            _make_gap_record("kw_1", "test", "en", GapType.OWN_GAP),
        ]

        result = summarise_cross_language(
            gap_records=records,
            languages=["en"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        assert result.summaries[0].is_universal_gap is True
        assert result.summaries[0].total_languages_analysed == 1

    def test_thin_content_counts_as_coverage(self) -> None:
        """Thin content is still coverage (we rank, just poorly)."""
        thin_record = ContentGapRecord(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            keyword_id="kw_1",
            keyword_text="test",
            language="en",
            gap_type=GapType.THIN_CONTENT,
            coverage_source=CoverageSource.GSC,
            our_ranking_position=22,
            our_page_url="/test",
        )
        records = [
            thin_record,
            _make_gap_record("kw_1", "test", "de", GapType.OWN_GAP),
        ]

        result = summarise_cross_language(
            gap_records=records,
            languages=["en", "de"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        summary = result.summaries[0]
        # Thin content = coverage, so not universal gap
        assert summary.is_universal_gap is False
        assert "en" in summary.languages_with_coverage
        assert "de" in summary.languages_with_gap

    def test_empty_records(self) -> None:
        result = summarise_cross_language(
            gap_records=[],
            languages=["en", "de"],
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
        )

        assert len(result.summaries) == 0
        assert len(result.universal_gap_keyword_ids) == 0
