"""Keyword gap analysis between our domain and competitors.

Compares our keyword set against competitor keyword/position data
to identify gaps (keywords they rank for that we don't).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from src.research_engine.models.keyword import KeywordGap


@dataclass(frozen=True)
class CompetitorKeyword:
    """A keyword that a competitor ranks for.

    Attributes:
        domain: Competitor domain.
        keyword: The keyword term (normalised).
        position: SERP position (1-based).
        url: Ranking URL (optional).
    """

    domain: str
    keyword: str
    position: int
    url: str | None = None


def analyse_gaps(
    our_keywords: set[str],
    competitor_keywords: list[CompetitorKeyword],
    campaign_id: str,
    tenant_id: uuid.UUID,
) -> list[KeywordGap]:
    """Identify keyword gaps between our site and competitors.

    A gap exists when a competitor ranks for a keyword that we don't.

    Args:
        our_keywords: Set of normalised keywords we rank for.
        competitor_keywords: List of competitor keyword/position data.
        campaign_id: Campaign ID for the gap records.
        tenant_id: Tenant ID for the gap records.

    Returns:
        List of KeywordGap records for keywords we don't rank for.
    """
    our_normalised = {kw.lower().strip() for kw in our_keywords}
    gaps: list[KeywordGap] = []

    for ck in competitor_keywords:
        normalised = ck.keyword.lower().strip()
        if normalised not in our_normalised:
            gaps.append(
                KeywordGap(
                    tenant_id=tenant_id,
                    campaign_id=campaign_id,
                    keyword_id=f"kw_gap_{uuid.uuid4().hex[:8]}",
                    competitor_domain=ck.domain,
                    competitor_url=ck.url,
                    competitor_position=ck.position,
                    our_position=None,
                )
            )

    return gaps
