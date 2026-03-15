"""JSON file storage adapter for keyword clusters.

Stores clusters as JSON files on disk, grouped by campaign and locale.
Implements the ClusterStoragePort protocol.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from src.research_engine.models.cluster import KeywordCluster
from src.research_engine.models.keyword import Keyword

logger = logging.getLogger(__name__)


class JsonFileClusterAdapter:
    """JSON file-based cluster storage.

    Stores clusters in files named ``clusters_{campaign_id}_{locale}.json``.

    Args:
        data_dir: Root directory for JSON files.
    """

    def __init__(self, data_dir: Path) -> None:  # noqa: D107
        self._data_dir = data_dir
        self._data_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _clusters_path(self, campaign_id: str, locale: str) -> Path:
        """Get the JSON file path for a campaign's clusters."""
        return self._data_dir / f"clusters_{campaign_id}_{locale}.json"

    def _keywords_path(self, campaign_id: str) -> Path:
        """Get the JSON file path for a campaign's keywords."""
        return self._data_dir / f"keywords_{campaign_id}.json"

    def _load_cluster_store(self, campaign_id: str, locale: str) -> dict[str, dict]:
        """Load clusters from JSON file, keyed by id."""
        path = self._clusters_path(campaign_id, locale)
        if not path.exists():
            return {}
        data = json.loads(path.read_text())
        return {item["id"]: item for item in data}

    def _persist_cluster_store(
        self, campaign_id: str, locale: str, store: dict[str, dict]
    ) -> None:
        """Write clusters dict to JSON file."""
        path = self._clusters_path(campaign_id, locale)
        path.write_text(json.dumps(list(store.values()), indent=2, default=str))

    # ------------------------------------------------------------------
    # ClusterStoragePort implementation
    # ------------------------------------------------------------------

    def save_clusters(self, clusters: list[KeywordCluster]) -> int:
        """Save clusters with upsert by id.

        Args:
            clusters: List of clusters to persist.

        Returns:
            Number of clusters saved/updated.
        """
        if not clusters:
            return 0

        by_file: dict[tuple[str, str], list[KeywordCluster]] = {}
        for cluster in clusters:
            key = (cluster.campaign_id, cluster.locale)
            by_file.setdefault(key, []).append(cluster)

        total = 0
        for (campaign_id, locale), file_clusters in by_file.items():
            store = self._load_cluster_store(campaign_id, locale)
            for cluster in file_clusters:
                store[cluster.id] = cluster.model_dump(mode="json")
                total += 1
            self._persist_cluster_store(campaign_id, locale, store)

        return total

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
        store = self._load_cluster_store(campaign_id, locale)
        results: list[KeywordCluster] = []
        for data in store.values():
            cluster = KeywordCluster.model_validate(data)
            if not include_deleted and cluster.deleted_at is not None:
                continue
            results.append(cluster)
        return results

    def soft_delete(self, cluster_ids: list[str]) -> int:
        """Soft-delete clusters by setting deleted_at.

        Scans all cluster files in the data directory.

        Args:
            cluster_ids: IDs of clusters to soft-delete.

        Returns:
            Number of clusters soft-deleted.
        """
        if not cluster_ids:
            return 0

        ids_to_delete = set(cluster_ids)
        count = 0

        for path in self._data_dir.glob("clusters_*.json"):
            data = json.loads(path.read_text())
            modified = False
            for item in data:
                if item["id"] in ids_to_delete and item.get("deleted_at") is None:
                    item["deleted_at"] = datetime.now(tz=UTC).isoformat()
                    ids_to_delete.discard(item["id"])
                    count += 1
                    modified = True
            if modified:
                path.write_text(json.dumps(data, indent=2, default=str))

        return count

    def update_keyword_cluster_ids(
        self,
        assignments: dict[str, str | None],
        campaign_id: str,
    ) -> int:
        """Bulk update keyword.cluster_id foreign keys.

        Args:
            assignments: Mapping of keyword_id to cluster_id (None to unassign).
            campaign_id: Campaign whose keyword file to update.

        Returns:
            Number of keywords updated.
        """
        if not assignments:
            return 0

        path = self._keywords_path(campaign_id)
        if not path.exists():
            return 0

        data = json.loads(path.read_text())
        count = 0
        for item in data:
            kw_id = item.get("id")
            if kw_id in assignments:
                item["cluster_id"] = assignments[kw_id]
                count += 1

        if count > 0:
            path.write_text(json.dumps(data, indent=2, default=str))

        return count

    # ------------------------------------------------------------------
    # Keyword file helpers (for FK updates)
    # ------------------------------------------------------------------

    def save_keywords(self, keywords: list[Keyword], campaign_id: str) -> None:
        """Save keywords to JSON file (used by tests to pre-populate).

        Args:
            keywords: Keywords to persist.
            campaign_id: Campaign ID for file naming.
        """
        path = self._keywords_path(campaign_id)
        data = [kw.model_dump(mode="json") for kw in keywords]
        path.write_text(json.dumps(data, indent=2, default=str))

    def load_keywords(self, campaign_id: str) -> list[dict]:
        """Load raw keyword dicts from JSON file.

        Args:
            campaign_id: Campaign ID to load.

        Returns:
            List of keyword dicts.
        """
        path = self._keywords_path(campaign_id)
        if not path.exists():
            return []
        result: list[dict] = json.loads(path.read_text())
        return result
