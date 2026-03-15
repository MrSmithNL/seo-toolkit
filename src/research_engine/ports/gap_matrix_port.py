"""Gap matrix storage port for F-006 Content Gap Identification.

Defines the interface for persisting and querying gap analysis results.

TypeScript equivalent: modules/content-engine/research/ports/gap-matrix-port.ts
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.research_engine.models.content_gap import (
    ContentGapRecord,
    CrossLanguageSummaryRecord,
    GapType,
)


@runtime_checkable
class GapMatrixPort(Protocol):
    """Interface for gap matrix persistence.

    Implementations:
    - FileGapMatrixRepo: JSON file storage (standalone mode)
    - DatabaseGapMatrixRepo: PostgreSQL (platform mode, R2+)
    """

    def save_gaps(self, gaps: list[ContentGapRecord]) -> int:
        """Save gap records, upserting by (keyword_id, language).

        Args:
            gaps: Gap records to persist.

        Returns:
            Number of records saved.
        """
        ...

    def save_summaries(self, summaries: list[CrossLanguageSummaryRecord]) -> int:
        """Save cross-language summary records.

        Args:
            summaries: Summary records to persist.

        Returns:
            Number of records saved.
        """
        ...

    def get_gap_matrix(
        self,
        campaign_id: str,
        language: str,
        gap_type: GapType | None = None,
        sort_by: str | None = None,
        min_score: float | None = None,
    ) -> list[ContentGapRecord]:
        """Query gap matrix with filters.

        Args:
            campaign_id: Campaign identifier.
            language: BCP 47 language code.
            gap_type: Optional filter by gap classification.
            sort_by: Optional sort field (e.g. 'opportunity_score').
            min_score: Optional minimum score threshold.

        Returns:
            Filtered and sorted gap records.
        """
        ...

    def get_top_opportunities(
        self,
        campaign_id: str,
        language: str,
        limit: int = 20,
    ) -> list[ContentGapRecord]:
        """Get top-scoring opportunities for F-007 consumption.

        Args:
            campaign_id: Campaign identifier.
            language: BCP 47 language code.
            limit: Maximum records to return.

        Returns:
            Top opportunities sorted by opportunity_score descending.
        """
        ...
