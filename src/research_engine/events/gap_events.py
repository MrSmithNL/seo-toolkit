"""Content Gap analysis event models for F-006.

Events emitted as structured JSON logs.
Same event names and payloads will be used when migrating
to a real event bus.

TypeScript equivalent: modules/content-engine/research/events/gap-events.ts
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


class GapMatrixGeneratedEvent(BaseModel):
    """Emitted when a per-language gap matrix generation completes.

    Consumed by F-007 (Content Calendar), monitoring.
    """

    type: str = "research.gap.matrix_generated"
    tenant_id: uuid.UUID
    campaign_id: str
    language: str
    own_gap_count: int
    thin_content_count: int
    new_opportunity_count: int
    own_coverage_count: int
    coverage_source: str
    duration_seconds: float = 0.0
    timestamp: datetime = Field(default_factory=_now_utc)


class CrossLanguageSummaryGeneratedEvent(BaseModel):
    """Emitted when cross-language summarisation completes."""

    type: str = "research.gap.cross_language_summary"
    tenant_id: uuid.UUID
    campaign_id: str
    universal_gap_count: int
    languages_analysed: int
    timestamp: datetime = Field(default_factory=_now_utc)


def emit_gap_event(
    event: GapMatrixGeneratedEvent | CrossLanguageSummaryGeneratedEvent,
) -> None:
    """Emit a gap analysis event as a structured JSON log line.

    Args:
        event: The event to emit.
    """
    logger.info(
        "Event: %s",
        event.model_dump_json(),
        extra={"event_type": event.type},
    )
