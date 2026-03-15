"""File-based gap matrix repository for F-006 Content Gap Identification.

Standalone mode: saves gap matrix to data/gap-analysis/{domain}/{language}.json

TypeScript equivalent: modules/content-engine/research/repos/file-gap-matrix-repo.ts
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from src.research_engine.models.content_gap import (
    ContentGapRecord,
    CrossLanguageSummaryRecord,
    GapType,
)

logger = logging.getLogger(__name__)


class FileGapMatrixRepo:
    """File-based implementation of GapMatrixPort.

    Stores gap records as JSON files organised by domain and language.
    Supports upsert by (keyword_id, language) to prevent duplicates.
    """

    def __init__(self, data_dir: Path, domain: str) -> None:
        """Initialise file repository.

        Args:
            data_dir: Root data directory (e.g., Path("data/gap-analysis")).
            domain: User's domain for directory organisation.
        """
        self._data_dir = data_dir / domain
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._domain = domain

    def save_gaps(self, gaps: list[ContentGapRecord]) -> int:
        """Save gap records, upserting by (keyword_id, language).

        Groups records by language and writes one JSON file per language.
        """
        if not gaps:
            return 0

        # Group by language
        by_language: dict[str, list[ContentGapRecord]] = {}
        for gap in gaps:
            by_language.setdefault(gap.language, []).append(gap)

        total_saved = 0
        for language, records in by_language.items():
            file_path = self._data_dir / f"{language}.json"

            # Load existing records
            existing = self._load_records(file_path)

            # Build index for upsert
            index = {(r.keyword_id, r.language): r for r in existing}

            # Upsert new records
            for record in records:
                index[(record.keyword_id, record.language)] = record
                total_saved += 1

            # Write back
            self._write_records(file_path, list(index.values()))

        logger.info("Saved %d gap records for domain=%s", total_saved, self._domain)
        return total_saved

    def save_summaries(self, summaries: list[CrossLanguageSummaryRecord]) -> int:
        """Save cross-language summary records."""
        if not summaries:
            return 0

        file_path = self._data_dir / "cross_language_summary.json"

        # Load existing
        existing_data = []
        if file_path.exists():
            existing_data = json.loads(file_path.read_text(encoding="utf-8"))

        # Build index for upsert
        index = {item.get("keyword_id", ""): item for item in existing_data}
        for summary in summaries:
            index[summary.keyword_id] = summary.model_dump(mode="json")

        file_path.write_text(
            json.dumps(list(index.values()), indent=2, default=str),
            encoding="utf-8",
        )

        logger.info(
            "Saved %d cross-language summaries for domain=%s",
            len(summaries),
            self._domain,
        )
        return len(summaries)

    def get_gap_matrix(
        self,
        campaign_id: str,
        language: str,
        gap_type: GapType | None = None,
        sort_by: str | None = None,
        min_score: float | None = None,
    ) -> list[ContentGapRecord]:
        """Query gap matrix with filters."""
        file_path = self._data_dir / f"{language}.json"
        records = self._load_records(file_path)

        # Filter by campaign
        records = [r for r in records if r.campaign_id == campaign_id]

        # Filter by gap_type
        if gap_type is not None:
            records = [r for r in records if r.gap_type == gap_type]

        # Filter by min_score
        if min_score is not None:
            records = [
                r
                for r in records
                if (
                    r.opportunity_score is not None and r.opportunity_score >= min_score
                )
                or (
                    r.thin_content_priority_score is not None
                    and r.thin_content_priority_score >= min_score
                )
            ]

        # Sort
        if sort_by == "opportunity_score":
            records.sort(key=lambda r: r.opportunity_score or 0.0, reverse=True)
        elif sort_by == "thin_content_priority_score":
            records.sort(
                key=lambda r: r.thin_content_priority_score or 0.0,
                reverse=True,
            )

        return records

    def get_top_opportunities(
        self,
        campaign_id: str,
        language: str,
        limit: int = 20,
    ) -> list[ContentGapRecord]:
        """Get top opportunities sorted by score."""
        records = self.get_gap_matrix(
            campaign_id=campaign_id,
            language=language,
            sort_by="opportunity_score",
        )
        # Include own_gap and new_opportunity only
        records = [
            r
            for r in records
            if r.gap_type in (GapType.OWN_GAP, GapType.NEW_OPPORTUNITY)
        ]
        return records[:limit]

    def _load_records(self, file_path: Path) -> list[ContentGapRecord]:
        """Load gap records from a JSON file."""
        if not file_path.exists():
            return []

        data = json.loads(file_path.read_text(encoding="utf-8"))
        return [ContentGapRecord.model_validate(item) for item in data]

    def _write_records(self, file_path: Path, records: list[ContentGapRecord]) -> None:
        """Write gap records to a JSON file."""
        data = [r.model_dump(mode="json") for r in records]
        file_path.write_text(
            json.dumps(data, indent=2, default=str),
            encoding="utf-8",
        )
