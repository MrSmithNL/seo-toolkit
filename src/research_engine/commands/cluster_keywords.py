"""Pipeline orchestrator for F-002 Topic Clustering.

Orchestrates: load keywords -> chunk -> build prompt -> call LLM ->
parse response -> validate -> match existing -> select pillars ->
validate coherence -> persist -> update FKs -> soft-delete orphans ->
emit event.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field

from src.research_engine.config import ResearchConfig
from src.research_engine.domain.cluster_matcher import (
    find_orphaned_clusters,
    match_clusters,
)
from src.research_engine.domain.clustering import (
    build_clustering_prompt,
    chunk_keywords,
    parse_clustering_response,
)
from src.research_engine.domain.coherence_scorer import validate_coherence
from src.research_engine.domain.pillar_selector import select_pillar
from src.research_engine.events.clustering_events import (
    ClusteringCompletedEvent,
    emit_clustering_event,
)
from src.research_engine.models.cluster import KeywordCluster
from src.research_engine.models.keyword import Keyword
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.ports.cluster_storage import ClusterStoragePort
from src.research_engine.ports.llm_gateway import LlmGateway
from src.research_engine.ports.storage import KeywordStoragePort

logger = logging.getLogger(__name__)

MAX_LLM_RETRIES = 1


@dataclass
class ClusterKeywordsCommand:
    """Input for the clustering pipeline.

    Attributes:
        tenant_id: Tenant identifier.
        campaign_id: Campaign identifier.
        locale: Locale for clustering.
        force_recluster: Ignore existing clusters and recluster from scratch.
        volume_map: Optional keyword_id -> volume for pillar selection.
    """

    tenant_id: uuid.UUID
    campaign_id: str
    locale: str = "en"
    force_recluster: bool = False
    volume_map: dict[str, int] = field(default_factory=dict)


@dataclass
class ClusterKeywordsResult:
    """Output from the clustering pipeline.

    Attributes:
        run_id: Unique pipeline run identifier.
        clusters_created: Number of clusters persisted.
        unclustered_count: Number of unclustered keywords.
        orphans_deleted: Number of orphaned clusters soft-deleted.
        duration_ms: Pipeline duration in milliseconds.
    """

    run_id: str
    clusters_created: int
    unclustered_count: int
    orphans_deleted: int
    duration_ms: int


def cluster_keywords(  # noqa: C901
    cmd: ClusterKeywordsCommand,
    config: ResearchConfig,
    keyword_storage: KeywordStoragePort,
    cluster_storage: ClusterStoragePort,
    llm: LlmGateway,
) -> Result[ClusterKeywordsResult, str]:
    """Execute the F-002 topic clustering pipeline.

    Steps:
    1. Feature flag check
    2. Load keywords from storage
    3. Chunk keywords if > 150
    4. Build prompt and call LLM
    5. Parse and validate response
    6. Match existing clusters (Jaccard)
    7. Select pillars per cluster
    8. Validate coherence scores
    9. Persist clusters
    10. Update keyword.cluster_id FKs
    11. Soft-delete orphaned clusters
    12. Emit completion event

    Args:
        cmd: Pipeline command with parameters.
        config: Research engine configuration.
        keyword_storage: Keyword storage adapter.
        cluster_storage: Cluster storage adapter.
        llm: LLM gateway for clustering.

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    start_time = time.monotonic()
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    # Step 1: Feature flag
    if not config.feature_topic_clustering:
        return Err("Feature flag FEATURE_TOPIC_CLUSTERING is disabled")

    # Step 2: Load keywords
    logger.info("Step 2: Loading keywords for %s/%s", cmd.campaign_id, cmd.locale)
    keywords = keyword_storage.get_by_campaign(cmd.campaign_id, locale=cmd.locale)
    if not keywords:
        return Err("No keywords found for clustering")

    terms = [kw.term for kw in keywords]
    term_to_keyword: dict[str, Keyword] = {kw.term.lower(): kw for kw in keywords}
    logger.info("Loaded %d keywords", len(keywords))

    # Step 3: Chunk
    chunks = chunk_keywords(terms)
    logger.info("Split into %d chunk(s)", len(chunks))

    # Step 4-5: Build prompt, call LLM, parse response
    all_cluster_data = []
    all_unclustered: list[str] = []

    for i, chunk in enumerate(chunks):
        prompt = build_clustering_prompt(chunk)
        logger.info("Chunk %d: calling LLM with %d keywords", i + 1, len(chunk))

        # LLM call with retry
        raw_response = None
        for attempt in range(MAX_LLM_RETRIES + 1):
            try:
                raw_response = llm.complete(prompt)
                break
            except Exception:  # noqa: BLE001
                if attempt < MAX_LLM_RETRIES:
                    logger.warning(
                        "LLM call failed (attempt %d), retrying", attempt + 1
                    )
                else:
                    logger.error(
                        "LLM call failed after %d retries", MAX_LLM_RETRIES + 1
                    )

        if raw_response is None:
            # Graceful failure: all keywords unclustered
            logger.warning("LLM unavailable — marking all keywords as unclustered")
            all_unclustered.extend(chunk)
            continue

        parsed = parse_clustering_response(raw_response, chunk)
        if isinstance(parsed, Err):
            logger.warning(
                "Parse failed: %s — marking chunk as unclustered", parsed.error
            )
            all_unclustered.extend(chunk)
            continue

        all_cluster_data.extend(parsed.value.clusters)
        all_unclustered.extend(parsed.value.unclustered)

    # Step 6: Match existing clusters
    existing_clusters = cluster_storage.get_clusters(
        cmd.campaign_id, cmd.locale, include_deleted=False
    )
    new_names = [c.name for c in all_cluster_data]
    matched = match_clusters(new_names, existing_clusters) if existing_clusters else {}

    # Step 7-8: Build KeywordCluster objects with pillar + coherence
    built_clusters: list[KeywordCluster] = []
    kw_assignments: dict[str, str | None] = {}

    for llm_cluster in all_cluster_data:
        # Resolve or generate cluster ID
        cluster_id = matched.get(llm_cluster.name)
        if cluster_id is None or cmd.force_recluster:
            cluster_id = f"tc_{uuid.uuid4().hex[:12]}"

        # Resolve keywords in this cluster
        cluster_keywords_list: list[Keyword] = []
        for term in llm_cluster.keywords:
            kw = term_to_keyword.get(term.lower())
            if kw:
                cluster_keywords_list.append(kw)

        # Step 7: Pillar selection
        pillar = select_pillar(
            cluster_keywords_list,
            llm_cluster.pillar_keyword,
            cmd.volume_map,
        )

        # Step 8: Coherence validation
        coherence = validate_coherence(
            llm_cluster.coherence_score,
            llm_cluster.coherence_rationale,
        )
        coherence_score = None
        coherence_rationale = None
        low_warning = None
        if isinstance(coherence, Ok):
            coherence_score = coherence.value.score
            coherence_rationale = coherence.value.rationale
            low_warning = coherence.value.low_coherence_warning

        cluster = KeywordCluster(
            id=cluster_id,
            tenant_id=cmd.tenant_id,
            campaign_id=cmd.campaign_id,
            locale=cmd.locale,
            name=llm_cluster.name,
            rationale=llm_cluster.rationale,
            pillar_keyword_id=pillar.keyword_id,
            pillar_rationale=pillar.rationale,
            keyword_count=len(cluster_keywords_list),
            coherence_score=coherence_score,
            coherence_rationale=coherence_rationale,
            no_pillar_flag=pillar.no_pillar_flag or low_warning,
        )
        built_clusters.append(cluster)

        # Track FK assignments
        for kw in cluster_keywords_list:
            kw_assignments[kw.id] = cluster_id

    # Step 9: Persist clusters
    if built_clusters:
        cluster_storage.save_clusters(built_clusters)
        logger.info("Persisted %d clusters", len(built_clusters))

    # Step 10: Update keyword cluster_id FKs
    if kw_assignments:
        cluster_storage.update_keyword_cluster_ids(kw_assignments, cmd.campaign_id)

    # Step 11: Soft-delete orphans
    orphans_deleted = 0
    if existing_clusters and not cmd.force_recluster:
        matched_ids = {v for v in matched.values() if v is not None}
        orphan_ids = find_orphaned_clusters(existing_clusters, matched_ids)
        if orphan_ids:
            orphans_deleted = cluster_storage.soft_delete(orphan_ids)
            logger.info("Soft-deleted %d orphaned clusters", orphans_deleted)

    # Step 12: Emit event
    duration_ms = int((time.monotonic() - start_time) * 1000)
    event = ClusteringCompletedEvent(
        tenant_id=cmd.tenant_id,
        campaign_id=cmd.campaign_id,
        run_id=run_id,
        cluster_count=len(built_clusters),
        unclustered_count=len(all_unclustered),
        locale=cmd.locale,
    )
    emit_clustering_event(event)

    logger.info(
        "Clustering complete: %d clusters, %d unclustered in %dms",
        len(built_clusters),
        len(all_unclustered),
        duration_ms,
    )

    return Ok(
        ClusterKeywordsResult(
            run_id=run_id,
            clusters_created=len(built_clusters),
            unclustered_count=len(all_unclustered),
            orphans_deleted=orphans_deleted,
            duration_ms=duration_ms,
        )
    )
