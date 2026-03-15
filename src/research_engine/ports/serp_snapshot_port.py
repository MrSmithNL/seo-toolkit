"""SerpSnapshotPort protocol for SERP snapshot storage.

Defines the interface for SERP snapshot persistence adapters.
Implemented by FileSerpSnapshotRepo (standalone) and
DatabaseSerpSnapshotRepo (platform mode, R2+).

TypeScript equivalent: modules/content-engine/research/ports/serp-snapshot-port.ts
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.research_engine.models.serp import SerpResult, SerpSnapshot


@runtime_checkable
class SerpSnapshotPort(Protocol):
    """Protocol for SERP snapshot storage adapters."""

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
        ...

    def get_latest(
        self,
        keyword_text: str,
        language: str,
        tenant_id: str,
        *,
        max_age_days: int = 7,
    ) -> SerpSnapshot | None:
        """Get the most recent snapshot for a keyword.

        Returns None if no snapshot exists or the latest is older than max_age_days.

        Args:
            keyword_text: The keyword to look up.
            language: BCP 47 language code.
            tenant_id: Tenant UUID string.
            max_age_days: Maximum age in days for cache validity.

        Returns:
            The latest snapshot, or None.
        """
        ...

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
        ...

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
        ...
