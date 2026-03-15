"""CompetitorSnapshotPort protocol for F-005 snapshot storage.

Defines the interface for competitor snapshot persistence adapters.
Implemented by FileCompetitorSnapshotRepo (standalone) and
DatabaseCompetitorSnapshotRepo (platform mode, R2+).

TypeScript equivalent: modules/content-engine/research/ports/competitor-snapshot-port.ts
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.research_engine.models.competitor import (
    CompetitorBenchmark,
    CompetitorSnapshot,
)


@runtime_checkable
class CompetitorSnapshotPort(Protocol):
    """Protocol for competitor snapshot storage adapters."""

    def save_snapshot(self, snapshot: CompetitorSnapshot) -> str:
        """Persist a competitor snapshot (append-only).

        Args:
            snapshot: The snapshot to save.

        Returns:
            The snapshot ID.
        """
        ...

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
        ...

    def get_by_keyword(
        self,
        keyword_id: str,
        tenant_id: str,
    ) -> list[CompetitorBenchmark]:
        """Get competitor benchmarks for a keyword (F-006 consumer).

        Args:
            keyword_id: The keyword ID.
            tenant_id: Tenant UUID string.

        Returns:
            List of competitor benchmarks.
        """
        ...

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
        ...
