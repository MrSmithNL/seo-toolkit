"""File-based SERP snapshot repository for standalone mode.

Persists snapshots to JSON files at:
  data/serp/{tenant_id}/{language}/{keyword_slug}-{timestamp}.json

Append-only: each fetch creates a new file, never overwrites.

TypeScript equivalent: modules/content-engine/research/repos/file-serp-snapshot-repo.ts
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime, timedelta
from pathlib import Path

from src.research_engine.models.serp import SerpResult, SerpSnapshot


class FileSerpSnapshotRepo:
    """File-based SERP snapshot storage.

    Implements SerpSnapshotPort protocol using JSON files.
    Each snapshot is stored as a separate file with embedded results.
    """

    def __init__(self, data_dir: Path) -> None:
        """Initialise with base data directory.

        Args:
            data_dir: Base directory for SERP snapshot files.
        """
        self._data_dir = data_dir

    def save_snapshot(
        self,
        snapshot: SerpSnapshot,
        results: list[SerpResult],
    ) -> str:
        """Persist a SERP snapshot with its organic results.

        Args:
            snapshot: The SERP snapshot to save.
            results: The organic results associated with the snapshot.

        Returns:
            The snapshot ID.
        """
        dir_path = self._snapshot_dir(str(snapshot.tenant_id), snapshot.language)
        dir_path.mkdir(parents=True, exist_ok=True)

        slug = _slugify(snapshot.keyword_text)
        ts = snapshot.fetched_at.strftime("%Y%m%dT%H%M%S")
        filename = f"{slug}-{ts}.json"
        file_path = dir_path / filename

        data = {
            "snapshot": snapshot.model_dump(mode="json"),
            "results": [r.model_dump(mode="json") for r in results],
        }
        file_path.write_text(json.dumps(data, indent=2, default=str))
        return snapshot.id

    def get_latest(
        self,
        keyword_text: str,
        language: str,
        tenant_id: str,
        *,
        max_age_days: int = 7,
    ) -> SerpSnapshot | None:
        """Get the most recent snapshot for a keyword.

        Returns None if no snapshot exists or if it's older than max_age_days.

        Args:
            keyword_text: The keyword to look up.
            language: BCP 47 language code.
            tenant_id: Tenant UUID string.
            max_age_days: Maximum age in days for cache validity.

        Returns:
            The latest snapshot or None.
        """
        snapshots = self._load_snapshots(keyword_text, language, tenant_id)
        if not snapshots:
            return None

        # Sort by fetched_at descending — newest first
        snapshots.sort(key=lambda s: s.fetched_at, reverse=True)
        latest = snapshots[0]

        cutoff = datetime.now(tz=UTC) - timedelta(days=max_age_days)
        if latest.fetched_at < cutoff:
            return None

        return latest

    def get_history(
        self,
        keyword_text: str,
        language: str,
        tenant_id: str,
        *,
        limit: int = 10,
    ) -> list[SerpSnapshot]:
        """Get historical snapshots for a keyword, newest first.

        Args:
            keyword_text: The keyword to look up.
            language: BCP 47 language code.
            tenant_id: Tenant UUID string.
            limit: Maximum number of snapshots to return.

        Returns:
            List of snapshots, ordered by fetched_at descending.
        """
        snapshots = self._load_snapshots(keyword_text, language, tenant_id)
        snapshots.sort(key=lambda s: s.fetched_at, reverse=True)
        return snapshots[:limit]

    def get_results_for_snapshot(
        self,
        snapshot_id: str,
    ) -> list[SerpResult]:
        """Get organic results for a specific snapshot.

        Args:
            snapshot_id: The snapshot ID to look up.

        Returns:
            List of organic results for the snapshot.
        """
        # Scan all files to find the matching snapshot
        for json_file in self._data_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                if data.get("snapshot", {}).get("id") == snapshot_id:
                    return [
                        SerpResult.model_validate(r) for r in data.get("results", [])
                    ]
            except (json.JSONDecodeError, KeyError):
                continue
        return []

    def _snapshot_dir(self, tenant_id: str, language: str) -> Path:
        """Build the directory path for a tenant/language combo."""
        return self._data_dir / tenant_id / language

    def _load_snapshots(
        self,
        keyword_text: str,
        language: str,
        tenant_id: str,
    ) -> list[SerpSnapshot]:
        """Load all snapshots matching keyword/language/tenant.

        Args:
            keyword_text: The keyword to match.
            language: BCP 47 language code.
            tenant_id: Tenant UUID string.

        Returns:
            List of matching snapshots (unordered).
        """
        dir_path = self._snapshot_dir(tenant_id, language)
        if not dir_path.exists():
            return []

        slug = _slugify(keyword_text)
        snapshots: list[SerpSnapshot] = []

        for json_file in dir_path.glob(f"{slug}-*.json"):
            try:
                data = json.loads(json_file.read_text())
                snapshot = SerpSnapshot.model_validate(data["snapshot"])
                snapshots.append(snapshot)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

        return snapshots


def _slugify(text: str) -> str:
    """Convert text to a URL-friendly slug.

    Args:
        text: The text to slugify.

    Returns:
        Lowercase, hyphenated slug.
    """
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_]+", "-", text)
