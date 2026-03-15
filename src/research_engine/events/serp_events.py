"""SERP analysis event models for F-004.

Events emitted as structured JSON logs for now.
Same event names and payloads will be used when migrating
to a real event bus.

TypeScript equivalent: modules/content-engine/research/events/serp-events.ts
"""

from __future__ import annotations

import logging
import uuid
from datetime import UTC, datetime

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(tz=UTC)


class SerpAnalysisCompletedEvent(BaseModel):
    """Emitted when a single SERP analysis completes.

    Consumed by F-005 (Competitor Content Analysis),
    F-006 (Content Gap Identification), and F-007 (Priority Scoring).
    """

    type: str = "research.serp.analysis_completed"
    tenant_id: uuid.UUID
    keyword_text: str
    language: str
    snapshot_id: str
    from_cache: bool
    has_ai_overview: bool = False
    warnings: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=_now_utc)


class SerpDailyLimitReachedEvent(BaseModel):
    """Emitted when the daily SERP request limit is reached.

    Remaining keywords are queued for the next day.
    """

    type: str = "research.serp.daily_limit_reached"
    tenant_id: uuid.UUID
    source: str
    daily_limit: int
    keywords_queued: int
    timestamp: datetime = Field(default_factory=_now_utc)


def emit_serp_event(
    event: SerpAnalysisCompletedEvent | SerpDailyLimitReachedEvent,
) -> None:
    """Emit a SERP event as a structured JSON log line.

    Args:
        event: The event to emit.
    """
    logger.info(
        "Event: %s",
        event.model_dump_json(),
        extra={"event_type": event.type},
    )
