"""Pipeline orchestrator for F-004 SERP Analysis.

Orchestrates the full SERP analysis flow: check cache -> check rate limiter
-> fetch SERP data via adapter -> detect features -> persist snapshot -> emit events.

Includes both single-keyword (AnalyseSerpCommand) and batch
(BatchAnalyseSerpCommand) commands.

TypeScript equivalent: modules/content-engine/research/commands/analyse-serp.ts
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field

from src.research_engine.config import ResearchConfig
from src.research_engine.events.serp_events import (
    SerpAnalysisCompletedEvent,
    SerpDailyLimitReachedEvent,
    emit_serp_event,
)
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.models.serp import (
    ApiSource,
    ContentType,
    SerpFeatures,
    SerpResult,
    SerpSnapshot,
)
from src.research_engine.ports.serp_data_source import SerpDataSource
from src.research_engine.ports.serp_snapshot_port import SerpSnapshotPort
from src.research_engine.services.serp_feature_detector import SerpFeatureDetector
from src.research_engine.services.serp_rate_limiter import SerpRateLimiter

logger = logging.getLogger(__name__)

# DataForSEO cost per request (approximate)
_COST_PER_REQUEST_USD = 0.0006


# ---------------------------------------------------------------------------
# Command + Result data classes
# ---------------------------------------------------------------------------


@dataclass
class AnalyseSerpCommand:
    """Input for a single SERP analysis.

    Attributes:
        tenant_id: Tenant identifier.
        keyword_id: Keyword record ID (from F-001).
        keyword_text: The search query text.
        language: BCP 47 language code.
        country: ISO 3166-1 country code.
        pipeline_run_id: Optional pipeline run ID for batch tracking.
        force_refresh: Bypass cache TTL.
    """

    tenant_id: uuid.UUID
    keyword_id: str
    keyword_text: str
    language: str
    country: str
    pipeline_run_id: str | None = None
    force_refresh: bool = False


@dataclass
class AnalyseSerpResult:
    """Output from a single SERP analysis.

    Attributes:
        snapshot_id: The persisted snapshot ID.
        result_count: Number of organic results.
        serp_features: Detected SERP features.
        from_cache: Whether the snapshot was served from cache.
        cost_estimate_usd: Estimated cost for this request.
        warnings: Warning flags (e.g., ai_overview_detected).
    """

    snapshot_id: str
    result_count: int
    serp_features: SerpFeatures
    from_cache: bool
    cost_estimate_usd: str
    warnings: list[str] = field(default_factory=list)


@dataclass
class BatchAnalyseSerpCommand:
    """Input for batch SERP analysis.

    Attributes:
        tenant_id: Tenant identifier.
        keywords: Keyword dicts with keyword_id, keyword_text, language, country.
        pipeline_run_id: Pipeline run ID for tracking.
    """

    tenant_id: uuid.UUID
    keywords: list[dict[str, str]]
    pipeline_run_id: str


@dataclass
class BatchAnalyseSerpResult:
    """Output from batch SERP analysis.

    Attributes:
        completed: Total keywords processed (fresh + cached).
        cached: Keywords served from cache.
        failed: Keywords that failed.
        queued_for_tomorrow: Keywords queued due to daily limit.
        snapshots: Individual snapshot results.
        errors: List of error dicts with keyword_id and error message.
    """

    completed: int
    cached: int
    failed: int
    queued_for_tomorrow: int
    snapshots: list[AnalyseSerpResult]
    errors: list[dict[str, str]]


# ---------------------------------------------------------------------------
# Single keyword analysis
# ---------------------------------------------------------------------------


def analyse_serp(
    cmd: AnalyseSerpCommand,
    config: ResearchConfig,
    source: SerpDataSource,
    rate_limiter: SerpRateLimiter,
    repo: SerpSnapshotPort,
) -> Result[AnalyseSerpResult, str]:
    """Execute SERP analysis for a single keyword.

    Steps:
    1. Feature flag check
    2. Cache check (serve from cache if within TTL)
    3. Rate limiter check
    4. Fetch SERP data via adapter
    5. Detect features + generate warnings
    6. Persist snapshot + results
    7. Emit event

    Args:
        cmd: Analysis command with keyword details.
        config: Research engine configuration.
        source: SERP data source adapter.
        rate_limiter: Per-source daily rate limiter.
        repo: Snapshot storage adapter.

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    start_time = time.monotonic()

    # Step 1: Feature flag
    if not config.feature_serp_analysis:
        return Err("Feature flag FEATURE_SERP_ANALYSIS is disabled")

    tenant_str = str(cmd.tenant_id)
    api_source_name = getattr(source, "api_source", "mock")

    # Step 2: Cache check
    if not cmd.force_refresh:
        cached = repo.get_latest(
            cmd.keyword_text,
            cmd.language,
            tenant_str,
            max_age_days=config.serp_cache_days,
        )
        if cached is not None:
            logger.info(
                "Cache hit for '%s' (%s) — snapshot %s",
                cmd.keyword_text,
                cmd.language,
                cached.id,
            )
            return Ok(
                AnalyseSerpResult(
                    snapshot_id=cached.id,
                    result_count=cached.result_count,
                    serp_features=cached.serp_features,
                    from_cache=True,
                    cost_estimate_usd="0.0000",
                    warnings=SerpFeatureDetector.get_warnings(cached.serp_features),
                )
            )

    # Step 3: Rate limiter check
    allowed, remaining = rate_limiter.can_request(api_source_name)
    if not allowed:
        msg = rate_limiter.limit_message(api_source_name)
        logger.warning("Rate limit reached: %s", msg)
        return Err(f"SERP daily limit reached: {msg}")

    # Step 4: Fetch SERP data
    try:
        raw_response = source.fetch_serp(cmd.keyword_text, cmd.language, cmd.country)
    except Exception as exc:
        logger.error(
            "SERP fetch failed for '%s': %s",
            cmd.keyword_text,
            exc,
        )
        return Err(f"serp_unavailable: {exc}")

    # Record the request after successful fetch
    rate_limiter.record_request(api_source_name)

    # Step 5: Detect features + warnings
    features = raw_response.features
    warnings = SerpFeatureDetector.get_warnings(features)

    # Step 6: Build and persist snapshot + results
    snapshot = SerpSnapshot(
        tenant_id=cmd.tenant_id,
        keyword_id=cmd.keyword_id,
        keyword_text=cmd.keyword_text,
        language=cmd.language,
        country=cmd.country,
        api_source=ApiSource(raw_response.api_source),
        result_count=len(raw_response.organic_results),
        no_organic_results=raw_response.no_organic_results,
        serp_features=features,
        pipeline_run_id=cmd.pipeline_run_id,
        cost_estimate_usd=f"{_COST_PER_REQUEST_USD:.4f}",
    )

    results = [
        SerpResult(
            tenant_id=cmd.tenant_id,
            snapshot_id=snapshot.id,
            position=r.position,
            url=r.url,
            domain=r.domain,
            title=r.title,
            meta_description=r.meta_description,
            estimated_word_count=r.estimated_word_count,
            content_type=ContentType(r.content_type) if r.content_type else None,
        )
        for r in raw_response.organic_results
    ]

    repo.save_snapshot(snapshot, results)

    # Step 7: Emit event
    duration_ms = int((time.monotonic() - start_time) * 1000)
    event = SerpAnalysisCompletedEvent(
        tenant_id=cmd.tenant_id,
        keyword_text=cmd.keyword_text,
        language=cmd.language,
        snapshot_id=snapshot.id,
        from_cache=False,
        has_ai_overview=features.ai_overview,
        warnings=warnings,
    )
    emit_serp_event(event)

    logger.info(
        "SERP analysis complete: keyword='%s' lang=%s results=%d cost=%s duration=%dms",
        cmd.keyword_text,
        cmd.language,
        len(results),
        snapshot.cost_estimate_usd,
        duration_ms,
    )

    return Ok(
        AnalyseSerpResult(
            snapshot_id=snapshot.id,
            result_count=len(raw_response.organic_results),
            serp_features=features,
            from_cache=False,
            cost_estimate_usd=f"{_COST_PER_REQUEST_USD:.4f}",
            warnings=warnings,
        )
    )


# ---------------------------------------------------------------------------
# Batch keyword analysis
# ---------------------------------------------------------------------------


def batch_analyse_serp(
    cmd: BatchAnalyseSerpCommand,
    config: ResearchConfig,
    source: SerpDataSource,
    rate_limiter: SerpRateLimiter,
    repo: SerpSnapshotPort,
) -> Result[BatchAnalyseSerpResult, str]:
    """Execute SERP analysis for a batch of keywords.

    Processes keywords sequentially. When the daily limit is reached,
    remaining keywords are queued (counted as queued_for_tomorrow).
    API failures don't halt the pipeline — failed keywords are counted
    and reported in the errors list.

    Args:
        cmd: Batch command with keyword list.
        config: Research engine configuration.
        source: SERP data source adapter.
        rate_limiter: Per-source daily rate limiter.
        repo: Snapshot storage adapter.

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    # Feature flag
    if not config.feature_serp_analysis:
        return Err("Feature flag FEATURE_SERP_ANALYSIS is disabled")

    completed = 0
    cached = 0
    failed = 0
    queued_for_tomorrow = 0
    snapshots: list[AnalyseSerpResult] = []
    errors: list[dict[str, str]] = []
    limit_reached = False

    for kw in cmd.keywords:
        keyword_id = kw["keyword_id"]
        keyword_text = kw["keyword_text"]
        language = kw["language"]
        country = kw["country"]

        # If limit already reached, queue remaining
        if limit_reached:
            queued_for_tomorrow += 1
            continue

        single_cmd = AnalyseSerpCommand(
            tenant_id=cmd.tenant_id,
            keyword_id=keyword_id,
            keyword_text=keyword_text,
            language=language,
            country=country,
            pipeline_run_id=cmd.pipeline_run_id,
        )

        result = analyse_serp(single_cmd, config, source, rate_limiter, repo)

        if isinstance(result, Ok):
            completed += 1
            if result.value.from_cache:
                cached += 1
            snapshots.append(result.value)
        elif isinstance(result, Err) and "daily limit" in result.error.lower():
            # Daily limit reached — queue this and all remaining
            limit_reached = True
            queued_for_tomorrow += 1

            # Emit limit reached event
            api_source_name = getattr(source, "api_source", "mock")
            remaining_count = (
                len(cmd.keywords) - completed - failed - queued_for_tomorrow
            )
            emit_serp_event(
                SerpDailyLimitReachedEvent(
                    tenant_id=cmd.tenant_id,
                    source=api_source_name,
                    daily_limit=config.serp_daily_limit,
                    keywords_queued=remaining_count + 1,
                )
            )
        else:
            failed += 1
            errors.append({"keyword_id": keyword_id, "error": result.error})

    logger.info(
        "Batch SERP analysis: completed=%d cached=%d failed=%d queued=%d",
        completed,
        cached,
        failed,
        queued_for_tomorrow,
    )

    return Ok(
        BatchAnalyseSerpResult(
            completed=completed,
            cached=cached,
            failed=failed,
            queued_for_tomorrow=queued_for_tomorrow,
            snapshots=snapshots,
            errors=errors,
        )
    )
