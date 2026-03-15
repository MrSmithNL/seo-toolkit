"""Tests for F-006 FileGapMatrixRepo.

Covers: INT-006 (standalone JSON output), PI-002 (no duplicates).
"""

from __future__ import annotations

import uuid
from pathlib import Path

from src.research_engine.models.content_gap import (
    ContentGapRecord,
    CoverageSource,
    CrossLanguageSummaryRecord,
    GapType,
    ScoreInputs,
)
from src.research_engine.repos.file_gap_matrix_repo import FileGapMatrixRepo

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN_ID = "camp_1"


def _make_scored_gap(
    keyword_id: str,
    keyword_text: str,
    language: str,
    gap_type: GapType,
    score: float = 0.5,
) -> ContentGapRecord:
    """Create a scored gap record for testing."""
    kwargs: dict = {
        "tenant_id": TENANT_ID,
        "campaign_id": CAMPAIGN_ID,
        "keyword_id": keyword_id,
        "keyword_text": keyword_text,
        "language": language,
        "gap_type": gap_type,
        "coverage_source": CoverageSource.GSC,
    }
    if gap_type == GapType.THIN_CONTENT:
        kwargs["our_ranking_position"] = 22
        kwargs["our_page_url"] = "/test"
        kwargs["thin_content_priority_score"] = score
    else:
        kwargs["opportunity_score"] = score
        kwargs["score_inputs"] = ScoreInputs(
            volume=1000,
            volume_normalised=0.5,
            difficulty=50,
            difficulty_inverse_normalised=0.5,
            gap_score=0.7,
        )
    return ContentGapRecord(**kwargs)


# ---------------------------------------------------------------------------
# INT-006: Standalone JSON output
# ---------------------------------------------------------------------------


class TestStandaloneJsonOutput:
    """INT-006: Gap matrix saved to data/gap-analysis/{domain}/{language}.json."""

    def test_save_and_load(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        gaps = [
            _make_scored_gap("kw_1", "FUE vs DHI", "en", GapType.OWN_GAP, 0.74),
            _make_scored_gap("kw_2", "hair cost", "en", GapType.NEW_OPPORTUNITY, 0.5),
        ]
        saved = repo.save_gaps(gaps)
        assert saved == 2

        # Verify file created
        json_file = tmp_path / "hairgenetix.com" / "en.json"
        assert json_file.exists()

        # Load back
        loaded = repo.get_gap_matrix(CAMPAIGN_ID, "en")
        assert len(loaded) == 2

    def test_per_language_files(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        gaps = [
            _make_scored_gap("kw_1", "keyword", "en", GapType.OWN_GAP),
            _make_scored_gap("kw_1", "keyword", "de", GapType.OWN_GAP),
        ]
        repo.save_gaps(gaps)

        en_file = tmp_path / "hairgenetix.com" / "en.json"
        de_file = tmp_path / "hairgenetix.com" / "de.json"
        assert en_file.exists()
        assert de_file.exists()


# ---------------------------------------------------------------------------
# PI-002: No duplicate (keyword, language) entries
# ---------------------------------------------------------------------------


class TestNoDuplicates:
    """PI-002: Upsert prevents duplicate (keyword_id, language) rows."""

    def test_upsert_on_save(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        gap1 = _make_scored_gap("kw_1", "FUE vs DHI", "en", GapType.OWN_GAP, 0.5)
        gap2 = _make_scored_gap("kw_1", "FUE vs DHI", "en", GapType.OWN_GAP, 0.8)

        repo.save_gaps([gap1])
        repo.save_gaps([gap2])

        loaded = repo.get_gap_matrix(CAMPAIGN_ID, "en")
        assert len(loaded) == 1
        # Latest version wins
        assert loaded[0].opportunity_score == 0.8


# ---------------------------------------------------------------------------
# Query tests
# ---------------------------------------------------------------------------


class TestQueries:
    """Query gap matrix with filters, sorting, and limits."""

    def test_filter_by_gap_type(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        gaps = [
            _make_scored_gap("kw_1", "kw1", "en", GapType.OWN_GAP, 0.7),
            _make_scored_gap("kw_2", "kw2", "en", GapType.NEW_OPPORTUNITY, 0.5),
            _make_scored_gap("kw_3", "kw3", "en", GapType.OWN_COVERAGE),
        ]
        repo.save_gaps(gaps)

        own_gaps = repo.get_gap_matrix(CAMPAIGN_ID, "en", gap_type=GapType.OWN_GAP)
        assert len(own_gaps) == 1
        assert own_gaps[0].keyword_id == "kw_1"

    def test_sort_by_opportunity_score(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        gaps = [
            _make_scored_gap("kw_1", "kw1", "en", GapType.OWN_GAP, 0.3),
            _make_scored_gap("kw_2", "kw2", "en", GapType.OWN_GAP, 0.9),
            _make_scored_gap("kw_3", "kw3", "en", GapType.OWN_GAP, 0.6),
        ]
        repo.save_gaps(gaps)

        sorted_gaps = repo.get_gap_matrix(
            CAMPAIGN_ID, "en", sort_by="opportunity_score"
        )
        scores = [g.opportunity_score for g in sorted_gaps]
        assert scores == sorted(scores, reverse=True)

    def test_min_score_filter(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        gaps = [
            _make_scored_gap("kw_1", "kw1", "en", GapType.OWN_GAP, 0.3),
            _make_scored_gap("kw_2", "kw2", "en", GapType.OWN_GAP, 0.8),
        ]
        repo.save_gaps(gaps)

        filtered = repo.get_gap_matrix(CAMPAIGN_ID, "en", min_score=0.5)
        assert len(filtered) == 1
        assert filtered[0].keyword_id == "kw_2"

    def test_get_top_opportunities(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        gaps = [
            _make_scored_gap("kw_1", "kw1", "en", GapType.OWN_GAP, 0.9),
            _make_scored_gap("kw_2", "kw2", "en", GapType.OWN_GAP, 0.7),
            _make_scored_gap("kw_3", "kw3", "en", GapType.OWN_COVERAGE, 0.5),
        ]
        repo.save_gaps(gaps)

        top = repo.get_top_opportunities(CAMPAIGN_ID, "en", limit=5)
        # Only own_gap and new_opportunity, sorted by score
        assert len(top) == 2
        assert top[0].opportunity_score >= top[1].opportunity_score

    def test_get_top_opportunities_limit(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        gaps = [
            _make_scored_gap(f"kw_{i}", f"kw{i}", "en", GapType.OWN_GAP, 0.5)
            for i in range(10)
        ]
        repo.save_gaps(gaps)

        top = repo.get_top_opportunities(CAMPAIGN_ID, "en", limit=3)
        assert len(top) == 3


# ---------------------------------------------------------------------------
# Summary persistence
# ---------------------------------------------------------------------------


class TestSummaryPersistence:
    """Cross-language summary save and load."""

    def test_save_summaries(self, tmp_path: Path) -> None:
        repo = FileGapMatrixRepo(tmp_path, "hairgenetix.com")

        summaries = [
            CrossLanguageSummaryRecord(
                tenant_id=TENANT_ID,
                campaign_id=CAMPAIGN_ID,
                keyword_id="kw_1",
                keyword_text="FUE vs DHI",
                is_universal_gap=True,
                languages_with_gap=["en", "de"],
                total_languages_analysed=2,
            ),
        ]
        saved = repo.save_summaries(summaries)
        assert saved == 1

        summary_file = tmp_path / "hairgenetix.com" / "cross_language_summary.json"
        assert summary_file.exists()
