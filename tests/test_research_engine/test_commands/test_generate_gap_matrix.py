"""Tests for F-006 GenerateGapMatrix command.

Covers: ATS-001, ATS-004, ATS-006, INT-001, INT-003.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from src.research_engine.commands.generate_gap_matrix import (
    GenerateGapMatrixCommand,
    generate_gap_matrix,
)
from src.research_engine.models.content_gap import (
    CompetitorEntry,
    CoverageSource,
    GapType,
    GscQueryData,
    KeywordInput,
    SerpEntry,
)
from src.research_engine.models.result import Err, Ok
from src.research_engine.scoring_config import ScoringConfig

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN_ID = "camp_1"


# ---------------------------------------------------------------------------
# Mock data sources
# ---------------------------------------------------------------------------


class MockGscAvailable:
    """GSC source that returns data for known keywords."""

    def __init__(self, data: dict[str, GscQueryData | None] | None = None):
        self._data = data or {}

    def get_coverage(self, keyword_text: str, language: str) -> GscQueryData | None:
        return self._data.get(keyword_text)

    def is_available(self) -> bool:
        return True


class MockGscUnavailable:
    """GSC source that is unavailable."""

    def get_coverage(self, keyword_text: str, language: str) -> GscQueryData | None:
        return None

    def is_available(self) -> bool:
        return False


@dataclass
class MockGapMatrixRepo:
    """In-memory gap matrix repo for testing."""

    saved_gaps: list = None  # type: ignore[assignment]
    saved_summaries: list = None  # type: ignore[assignment]

    def __post_init__(self) -> None:  # noqa: D105
        if self.saved_gaps is None:
            self.saved_gaps = []
        if self.saved_summaries is None:
            self.saved_summaries = []

    def save_gaps(self, gaps: list) -> int:
        self.saved_gaps.extend(gaps)
        return len(gaps)

    def save_summaries(self, summaries: list) -> int:
        self.saved_summaries.extend(summaries)
        return len(summaries)

    def get_gap_matrix(self, *args: Any, **kwargs: Any) -> list:
        return self.saved_gaps

    def get_top_opportunities(self, *args: Any, **kwargs: Any) -> list:
        return [
            g
            for g in self.saved_gaps
            if g.gap_type in (GapType.OWN_GAP, GapType.NEW_OPPORTUNITY)
        ]


class MockEvents:
    """Collects emitted events for verification."""

    def __init__(self) -> None:
        self.events: list = []

    def emit(self, event: Any) -> None:
        self.events.append(event)


# ---------------------------------------------------------------------------
# ATS-001: Happy path — GSC available, gap found
# ---------------------------------------------------------------------------


class TestHappyPathGscGap:
    """ATS-001: GSC available, keyword not covered → own_gap."""

    def test_gsc_gap_found(self) -> None:
        keywords = [
            KeywordInput(
                keyword_id="kw_1", keyword_text="FUE vs DHI", volume=1000, difficulty=40
            ),
        ]
        serp_data = {
            "kw_1": [
                SerpEntry(
                    url="https://competitor.com/fue",
                    domain="competitor.com",
                    position=3,
                    word_count=3200,
                ),
            ],
        }
        competitor_data = {
            "kw_1": [
                CompetitorEntry(
                    url="https://competitor.com/fue",
                    domain="competitor.com",
                    position=3,
                    word_count=3200,
                    depth_score=4,
                ),
            ],
        }
        gsc_source = MockGscAvailable(data={})  # No GSC data → gap

        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="hairgenetix.com",
            keywords=keywords,
            serp_data=serp_data,
            competitor_data=competitor_data,
        )

        repo = MockGapMatrixRepo()
        events = MockEvents()

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=gsc_source,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.own_gap_count == 1
        assert output.new_opportunity_count == 0
        assert output.coverage_source == "gsc"

        # Verify persisted
        assert len(repo.saved_gaps) == 1
        gap = repo.saved_gaps[0]
        assert gap.gap_type == GapType.OWN_GAP
        assert gap.keyword_id == "kw_1"
        assert gap.opportunity_score is not None
        assert gap.score_inputs is not None

        # Verify event emitted
        assert len(events.events) == 1

    def test_gsc_coverage_found(self) -> None:
        """GSC shows impressions → own_coverage."""
        keywords = [
            KeywordInput(
                keyword_id="kw_1",
                keyword_text="hair transplant",
                volume=5000,
                difficulty=60,
            ),
        ]
        gsc_source = MockGscAvailable(
            data={
                "hair transplant": GscQueryData(
                    keyword_text="hair transplant",
                    impressions=500,
                    clicks=30,
                    position=8.0,
                    page_url="/hair-transplant",
                ),
            }
        )

        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="hairgenetix.com",
            keywords=keywords,
            serp_data={},
            competitor_data={},
        )

        repo = MockGapMatrixRepo()
        events = MockEvents()

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=gsc_source,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.own_coverage_count == 1
        assert output.own_gap_count == 0


# ---------------------------------------------------------------------------
# ATS-004: No GSC fallback → SERP coverage
# ---------------------------------------------------------------------------


class TestSerpFallback:
    """ATS-004: GSC unavailable, SERP used for coverage check."""

    def test_serp_fallback_gap(self) -> None:
        keywords = [
            KeywordInput(
                keyword_id="kw_1",
                keyword_text="FUE recovery",
                volume=800,
                difficulty=30,
            ),
        ]
        serp_data = {
            "kw_1": [
                SerpEntry(
                    url="https://competitor.com/recovery",
                    domain="competitor.com",
                    position=2,
                ),
            ],
        }
        competitor_data = {
            "kw_1": [
                CompetitorEntry(
                    url="https://competitor.com/recovery",
                    domain="competitor.com",
                    position=2,
                    word_count=2500,
                ),
            ],
        }

        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="hairgenetix.com",
            keywords=keywords,
            serp_data=serp_data,
            competitor_data=competitor_data,
        )

        repo = MockGapMatrixRepo()
        events = MockEvents()

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=None,  # No GSC available
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.coverage_source == "serp_fallback"
        assert output.own_gap_count == 1

        gap = repo.saved_gaps[0]
        assert gap.coverage_source == CoverageSource.SERP_FALLBACK


# ---------------------------------------------------------------------------
# ATS-006: Missing competitor data handled gracefully
# ---------------------------------------------------------------------------


class TestMissingCompetitorData:
    """ATS-006: Competitor crawl_failed → partial_data flag set."""

    def test_all_competitors_crawl_failed(self) -> None:
        keywords = [
            KeywordInput(
                keyword_id="kw_1", keyword_text="hair care", volume=500, difficulty=20
            ),
        ]
        competitor_data = {
            "kw_1": [
                CompetitorEntry(
                    url="https://c1.com/p",
                    domain="c1.com",
                    position=1,
                    crawl_failed=True,
                ),
                CompetitorEntry(
                    url="https://c2.com/p",
                    domain="c2.com",
                    position=2,
                    crawl_failed=True,
                ),
            ],
        }

        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="hairgenetix.com",
            keywords=keywords,
            serp_data={},
            competitor_data=competitor_data,
        )

        repo = MockGapMatrixRepo()
        events = MockEvents()

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=None,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        gap = repo.saved_gaps[0]
        assert gap.partial_data is True
        assert gap.competitors_excluded == 2


# ---------------------------------------------------------------------------
# INT-001: Pipeline integration — F-004 + F-005 → F-006
# ---------------------------------------------------------------------------


class TestPipelineIntegration:
    """INT-001: SERP (F-004) + competitor (F-005) data feeds gap matrix."""

    def test_full_pipeline_flow(self) -> None:
        """Multiple keywords with different classifications."""
        keywords = [
            KeywordInput(
                keyword_id="kw_1", keyword_text="FUE vs DHI", volume=2000, difficulty=45
            ),
            KeywordInput(
                keyword_id="kw_2",
                keyword_text="scalp massage",
                volume=300,
                difficulty=10,
            ),
            KeywordInput(
                keyword_id="kw_3",
                keyword_text="hair transplant UK",
                volume=5000,
                difficulty=70,
            ),
        ]
        serp_data = {
            "kw_1": [
                SerpEntry(url="https://c1.com/fue", domain="c1.com", position=3),
            ],
            "kw_2": [],  # No SERP results → new opportunity
            "kw_3": [
                SerpEntry(
                    url="https://hairgenetix.com/uk",
                    domain="hairgenetix.com",
                    position=15,
                ),
                SerpEntry(
                    url="https://c1.com/uk",
                    domain="c1.com",
                    position=1,
                    word_count=4000,
                ),
            ],
        }
        competitor_data = {
            "kw_1": [
                CompetitorEntry(
                    url="https://c1.com/fue",
                    domain="c1.com",
                    position=3,
                    word_count=3200,
                ),
            ],
            "kw_2": [],
            "kw_3": [
                CompetitorEntry(
                    url="https://c1.com/uk",
                    domain="c1.com",
                    position=1,
                    word_count=4000,
                ),
            ],
        }

        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="hairgenetix.com",
            keywords=keywords,
            serp_data=serp_data,
            competitor_data=competitor_data,
        )

        repo = MockGapMatrixRepo()
        events = MockEvents()

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=None,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.total_keywords == 3
        assert (
            output.own_gap_count
            + output.own_coverage_count
            + output.thin_content_count
            + output.new_opportunity_count
            == 3
        )

        # Event emitted
        assert len(events.events) == 1


# ---------------------------------------------------------------------------
# Feature flag
# ---------------------------------------------------------------------------


class TestFeatureFlag:
    """Feature flag FEATURE_CONTENT_GAP checked at entry."""

    def test_feature_flag_disabled(self) -> None:
        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="hairgenetix.com",
            keywords=[],
            serp_data={},
            competitor_data={},
        )

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=None,
            repo=MockGapMatrixRepo(),
            emit_event=lambda e: None,
            feature_enabled=False,
        )

        assert isinstance(result, Err)
        assert "disabled" in result.error.lower()


# ---------------------------------------------------------------------------
# INT-003: Output consumable by F-007
# ---------------------------------------------------------------------------


class TestOutputFormat:
    """INT-003: Output format consumable by downstream features."""

    def test_result_has_required_fields(self) -> None:
        keywords = [
            KeywordInput(
                keyword_id="kw_1", keyword_text="test", volume=100, difficulty=10
            ),
        ]
        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="test.com",
            keywords=keywords,
            serp_data={},
            competitor_data={},
        )

        repo = MockGapMatrixRepo()
        events = MockEvents()

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=None,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value

        # Result must have all fields F-007 expects
        assert hasattr(output, "own_gap_count")
        assert hasattr(output, "thin_content_count")
        assert hasattr(output, "new_opportunity_count")
        assert hasattr(output, "own_coverage_count")
        assert hasattr(output, "coverage_source")
        assert hasattr(output, "duration_seconds")
        assert hasattr(output, "total_keywords")

    def test_empty_keywords_returns_zero_counts(self) -> None:
        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="test.com",
            keywords=[],
            serp_data={},
            competitor_data={},
        )

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=None,
            repo=MockGapMatrixRepo(),
            emit_event=lambda e: None,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.total_keywords == 0
        assert output.own_gap_count == 0


# ---------------------------------------------------------------------------
# Thin content detection in pipeline
# ---------------------------------------------------------------------------


class TestThinContentInPipeline:
    """Thin content detected when own coverage + rank 11-50 + low word count."""

    def test_thin_content_detected(self) -> None:
        """Ranking at #22 with 450 words vs 2800 avg → thin content."""
        keywords = [
            KeywordInput(
                keyword_id="kw_1",
                keyword_text="recovery week 3",
                volume=800,
                difficulty=30,
            ),
        ]
        serp_data = {
            "kw_1": [
                SerpEntry(
                    url="https://hairgenetix.com/recovery",
                    domain="hairgenetix.com",
                    position=22,
                    word_count=450,
                ),
                SerpEntry(
                    url="https://c1.com/recovery",
                    domain="c1.com",
                    position=1,
                    word_count=2800,
                ),
                SerpEntry(
                    url="https://c2.com/recovery",
                    domain="c2.com",
                    position=3,
                    word_count=3000,
                ),
                SerpEntry(
                    url="https://c3.com/recovery",
                    domain="c3.com",
                    position=5,
                    word_count=2600,
                ),
            ],
        }
        competitor_data = {
            "kw_1": [
                CompetitorEntry(
                    url="https://c1.com/recovery",
                    domain="c1.com",
                    position=1,
                    word_count=2800,
                ),
                CompetitorEntry(
                    url="https://c2.com/recovery",
                    domain="c2.com",
                    position=3,
                    word_count=3000,
                ),
                CompetitorEntry(
                    url="https://c3.com/recovery",
                    domain="c3.com",
                    position=5,
                    word_count=2600,
                ),
            ],
        }

        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="hairgenetix.com",
            keywords=keywords,
            serp_data=serp_data,
            competitor_data=competitor_data,
        )

        repo = MockGapMatrixRepo()
        events = MockEvents()

        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=None,
            repo=repo,
            emit_event=events.emit,
        )

        assert isinstance(result, Ok)
        output = result.value
        assert output.thin_content_count == 1

        gap = repo.saved_gaps[0]
        assert gap.gap_type == GapType.THIN_CONTENT
        assert gap.our_ranking_position == 22
        assert gap.thin_content_priority_score is not None


# ---------------------------------------------------------------------------
# Scoring: opportunity scores populated
# ---------------------------------------------------------------------------


class TestScoring:
    """Opportunity scores calculated and persisted."""

    def test_scores_populated_for_gaps(self) -> None:
        keywords = [
            KeywordInput(
                keyword_id="kw_1", keyword_text="FUE", volume=2000, difficulty=40
            ),
        ]
        competitor_data = {
            "kw_1": [
                CompetitorEntry(
                    url="https://c1.com/p", domain="c1.com", position=5, word_count=3000
                ),
            ],
        }

        cmd = GenerateGapMatrixCommand(
            tenant_id=TENANT_ID,
            campaign_id=CAMPAIGN_ID,
            language="en",
            user_domain="hairgenetix.com",
            keywords=keywords,
            serp_data={
                "kw_1": [SerpEntry(url="https://c1.com/p", domain="c1.com", position=5)]
            },
            competitor_data=competitor_data,
        )

        repo = MockGapMatrixRepo()
        result = generate_gap_matrix(
            cmd=cmd,
            config=ScoringConfig(),
            gsc_source=None,
            repo=repo,
            emit_event=lambda e: None,
        )

        assert isinstance(result, Ok)
        gap = repo.saved_gaps[0]
        assert gap.opportunity_score is not None
        assert gap.score_inputs is not None
        assert gap.score_rationale is not None
        assert 0.0 <= gap.opportunity_score <= 1.0
