"""Pipeline orchestrator for F-006 Content Gap Matrix generation.

Orchestrates the full gap matrix flow per language:
  classify coverage → detect thin content → score opportunities →
  persist results → emit event.

Zero LLM calls — F-006 is pure computation over F-004/F-005 data.

TypeScript equivalent:
  modules/content-engine/research/commands/generate-gap-matrix.ts
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from src.research_engine.events.gap_events import (
    GapMatrixGeneratedEvent,
)
from src.research_engine.models.content_gap import (
    CompetitorEntry,
    ContentGapRecord,
    CoverageSource,
    GapType,
    KeywordInput,
    SerpEntry,
)
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.scoring_config import ScoringConfig
from src.research_engine.services.coverage_classifier import (
    CoverageResult,
    classify_coverage,
)
from src.research_engine.services.opportunity_scorer import (
    calculate_opportunity_score,
    calculate_thin_content_priority_score,
)
from src.research_engine.services.thin_content_detector import (
    detect_thin_content,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Command + Result data classes
# ---------------------------------------------------------------------------


@dataclass
class GenerateGapMatrixCommand:
    """Input for per-language gap matrix generation.

    Attributes:
        tenant_id: Tenant identifier.
        campaign_id: Campaign identifier.
        language: BCP 47 language code.
        user_domain: User's own domain.
        keywords: Keywords from F-001 to analyse.
        serp_data: SERP results per keyword_id from F-004.
        competitor_data: Competitor data per keyword_id from F-005.
        pipeline_run_id: Optional pipeline run ID for tracking.
    """

    tenant_id: uuid.UUID
    campaign_id: str
    language: str
    user_domain: str
    keywords: list[KeywordInput]
    serp_data: dict[str, list[SerpEntry]]
    competitor_data: dict[str, list[CompetitorEntry]]
    pipeline_run_id: str | None = None


@dataclass
class GenerateGapMatrixResult:
    """Output from gap matrix generation.

    Attributes:
        total_keywords: Total keywords processed.
        own_gap_count: Keywords classified as own_gap.
        thin_content_count: Keywords classified as thin_content.
        new_opportunity_count: Keywords classified as new_opportunity.
        own_coverage_count: Keywords classified as own_coverage.
        coverage_source: Primary coverage source used.
        duration_seconds: Wall-clock time for generation.
    """

    total_keywords: int
    own_gap_count: int
    thin_content_count: int
    new_opportunity_count: int
    own_coverage_count: int
    coverage_source: str
    duration_seconds: float


# ---------------------------------------------------------------------------
# Helpers (extracted to reduce cyclomatic complexity)
# ---------------------------------------------------------------------------


@dataclass
class _CompetitorStats:
    """Aggregated competitor statistics for a keyword."""

    best_position: int | None = None
    best_url: str | None = None
    avg_word_count: int | None = None
    avg_depth: float | None = None
    valid_count: int = 0
    excluded_count: int = 0
    partial_data: bool = False


def _compute_competitor_stats(
    competitors: list[CompetitorEntry],
) -> _CompetitorStats:
    """Aggregate competitor statistics for a keyword."""
    excluded = sum(1 for c in competitors if c.crawl_failed)
    valid = [c for c in competitors if not c.crawl_failed]
    stats = _CompetitorStats(
        valid_count=len(valid),
        excluded_count=excluded,
        partial_data=excluded > 0 and len(valid) == 0,
    )

    if not valid:
        return stats

    best = min(valid, key=lambda c: c.position)
    stats.best_position = best.position
    stats.best_url = best.url

    wc = [c.word_count for c in valid if c.word_count]
    if wc:
        stats.avg_word_count = sum(wc) // len(wc)

    depths = [c.depth_score for c in valid if c.depth_score]
    if depths:
        stats.avg_depth = round(sum(depths) / len(depths), 1)

    return stats


def _check_thin_content(
    coverage: CoverageResult,
    serp_results: list[SerpEntry],
    competitors: list[CompetitorEntry],
    user_domain: str,
    config: ScoringConfig,
) -> tuple[GapType, int | None, str | None, int | None, float | None]:
    """Check for thin content when we have coverage.

    Returns:
        Tuple of (gap_type, our_word_count, rationale,
                  word_count_gap, thin_priority_score).
    """
    our_position = coverage.our_ranking_position
    if coverage.gap_type != GapType.OWN_COVERAGE or our_position is None:
        return coverage.gap_type, None, None, None, None

    # Find our word count from SERP data
    our_word_count: int | None = None
    for entry in serp_results:
        if entry.domain.lower() == user_domain.lower():
            our_word_count = entry.word_count
            break

    thin_result = detect_thin_content(
        our_ranking_position=our_position,
        our_word_count=our_word_count,
        competitors=competitors,
        config=config,
    )

    if not thin_result.is_thin:
        return GapType.OWN_COVERAGE, our_word_count, None, None, None

    max_wc_gap = thin_result.word_count_gap or 1
    thin_score = calculate_thin_content_priority_score(
        current_position=our_position,
        our_word_count=our_word_count or 0,
        competitor_avg_word_count=thin_result.competitor_avg_word_count,
        max_word_count_gap=max_wc_gap,
        config=config,
    )

    return (
        GapType.THIN_CONTENT,
        our_word_count,
        thin_score.rationale,
        thin_result.word_count_gap,
        thin_score.score,
    )


def _build_gap_record(  # noqa: PLR0913
    cmd: GenerateGapMatrixCommand,
    kw: KeywordInput,
    gap_type: GapType,
    coverage: CoverageResult,
    stats: _CompetitorStats,
    our_word_count: int | None,
    thin_rationale: str | None,
    word_count_gap: int | None,
    thin_priority: float | None,
    opportunity_score: float | None,
    score_rationale: str | None,
    score_inputs: Any,
) -> ContentGapRecord:
    """Build a ContentGapRecord from processed keyword data."""
    kwargs: dict[str, Any] = {
        "tenant_id": cmd.tenant_id,
        "campaign_id": cmd.campaign_id,
        "keyword_id": kw.keyword_id,
        "keyword_text": kw.keyword_text,
        "language": cmd.language,
        "gap_type": gap_type,
        "coverage_source": CoverageSource(coverage.coverage_source.value),
        "our_ranking_position": coverage.our_ranking_position,
        "our_page_url": coverage.our_page_url,
        "our_word_count": our_word_count,
        "gsc_impressions": coverage.gsc_impressions,
        "competitor_best_position": stats.best_position,
        "competitor_best_url": stats.best_url,
        "competitor_avg_word_count": stats.avg_word_count,
        "competitor_avg_depth_score": stats.avg_depth,
        "competitors_analysed": stats.valid_count,
        "competitors_excluded": stats.excluded_count,
        "word_count_gap": word_count_gap,
        "thin_content_rationale": thin_rationale,
        "opportunity_score": opportunity_score,
        "thin_content_priority_score": thin_priority,
        "score_rationale": score_rationale,
        "score_inputs": score_inputs,
        "partial_data": stats.partial_data,
        "pipeline_run_id": cmd.pipeline_run_id,
    }

    if stats.partial_data:
        kwargs["partial_data_reason"] = (
            f"{stats.excluded_count} competitor(s) crawl failed"
        )

    return ContentGapRecord(**kwargs)


_GAP_TYPE_COUNTS = {
    GapType.OWN_GAP: "own_gap_count",
    GapType.THIN_CONTENT: "thin_content_count",
    GapType.NEW_OPPORTUNITY: "new_opportunity_count",
    GapType.OWN_COVERAGE: "own_coverage_count",
}


# ---------------------------------------------------------------------------
# Command handler
# ---------------------------------------------------------------------------


def generate_gap_matrix(
    cmd: GenerateGapMatrixCommand,
    config: ScoringConfig,
    gsc_source: Any | None,
    repo: Any,
    emit_event: Callable,
    feature_enabled: bool = True,
) -> Result[GenerateGapMatrixResult, str]:
    """Execute gap matrix generation for a single language.

    Steps:
    1. Feature flag check
    2. For each keyword: classify → thin detect → score → build record
    3. Persist all gap records
    4. Emit GapMatrixGenerated event

    Args:
        cmd: Generation command with keyword + SERP + competitor data.
        config: Scoring configuration.
        gsc_source: Optional GSC data source (None if unavailable).
        repo: GapMatrixPort implementation.
        emit_event: Event emission callable.
        feature_enabled: Feature flag for content gap (default True).

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    if not feature_enabled:
        return Err("Feature flag FEATURE_CONTENT_GAP is disabled")

    start_time = time.monotonic()

    # Determine coverage source
    coverage_source_str = "gsc"
    if gsc_source is None or not gsc_source.is_available():
        coverage_source_str = "serp_fallback"

    # Find max volume for normalisation
    max_volume = max((kw.volume for kw in cmd.keywords), default=1) or 1

    counts: dict[str, int] = {v: 0 for v in _GAP_TYPE_COUNTS.values()}
    gap_records: list[ContentGapRecord] = []

    for kw in cmd.keywords:
        serp_results = cmd.serp_data.get(kw.keyword_id, [])
        competitors = cmd.competitor_data.get(kw.keyword_id, [])

        coverage = classify_coverage(
            keyword_text=kw.keyword_text,
            language=cmd.language,
            user_domain=cmd.user_domain,
            serp_results=serp_results,
            competitors=competitors,
            gsc_source=gsc_source,
        )

        stats = _compute_competitor_stats(competitors)

        # Thin content check
        gap_type, our_wc, thin_rat, wc_gap, thin_pri = _check_thin_content(
            coverage, serp_results, competitors, cmd.user_domain, config
        )

        # Opportunity scoring for gaps
        opp_score: float | None = None
        score_rat: str | None = None
        score_inp = None
        if gap_type in (GapType.OWN_GAP, GapType.NEW_OPPORTUNITY):
            opp = calculate_opportunity_score(
                volume=kw.volume,
                difficulty=kw.difficulty,
                competitor_best_position=stats.best_position,
                max_volume=max_volume,
                is_universal_gap=False,
                config=config,
            )
            opp_score, score_rat, score_inp = opp.score, opp.rationale, opp.inputs

        record = _build_gap_record(
            cmd,
            kw,
            gap_type,
            coverage,
            stats,
            our_wc,
            thin_rat,
            wc_gap,
            thin_pri,
            opp_score,
            score_rat,
            score_inp,
        )
        gap_records.append(record)
        counts[_GAP_TYPE_COUNTS[gap_type]] += 1

    # Persist
    if gap_records:
        repo.save_gaps(gap_records)

    duration = round(time.monotonic() - start_time, 2)

    # Emit event
    event = GapMatrixGeneratedEvent(
        tenant_id=cmd.tenant_id,
        campaign_id=cmd.campaign_id,
        language=cmd.language,
        own_gap_count=counts["own_gap_count"],
        thin_content_count=counts["thin_content_count"],
        new_opportunity_count=counts["new_opportunity_count"],
        own_coverage_count=counts["own_coverage_count"],
        coverage_source=coverage_source_str,
        duration_seconds=duration,
    )
    emit_event(event)

    logger.info(
        "Gap matrix generated: lang=%s keywords=%d gaps=%d thin=%d "
        "new_opp=%d covered=%d dur=%.1fs",
        cmd.language,
        len(cmd.keywords),
        counts["own_gap_count"],
        counts["thin_content_count"],
        counts["new_opportunity_count"],
        counts["own_coverage_count"],
        duration,
    )

    return Ok(
        GenerateGapMatrixResult(
            total_keywords=len(cmd.keywords),
            own_gap_count=counts["own_gap_count"],
            thin_content_count=counts["thin_content_count"],
            new_opportunity_count=counts["new_opportunity_count"],
            own_coverage_count=counts["own_coverage_count"],
            coverage_source=coverage_source_str,
            duration_seconds=duration,
        )
    )
