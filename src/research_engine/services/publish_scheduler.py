"""PublishScheduler — assigns suggested_publish_date to briefs by priority.

Sorts briefs by opportunity_score descending, assigns round-robin with
configurable cadence (default 2/week), starting from next Monday.
New content before thin content updates.

TypeScript equivalent:
  modules/content-engine/research/services/publish-scheduler.ts
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.research_engine.models.content_brief import ContentBrief

logger = logging.getLogger(__name__)


def _next_monday(from_date: date) -> date:
    """Return the next Monday on or after from_date."""
    days_ahead = (7 - from_date.weekday()) % 7
    if days_ahead == 0 and from_date.weekday() != 0:
        days_ahead = 7
    return from_date + timedelta(days=days_ahead)


def _assign_dates(
    briefs: list[ContentBrief],
    start_date: date,
    cadence_per_week: int,
) -> list[ContentBrief]:
    """Assign publish dates to a list of briefs in order.

    Args:
        briefs: Briefs sorted by priority (highest first).
        start_date: First publish date (should be a Monday).
        cadence_per_week: Articles per week.

    Returns:
        Same briefs with suggested_publish_date set.
    """
    if cadence_per_week < 1:
        cadence_per_week = 1

    current_date = start_date
    slot_in_week = 0

    for brief in briefs:
        brief.suggested_publish_date = current_date.isoformat()
        slot_in_week += 1
        if slot_in_week >= cadence_per_week:
            slot_in_week = 0
            current_date += timedelta(weeks=1)

    return briefs


def schedule_publish_dates(
    briefs: list[ContentBrief],
    pipeline_run_date: date | None = None,
    cadence_per_week: int = 2,
    start_date: date | None = None,
) -> list[ContentBrief]:
    """Assign suggested_publish_date to each brief based on priority.

    New content briefs are scheduled before thin content updates.
    Within each group, sorted by opportunity_score descending.

    Args:
        briefs: List of ContentBrief records to schedule.
        pipeline_run_date: Date of pipeline run (for next-Monday calc).
        cadence_per_week: Articles per week (default 2).
        start_date: Explicit start date (overrides next-Monday calc).

    Returns:
        Briefs with suggested_publish_date populated.
    """
    from src.research_engine.models.content_brief import GapType

    if not briefs:
        return briefs

    # Determine start date
    if start_date is None:
        base = pipeline_run_date or date.today()
        start = _next_monday(base)
    else:
        start = start_date

    # Split new content vs thin content updates
    new_content = [
        b for b in briefs if b.gap_type in (GapType.OWN_GAP, GapType.NEW_OPPORTUNITY)
    ]
    thin_content = [b for b in briefs if b.gap_type == GapType.THIN_CONTENT]

    # Sort each group by opportunity_score descending
    new_content.sort(key=lambda b: b.opportunity_score, reverse=True)
    thin_content.sort(key=lambda b: b.opportunity_score, reverse=True)

    # Schedule new content first
    _assign_dates(new_content, start, cadence_per_week)

    # Continue thin content after new content
    if new_content and thin_content:
        # Calculate where new content ended
        last_new = date.fromisoformat(new_content[-1].suggested_publish_date)
        # Next available week
        thin_start = last_new + timedelta(weeks=1)
        _assign_dates(thin_content, thin_start, cadence_per_week)
    elif thin_content:
        _assign_dates(thin_content, start, cadence_per_week)

    logger.info(
        "Scheduled %d briefs: %d new content, %d thin content updates, "
        "cadence=%d/week, start=%s",
        len(briefs),
        len(new_content),
        len(thin_content),
        cadence_per_week,
        start.isoformat(),
    )

    return briefs
