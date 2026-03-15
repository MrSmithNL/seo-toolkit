"""Tests for cluster query handlers.

TDD: Tests written BEFORE implementation.
Covers: F-002 T-008 (Query Handlers)
"""

from __future__ import annotations

import uuid

from src.research_engine.models.cluster import KeywordCluster
from src.research_engine.models.keyword import Keyword, KeywordSource
from src.research_engine.queries.get_clusters import (
    GetClustersQuery,
    get_cluster_detail,
    get_clusters,
)
from tests.test_research_engine.conftest import MockClusterStorage, MockStorage

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN = "camp_1"
LOCALE = "en"


def _cluster(name: str, cluster_id: str, coherence: int | None = 7) -> KeywordCluster:
    """Create a test cluster."""
    return KeywordCluster(
        id=cluster_id,
        tenant_id=TENANT,
        campaign_id=CAMPAIGN,
        locale=LOCALE,
        name=name,
        rationale=f"Rationale for {name}",
        coherence_score=coherence,
    )


def _keyword(term: str, keyword_id: str, cluster_id: str | None = None) -> Keyword:
    """Create a test keyword with optional cluster_id."""
    kw = Keyword(
        id=keyword_id,
        tenant_id=TENANT,
        campaign_id=CAMPAIGN,
        term=term,
        source=KeywordSource.URL_EXTRACTION,
    )
    if cluster_id:
        object.__setattr__(kw, "cluster_id", cluster_id)
    return kw


class TestGetClusters:
    """Tests for get_clusters query."""

    def test_returns_all_active_clusters(self) -> None:
        """Returns all non-deleted clusters."""
        storage = MockClusterStorage()
        storage.save_clusters(
            [
                _cluster("Hair Loss", "tc_001"),
                _cluster("Hair Care", "tc_002"),
            ]
        )

        query = GetClustersQuery(campaign_id=CAMPAIGN, locale=LOCALE)
        results = get_clusters(query, storage)
        assert len(results) == 2

    def test_excludes_deleted_by_default(self) -> None:
        """Soft-deleted clusters excluded by default."""
        storage = MockClusterStorage()
        storage.save_clusters(
            [
                _cluster("Active", "tc_001"),
                _cluster("Deleted", "tc_002"),
            ]
        )
        storage.soft_delete(["tc_002"])

        query = GetClustersQuery(campaign_id=CAMPAIGN, locale=LOCALE)
        results = get_clusters(query, storage)
        assert len(results) == 1
        assert results[0].id == "tc_001"

    def test_include_deleted(self) -> None:
        """include_deleted=True returns all."""
        storage = MockClusterStorage()
        storage.save_clusters(
            [
                _cluster("Active", "tc_001"),
                _cluster("Deleted", "tc_002"),
            ]
        )
        storage.soft_delete(["tc_002"])

        query = GetClustersQuery(
            campaign_id=CAMPAIGN, locale=LOCALE, include_deleted=True
        )
        results = get_clusters(query, storage)
        assert len(results) == 2

    def test_filter_by_min_coherence(self) -> None:
        """min_coherence filters out low-scoring clusters."""
        storage = MockClusterStorage()
        storage.save_clusters(
            [
                _cluster("High", "tc_001", coherence=8),
                _cluster("Low", "tc_002", coherence=3),
                _cluster("None", "tc_003", coherence=None),
            ]
        )

        query = GetClustersQuery(campaign_id=CAMPAIGN, locale=LOCALE, min_coherence=5)
        results = get_clusters(query, storage)
        assert len(results) == 1
        assert results[0].id == "tc_001"

    def test_empty_storage_returns_empty(self) -> None:
        """Empty storage returns empty list."""
        storage = MockClusterStorage()
        query = GetClustersQuery(campaign_id=CAMPAIGN, locale=LOCALE)
        assert get_clusters(query, storage) == []


class TestGetClusterDetail:
    """Tests for get_cluster_detail query."""

    def test_returns_cluster_with_keywords(self) -> None:
        """Returns cluster and its member keywords."""
        cluster_storage = MockClusterStorage()
        cluster_storage.save_clusters([_cluster("Hair Loss", "tc_001")])

        kw_storage = MockStorage()
        kw_storage.save(
            [
                _keyword("hair loss", "kw_001", cluster_id="tc_001"),
                _keyword("fue surgery", "kw_002", cluster_id="tc_001"),
                _keyword("other term", "kw_003", cluster_id="tc_002"),
            ]
        )

        detail = get_cluster_detail(
            "tc_001", CAMPAIGN, LOCALE, cluster_storage, kw_storage
        )
        assert detail is not None
        assert detail.cluster.id == "tc_001"
        assert len(detail.keywords) == 2

    def test_nonexistent_cluster_returns_none(self) -> None:
        """Nonexistent cluster_id returns None."""
        cluster_storage = MockClusterStorage()
        kw_storage = MockStorage()

        detail = get_cluster_detail(
            "tc_nonexistent", CAMPAIGN, LOCALE, cluster_storage, kw_storage
        )
        assert detail is None

    def test_cluster_with_no_keywords(self) -> None:
        """Cluster with no assigned keywords returns empty keyword list."""
        cluster_storage = MockClusterStorage()
        cluster_storage.save_clusters([_cluster("Empty Cluster", "tc_001")])

        kw_storage = MockStorage()
        detail = get_cluster_detail(
            "tc_001", CAMPAIGN, LOCALE, cluster_storage, kw_storage
        )
        assert detail is not None
        assert detail.keywords == []
