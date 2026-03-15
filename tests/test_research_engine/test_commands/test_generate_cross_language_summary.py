"""Tests for F-006 GenerateCrossLanguageSummary command.

Covers: ATS-016 (via command), INT-003.
"""

from __future__ import annotations

import uuid
from typing import Any

from src.research_engine.commands.generate_cross_language_summary import (
    GenerateCrossLanguageSummaryCommand,
    generate_cross_language_summary,
)
from src.research_engine.models.content_gap import (
    ContentGapRecord,
    CoverageSource,
    GapType,
)
from src.research_engine.models.result import Err, Ok

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN_ID = "camp_1"


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------


class MockGapMatrixRepo:
    """In-memory repo for testing."""

    def __init__(self, gaps: list[ContentGapRecord] | None = None):
        self._gaps = gaps or []
        self.saved_summaries: list = []
        self.updated_gaps: list = []

    def get_gap_matrix(
        self, campaign_id: str, language: str, **kwargs: Any
    ) -> list[ContentGapRecord]:
        return [g for g in self._gaps if g.language == language]

    def save_summaries(self, summaries: list) -> int:
        self.saved_summaries.extend(summaries)
        return len(summaries)

    def save_gaps(self, gaps: list) -> int:
        self.updated_gaps.extend(gaps)
        return len(gaps)


class MockEvents:
    """Collects emitted events for verification."""

    def __init__(self) -> None:
        self.events: list = []

    def emit(self, event: Any) -> None:
        self.events.append(event)


def _make_gap(
    keyword_id: str,
    keyword_text: str,
    language: str,
    gap_type: GapType,
) -> ContentGapRecord:
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
    return ContentGapRecord(**kwargs)


# ---------------------------------------------------------------------------
# Happy path: cross-language summary produced
# ---------------------------------------------------------------------------


class TestCrossLanguageSummaryCommand:
    """Cross-language summary command orchestrates summariser + persist."""

    def test_universal_gap_summary(self) -> None:
        """Keyword is gap in all languages → universal gap summary."""
        gaps = [
            _make_gap("kw_1", "FUE vs DHI", "en", GapType.OWN_GAP),
            _make_gap("kw_1", "FUE vs DHI", "de", GapType.OWN_GAP),
        ]

        repo = MockGapMatrixRepo(gaps=gaps)
        events = MockEvents()

        cmd = GenerateCrossLanguageSummaryCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            languages=["en", "de"],
        )

        result = generate_cross_language_summary(
            cmd=cmd,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.universal_gap_count == 1
        assert output.languages_analysed == 2

        # Summaries persisted
        assert len(repo.saved_summaries) == 1

        # Event emitted
        assert len(events.events) == 1

    def test_mixed_gaps_and_coverage(self) -> None:
        """Mix of universal, language-specific, and full coverage."""
        gaps = [
            # kw_1: universal gap
            _make_gap("kw_1", "FUE", "en", GapType.OWN_GAP),
            _make_gap("kw_1", "FUE", "de", GapType.OWN_GAP),
            # kw_2: language-specific (DE only)
            _make_gap("kw_2", "Kosten", "de", GapType.OWN_GAP),
            _make_gap("kw_2", "Kosten", "en", GapType.OWN_COVERAGE),
            # kw_3: fully covered
            _make_gap("kw_3", "surgery", "en", GapType.OWN_COVERAGE),
            _make_gap("kw_3", "surgery", "de", GapType.OWN_COVERAGE),
        ]

        repo = MockGapMatrixRepo(gaps=gaps)
        events = MockEvents()

        cmd = GenerateCrossLanguageSummaryCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            languages=["en", "de"],
        )

        result = generate_cross_language_summary(
            cmd=cmd,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.universal_gap_count == 1
        assert output.total_summaries == 2  # kw_1 + kw_2

    def test_empty_gaps(self) -> None:
        """No gaps → no summaries."""
        repo = MockGapMatrixRepo(gaps=[])
        events = MockEvents()

        cmd = GenerateCrossLanguageSummaryCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            languages=["en"],
        )

        result = generate_cross_language_summary(
            cmd=cmd,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.universal_gap_count == 0
        assert output.total_summaries == 0


# ---------------------------------------------------------------------------
# Feature flag
# ---------------------------------------------------------------------------


class TestFeatureFlag:
    """Feature flag FEATURE_CONTENT_GAP checked at entry."""

    def test_feature_disabled(self) -> None:
        cmd = GenerateCrossLanguageSummaryCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            languages=["en"],
        )

        result = generate_cross_language_summary(
            cmd=cmd,
            repo=MockGapMatrixRepo(),
            emit_event=lambda e: None,
            feature_enabled=False,
        )

        assert isinstance(result, Err)
        assert "disabled" in result.error.lower()


# ---------------------------------------------------------------------------
# Output format
# ---------------------------------------------------------------------------


class TestOutputFormat:
    """INT-003: Output format consumable by downstream features."""

    def test_result_has_required_fields(self) -> None:
        repo = MockGapMatrixRepo(gaps=[])
        cmd = GenerateCrossLanguageSummaryCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            languages=["en"],
        )

        result = generate_cross_language_summary(
            cmd=cmd,
            repo=repo,
            emit_event=lambda e: None,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert hasattr(output, "universal_gap_count")
        assert hasattr(output, "languages_analysed")
        assert hasattr(output, "total_summaries")
        assert hasattr(output, "duration_seconds")
