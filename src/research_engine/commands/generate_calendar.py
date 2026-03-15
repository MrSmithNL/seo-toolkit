"""Pipeline orchestrator for F-007 Content Calendar generation.

Orchestrates the full content calendar flow:
  load gap data → build ContentBriefs → get LLM recommendations →
  schedule publish dates → stagger languages → render output → persist → emit event.

TypeScript equivalent:
  modules/content-engine/research/commands/generate-calendar.ts
"""

from __future__ import annotations

import logging
import math
import time
import uuid
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

from src.research_engine.events.calendar_events import (
    CalendarGeneratedEvent,
    emit_calendar_event,
)
from src.research_engine.models.content_brief import (
    ContentBrief,
    ContentType,
    GapType,
    SearchIntent,
)
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.services.calendar_renderer import write_calendar_files
from src.research_engine.services.language_scheduler import stagger_languages
from src.research_engine.services.publish_scheduler import schedule_publish_dates
from src.research_engine.services.rationale_builder import (
    build_aiso_only_rationale,
    build_new_content_rationale,
    build_thin_content_rationale,
)
from src.research_engine.services.recommendation_engine import get_recommendations

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Input types (from upstream pipeline data)
# ---------------------------------------------------------------------------


@dataclass
class GapInput:
    """Gap record from F-006 for calendar generation."""

    keyword_text: str
    keyword_id: str
    language: str
    gap_type: str
    volume: int = 0
    difficulty: int = 0
    opportunity_score: float = 0.0
    our_ranking_position: int | None = None
    our_page_url: str | None = None
    our_word_count: int | None = None
    competitor_avg_word_count: int = 0
    competitor_depth_scores: list[int] = field(default_factory=list)
    top_competitor_url: str | None = None
    competitor_schema_types: list[str] = field(default_factory=list)
    competitors_have_faq: bool = False
    competitor_headings: list[list[str]] = field(default_factory=list)
    search_intent: str = "informational"
    topic_cluster: str | None = None


# ---------------------------------------------------------------------------
# Command + Result
# ---------------------------------------------------------------------------


@dataclass
class GenerateCalendarCommand:
    """Input for content calendar generation.

    Attributes:
        tenant_id: Tenant identifier.
        campaign_id: Campaign identifier.
        domain: User's domain (for file paths).
        gap_data: Gap records from F-006.
        pipeline_run_date: Date the pipeline ran (default: today).
        cadence_per_week: Articles per week (default: 2).
        primary_language: Primary language code (default: en).
        output_dir: Base output directory.
    """

    tenant_id: uuid.UUID
    campaign_id: str
    domain: str
    gap_data: list[GapInput]
    pipeline_run_date: date | None = None
    cadence_per_week: int = 2
    primary_language: str = "en"
    output_dir: Path | None = None


@dataclass
class GenerateCalendarResult:
    """Output from calendar generation."""

    brief_count: int
    new_content_count: int
    thin_content_count: int
    languages: list[str]
    calendar_batch_id: str
    markdown_path: Path | None = None
    json_path: Path | None = None
    duration_seconds: float = 0.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_GAP_TYPE_MAP = {
    "own_gap": GapType.OWN_GAP,
    "thin_content": GapType.THIN_CONTENT,
    "new_opportunity": GapType.NEW_OPPORTUNITY,
}

_INTENT_MAP = {
    "informational": SearchIntent.INFORMATIONAL,
    "transactional": SearchIntent.TRANSACTIONAL,
    "navigational": SearchIntent.NAVIGATIONAL,
    "commercial": SearchIntent.COMMERCIAL,
}


def _compute_rec_word_count(competitor_avg: int) -> int:
    """10% above competitor average, rounded to nearest 100. Min 300."""
    if competitor_avg <= 0:
        return 300
    raw = competitor_avg * 1.1
    return max(100, int(math.ceil(raw / 100) * 100))


def _build_rationale(gap: GapInput) -> str:
    """Build rationale string from gap input."""
    if gap.volume == 0:
        return build_aiso_only_rationale(
            score=gap.opportunity_score,
            difficulty=gap.difficulty,
        )
    if gap.gap_type == "thin_content":
        return build_thin_content_rationale(
            score=gap.opportunity_score,
            our_position=gap.our_ranking_position or 0,
            our_word_count=gap.our_word_count or 0,
            competitor_avg_word_count=gap.competitor_avg_word_count,
        )
    return build_new_content_rationale(
        score=gap.opportunity_score,
        volume=gap.volume,
        difficulty=gap.difficulty,
        competitor_best_position=None,
    )


def _build_brief_from_gap(gap: GapInput, tenant_id: uuid.UUID) -> ContentBrief:
    """Build a ContentBrief directly from a GapInput."""
    gap_type = _GAP_TYPE_MAP.get(gap.gap_type, GapType.NEW_OPPORTUNITY)
    intent = _INTENT_MAP.get(gap.search_intent, SearchIntent.INFORMATIONAL)
    existing_url = gap.our_page_url if gap.gap_type == "thin_content" else None

    return ContentBrief(
        tenant_id=tenant_id,
        target_keyword=gap.keyword_text,
        target_language=gap.language,
        target_country=gap.language.upper()[:2] if len(gap.language) >= 2 else "XX",
        search_intent=intent,
        topic_cluster=gap.topic_cluster,
        content_type=ContentType.BLOG_POST,  # overridden by recommendations
        keyword_volume=gap.volume,
        keyword_difficulty=gap.difficulty,
        opportunity_score=gap.opportunity_score,
        opportunity_score_rationale=_build_rationale(gap),
        gap_type=gap_type,
        existing_page_url=existing_url,
        competitor_avg_word_count=gap.competitor_avg_word_count,
        competitor_depth_scores=gap.competitor_depth_scores,
        top_competitor_url=gap.top_competitor_url,
        competitor_schema_types=gap.competitor_schema_types,
        competitors_have_faq=gap.competitors_have_faq,
        recommended_word_count=_compute_rec_word_count(gap.competitor_avg_word_count),
        include_faq=gap.competitors_have_faq or intent == SearchIntent.INFORMATIONAL,
        suggested_publish_date="2026-01-01",  # placeholder, overridden by scheduler
    )


# ---------------------------------------------------------------------------
# Command handler
# ---------------------------------------------------------------------------


def generate_calendar(
    cmd: GenerateCalendarCommand,
    llm: Any | None = None,
    repo: Any | None = None,
    feature_enabled: bool = True,
) -> Result[GenerateCalendarResult, str]:
    """Execute content calendar generation.

    Steps:
    1. Feature flag check
    2. Build ContentBriefs from gap data
    3. Get LLM recommendations (with fallback)
    4. Schedule publish dates
    5. Stagger languages
    6. Render Markdown + JSON output
    7. Persist briefs (if repo provided)
    8. Emit CalendarGenerated event

    Args:
        cmd: Generation command with gap data.
        llm: Optional LlmGateway for recommendations.
        repo: Optional FileContentBriefRepo for persistence.
        feature_enabled: Feature flag check.

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    if not feature_enabled:
        return Err("Feature flag FEATURE_CONTENT_CALENDAR is disabled")

    start_time = time.monotonic()
    calendar_batch_id = f"cal_{uuid.uuid4().hex[:12]}"

    if not cmd.gap_data:
        return Ok(
            GenerateCalendarResult(
                brief_count=0,
                new_content_count=0,
                thin_content_count=0,
                languages=[],
                calendar_batch_id=calendar_batch_id,
            )
        )

    run_date = cmd.pipeline_run_date or date.today()

    # Step 2: Build ContentBriefs from GapInput
    briefs: list[ContentBrief] = []
    for gap in cmd.gap_data:
        brief = _build_brief_from_gap(gap, cmd.tenant_id)
        briefs.append(brief)

    # Step 3: LLM recommendations (best-effort, with fallback)
    for i, brief in enumerate(briefs):
        gap = cmd.gap_data[i]
        rec = get_recommendations(
            keyword=brief.target_keyword,
            intent=brief.search_intent,
            competitor_headings=gap.competitor_headings,
            competitor_schema_types=gap.competitor_schema_types,
            llm=llm,
        )
        briefs[i] = brief.model_copy(
            update={
                "content_type": rec.content_type,
                "recommended_headings": rec.recommended_headings,
                "recommended_schema_types": rec.recommended_schema_types,
            }
        )

    # Step 4: Schedule publish dates
    briefs = schedule_publish_dates(
        briefs,
        pipeline_run_date=run_date,
        cadence_per_week=cmd.cadence_per_week,
    )

    # Step 5: Stagger languages
    briefs = stagger_languages(
        briefs,
        primary_language=cmd.primary_language,
    )

    # Step 6: Render output
    md_path: Path | None = None
    json_path: Path | None = None
    if cmd.output_dir:
        output = cmd.output_dir / "calendar" / cmd.domain
        md_path, json_path = write_calendar_files(briefs, output, run_date.isoformat())

    # Step 7: Persist
    if repo is not None:
        repo.save_briefs(briefs)

    # Compute counts
    new_types = {GapType.OWN_GAP, GapType.NEW_OPPORTUNITY}
    new_count = sum(1 for b in briefs if b.gap_type in new_types)
    thin_count = sum(1 for b in briefs if b.gap_type == GapType.THIN_CONTENT)
    languages = sorted({b.target_language for b in briefs})

    duration = round(time.monotonic() - start_time, 2)

    # Step 8: Emit event
    event = CalendarGeneratedEvent(
        tenant_id=cmd.tenant_id,
        campaign_id=cmd.campaign_id,
        calendar_batch_id=calendar_batch_id,
        brief_count=len(briefs),
        languages=languages,
    )
    emit_calendar_event(event)

    logger.info(
        "Calendar generated: domain=%s briefs=%d new=%d thin=%d "
        "languages=%s dur=%.1fs",
        cmd.domain,
        len(briefs),
        new_count,
        thin_count,
        languages,
        duration,
    )

    return Ok(
        GenerateCalendarResult(
            brief_count=len(briefs),
            new_content_count=new_count,
            thin_content_count=thin_count,
            languages=languages,
            calendar_batch_id=calendar_batch_id,
            markdown_path=md_path,
            json_path=json_path,
            duration_seconds=duration,
        )
    )
