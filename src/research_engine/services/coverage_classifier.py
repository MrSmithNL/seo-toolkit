"""Coverage classifier for F-006 Content Gap Identification.

Classifies keywords into own_gap / own_coverage / new_opportunity
using GSC data (primary) or SERP fallback (ADR-F006-001).

TypeScript equivalent: modules/content-engine/research/services/coverage-classifier.ts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from src.research_engine.models.content_gap import (
    CompetitorEntry,
    CoverageSource,
    GapType,
    GscQueryData,
    SerpEntry,
)

if TYPE_CHECKING:
    from src.research_engine.ports.coverage_data_source import CoverageDataSource

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CoverageResult:
    """Result of classifying a keyword's coverage.

    Attributes:
        gap_type: Classification (own_gap, own_coverage, new_opportunity).
        coverage_source: Whether GSC or SERP fallback was used.
        our_ranking_position: Our position if ranking (None if not).
        our_page_url: Our page URL if ranking (None if not).
        gsc_impressions: GSC impression count (None if GSC unavailable).
    """

    gap_type: GapType
    coverage_source: CoverageSource
    our_ranking_position: int | None = None
    our_page_url: str | None = None
    gsc_impressions: int | None = None


def classify_coverage(
    keyword_text: str,
    language: str,
    user_domain: str,
    serp_results: list[SerpEntry],
    competitors: list[CompetitorEntry],
    gsc_source: CoverageDataSource | None = None,
) -> CoverageResult:
    """Classify a keyword's coverage for the user's site.

    Logic (ADR-F006-001):
    1. If GSC available: impressions > 0 → own_coverage.
       No impressions + competitor ranks → own_gap.
       No impressions + no competitor → new_opportunity.
    2. If GSC unavailable: check SERP top-50 for user domain.
       Present → own_coverage. Absent + competitor → own_gap.
       Absent + no competitor → new_opportunity.

    Args:
        keyword_text: The keyword to classify.
        language: BCP 47 language code.
        user_domain: The user's domain (e.g., 'hairgenetix.com').
        serp_results: SERP results from F-004 for this keyword.
        competitors: Competitor data from F-005.
        gsc_source: Optional GSC data source (None if unavailable).

    Returns:
        CoverageResult with classification and metadata.
    """
    # Check for competitors in top 10
    has_competitor_top_10 = any(
        c.position <= 10 for c in competitors if not c.crawl_failed
    )

    # Try GSC first (primary source)
    if gsc_source is not None and gsc_source.is_available():
        gsc_data = gsc_source.get_coverage(keyword_text, language)
        return _classify_from_gsc(gsc_data, has_competitor_top_10)

    # Fallback to SERP-based coverage
    return _classify_from_serp(
        user_domain=user_domain,
        serp_results=serp_results,
        has_competitor_top_10=has_competitor_top_10,
    )


def _classify_from_gsc(
    gsc_data: GscQueryData | None,
    has_competitor_top_10: bool,
) -> CoverageResult:
    """Classify using GSC data (primary source).

    Args:
        gsc_data: GSC query data, or None if no impressions.
        has_competitor_top_10: Whether any competitor ranks in top 10.

    Returns:
        CoverageResult with GSC-based classification.
    """
    if gsc_data is not None and gsc_data.impressions > 0:
        position = int(gsc_data.position) if gsc_data.position is not None else None
        return CoverageResult(
            gap_type=GapType.OWN_COVERAGE,
            coverage_source=CoverageSource.GSC,
            our_ranking_position=position,
            our_page_url=gsc_data.page_url,
            gsc_impressions=gsc_data.impressions,
        )

    # No GSC impressions
    if has_competitor_top_10:
        return CoverageResult(
            gap_type=GapType.OWN_GAP,
            coverage_source=CoverageSource.GSC,
            gsc_impressions=0,
        )

    return CoverageResult(
        gap_type=GapType.NEW_OPPORTUNITY,
        coverage_source=CoverageSource.GSC,
        gsc_impressions=0,
    )


def _classify_from_serp(
    user_domain: str,
    serp_results: list[SerpEntry],
    has_competitor_top_10: bool,
) -> CoverageResult:
    """Classify using SERP fallback (top-50 check).

    Args:
        user_domain: User's domain to look for in SERP results.
        serp_results: Top-50 SERP results.
        has_competitor_top_10: Whether any competitor ranks in top 10.

    Returns:
        CoverageResult with SERP-based classification.
    """
    # Normalise user domain for matching
    user_domain_clean = user_domain.lower().strip().rstrip("/")

    # Find user domain in SERP results
    for entry in serp_results:
        entry_domain = entry.domain.lower().strip().rstrip("/")
        if entry_domain == user_domain_clean:
            return CoverageResult(
                gap_type=GapType.OWN_COVERAGE,
                coverage_source=CoverageSource.SERP_FALLBACK,
                our_ranking_position=entry.position,
                our_page_url=entry.url,
            )

    # Not found in SERP
    if has_competitor_top_10:
        return CoverageResult(
            gap_type=GapType.OWN_GAP,
            coverage_source=CoverageSource.SERP_FALLBACK,
        )

    return CoverageResult(
        gap_type=GapType.NEW_OPPORTUNITY,
        coverage_source=CoverageSource.SERP_FALLBACK,
    )
