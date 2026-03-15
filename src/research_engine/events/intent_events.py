"""Intent classification event models.

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


class IntentClassificationCompletedEvent(BaseModel):
    """Emitted when F-003 intent classification pipeline completes.

    Consumed by F-007 (Content Calendar) and monitoring.
    """

    type: str = "research.intent.completed"
    tenant_id: uuid.UUID
    campaign_id: str
    run_id: str
    locale: str
    keywords_classified: int
    intent_distribution: dict[str, int]
    timestamp: datetime = Field(default_factory=_now_utc)


def emit_intent_event(event: IntentClassificationCompletedEvent) -> None:
    """Emit an intent classification event as structured JSON log.

    Args:
        event: The event to emit.
    """
    logger.info(
        "Event: %s",
        event.model_dump_json(),
        extra={"event_type": event.type, "run_id": event.run_id},
    )
