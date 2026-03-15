"""Read queries for cluster data.

Thin query layer over the cluster storage port. Keeps command/query
separation clean for future CQRS migration.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.research_engine.models.cluster import KeywordCluster
from src.research_engine.models.keyword import Keyword
from src.research_engine.ports.cluster_storage import ClusterStoragePort
from src.research_engine.ports.storage import KeywordStoragePort


@dataclass
class GetClustersQuery:
    """Query for clusters by campaign and locale.

    Attributes:
        campaign_id: Campaign to query.
        locale: Locale to query.
        include_deleted: Include soft-deleted clusters.
        min_coherence: Optional minimum coherence score filter.
    """

    campaign_id: str
    locale: str
    include_deleted: bool = False
    min_coherence: int | None = None


@dataclass
class ClusterDetail:
    """A cluster with its member keywords.

    Attributes:
        cluster: The cluster record.
        keywords: Keywords belonging to this cluster.
    """

    cluster: KeywordCluster
    keywords: list[Keyword]


def get_clusters(
    query: GetClustersQuery,
    storage: ClusterStoragePort,
) -> list[KeywordCluster]:
    """Execute a cluster query against storage.

    Args:
        query: Query parameters.
        storage: Cluster storage adapter.

    Returns:
        List of matching clusters, optionally filtered by coherence.
    """
    clusters = storage.get_clusters(
        campaign_id=query.campaign_id,
        locale=query.locale,
        include_deleted=query.include_deleted,
    )

    if query.min_coherence is not None:
        clusters = [
            c
            for c in clusters
            if c.coherence_score is not None
            and c.coherence_score >= query.min_coherence
        ]

    return clusters


def get_cluster_detail(
    cluster_id: str,
    campaign_id: str,
    locale: str,
    cluster_storage: ClusterStoragePort,
    keyword_storage: KeywordStoragePort,
) -> ClusterDetail | None:
    """Get a single cluster with its member keywords.

    Args:
        cluster_id: ID of the cluster to retrieve.
        campaign_id: Campaign ID.
        locale: Locale.
        cluster_storage: Cluster storage adapter.
        keyword_storage: Keyword storage adapter.

    Returns:
        ClusterDetail if found, None otherwise.
    """
    clusters = cluster_storage.get_clusters(
        campaign_id=campaign_id,
        locale=locale,
        include_deleted=True,
    )
    cluster = next((c for c in clusters if c.id == cluster_id), None)
    if cluster is None:
        return None

    all_keywords = keyword_storage.get_by_campaign(campaign_id, locale=locale)
    member_keywords = [kw for kw in all_keywords if kw.cluster_id == cluster_id]

    return ClusterDetail(cluster=cluster, keywords=member_keywords)
