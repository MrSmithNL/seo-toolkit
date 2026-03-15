"""LanguageScheduler — multilingual calendar staggering.

For multilingual campaigns, groups briefs by keyword and staggers
languages across consecutive weeks to avoid publishing the same topic
in 9 languages in one week.

TypeScript equivalent:
  modules/content-engine/research/services/language-scheduler.ts
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.research_engine.models.content_brief import ContentBrief

logger = logging.getLogger(__name__)


def stagger_languages(
    briefs: list[ContentBrief],
    primary_language: str = "en",
) -> list[ContentBrief]:
    """Stagger multilingual briefs across weeks.

    Groups briefs by keyword. Within each keyword group:
    - Primary language gets the earliest assigned date (unchanged)
    - Each subsequent language is pushed 1 week later

    Args:
        briefs: Briefs already scheduled by PublishScheduler.
        primary_language: Language that publishes first (default "en").

    Returns:
        Same briefs with adjusted suggested_publish_date for non-primary languages.
    """
    if not briefs:
        return briefs

    # Group by keyword
    keyword_groups: dict[str, list[ContentBrief]] = defaultdict(list)
    for brief in briefs:
        keyword_groups[brief.target_keyword].append(brief)

    # Only stagger groups with multiple languages
    for _keyword, group in keyword_groups.items():
        languages = {b.target_language for b in group}
        if len(languages) <= 1:
            continue

        # Sort: primary language first, then alphabetically
        group.sort(
            key=lambda b: (
                0 if b.target_language == primary_language else 1,
                b.target_language,
            )
        )

        # Primary language keeps its date; others get +1 week per position
        base_date_str = group[0].suggested_publish_date
        base_date = date.fromisoformat(base_date_str)

        for i, brief in enumerate(group):
            if i == 0:
                continue  # primary keeps its date
            new_date = base_date + timedelta(weeks=i)
            brief.suggested_publish_date = new_date.isoformat()

    logger.info(
        "Language staggering applied: %d briefs, %d keyword groups",
        len(briefs),
        len(keyword_groups),
    )

    return briefs
