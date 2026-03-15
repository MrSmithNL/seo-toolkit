"""Tests for ContentBriefBuilder.

Covers: ATS-001, ATS-002, ATS-003, PI-008, PI-012.
"""

from __future__ import annotations

import uuid

from src.research_engine.models.competitor import CompetitorBenchmark
from src.research_engine.models.content_brief import (
    ContentType,
    GapType,
    SearchIntent,
)
from src.research_engine.models.content_gap import (
    ContentGapRecord,
    CoverageSource,
    ScoreInputs,
)
from src.research_engine.models.content_gap import (
    GapType as CgGapType,
)
from src.research_engine.services.content_brief_builder import (
    _compute_recommended_word_count,
    _determine_include_faq,
    build_content_brief,
)

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _make_gap(
    gap_type: str = "own_gap",
    volume: int = 8100,
    difficulty: int = 32,
    score: float = 0.74,
    keyword: str = "hair transplant cost",
    language: str = "en",
    **overrides,
) -> ContentGapRecord:
    """Create a test gap record."""
    defaults = {
        "tenant_id": TENANT,
        "campaign_id": "camp_001",
        "keyword_id": "kw_001",
        "keyword_text": keyword,
        "language": language,
        "gap_type": CgGapType(gap_type),
        "coverage_source": CoverageSource.SERP_FALLBACK,
        "opportunity_score": score,
        "score_inputs": ScoreInputs(
            volume=volume,
            volume_normalised=0.5,
            difficulty=difficulty,
            difficulty_inverse_normalised=0.68,
            gap_score=1.0,
        ),
    }
    if gap_type == "thin_content":
        defaults.update(
            {
                "our_ranking_position": 18,
                "our_page_url": "https://example.com/page",
                "our_word_count": 420,
            }
        )
    defaults.update(overrides)
    return ContentGapRecord(**defaults)


def _make_benchmarks(count: int = 3) -> list[CompetitorBenchmark]:
    """Create test competitor benchmarks."""
    return [
        CompetitorBenchmark(
            url=f"https://comp{i}.com/page",
            domain=f"comp{i}.com",
            serp_position=i + 1,
            word_count=2000 + i * 200,
            depth_score=3 + (i % 3),
            h2_texts=["Heading A", "Heading B", "Heading C"],
            schema_types=["Article", "FAQPage"],
            has_faq_section=True,
        )
        for i in range(count)
    ]


class TestComputeRecommendedWordCount:
    """recommended_word_count = competitor_avg * 1.1, rounded to 100."""

    def test_standard_calculation(self) -> None:
        assert _compute_recommended_word_count(2400) == 2700  # 2640 → ceil to 2700

    def test_zero_competitor_avg(self) -> None:
        assert _compute_recommended_word_count(0) == 300

    def test_small_competitor_avg(self) -> None:
        assert _compute_recommended_word_count(100) == 200  # 110 → ceil to 200


class TestDetermineIncludeFaq:
    """FAQ if competitors have FAQ OR informational intent."""

    def test_competitors_have_faq(self) -> None:
        assert _determine_include_faq(True, SearchIntent.COMMERCIAL) is True

    def test_informational_intent(self) -> None:
        assert _determine_include_faq(False, SearchIntent.INFORMATIONAL) is True

    def test_neither(self) -> None:
        assert _determine_include_faq(False, SearchIntent.TRANSACTIONAL) is False


class TestBuildContentBrief:
    """ATS-001: Builds a valid ContentBrief from pipeline data."""

    def test_happy_path(self) -> None:
        """Gap record + benchmarks → valid ContentBrief."""
        gap = _make_gap()
        benchmarks = _make_benchmarks()

        brief = build_content_brief(
            gap=gap,
            tenant_id=TENANT,
            campaign_id="camp_001",
            competitor_benchmarks=benchmarks,
            search_intent=SearchIntent.COMMERCIAL,
            topic_cluster="Hair Transplant Costs",
            content_type=ContentType.COMPARISON,
            recommended_headings=["Cost overview", "FUE vs DHI"],
            suggested_publish_date="2026-03-16",
        )

        assert brief.target_keyword == "hair transplant cost"
        assert brief.status.value == "pending_review"
        assert brief.opportunity_score == 0.74
        assert brief.gap_type == GapType.OWN_GAP
        assert brief.include_faq is True  # competitors have FAQ
        assert brief.recommended_word_count > 0  # PI-008
        assert brief.competitor_avg_word_count > 0

    def test_thin_content_has_existing_url(self) -> None:
        """PI-012: thin_content → existing_page_url non-null."""
        gap = _make_gap(gap_type="thin_content")
        benchmarks = _make_benchmarks()

        brief = build_content_brief(
            gap=gap,
            tenant_id=TENANT,
            campaign_id="camp_001",
            competitor_benchmarks=benchmarks,
            search_intent=SearchIntent.INFORMATIONAL,
        )

        assert brief.gap_type == GapType.THIN_CONTENT
        assert brief.existing_page_url is not None

    def test_own_gap_no_existing_url(self) -> None:
        """own_gap should have None existing_page_url."""
        gap = _make_gap(gap_type="own_gap")
        benchmarks = _make_benchmarks()

        brief = build_content_brief(
            gap=gap,
            tenant_id=TENANT,
            campaign_id="camp_001",
            competitor_benchmarks=benchmarks,
            search_intent=SearchIntent.COMMERCIAL,
        )

        assert brief.existing_page_url is None

    def test_schema_types_from_competitors(self) -> None:
        """ATS-003: Competitors with Article + FAQPage → schema types include both."""
        gap = _make_gap()
        benchmarks = _make_benchmarks()

        brief = build_content_brief(
            gap=gap,
            tenant_id=TENANT,
            campaign_id="camp_001",
            competitor_benchmarks=benchmarks,
            search_intent=SearchIntent.COMMERCIAL,
        )

        assert "Article" in brief.competitor_schema_types
        assert "FAQPage" in brief.competitor_schema_types
