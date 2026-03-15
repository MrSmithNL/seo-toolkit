"""Pipeline orchestrator for F-006 Cross-Language Summary generation.

Runs after all per-language gap matrices are built.
Groups gap records across languages to identify universal vs
language-specific gaps (ADR-F006-003).

Zero LLM calls — pure computation.

TypeScript equivalent:
  modules/content-engine/research/commands/generate-cross-language-summary.ts
"""

from __future__ import annotations

import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from src.research_engine.events.gap_events import (
    CrossLanguageSummaryGeneratedEvent,
)
from src.research_engine.models.content_gap import ContentGapRecord
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.services.cross_language_summariser import (
    summarise_cross_language,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Command + Result data classes
# ---------------------------------------------------------------------------


@dataclass
class GenerateCrossLanguageSummaryCommand:
    """Input for cross-language summary generation.

    Attributes:
        tenant_id: Tenant identifier.
        campaign_id: Campaign identifier.
        languages: List of languages to summarise across.
        pipeline_run_id: Optional pipeline run ID for tracking.
    """

    tenant_id: uuid.UUID
    campaign_id: str
    languages: list[str]
    pipeline_run_id: str | None = None


@dataclass
class GenerateCrossLanguageSummaryResult:
    """Output from cross-language summary generation.

    Attributes:
        universal_gap_count: Keywords that are gaps in all languages.
        total_summaries: Total summary records produced.
        languages_analysed: Number of languages analysed.
        duration_seconds: Wall-clock time.
    """

    universal_gap_count: int
    total_summaries: int
    languages_analysed: int
    duration_seconds: float


# ---------------------------------------------------------------------------
# Command handler
# ---------------------------------------------------------------------------


def generate_cross_language_summary(
    cmd: GenerateCrossLanguageSummaryCommand,
    repo: Any,
    emit_event: Callable,
    feature_enabled: bool = True,
) -> Result[GenerateCrossLanguageSummaryResult, str]:
    """Execute cross-language summary generation.

    Steps:
    1. Feature flag check
    2. Load all gap records across languages
    3. Run cross-language summariser
    4. Persist summaries
    5. Emit event

    Args:
        cmd: Summary command with languages to analyse.
        repo: GapMatrixPort implementation.
        emit_event: Event emission callable.
        feature_enabled: Feature flag (default True).

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    if not feature_enabled:
        return Err("Feature flag FEATURE_CONTENT_GAP is disabled")

    start_time = time.monotonic()

    # Step 1: Load all gap records across languages
    all_records: list[ContentGapRecord] = []
    for lang in cmd.languages:
        records = repo.get_gap_matrix(cmd.campaign_id, lang)
        all_records.extend(records)

    # Step 2: Run cross-language summariser
    summary_output = summarise_cross_language(
        gap_records=all_records,
        languages=cmd.languages,
        tenant_id=cmd.tenant_id,
        campaign_id=cmd.campaign_id,
        pipeline_run_id=cmd.pipeline_run_id,
    )

    # Step 3: Persist summaries
    if summary_output.summaries:
        repo.save_summaries(summary_output.summaries)

    duration = round(time.monotonic() - start_time, 2)

    # Step 4: Emit event
    event = CrossLanguageSummaryGeneratedEvent(
        tenant_id=cmd.tenant_id,
        campaign_id=cmd.campaign_id,
        universal_gap_count=len(summary_output.universal_gap_keyword_ids),
        languages_analysed=len(cmd.languages),
    )
    emit_event(event)

    logger.info(
        "Cross-language summary: %d languages, %d universal gaps, "
        "%d total summaries, dur=%.1fs",
        len(cmd.languages),
        len(summary_output.universal_gap_keyword_ids),
        len(summary_output.summaries),
        duration,
    )

    return Ok(
        GenerateCrossLanguageSummaryResult(
            universal_gap_count=len(summary_output.universal_gap_keyword_ids),
            total_summaries=len(summary_output.summaries),
            languages_analysed=len(cmd.languages),
            duration_seconds=duration,
        )
    )
