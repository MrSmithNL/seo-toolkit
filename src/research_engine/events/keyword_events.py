"""Keyword research event models.

Events emitted as structured JSON logs for now.
Same event names and payloads will be used when migrating
to a real event bus.
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


class KeywordResearchCompletedEvent(BaseModel):
    """Emitted when F-001 pipeline completes successfully.

    Consumed by F-002 (Clustering) and F-003 (Intent Classification).
    """

    type: str = "research.keywords.completed"
    tenant_id: uuid.UUID
    campaign_id: str
    run_id: str
    keyword_count: int
    locales: list[str]
    timestamp: datetime = Field(default_factory=_now_utc)


def emit_event(event: KeywordResearchCompletedEvent) -> None:
    """Emit an event as a structured JSON log line.

    Args:
        event: The event to emit.
    """
    logger.info(
        "Event: %s",
        event.model_dump_json(),
        extra={"event_type": event.type, "run_id": event.run_id},
    )
