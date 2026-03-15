"""Tests for JSON file cluster storage adapter.

TDD: Tests written BEFORE implementation.
Covers: F-002 T-006 (Cluster Storage Adapter)
"""

from __future__ import annotations

import uuid
from pathlib import Path

from src.research_engine.adapters.cluster_storage import JsonFileClusterAdapter
from src.research_engine.models.cluster import KeywordCluster
from src.research_engine.models.keyword import Keyword, KeywordSource
from src.research_engine.ports.cluster_storage import ClusterStoragePort

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN = "camp_1"
LOCALE = "en"


def _cluster(
    name: str,
    cluster_id: str = "",
    coherence: int | None = 7,
) -> KeywordCluster:
    """Create a test cluster."""
    return KeywordCluster(
        id=cluster_id or f"tc_{uuid.uuid4().hex[:12]}",
        tenant_id=TENANT,
        campaign_id=CAMPAIGN,
        locale=LOCALE,
        name=name,
        rationale=f"Rationale for {name}",
        coherence_score=coherence,
    )


def _keyword(term: str, keyword_id: str = "") -> Keyword:
    """Create a test keyword."""
    return Keyword(
        id=keyword_id or f"kw_{uuid.uuid4().hex[:12]}",
        tenant_id=TENANT,
        campaign_id=CAMPAIGN,
        term=term,
        source=KeywordSource.URL_EXTRACTION,
    )


class TestProtocolCompliance:
    """Adapter satisfies ClusterStoragePort protocol."""

    def test_implements_protocol(self, tmp_path: Path) -> None:
        """JsonFileClusterAdapter is a ClusterStoragePort."""
        adapter = JsonFileClusterAdapter(tmp_path)
        assert isinstance(adapter, ClusterStoragePort)


class TestSaveClusters:
    """Tests for save_clusters (upsert by ID)."""

    def test_save_and_retrieve(self, tmp_path: Path) -> None:
        """Round-trip: save then get returns the same clusters."""
        adapter = JsonFileClusterAdapter(tmp_path)
        c1 = _cluster("Hair Loss", cluster_id="tc_aaa")
        c2 = _cluster("Hair Care", cluster_id="tc_bbb")

        count = adapter.save_clusters([c1, c2])
        assert count == 2

        results = adapter.get_clusters(CAMPAIGN, LOCALE)
        assert len(results) == 2
        ids = {r.id for r in results}
        assert ids == {"tc_aaa", "tc_bbb"}

    def test_upsert_updates_existing(self, tmp_path: Path) -> None:
        """Saving a cluster with the same ID updates it."""
        adapter = JsonFileClusterAdapter(tmp_path)
        c1 = _cluster("Old Name", cluster_id="tc_aaa")
        adapter.save_clusters([c1])

        c1_updated = _cluster("New Name", cluster_id="tc_aaa")
        adapter.save_clusters([c1_updated])

        results = adapter.get_clusters(CAMPAIGN, LOCALE)
        assert len(results) == 1
        assert results[0].name == "New Name"

    def test_save_empty_list(self, tmp_path: Path) -> None:
        """Saving empty list returns 0."""
        adapter = JsonFileClusterAdapter(tmp_path)
        assert adapter.save_clusters([]) == 0

    def test_separate_campaigns(self, tmp_path: Path) -> None:
        """Clusters for different campaigns stored separately."""
        adapter = JsonFileClusterAdapter(tmp_path)
        c1 = KeywordCluster(
            tenant_id=TENANT,
            campaign_id="camp_1",
            locale=LOCALE,
            name="Cluster A",
            rationale="Test",
        )
        c2 = KeywordCluster(
            tenant_id=TENANT,
            campaign_id="camp_2",
            locale=LOCALE,
            name="Cluster B",
            rationale="Test",
        )
        adapter.save_clusters([c1, c2])

        assert len(adapter.get_clusters("camp_1", LOCALE)) == 1
        assert len(adapter.get_clusters("camp_2", LOCALE)) == 1


class TestGetClusters:
    """Tests for get_clusters with filtering."""

    def test_excludes_deleted_by_default(self, tmp_path: Path) -> None:
        """Soft-deleted clusters are excluded by default."""
        adapter = JsonFileClusterAdapter(tmp_path)
        c1 = _cluster("Active", cluster_id="tc_aaa")
        c2 = _cluster("Deleted", cluster_id="tc_bbb")
        adapter.save_clusters([c1, c2])
        adapter.soft_delete(["tc_bbb"])

        results = adapter.get_clusters(CAMPAIGN, LOCALE)
        assert len(results) == 1
        assert results[0].id == "tc_aaa"

    def test_include_deleted(self, tmp_path: Path) -> None:
        """include_deleted=True returns all clusters."""
        adapter = JsonFileClusterAdapter(tmp_path)
        c1 = _cluster("Active", cluster_id="tc_aaa")
        c2 = _cluster("Deleted", cluster_id="tc_bbb")
        adapter.save_clusters([c1, c2])
        adapter.soft_delete(["tc_bbb"])

        results = adapter.get_clusters(CAMPAIGN, LOCALE, include_deleted=True)
        assert len(results) == 2

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        """Querying nonexistent campaign returns empty list."""
        adapter = JsonFileClusterAdapter(tmp_path)
        assert adapter.get_clusters("nonexistent", LOCALE) == []

    def test_locale_filtering(self, tmp_path: Path) -> None:
        """Clusters for different locales are separate files."""
        adapter = JsonFileClusterAdapter(tmp_path)
        c_en = KeywordCluster(
            tenant_id=TENANT,
            campaign_id=CAMPAIGN,
            locale="en",
            name="English Cluster",
            rationale="Test",
        )
        c_de = KeywordCluster(
            tenant_id=TENANT,
            campaign_id=CAMPAIGN,
            locale="de",
            name="German Cluster",
            rationale="Test",
        )
        adapter.save_clusters([c_en, c_de])

        assert len(adapter.get_clusters(CAMPAIGN, "en")) == 1
        assert len(adapter.get_clusters(CAMPAIGN, "de")) == 1


class TestSoftDelete:
    """Tests for soft_delete."""

    def test_soft_delete_sets_deleted_at(self, tmp_path: Path) -> None:
        """Soft-deleted clusters have deleted_at set."""
        adapter = JsonFileClusterAdapter(tmp_path)
        c1 = _cluster("Test", cluster_id="tc_aaa")
        adapter.save_clusters([c1])

        count = adapter.soft_delete(["tc_aaa"])
        assert count == 1

        results = adapter.get_clusters(CAMPAIGN, LOCALE, include_deleted=True)
        assert results[0].deleted_at is not None

    def test_soft_delete_nonexistent_returns_zero(self, tmp_path: Path) -> None:
        """Soft-deleting nonexistent IDs returns 0."""
        adapter = JsonFileClusterAdapter(tmp_path)
        assert adapter.soft_delete(["tc_nonexistent"]) == 0

    def test_soft_delete_partial(self, tmp_path: Path) -> None:
        """Only matching IDs are deleted."""
        adapter = JsonFileClusterAdapter(tmp_path)
        adapter.save_clusters(
            [
                _cluster("A", cluster_id="tc_aaa"),
                _cluster("B", cluster_id="tc_bbb"),
            ]
        )

        count = adapter.soft_delete(["tc_aaa", "tc_nonexistent"])
        assert count == 1


class TestUpdateKeywordClusterIds:
    """Tests for bulk keyword cluster_id FK updates."""

    def test_assigns_cluster_ids(self, tmp_path: Path) -> None:
        """Keywords get cluster_id set via assignments map."""
        adapter = JsonFileClusterAdapter(tmp_path)

        # Pre-populate keywords via the keyword file
        kw1 = _keyword("hair transplant", keyword_id="kw_001")
        kw2 = _keyword("fue surgery", keyword_id="kw_002")
        adapter.save_keywords([kw1, kw2], CAMPAIGN)

        count = adapter.update_keyword_cluster_ids(
            {"kw_001": "tc_aaa", "kw_002": "tc_bbb"},
            CAMPAIGN,
        )
        assert count == 2

        # Verify by reading keywords back
        keywords = adapter.load_keywords(CAMPAIGN)
        kw_map = {kw["id"]: kw for kw in keywords}
        assert kw_map["kw_001"]["cluster_id"] == "tc_aaa"
        assert kw_map["kw_002"]["cluster_id"] == "tc_bbb"

    def test_unassign_cluster_id(self, tmp_path: Path) -> None:
        """None value clears cluster_id."""
        adapter = JsonFileClusterAdapter(tmp_path)

        kw1 = _keyword("hair transplant", keyword_id="kw_001")
        adapter.save_keywords([kw1], CAMPAIGN)
        adapter.update_keyword_cluster_ids({"kw_001": "tc_aaa"}, CAMPAIGN)
        adapter.update_keyword_cluster_ids({"kw_001": None}, CAMPAIGN)

        keywords = adapter.load_keywords(CAMPAIGN)
        assert keywords[0]["cluster_id"] is None

    def test_nonexistent_keyword_skipped(self, tmp_path: Path) -> None:
        """Assignments for nonexistent keywords are skipped."""
        adapter = JsonFileClusterAdapter(tmp_path)
        kw1 = _keyword("test", keyword_id="kw_001")
        adapter.save_keywords([kw1], CAMPAIGN)

        count = adapter.update_keyword_cluster_ids(
            {"kw_001": "tc_aaa", "kw_999": "tc_bbb"},
            CAMPAIGN,
        )
        assert count == 1
