"""Read queries for keyword data.

Thin query layer over the storage port. Keeps command/query
separation clean for future CQRS migration.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.research_engine.models.keyword import Keyword, KeywordGap
from src.research_engine.ports.storage import KeywordStoragePort


@dataclass
class GetKeywordsQuery:
    """Query for keywords by campaign with optional filters.

    Attributes:
        campaign_id: Campaign to query.
        locale: Optional locale filter.
        min_volume: Optional minimum volume filter.
        max_difficulty: Optional max difficulty filter.
    """

    campaign_id: str
    locale: str | None = None
    min_volume: int | None = None
    max_difficulty: int | None = None


def get_keywords(
    query: GetKeywordsQuery,
    storage: KeywordStoragePort,
) -> list[Keyword]:
    """Execute a keyword query against storage.

    Args:
        query: Query parameters.
        storage: Storage adapter.

    Returns:
        List of matching keywords.
    """
    return storage.get_by_campaign(
        campaign_id=query.campaign_id,
        locale=query.locale,
        min_volume=query.min_volume,
        max_difficulty=query.max_difficulty,
    )


def get_gaps(
    campaign_id: str,
    storage: KeywordStoragePort,
) -> list[KeywordGap]:
    """Get all gap records for a campaign.

    Args:
        campaign_id: Campaign to query.
        storage: Storage adapter.

    Returns:
        List of gap records.
    """
    return storage.get_gaps(campaign_id)
