"""Cluster name matching via Jaccard word-set similarity.

Pure functions for matching new cluster names to existing clusters
on pipeline re-runs, ensuring cluster ID stability.
"""

from __future__ import annotations

from src.research_engine.models.cluster import KeywordCluster

CLUSTER_MATCH_THRESHOLD = 0.8


def cluster_name_similarity(a: str, b: str) -> float:
    """Compute Jaccard similarity between two cluster names.

    Splits names into word sets (lowercased) and computes
    intersection / union.

    Args:
        a: First cluster name.
        b: Second cluster name.

    Returns:
        Similarity score 0.0-1.0.
    """
    words_a = set(a.lower().split())
    words_b = set(b.lower().split())

    if not words_a or not words_b:
        return 0.0

    intersection = words_a & words_b
    union = words_a | words_b
    return len(intersection) / len(union)


def match_clusters(
    new_names: list[str],
    existing: list[KeywordCluster],
    threshold: float = CLUSTER_MATCH_THRESHOLD,
) -> dict[str, str | None]:
    """Match new cluster names to existing cluster IDs.

    For each new name, finds the best-matching existing cluster
    above the similarity threshold.

    Args:
        new_names: List of new cluster names from LLM output.
        existing: List of existing clusters to match against.
        threshold: Minimum Jaccard similarity for a match.

    Returns:
        Mapping of new_name to existing cluster ID (or None if no match).
    """
    result: dict[str, str | None] = {}

    for name in new_names:
        best_id: str | None = None
        best_score = 0.0

        for cluster in existing:
            score = cluster_name_similarity(name, cluster.name)
            if score >= threshold and score > best_score:
                best_score = score
                best_id = cluster.id

        result[name] = best_id

    return result


def find_orphaned_clusters(
    existing: list[KeywordCluster],
    matched_ids: set[str],
) -> list[str]:
    """Find existing clusters that were not matched by any new cluster.

    Args:
        existing: List of existing clusters.
        matched_ids: Set of cluster IDs that were matched.

    Returns:
        List of orphaned cluster IDs (candidates for soft-delete).
    """
    return [c.id for c in existing if c.id not in matched_ids]
