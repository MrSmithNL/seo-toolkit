"""Competitor analysis event models for F-005.

Events emitted as structured JSON logs.
Same event names and payloads will be used when migrating
to a real event bus.

TypeScript equivalent: modules/content-engine/research/events/competitor-events.ts
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


class CompetitorAnalysisCompletedEvent(BaseModel):
    """Emitted when a single competitor page analysis completes.

    Consumed by F-006 (Content Gap Identification).
    """

    type: str = "research.competitor.analysed"
    tenant_id: uuid.UUID
    keyword_id: str
    snapshot_id: str
    crawl_status: str
    content_changed: bool
    timestamp: datetime = Field(default_factory=_now_utc)


class CompetitorBatchCompletedEvent(BaseModel):
    """Emitted when a batch competitor analysis completes."""

    type: str = "research.competitor.batch_completed"
    tenant_id: uuid.UUID
    pipeline_run_id: str
    total: int
    succeeded: int
    failed: int
    robots_blocked: int = 0
    llm_tokens_total: int = 0
    duration_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=_now_utc)


def emit_competitor_event(
    event: CompetitorAnalysisCompletedEvent | CompetitorBatchCompletedEvent,
) -> None:
    """Emit a competitor analysis event as a structured JSON log line.

    Args:
        event: The event to emit.
    """
    logger.info(
        "Event: %s",
        event.model_dump_json(),
        extra={"event_type": event.type},
    )
