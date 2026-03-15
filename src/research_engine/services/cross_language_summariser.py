"""Cross-language summariser for F-006 Content Gap Identification.

Groups gap records by keyword across languages to identify
universal gaps (all languages) vs language-specific gaps (ADR-F006-003).

TypeScript equivalent:
  modules/content-engine/research/services/cross-language-summariser.ts
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass

from src.research_engine.models.content_gap import (
    ContentGapRecord,
    CrossLanguageSummaryRecord,
    GapType,
)

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CrossLanguageSummaryOutput:
    """Output from cross-language summarisation.

    Attributes:
        summaries: Per-keyword summary records.
        universal_gap_keyword_ids: IDs of keywords that are universal gaps.
    """

    summaries: list[CrossLanguageSummaryRecord]
    universal_gap_keyword_ids: set[str]


def summarise_cross_language(
    gap_records: list[ContentGapRecord],
    languages: list[str],
    tenant_id: uuid.UUID,
    campaign_id: str,
    pipeline_run_id: str | None = None,
) -> CrossLanguageSummaryOutput:
    """Produce cross-language summary from per-language gap records.

    Groups gap records by keyword_id across languages. For each keyword:
    - If gap exists in ALL analysed languages → universal gap.
    - If gap exists in SOME languages → language-specific gap.
    - If covered in ALL languages → no summary needed.

    Args:
        gap_records: All gap records across all languages.
        languages: List of analysed languages.
        tenant_id: Tenant identifier.
        campaign_id: Campaign identifier.
        pipeline_run_id: Optional pipeline run ID.

    Returns:
        CrossLanguageSummaryOutput with summary records and universal gap IDs.
    """
    total_languages = len(languages)

    # Group records by keyword_id
    keyword_groups: dict[str, list[ContentGapRecord]] = defaultdict(list)
    for record in gap_records:
        keyword_groups[record.keyword_id].append(record)

    summaries: list[CrossLanguageSummaryRecord] = []
    universal_gap_ids: set[str] = set()

    for keyword_id, records in keyword_groups.items():
        # Get keyword text from first record
        keyword_text = records[0].keyword_text

        # Classify per language
        languages_with_gap: list[str] = []
        languages_with_coverage: list[str] = []

        for lang in languages:
            lang_records = [r for r in records if r.language == lang]
            if not lang_records:
                # No record for this language = gap
                languages_with_gap.append(lang)
                continue

            record = lang_records[0]
            if record.gap_type in (GapType.OWN_GAP, GapType.NEW_OPPORTUNITY):
                languages_with_gap.append(lang)
            else:
                languages_with_coverage.append(lang)

        # Determine if universal gap
        is_universal = (
            len(languages_with_gap) == total_languages and total_languages > 0
        )

        if is_universal:
            universal_gap_ids.add(keyword_id)

        # Only create summary if there's at least one gap
        if languages_with_gap:
            summary = CrossLanguageSummaryRecord(
                tenant_id=tenant_id,
                campaign_id=campaign_id,
                keyword_id=keyword_id,
                keyword_text=keyword_text,
                languages_with_gap=sorted(languages_with_gap),
                languages_with_coverage=sorted(languages_with_coverage),
                is_universal_gap=is_universal,
                total_languages_analysed=total_languages,
                pipeline_run_id=pipeline_run_id,
            )
            summaries.append(summary)

    logger.info(
        "Cross-language summary: %d keywords, %d universal gaps, "
        "%d language-specific gaps",
        len(keyword_groups),
        len(universal_gap_ids),
        len(summaries) - len(universal_gap_ids),
    )

    return CrossLanguageSummaryOutput(
        summaries=summaries,
        universal_gap_keyword_ids=universal_gap_ids,
    )
