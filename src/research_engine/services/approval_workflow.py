"""ApprovalWorkflow — approve/reject/export with state machine.

State machine:
  pending_review → approved → in_progress → published
  pending_review → rejected

Triple validation: on creation, on approval/rejection, on export.

TypeScript equivalent:
  modules/content-engine/research/services/approval-workflow.ts
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import ValidationError

from src.research_engine.models.content_brief import (
    SCHEMA_VERSION,
    ApprovedBriefsFile,
    BriefStatus,
    ContentBrief,
)
from src.research_engine.models.result import Err, Ok, Result

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Valid state transitions
# ---------------------------------------------------------------------------

_VALID_TRANSITIONS: dict[BriefStatus, set[BriefStatus]] = {
    BriefStatus.PENDING_REVIEW: {BriefStatus.APPROVED, BriefStatus.REJECTED},
    BriefStatus.APPROVED: {BriefStatus.IN_PROGRESS},
    BriefStatus.REJECTED: set(),
    BriefStatus.IN_PROGRESS: {BriefStatus.PUBLISHED},
    BriefStatus.PUBLISHED: set(),
}


def _validate_transition(current: BriefStatus, target: BriefStatus) -> str | None:
    """Return error message if transition is invalid, None if valid."""
    allowed = _VALID_TRANSITIONS.get(current, set())
    if target not in allowed:
        return (
            f"Invalid status transition: {current.value} → {target.value}. "
            f"Allowed transitions from {current.value}: "
            f"{', '.join(s.value for s in allowed) or 'none'}."
        )
    return None


# ---------------------------------------------------------------------------
# Approve brief
# ---------------------------------------------------------------------------


def approve_brief(
    brief: ContentBrief,
    reviewed_by: str,
    review_notes: str | None = None,
    overridden_word_count: int | None = None,
    overridden_publish_date: str | None = None,
) -> Result[ContentBrief, str]:
    """Approve a ContentBrief.

    Sets status to approved, populates audit fields, applies overrides.
    Validates the resulting brief against the schema.

    Returns:
        Ok(brief) on success, Err(message) on failure.
    """
    error = _validate_transition(brief.status, BriefStatus.APPROVED)
    if error:
        return Err(error)

    try:
        updated = brief.model_copy(
            update={
                "status": BriefStatus.APPROVED,
                "reviewed_by": reviewed_by,
                "reviewed_at": datetime.now(tz=UTC),
                "review_notes": review_notes,
                "overridden_word_count": overridden_word_count,
                "overridden_publish_date": overridden_publish_date,
            }
        )
        # Re-validate (triple validation step 2)
        ContentBrief.model_validate(updated.model_dump(mode="json"))
        return Ok(updated)
    except ValidationError as e:
        return Err(f"Validation failed on approve: {e}")


# ---------------------------------------------------------------------------
# Reject brief
# ---------------------------------------------------------------------------


def reject_brief(
    brief: ContentBrief,
    reviewed_by: str,
    review_notes: str | None = None,
) -> Result[ContentBrief, str]:
    """Reject a ContentBrief.

    Sets status to rejected, populates audit fields.
    """
    error = _validate_transition(brief.status, BriefStatus.REJECTED)
    if error:
        return Err(error)

    try:
        updated = brief.model_copy(
            update={
                "status": BriefStatus.REJECTED,
                "reviewed_by": reviewed_by,
                "reviewed_at": datetime.now(tz=UTC),
                "review_notes": review_notes,
            }
        )
        ContentBrief.model_validate(updated.model_dump(mode="json"))
        return Ok(updated)
    except ValidationError as e:
        return Err(f"Validation failed on reject: {e}")


# ---------------------------------------------------------------------------
# Export approved briefs
# ---------------------------------------------------------------------------


def export_approved_briefs(
    briefs: list[ContentBrief],
    campaign_id: str,
    output_path: Path | None = None,
) -> Result[Path, str]:
    """Export only approved briefs to a JSON file.

    Validates every brief against schema before writing.
    Rejected and pending briefs are excluded.

    Returns:
        Ok(path) on success, Err(message) on failure.
    """
    approved = [b for b in briefs if b.status == BriefStatus.APPROVED]

    # Validate each approved brief (triple validation step 3)
    for i, brief in enumerate(approved):
        try:
            ContentBrief.model_validate(brief.model_dump(mode="json"))
        except ValidationError as e:
            return Err(f"Invalid ContentBrief at index {i}: {e}")

    try:
        file = ApprovedBriefsFile(
            schema_version=SCHEMA_VERSION,
            generated_at=datetime.now(tz=UTC),
            campaign_id=campaign_id,
            briefs=approved,
        )
    except ValidationError as e:
        return Err(f"ApprovedBriefsFile validation failed: {e}")

    if output_path is None:
        output_path = Path(
            f"approved-briefs-{datetime.now(tz=UTC).strftime('%Y-%m-%d')}.json"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        file.model_dump_json(indent=2),
        encoding="utf-8",
    )

    logger.info(
        "Exported %d approved briefs to %s",
        len(approved),
        output_path,
    )

    return Ok(output_path)


# ---------------------------------------------------------------------------
# Load and validate from JSON file
# ---------------------------------------------------------------------------


def load_briefs_from_json(json_path: Path) -> Result[list[ContentBrief], str]:
    """Load ContentBrief records from a JSON file with validation.

    Returns:
        Ok(list) on success, Err(message) on failure.
    """
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return Err(f"Failed to read JSON: {e}")

    if not isinstance(data, list):
        return Err("Expected a JSON array of ContentBrief records")

    briefs: list[ContentBrief] = []
    for i, item in enumerate(data):
        try:
            brief = ContentBrief.model_validate(item)
            briefs.append(brief)
        except ValidationError as e:
            return Err(f"Invalid ContentBrief at index {i}: {e}")

    return Ok(briefs)
