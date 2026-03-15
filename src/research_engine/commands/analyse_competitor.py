"""Pipeline orchestrator for F-005 Competitor Content Analysis.

Orchestrates the full competitor analysis flow:
  robots check → rate limit → download → extract → quality assess →
  hash → persist → emit events.

Includes both single-page (AnalyseCompetitorPageCommand) and batch
(BatchAnalyseCompetitorsCommand) commands.

TypeScript equivalent: modules/content-engine/research/commands/analyse-competitor.ts
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from typing import Any

from src.research_engine.config import ResearchConfig
from src.research_engine.events.competitor_events import (
    CompetitorAnalysisCompletedEvent,
    CompetitorBatchCompletedEvent,
)
from src.research_engine.models.competitor import (
    CompetitorSnapshot,
    CrawlStatus,
    QualityAssessmentStatus,
)
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.services.content_extractor import compress_for_llm

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Command + Result data classes
# ---------------------------------------------------------------------------


@dataclass
class AnalyseCompetitorPageCommand:
    """Input for a single competitor page analysis.

    Attributes:
        tenant_id: Tenant identifier.
        keyword_id: Keyword record ID (from F-001).
        serp_snapshot_id: SERP snapshot this URL came from (F-004).
        url: Competitor page URL to analyse.
        domain: Domain extracted from URL.
        serp_position: Position in SERP results (1-10).
        pipeline_run_id: Optional pipeline run ID for batch tracking.
    """

    tenant_id: uuid.UUID
    keyword_id: str
    serp_snapshot_id: str
    url: str
    domain: str
    serp_position: int
    pipeline_run_id: str | None = None


@dataclass
class AnalyseCompetitorPageResult:
    """Output from a single competitor page analysis.

    Attributes:
        snapshot_id: The persisted snapshot ID.
        crawl_status: Status of the crawl attempt.
        word_count: Extracted word count (0 if crawl failed).
        depth_score: LLM quality score 1-5 (None if assessment skipped/failed).
        content_changed: Whether content changed since last crawl.
        llm_tokens_used: Tokens consumed by quality assessment.
    """

    snapshot_id: str
    crawl_status: CrawlStatus
    word_count: int
    depth_score: int | None
    content_changed: bool
    llm_tokens_used: int


@dataclass
class BatchAnalyseCompetitorsCommand:
    """Input for batch competitor analysis.

    Attributes:
        tenant_id: Tenant identifier.
        keyword_id: Keyword record ID.
        serp_snapshot_id: Source SERP snapshot.
        urls: List of dicts with url, domain, serp_position.
        pipeline_run_id: Pipeline run ID for tracking.
    """

    tenant_id: uuid.UUID
    keyword_id: str
    serp_snapshot_id: str
    urls: list[dict[str, str | int]]
    pipeline_run_id: str


@dataclass
class BatchAnalyseCompetitorsResult:
    """Output from batch competitor analysis.

    Attributes:
        total: Total URLs processed.
        succeeded: URLs with successful crawl.
        failed: URLs with crawl failure.
        robots_blocked: URLs blocked by robots.txt.
        llm_tokens_total: Total LLM tokens consumed.
        duration_seconds: Total wall-clock time.
        snapshots: Individual page results.
    """

    total: int
    succeeded: int
    failed: int
    robots_blocked: int
    llm_tokens_total: int
    duration_seconds: float
    snapshots: list[AnalyseCompetitorPageResult]


# ---------------------------------------------------------------------------
# Single page analysis
# ---------------------------------------------------------------------------


def analyse_competitor_page(  # noqa: PLR0913
    cmd: AnalyseCompetitorPageCommand,
    config: ResearchConfig,
    downloader: Any,
    extractor: Any,
    assessor: Any,
    repo: Any,
    events: Any,
) -> Result[AnalyseCompetitorPageResult, str]:
    """Execute competitor page analysis for a single URL.

    Steps:
    1. Feature flag check
    2. Download page (includes robots check + rate limiting)
    3. Extract structural content
    4. LLM quality assessment
    5. Change detection (hash comparison)
    6. Persist snapshot
    7. Emit event

    Args:
        cmd: Analysis command with URL details.
        config: Research engine configuration.
        downloader: PageDownloader instance.
        extractor: ContentExtractor wrapper or mock.
        assessor: QualityAssessor instance.
        repo: CompetitorSnapshotPort implementation.
        events: Event emitter.

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    # Step 1: Feature flag
    if not config.feature_competitor_analysis:
        return Err("Feature flag FEATURE_COMPETITOR_ANALYSIS is disabled")

    tenant_str = str(cmd.tenant_id)

    # Step 2: Download page
    dl_result = downloader.download(cmd.url)

    # Handle robots blocked
    if dl_result.is_robots_blocked:
        snapshot = CompetitorSnapshot(
            tenant_id=cmd.tenant_id,
            keyword_id=cmd.keyword_id,
            serp_snapshot_id=cmd.serp_snapshot_id,
            url=cmd.url,
            domain=cmd.domain,
            serp_position=cmd.serp_position,
            crawl_status=CrawlStatus.ROBOTS_BLOCKED,
            word_count=0,
            raw_html_hash="",
            content_changed=False,
        )
        repo.save_snapshot(snapshot)
        events.emit(
            CompetitorAnalysisCompletedEvent(
                tenant_id=cmd.tenant_id,
                keyword_id=cmd.keyword_id,
                snapshot_id=snapshot.id,
                crawl_status=CrawlStatus.ROBOTS_BLOCKED,
                content_changed=False,
            )
        )
        return Ok(
            AnalyseCompetitorPageResult(
                snapshot_id=snapshot.id,
                crawl_status=CrawlStatus.ROBOTS_BLOCKED,
                word_count=0,
                depth_score=None,
                content_changed=False,
                llm_tokens_used=0,
            )
        )

    # Handle download failure
    if not dl_result.success:
        snapshot = CompetitorSnapshot(
            tenant_id=cmd.tenant_id,
            keyword_id=cmd.keyword_id,
            serp_snapshot_id=cmd.serp_snapshot_id,
            url=cmd.url,
            domain=cmd.domain,
            serp_position=cmd.serp_position,
            crawl_status=CrawlStatus.CRAWL_FAILED,
            word_count=0,
            raw_html_hash="",
            content_changed=False,
        )
        repo.save_snapshot(snapshot)
        events.emit(
            CompetitorAnalysisCompletedEvent(
                tenant_id=cmd.tenant_id,
                keyword_id=cmd.keyword_id,
                snapshot_id=snapshot.id,
                crawl_status=CrawlStatus.CRAWL_FAILED,
                content_changed=False,
            )
        )
        return Ok(
            AnalyseCompetitorPageResult(
                snapshot_id=snapshot.id,
                crawl_status=CrawlStatus.CRAWL_FAILED,
                word_count=0,
                depth_score=None,
                content_changed=False,
                llm_tokens_used=0,
            )
        )

    # Step 3: Extract structural content
    extraction = extractor.extract(dl_result.html, cmd.url)

    # Determine crawl status based on extraction
    crawl_status = CrawlStatus.SUCCESS
    if extraction.is_js_rendered:
        crawl_status = CrawlStatus.JS_RENDERED

    # Step 4: LLM quality assessment
    depth_score: int | None = None
    topics_covered: list[str] = []
    has_original_data = False
    has_author_credentials = False
    eeat_signals: list[str] = []
    quality_rationale = ""
    quality_status = QualityAssessmentStatus.SKIPPED
    llm_tokens_used = 0

    if extraction.word_count > 0:
        compressed = compress_for_llm(extraction)
        assessment = assessor.assess_single(compressed, cmd.url)

        if (
            assessment.status == QualityAssessmentStatus.COMPLETED
            and assessment.profile
        ):
            depth_score = assessment.profile.depth_score
            topics_covered = assessment.profile.topics_covered
            has_original_data = assessment.profile.has_original_data
            has_author_credentials = assessment.profile.has_author_credentials
            eeat_signals = assessment.profile.eeat_signals
            quality_rationale = assessment.profile.quality_rationale
            quality_status = QualityAssessmentStatus.COMPLETED
            llm_tokens_used = assessment.tokens_used
        elif assessment.status == QualityAssessmentStatus.FAILED:
            quality_status = QualityAssessmentStatus.FAILED

    # Step 5: Change detection
    previous = repo.get_latest(cmd.url, tenant_str)
    content_changed = False
    if previous is not None and previous.raw_html_hash != dl_result.raw_html_hash:
        content_changed = True

    # Step 6: Persist snapshot
    snapshot = CompetitorSnapshot(
        tenant_id=cmd.tenant_id,
        keyword_id=cmd.keyword_id,
        serp_snapshot_id=cmd.serp_snapshot_id,
        url=cmd.url,
        domain=cmd.domain,
        serp_position=cmd.serp_position,
        crawl_status=crawl_status,
        word_count=extraction.word_count,
        h1_text=extraction.h1_text,
        h2_count=extraction.h2_count,
        h2_texts=extraction.h2_texts,
        h3_count=extraction.h3_count,
        schema_types=extraction.schema_types,
        has_faq_section=extraction.has_faq_section,
        internal_link_count=extraction.internal_link_count,
        external_link_count=extraction.external_link_count,
        image_count=extraction.image_count,
        depth_score=depth_score,
        topics_covered=topics_covered,
        has_original_data=has_original_data,
        has_author_credentials=has_author_credentials,
        eeat_signals=eeat_signals,
        quality_rationale=quality_rationale,
        quality_assessment_status=quality_status,
        raw_html_hash=dl_result.raw_html_hash,
        content_changed=content_changed,
        llm_tokens_used=llm_tokens_used,
        pipeline_run_id=cmd.pipeline_run_id,
    )
    repo.save_snapshot(snapshot)

    # Step 7: Emit event
    events.emit(
        CompetitorAnalysisCompletedEvent(
            tenant_id=cmd.tenant_id,
            keyword_id=cmd.keyword_id,
            snapshot_id=snapshot.id,
            crawl_status=crawl_status,
            content_changed=content_changed,
        )
    )

    logger.info(
        "Competitor analysis: url=%s crawl=%s words=%d "
        "depth=%s changed=%s tokens=%d",
        cmd.url,
        crawl_status.value,
        extraction.word_count,
        depth_score,
        content_changed,
        llm_tokens_used,
    )

    return Ok(
        AnalyseCompetitorPageResult(
            snapshot_id=snapshot.id,
            crawl_status=crawl_status,
            word_count=extraction.word_count,
            depth_score=depth_score,
            content_changed=content_changed,
            llm_tokens_used=llm_tokens_used,
        )
    )


# ---------------------------------------------------------------------------
# Batch analysis
# ---------------------------------------------------------------------------


def batch_analyse_competitors(  # noqa: PLR0913
    cmd: BatchAnalyseCompetitorsCommand,
    config: ResearchConfig,
    downloader: Any,
    extractor: Any,
    assessor: Any,
    repo: Any,
    events: Any,
) -> Result[BatchAnalyseCompetitorsResult, str]:
    """Execute competitor analysis for a batch of URLs.

    Processes URLs sequentially. Failures don't halt the pipeline —
    failed URLs are counted and reported.

    Args:
        cmd: Batch command with URL list.
        config: Research engine configuration.
        downloader: PageDownloader instance.
        extractor: ContentExtractor function/object.
        assessor: QualityAssessor instance.
        repo: CompetitorSnapshotPort implementation.
        events: Event emitter.

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    # Feature flag
    if not config.feature_competitor_analysis:
        return Err("Feature flag FEATURE_COMPETITOR_ANALYSIS is disabled")

    start_time = time.monotonic()

    succeeded = 0
    failed = 0
    robots_blocked = 0
    llm_tokens_total = 0
    snapshots: list[AnalyseCompetitorPageResult] = []

    for url_info in cmd.urls:
        single_cmd = AnalyseCompetitorPageCommand(
            tenant_id=cmd.tenant_id,
            keyword_id=cmd.keyword_id,
            serp_snapshot_id=cmd.serp_snapshot_id,
            url=str(url_info["url"]),
            domain=str(url_info["domain"]),
            serp_position=int(url_info["serp_position"]),
            pipeline_run_id=cmd.pipeline_run_id,
        )

        result = analyse_competitor_page(
            single_cmd,
            config,
            downloader,
            extractor,
            assessor,
            repo,
            events,
        )

        if isinstance(result, Ok):
            page_result = result.value
            snapshots.append(page_result)
            llm_tokens_total += page_result.llm_tokens_used

            if page_result.crawl_status == CrawlStatus.ROBOTS_BLOCKED:
                robots_blocked += 1
            elif page_result.crawl_status == CrawlStatus.CRAWL_FAILED:
                failed += 1
            else:
                succeeded += 1
        else:
            failed += 1

    duration = time.monotonic() - start_time

    # Emit batch completed event
    batch_event = CompetitorBatchCompletedEvent(
        tenant_id=cmd.tenant_id,
        pipeline_run_id=cmd.pipeline_run_id,
        total=len(cmd.urls),
        succeeded=succeeded,
        failed=failed,
        robots_blocked=robots_blocked,
        llm_tokens_total=llm_tokens_total,
        duration_seconds=round(duration, 2),
    )
    events.emit(batch_event)

    logger.info(
        "Batch competitor analysis: total=%d ok=%d "
        "fail=%d robots=%d tokens=%d dur=%.1fs",
        len(cmd.urls),
        succeeded,
        failed,
        robots_blocked,
        llm_tokens_total,
        duration,
    )

    return Ok(
        BatchAnalyseCompetitorsResult(
            total=len(cmd.urls),
            succeeded=succeeded,
            failed=failed,
            robots_blocked=robots_blocked,
            llm_tokens_total=llm_tokens_total,
            duration_seconds=round(duration, 2),
            snapshots=snapshots,
        )
    )
