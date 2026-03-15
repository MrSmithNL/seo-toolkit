"""Tests for F-006 CoverageClassifier.

Covers: ATS-001, ATS-003, ATS-004, ATS-005, PI-007.
"""

from __future__ import annotations

from src.research_engine.models.content_gap import (
    CompetitorEntry,
    CoverageSource,
    GapType,
    GscQueryData,
    SerpEntry,
)
from src.research_engine.services.coverage_classifier import (
    classify_coverage,
)

# ---------------------------------------------------------------------------
# Mock GSC source
# ---------------------------------------------------------------------------


class MockGscSource:
    """Mock GSC coverage source for testing."""

    def __init__(
        self,
        data: dict[str, GscQueryData] | None = None,
        available: bool = True,
    ) -> None:
        self._data = data or {}
        self._available = available

    def is_available(self) -> bool:
        return self._available

    def get_coverage(self, keyword_text: str, language: str) -> GscQueryData | None:
        return self._data.get(keyword_text)


class MockGscUnavailable:
    """Mock GSC source that's unavailable."""

    def is_available(self) -> bool:
        return False

    def get_coverage(self, keyword_text: str, language: str) -> GscQueryData | None:
        return None


# ---------------------------------------------------------------------------
# ATS-001: Happy path — GSC available, gap found
# ---------------------------------------------------------------------------


class TestGscAvailableGapFound:
    """ATS-001: GSC available, keyword not covered, competitor ranks."""

    def test_own_gap_with_gsc(self) -> None:
        gsc = MockGscSource(data={})  # No impressions for this keyword
        competitors = [
            CompetitorEntry(
                url="https://competitor.de/fue-vs-dhi",
                domain="competitor.de",
                position=3,
                word_count=3200,
                depth_score=4,
            ),
        ]

        result = classify_coverage(
            keyword_text="FUE vs DHI",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=[],
            competitors=competitors,
            gsc_source=gsc,
        )

        assert result.gap_type == GapType.OWN_GAP
        assert result.coverage_source == CoverageSource.GSC
        assert result.gsc_impressions == 0

    def test_own_coverage_with_gsc(self) -> None:
        gsc = MockGscSource(
            data={
                "hair transplant cost": GscQueryData(
                    keyword_text="hair transplant cost",
                    impressions=500,
                    clicks=20,
                    position=8.3,
                    page_url="/hair-transplant-cost",
                ),
            }
        )

        result = classify_coverage(
            keyword_text="hair transplant cost",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=[],
            competitors=[],
            gsc_source=gsc,
        )

        assert result.gap_type == GapType.OWN_COVERAGE
        assert result.coverage_source == CoverageSource.GSC
        assert result.gsc_impressions == 500
        assert result.our_ranking_position == 8
        assert result.our_page_url == "/hair-transplant-cost"


# ---------------------------------------------------------------------------
# ATS-003: No competitor, no GSC → new_opportunity
# ---------------------------------------------------------------------------


class TestNewOpportunity:
    """ATS-003: No competitor in top 10, no GSC impressions."""

    def test_new_opportunity_with_gsc(self) -> None:
        gsc = MockGscSource(data={})

        result = classify_coverage(
            keyword_text="post-FUE scalp massage timing",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=[],
            competitors=[],
            gsc_source=gsc,
        )

        assert result.gap_type == GapType.NEW_OPPORTUNITY
        assert result.coverage_source == CoverageSource.GSC

    def test_new_opportunity_serp_fallback(self) -> None:
        result = classify_coverage(
            keyword_text="post-FUE scalp massage timing",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=[],
            competitors=[],
            gsc_source=None,
        )

        assert result.gap_type == GapType.NEW_OPPORTUNITY
        assert result.coverage_source == CoverageSource.SERP_FALLBACK


# ---------------------------------------------------------------------------
# ATS-004: No GSC fallback → SERP-based coverage
# ---------------------------------------------------------------------------


class TestSerpFallback:
    """ATS-004: GSC unavailable, falls back to SERP-based coverage."""

    def test_serp_fallback_domain_found(self) -> None:
        serp_results = [
            SerpEntry(
                url="https://competitor.de/page",
                domain="competitor.de",
                position=1,
            ),
            SerpEntry(
                url="https://hairgenetix.com/our-page",
                domain="hairgenetix.com",
                position=5,
                word_count=1200,
            ),
        ]

        result = classify_coverage(
            keyword_text="hair transplant Turkey",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=serp_results,
            competitors=[],
            gsc_source=None,
        )

        assert result.gap_type == GapType.OWN_COVERAGE
        assert result.coverage_source == CoverageSource.SERP_FALLBACK
        assert result.our_ranking_position == 5
        assert result.our_page_url == "https://hairgenetix.com/our-page"

    def test_serp_fallback_domain_not_found(self) -> None:
        serp_results = [
            SerpEntry(
                url="https://competitor.de/page",
                domain="competitor.de",
                position=1,
            ),
        ]
        competitors = [
            CompetitorEntry(
                url="https://competitor.de/page",
                domain="competitor.de",
                position=1,
            ),
        ]

        result = classify_coverage(
            keyword_text="hair transplant Turkey",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=serp_results,
            competitors=competitors,
            gsc_source=None,
        )

        assert result.gap_type == GapType.OWN_GAP
        assert result.coverage_source == CoverageSource.SERP_FALLBACK

    def test_gsc_unavailable_triggers_fallback(self) -> None:
        """GSC source exists but is_available() returns False."""
        gsc = MockGscUnavailable()
        serp_results = [
            SerpEntry(
                url="https://hairgenetix.com/page",
                domain="hairgenetix.com",
                position=8,
            ),
        ]

        result = classify_coverage(
            keyword_text="test keyword",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=serp_results,
            competitors=[],
            gsc_source=gsc,
        )

        assert result.gap_type == GapType.OWN_COVERAGE
        assert result.coverage_source == CoverageSource.SERP_FALLBACK


# ---------------------------------------------------------------------------
# ATS-005: All topics covered — no gaps
# ---------------------------------------------------------------------------


class TestAllTopicsCovered:
    """ATS-005: User site covers every keyword."""

    def test_all_covered_via_gsc(self) -> None:
        gsc = MockGscSource(
            data={
                "keyword1": GscQueryData(keyword_text="keyword1", impressions=100),
                "keyword2": GscQueryData(keyword_text="keyword2", impressions=50),
            }
        )

        results = []
        for kw in ["keyword1", "keyword2"]:
            r = classify_coverage(
                keyword_text=kw,
                language="en",
                user_domain="hairgenetix.com",
                serp_results=[],
                competitors=[],
                gsc_source=gsc,
            )
            results.append(r)

        own_gaps = [r for r in results if r.gap_type == GapType.OWN_GAP]
        assert len(own_gaps) == 0


# ---------------------------------------------------------------------------
# PI-007: Per-language independence
# ---------------------------------------------------------------------------


class TestPerLanguageIndependence:
    """PI-007: Gap rows for DE and EN computed independently."""

    def test_different_languages_different_results(self) -> None:
        gsc_en = MockGscSource(
            data={
                "hair transplant cost": GscQueryData(
                    keyword_text="hair transplant cost",
                    impressions=200,
                ),
            }
        )
        gsc_de = MockGscSource(data={})
        competitors_de = [
            CompetitorEntry(
                url="https://de-competitor.de/kosten",
                domain="de-competitor.de",
                position=2,
            ),
        ]

        result_en = classify_coverage(
            keyword_text="hair transplant cost",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=[],
            competitors=[],
            gsc_source=gsc_en,
        )

        result_de = classify_coverage(
            keyword_text="hair transplant cost",
            language="de",
            user_domain="hairgenetix.com",
            serp_results=[],
            competitors=competitors_de,
            gsc_source=gsc_de,
        )

        assert result_en.gap_type == GapType.OWN_COVERAGE
        assert result_de.gap_type == GapType.OWN_GAP


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge case handling."""

    def test_crawl_failed_competitor_excluded(self) -> None:
        """Competitors with crawl_failed should not count as top-10 presence."""
        competitors = [
            CompetitorEntry(
                url="https://competitor.de/page",
                domain="competitor.de",
                position=3,
                crawl_failed=True,
            ),
        ]
        gsc = MockGscSource(data={})

        result = classify_coverage(
            keyword_text="test",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=[],
            competitors=competitors,
            gsc_source=gsc,
        )

        # Crawl-failed competitors don't count → new_opportunity not own_gap
        assert result.gap_type == GapType.NEW_OPPORTUNITY

    def test_domain_matching_case_insensitive(self) -> None:
        serp_results = [
            SerpEntry(
                url="https://HAIRGENETIX.COM/page",
                domain="HAIRGENETIX.COM",
                position=3,
            ),
        ]

        result = classify_coverage(
            keyword_text="test",
            language="en",
            user_domain="hairgenetix.com",
            serp_results=serp_results,
            competitors=[],
            gsc_source=None,
        )

        assert result.gap_type == GapType.OWN_COVERAGE
