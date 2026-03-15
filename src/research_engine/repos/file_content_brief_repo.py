"""File-based ContentBrief repository for standalone mode.

Stores briefs as individual JSON files under data/calendar/{domain}/briefs/.

TypeScript equivalent:
  modules/content-engine/research/repos/file-content-brief-repo.ts
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.research_engine.models.content_brief import BriefStatus, ContentBrief

logger = logging.getLogger(__name__)


class FileContentBriefRepo:
    """File-based ContentBrief storage.

    Each brief stored as {brief_id}.json.
    Supports: save, get_by_batch, get_by_status, update.
    """

    def __init__(self, data_dir: Path, domain: str) -> None:
        """Initialise repo with data directory and domain."""
        self.briefs_dir = data_dir / "calendar" / domain / "briefs"
        self.briefs_dir.mkdir(parents=True, exist_ok=True)

    def _brief_path(self, brief_id: str) -> Path:
        return self.briefs_dir / f"{brief_id}.json"

    def save_brief(self, brief: ContentBrief) -> None:
        """Save a single brief to file."""
        path = self._brief_path(brief.id)
        path.write_text(
            brief.model_dump_json(indent=2),
            encoding="utf-8",
        )

    def save_briefs(self, briefs: list[ContentBrief]) -> int:
        """Save multiple briefs. Returns count saved."""
        for brief in briefs:
            self.save_brief(brief)
        return len(briefs)

    def get_brief(self, brief_id: str) -> ContentBrief | None:
        """Get a brief by ID. Returns None if not found."""
        path = self._brief_path(brief_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        return ContentBrief.model_validate(data)

    def get_by_batch(self, calendar_batch_id: str | None = None) -> list[ContentBrief]:
        """Get all briefs, optionally filtered by batch.

        Without batch filter, returns all briefs in the directory.
        """
        briefs: list[ContentBrief] = []
        for path in sorted(self.briefs_dir.glob("cb_*.json")):
            data = json.loads(path.read_text(encoding="utf-8"))
            brief = ContentBrief.model_validate(data)
            briefs.append(brief)
        return briefs

    def get_by_status(self, status: BriefStatus) -> list[ContentBrief]:
        """Get all briefs with a specific status."""
        return [b for b in self.get_by_batch() if b.status == status]

    def update_brief(self, brief: ContentBrief) -> None:
        """Update an existing brief (overwrite file)."""
        self.save_brief(brief)

    def delete_all(self) -> int:
        """Delete all brief files. Returns count deleted."""
        count = 0
        for path in self.briefs_dir.glob("cb_*.json"):
            path.unlink()
            count += 1
        return count
