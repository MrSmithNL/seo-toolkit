"""KeywordStoragePort protocol for keyword persistence.

Both SQLite and JSON file adapters implement this protocol.
Mirrors the TypeScript KeywordStoragePort interface.
"""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from src.research_engine.models.keyword import Keyword, KeywordGap


@runtime_checkable
class KeywordStoragePort(Protocol):
    """Protocol for keyword storage adapters."""

    def save(self, keywords: list[Keyword]) -> int:
        """Save keywords (upsert by campaign_id + normalized_key).

        Args:
            keywords: List of keywords to persist.

        Returns:
            Number of keywords saved/updated.
        """
        ...

    def get_by_campaign(
        self,
        campaign_id: str,
        locale: str | None = None,
        min_volume: int | None = None,
        max_difficulty: int | None = None,
    ) -> list[Keyword]:
        """Query keywords with optional filters.

        Args:
            campaign_id: Campaign to query.
            locale: Optional locale filter.
            min_volume: Optional minimum volume filter.
            max_difficulty: Optional max difficulty filter.

        Returns:
            Filtered list of keywords.
        """
        ...

    def save_gaps(self, gaps: list[KeywordGap]) -> int:
        """Save keyword gap records.

        Args:
            gaps: List of gap records.

        Returns:
            Number of gaps saved.
        """
        ...

    def get_gaps(self, campaign_id: str) -> list[KeywordGap]:
        """Get all gap records for a campaign.

        Args:
            campaign_id: Campaign to query.

        Returns:
            List of gap records.
        """
        ...

    def update_intent_fields(
        self,
        keyword_id: str,
        intent: str,
        intent_confidence: str,
        intent_rationale: str,
        recommended_format: str,
        format_signal: str | None,
        classified_at: datetime,
    ) -> bool:
        """Update intent classification fields on a keyword.

        Args:
            keyword_id: ID of the keyword to update.
            intent: Intent type string.
            intent_confidence: Confidence level string.
            intent_rationale: One-sentence rationale.
            recommended_format: Content format string.
            format_signal: Detected signal or None.
            classified_at: When classification was performed.

        Returns:
            True if keyword was found and updated.
        """
        ...
