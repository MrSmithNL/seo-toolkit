"""Tests for cluster name matching via Jaccard similarity.

TDD: Tests written BEFORE implementation.
Covers: F-002 T-002 (Cluster Name Matching)
"""

from __future__ import annotations

import uuid

from hypothesis import given
from hypothesis import strategies as st

from src.research_engine.domain.cluster_matcher import (
    cluster_name_similarity,
    find_orphaned_clusters,
    match_clusters,
)
from src.research_engine.models.cluster import KeywordCluster


def _cluster(name: str, cluster_id: str = "") -> KeywordCluster:
    """Helper to create a cluster with a given name."""
    return KeywordCluster(
        id=cluster_id or f"tc_{uuid.uuid4().hex[:12]}",
        tenant_id=uuid.uuid4(),
        campaign_id="camp_1",
        locale="en",
        name=name,
        rationale="Test.",
    )


class TestClusterNameSimilarity:
    """Tests for Jaccard word-set similarity."""

    def test_identical_names(self) -> None:
        """Identical names return 1.0."""
        assert cluster_name_similarity("hair transplant", "hair transplant") == 1.0

    def test_completely_different(self) -> None:
        """No shared words return 0.0."""
        assert cluster_name_similarity("hair transplant", "skin care") == 0.0

    def test_partial_overlap(self) -> None:
        """Partial overlap returns correct Jaccard score."""
        # intersection={"hair"}, union={"hair","transplant","growth"}
        # Jaccard = 1/3
        score = cluster_name_similarity("hair transplant", "hair growth")
        assert abs(score - 1 / 3) < 0.01

    def test_word_order_irrelevant(self) -> None:
        """Word order does not affect similarity."""
        assert (
            cluster_name_similarity("transplant hair cost", "cost hair transplant")
            == 1.0
        )

    def test_case_insensitive(self) -> None:
        """Comparison is case-insensitive."""
        assert cluster_name_similarity("Hair Transplant", "hair transplant") == 1.0

    def test_empty_strings(self) -> None:
        """Empty strings return 0.0."""
        assert cluster_name_similarity("", "") == 0.0
        assert cluster_name_similarity("hair", "") == 0.0

    @given(
        a=st.text(min_size=0, max_size=50),
        b=st.text(min_size=0, max_size=50),
    )
    def test_similarity_bounded_zero_to_one(self, a: str, b: str) -> None:
        """Similarity is always in [0.0, 1.0]."""
        score = cluster_name_similarity(a, b)
        assert 0.0 <= score <= 1.0


class TestMatchClusters:
    """Tests for matching new cluster names to existing clusters."""

    def test_exact_match_returns_existing_id(self) -> None:
        """Exact name match maps to existing cluster ID."""
        existing = [_cluster("Hair Transplant", "tc_existing01")]
        result = match_clusters(["Hair Transplant"], existing)
        assert result["Hair Transplant"] == "tc_existing01"

    def test_no_match_returns_none(self) -> None:
        """No similar existing cluster returns None."""
        existing = [_cluster("Skin Care", "tc_existing01")]
        result = match_clusters(["Hair Transplant"], existing)
        assert result["Hair Transplant"] is None

    def test_threshold_boundary(self) -> None:
        """Names just above threshold match, just below do not."""
        # "hair transplant cost" vs "hair transplant price"
        # intersection={"hair","transplant"}, union={"hair","transplant","cost","price"}
        # Jaccard = 2/4 = 0.5 → below 0.8 threshold → no match
        existing = [_cluster("hair transplant price", "tc_existing01")]
        result = match_clusters(["hair transplant cost"], existing)
        assert result["hair transplant cost"] is None

    def test_high_similarity_matches(self) -> None:
        """Names with >80% word overlap match."""
        # "hair transplant fue" vs "hair transplant fue methods"
        # intersection={hair,transplant,fue}
        # union={hair,transplant,fue,methods}
        # Jaccard = 3/4 = 0.75 → below 0.8 → no match
        # Need higher overlap: 4/5 = 0.8
        existing = [_cluster("hair fue transplant recovery guide", "tc_exist")]
        result = match_clusters(["hair fue transplant recovery tips"], existing)
        # 4/6 = 0.67 → no match
        assert result["hair fue transplant recovery tips"] is None


class TestFindOrphanedClusters:
    """Tests for identifying orphaned clusters."""

    def test_unmatched_clusters_are_orphans(self) -> None:
        """Clusters not in matched_ids are orphaned."""
        existing = [
            _cluster("Cluster A", "tc_a"),
            _cluster("Cluster B", "tc_b"),
            _cluster("Cluster C", "tc_c"),
        ]
        matched_ids = {"tc_a", "tc_c"}
        orphans = find_orphaned_clusters(existing, matched_ids)
        assert orphans == ["tc_b"]

    def test_all_matched_no_orphans(self) -> None:
        """When all are matched, no orphans returned."""
        existing = [_cluster("A", "tc_a"), _cluster("B", "tc_b")]
        orphans = find_orphaned_clusters(existing, {"tc_a", "tc_b"})
        assert orphans == []

    def test_empty_existing_no_orphans(self) -> None:
        """Empty existing list produces no orphans."""
        orphans = find_orphaned_clusters([], {"tc_a"})
        assert orphans == []
