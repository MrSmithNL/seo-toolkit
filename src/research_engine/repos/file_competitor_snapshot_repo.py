"""File-based competitor snapshot repository for standalone mode.

Persists snapshots to JSON files at:
  data/competitor-snapshots/{domain}/{path-slug}.json

Append-only: each crawl creates a new file entry, never overwrites.

TS equivalent: modules/content-engine/research/repos/file-competitor-snapshot-repo.ts
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from src.research_engine.models.competitor import (
    CompetitorBenchmark,
    CompetitorSnapshot,
)


class FileCompetitorSnapshotRepo:
    """File-based competitor snapshot storage.

    Implements CompetitorSnapshotPort protocol using JSON files.
    Each snapshot stored as separate timestamped file.
    """

    def __init__(self, data_dir: Path) -> None:
        """Initialise with base data directory.

        Args:
            data_dir: Base directory for snapshot files.
        """
        self._data_dir = data_dir

    def save_snapshot(self, snapshot: CompetitorSnapshot) -> str:
        """Persist a competitor snapshot.

        Append-only: creates a new file per snapshot.

        Args:
            snapshot: The snapshot to save.

        Returns:
            The snapshot ID.
        """
        dir_path = self._snapshot_dir(snapshot.domain)
        dir_path.mkdir(parents=True, exist_ok=True)

        slug = _slugify(snapshot.url)
        ts = snapshot.crawled_at.strftime("%Y%m%dT%H%M%S")
        filename = f"{slug}-{ts}.json"
        file_path = dir_path / filename

        data = snapshot.model_dump(mode="json")
        file_path.write_text(json.dumps(data, indent=2, default=str))
        return snapshot.id

    def get_latest(
        self,
        url: str,
        tenant_id: str,
    ) -> CompetitorSnapshot | None:
        """Get the most recent snapshot for a URL.

        Args:
            url: The competitor URL.
            tenant_id: Tenant UUID string.

        Returns:
            The latest snapshot, or None.
        """
        snapshots = self._load_snapshots_for_url(url, tenant_id)
        if not snapshots:
            return None

        snapshots.sort(key=lambda s: s.crawled_at, reverse=True)
        return snapshots[0]

    def get_by_keyword(
        self,
        keyword_id: str,
        tenant_id: str,
    ) -> list[CompetitorBenchmark]:
        """Get competitor benchmarks for a keyword.

        Scans all snapshot files and returns the latest snapshot per URL
        for the given keyword.

        Args:
            keyword_id: The keyword ID.
            tenant_id: Tenant UUID string.

        Returns:
            List of competitor benchmarks.
        """
        # Scan all files
        latest_per_url: dict[str, CompetitorSnapshot] = {}

        for json_file in self._data_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                snapshot = CompetitorSnapshot.model_validate(data)
                if (
                    snapshot.keyword_id == keyword_id
                    and str(snapshot.tenant_id) == tenant_id
                ):
                    existing = latest_per_url.get(snapshot.url)
                    if existing is None or snapshot.crawled_at > existing.crawled_at:
                        latest_per_url[snapshot.url] = snapshot
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

        return [
            CompetitorBenchmark(
                url=s.url,
                domain=s.domain,
                serp_position=s.serp_position,
                word_count=s.word_count,
                depth_score=s.depth_score,
                h2_texts=s.h2_texts,
                schema_types=s.schema_types,
                has_faq_section=s.has_faq_section,
                topics_covered=s.topics_covered,
            )
            for s in sorted(latest_per_url.values(), key=lambda x: x.serp_position)
        ]

    def get_history(
        self,
        url: str,
        tenant_id: str,
        *,
        limit: int = 10,
    ) -> list[CompetitorSnapshot]:
        """Get historical snapshots for a URL, newest first.

        Args:
            url: The competitor URL.
            tenant_id: Tenant UUID string.
            limit: Maximum number of snapshots.

        Returns:
            List of snapshots, newest first.
        """
        snapshots = self._load_snapshots_for_url(url, tenant_id)
        snapshots.sort(key=lambda s: s.crawled_at, reverse=True)
        return snapshots[:limit]

    def _snapshot_dir(self, domain: str) -> Path:
        """Build the directory path for a domain."""
        return self._data_dir / _slugify(domain)

    def _load_snapshots_for_url(
        self,
        url: str,
        tenant_id: str,
    ) -> list[CompetitorSnapshot]:
        """Load all snapshots matching a URL and tenant.

        Args:
            url: The competitor URL.
            tenant_id: Tenant UUID string.

        Returns:
            List of matching snapshots.
        """
        snapshots: list[CompetitorSnapshot] = []

        for json_file in self._data_dir.rglob("*.json"):
            try:
                data = json.loads(json_file.read_text())
                snapshot = CompetitorSnapshot.model_validate(data)
                if snapshot.url == url and str(snapshot.tenant_id) == tenant_id:
                    snapshots.append(snapshot)
            except (json.JSONDecodeError, KeyError, ValueError):
                continue

        return snapshots


def _slugify(text: str) -> str:
    """Convert text to a filesystem-friendly slug.

    Args:
        text: The text to slugify.

    Returns:
        Lowercase, hyphenated slug.
    """
    text = text.lower().strip()
    # Remove scheme
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"[^\w\s-]", "-", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")[:100]  # Cap length
