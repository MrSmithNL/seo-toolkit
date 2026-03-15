"""Content Calendar event models for F-007.

Events emitted as structured JSON logs.
Same event names and payloads will be used when migrating to a real event bus.

TypeScript equivalent: modules/content-engine/research/events/calendar-events.ts
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


class CalendarGeneratedEvent(BaseModel):
    """Emitted when calendar generation completes."""

    type: str = "research.calendar.generated"
    tenant_id: uuid.UUID
    campaign_id: str
    calendar_batch_id: str
    brief_count: int
    languages: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=_now_utc)


class BriefApprovedEvent(BaseModel):
    """Emitted when a ContentBrief is approved."""

    type: str = "research.brief.approved"
    tenant_id: uuid.UUID
    brief_id: str
    keyword: str
    timestamp: datetime = Field(default_factory=_now_utc)


class BriefRejectedEvent(BaseModel):
    """Emitted when a ContentBrief is rejected."""

    type: str = "research.brief.rejected"
    tenant_id: uuid.UUID
    brief_id: str
    keyword: str
    timestamp: datetime = Field(default_factory=_now_utc)


class ApprovedBriefsExportedEvent(BaseModel):
    """Emitted when approved briefs are exported."""

    type: str = "research.calendar.approved_exported"
    tenant_id: uuid.UUID
    campaign_id: str
    brief_count: int
    output_path: str
    timestamp: datetime = Field(default_factory=_now_utc)


def emit_calendar_event(
    event: (
        CalendarGeneratedEvent
        | BriefApprovedEvent
        | BriefRejectedEvent
        | ApprovedBriefsExportedEvent
    ),
) -> None:
    """Emit a calendar event as a structured JSON log line."""
    logger.info(
        "Event: %s",
        event.model_dump_json(),
        extra={"event_type": event.type},
    )
