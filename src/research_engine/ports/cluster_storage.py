"""ClusterStoragePort protocol for cluster persistence.

Both JSON file and SQLite adapters implement this protocol.
Mirrors the TypeScript ClusterStoragePort interface.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.research_engine.models.cluster import KeywordCluster


@runtime_checkable
class ClusterStoragePort(Protocol):
    """Protocol for cluster storage adapters."""

    def save_clusters(self, clusters: list[KeywordCluster]) -> int:
        """Save clusters (upsert by id).

        Args:
            clusters: List of clusters to persist.

        Returns:
            Number of clusters saved/updated.
        """
        ...

    def get_clusters(
        self,
        campaign_id: str,
        locale: str,
        include_deleted: bool = False,
    ) -> list[KeywordCluster]:
        """Query clusters for a campaign and locale.

        Args:
            campaign_id: Campaign to query.
            locale: Locale to query.
            include_deleted: Include soft-deleted clusters.

        Returns:
            List of matching clusters.
        """
        ...

    def soft_delete(self, cluster_ids: list[str]) -> int:
        """Soft-delete clusters by setting deleted_at.

        Args:
            cluster_ids: IDs of clusters to soft-delete.

        Returns:
            Number of clusters soft-deleted.
        """
        ...

    def update_keyword_cluster_ids(
        self,
        assignments: dict[str, str | None],
        campaign_id: str,
    ) -> int:
        """Bulk update keyword.cluster_id foreign keys.

        Args:
            assignments: Mapping of keyword_id to cluster_id (None to unassign).
            campaign_id: Campaign whose keywords to update.

        Returns:
            Number of keywords updated.
        """
        ...
