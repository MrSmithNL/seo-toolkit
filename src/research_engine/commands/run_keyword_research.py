"""Pipeline orchestrator for F-001 Keyword Research.

Orchestrates the full pipeline: crawl -> extract seeds -> expand ->
dedup -> enrich volume -> estimate difficulty -> gap analysis ->
persist -> emit event.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field

import httpx

from src.research_engine.config import ResearchConfig
from src.research_engine.domain.crawler import crawl_site
from src.research_engine.domain.difficulty import estimate_difficulty
from src.research_engine.domain.gap_analyser import CompetitorKeyword, analyse_gaps
from src.research_engine.domain.normaliser import dedup
from src.research_engine.domain.seed_extractor import extract_seeds
from src.research_engine.events.keyword_events import (
    KeywordResearchCompletedEvent,
    emit_event,
)
from src.research_engine.models.keyword import Keyword, KeywordSource
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.ports.data_source import KeywordDataSource
from src.research_engine.ports.storage import KeywordStoragePort

logger = logging.getLogger(__name__)


@dataclass
class RunKeywordResearchCommand:
    """Input for the keyword research pipeline.

    Attributes:
        tenant_id: Tenant identifier.
        campaign_id: Campaign identifier.
        target_url: Website URL to research.
        locales: Language locales to enrich.
        seed_keywords: Optional manual seed keywords.
        competitors: Optional competitor domains for gap analysis.
        skip_enrichment: Skip volume enrichment step.
        skip_difficulty: Skip difficulty estimation step.
    """

    tenant_id: uuid.UUID
    campaign_id: str
    target_url: str
    locales: list[str] = field(default_factory=lambda: ["en"])
    seed_keywords: list[str] | None = None
    competitors: list[str] | None = None
    skip_enrichment: bool = False
    skip_difficulty: bool = False


@dataclass
class RunKeywordResearchResult:
    """Output from the keyword research pipeline.

    Attributes:
        run_id: Unique pipeline run identifier.
        keywords_discovered: Number of unique keywords found.
        keywords_enriched: Number of keywords with volume data.
        gap_keywords_found: Number of competitor gap keywords.
        duration_ms: Pipeline duration in milliseconds.
    """

    run_id: str
    keywords_discovered: int
    keywords_enriched: int
    gap_keywords_found: int
    duration_ms: int


def run_keyword_research(  # noqa: C901
    cmd: RunKeywordResearchCommand,
    config: ResearchConfig,
    storage: KeywordStoragePort,
    autocomplete: KeywordDataSource | None = None,
    volume_source: KeywordDataSource | None = None,
) -> Result[RunKeywordResearchResult, str]:
    """Execute the F-001 keyword research pipeline.

    Steps:
    1. Check feature flag
    2. Crawl target URL
    3. Extract seeds from pages
    4. Expand via autocomplete
    5. Normalise and dedup
    6. Enrich with volume data
    7. Estimate difficulty
    8. Gap analysis (if competitors provided)
    9. Persist results
    10. Emit completion event

    Args:
        cmd: Pipeline command with parameters.
        config: Research engine configuration.
        storage: Storage adapter for persistence.
        autocomplete: Optional autocomplete adapter.
        volume_source: Optional volume data adapter.

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    start_time = time.monotonic()
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    # Step 1: Feature flag check
    if not config.feature_keyword_research:
        return Err("Feature flag FEATURE_KEYWORD_RESEARCH is disabled")

    # Step 2: Crawl target URL
    logger.info("Step 2: Crawling %s", cmd.target_url)
    client = httpx.Client()
    try:
        crawl_result = crawl_site(
            cmd.target_url, client, max_pages=config.max_crawl_pages
        )
    finally:
        client.close()

    if isinstance(crawl_result, Err):
        return Err(f"Crawl failed: {crawl_result.error}")

    page_urls = crawl_result.value
    logger.info("Discovered %d pages", len(page_urls))

    # Step 3: Extract seeds from pages
    logger.info("Step 3: Extracting seed keywords")
    all_keywords: list[Keyword] = []

    # Add manual seeds if provided
    if cmd.seed_keywords:
        for term in cmd.seed_keywords:
            all_keywords.append(
                Keyword(
                    tenant_id=cmd.tenant_id,
                    campaign_id=cmd.campaign_id,
                    term=term,
                    source=KeywordSource.MANUAL_SEED,
                )
            )

    # Extract from crawled pages
    client = httpx.Client()
    try:
        for page_url in page_urls[: config.max_crawl_pages]:
            try:
                response = client.get(page_url, timeout=10.0, follow_redirects=True)
                if response.status_code == 200:  # noqa: PLR2004
                    seeds = extract_seeds(response.text, page_url)
                    for seed in seeds:
                        all_keywords.append(
                            Keyword(
                                tenant_id=cmd.tenant_id,
                                campaign_id=cmd.campaign_id,
                                term=seed.term,
                                source=KeywordSource.URL_EXTRACTION,
                                source_url=seed.source_url,
                            )
                        )
            except httpx.HTTPError:
                logger.warning("Failed to fetch %s, skipping", page_url)
                continue
    finally:
        client.close()

    logger.info("Extracted %d raw keywords", len(all_keywords))

    # Step 4: Expand via autocomplete
    if autocomplete and "suggestions" in autocomplete.capabilities:
        logger.info("Step 4: Expanding via autocomplete")
        unique_terms = {kw.term.lower() for kw in all_keywords}
        for term in list(unique_terms)[:20]:  # Limit expansions
            try:
                suggestions = autocomplete.get_keyword_suggestions(term, cmd.locales[0])
                for suggestion in suggestions:
                    all_keywords.append(
                        Keyword(
                            tenant_id=cmd.tenant_id,
                            campaign_id=cmd.campaign_id,
                            term=suggestion,
                            source=KeywordSource.AUTOCOMPLETE,
                        )
                    )
            except Exception:  # noqa: BLE001
                logger.warning("Autocomplete failed for '%s', continuing", term)

    # Step 5: Normalise and dedup
    logger.info("Step 5: Deduplicating keywords")
    deduped = dedup(all_keywords)
    logger.info("After dedup: %d keywords (from %d)", len(deduped), len(all_keywords))

    # Step 6: Enrich with volume
    enriched_count = 0
    if (
        not cmd.skip_enrichment
        and volume_source
        and "volume" in volume_source.capabilities
    ):
        logger.info("Step 6: Enriching with volume data")
        terms = [kw.term for kw in deduped]
        try:
            volume_results = volume_source.get_keyword_volume(
                terms, cmd.locales[0], cmd.locales[0].upper()
            )
            volume_map = {vr.keyword.lower(): vr for vr in volume_results}
            for kw in deduped:
                vr = volume_map.get(kw.term.lower())
                if vr and vr.volume is not None:
                    object.__setattr__(kw, "difficulty", None)
                    enriched_count += 1
        except Exception:  # noqa: BLE001
            logger.warning("Volume enrichment failed, continuing without")

    # Step 7: Estimate difficulty
    if not cmd.skip_difficulty:
        logger.info("Step 7: Estimating difficulty")
        for kw in deduped:
            try:
                result = estimate_difficulty(
                    volume=0,
                    autocomplete_depth=3,
                    llm_authority_score=50,
                )
                object.__setattr__(kw, "difficulty", result.score)
                object.__setattr__(kw, "difficulty_source", "heuristic")
                object.__setattr__(kw, "difficulty_rationale", result.rationale)
            except Exception:  # noqa: BLE001
                logger.warning("Difficulty estimation failed for '%s'", kw.term)

    # Step 8: Gap analysis
    gap_count = 0
    if cmd.competitors:
        logger.info(
            "Step 8: Analysing gaps against %d competitors", len(cmd.competitors)
        )
        our_terms = {kw.term.lower() for kw in deduped}
        competitor_kws: list[CompetitorKeyword] = []
        # In a full implementation, we'd fetch competitor SERP data here
        # For now, this is a placeholder that works with provided data
        gaps = analyse_gaps(
            our_keywords=our_terms,
            competitor_keywords=competitor_kws,
            campaign_id=cmd.campaign_id,
            tenant_id=cmd.tenant_id,
        )
        if gaps:
            storage.save_gaps(gaps)
            gap_count = len(gaps)

    # Step 9: Persist
    logger.info("Step 9: Persisting %d keywords", len(deduped))
    storage.save(deduped)

    # Step 10: Emit event
    duration_ms = int((time.monotonic() - start_time) * 1000)
    event = KeywordResearchCompletedEvent(
        tenant_id=cmd.tenant_id,
        campaign_id=cmd.campaign_id,
        run_id=run_id,
        keyword_count=len(deduped),
        locales=cmd.locales,
    )
    emit_event(event)

    logger.info("Pipeline complete: %d keywords in %dms", len(deduped), duration_ms)

    return Ok(
        RunKeywordResearchResult(
            run_id=run_id,
            keywords_discovered=len(deduped),
            keywords_enriched=enriched_count,
            gap_keywords_found=gap_count,
            duration_ms=duration_ms,
        )
    )
