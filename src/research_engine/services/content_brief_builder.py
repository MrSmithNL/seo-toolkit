"""ContentBriefBuilder — assembles ContentBrief records from pipeline data.

Takes gap record (F-006), keyword (F-001), competitor benchmarks (F-005),
intent (F-003). Computes derived fields: recommended_word_count, include_faq,
existing_page_url.

TypeScript equivalent:
  modules/content-engine/research/services/content-brief-builder.ts
"""

from __future__ import annotations

import logging
import math
import uuid
from typing import TYPE_CHECKING

from src.research_engine.models.content_brief import (
    SCHEMA_VERSION,
    BriefStatus,
    ContentBrief,
    ContentType,
    GapType,
    SearchIntent,
)
from src.research_engine.services.rationale_builder import (
    build_aiso_only_rationale,
    build_new_content_rationale,
    build_thin_content_rationale,
)

if TYPE_CHECKING:
    from src.research_engine.models.competitor import CompetitorBenchmark
    from src.research_engine.models.content_gap import ContentGapRecord

logger = logging.getLogger(__name__)


def _compute_recommended_word_count(competitor_avg: int) -> int:
    """10% above competitor average, rounded to nearest 100. Min 300."""
    if competitor_avg <= 0:
        return 300
    raw = competitor_avg * 1.1
    return max(100, int(math.ceil(raw / 100) * 100))


def _determine_include_faq(
    competitors_have_faq: bool,
    search_intent: SearchIntent,
) -> bool:
    """FAQ recommended if competitors have FAQ OR intent is informational."""
    return competitors_have_faq or search_intent == SearchIntent.INFORMATIONAL


def _build_rationale(
    gap: ContentGapRecord,
    competitor_best_position: int | None,
) -> str:
    """Build opportunity score rationale based on gap type."""
    score = gap.opportunity_score or 0.0
    volume = gap.score_inputs.volume if gap.score_inputs else 0
    difficulty = gap.score_inputs.difficulty if gap.score_inputs else 0

    # Zero-volume AISO topic
    if volume == 0:
        return build_aiso_only_rationale(score=score, difficulty=difficulty)

    # Thin content
    if gap.gap_type.value == "thin_content":
        return build_thin_content_rationale(
            score=gap.thin_content_priority_score or score,
            our_position=gap.our_ranking_position or 0,
            our_word_count=gap.our_word_count or 0,
            competitor_avg_word_count=gap.competitor_avg_word_count or 0,
        )

    # Own gap or new opportunity
    return build_new_content_rationale(
        score=score,
        volume=volume,
        difficulty=difficulty,
        competitor_best_position=competitor_best_position,
    )


def build_content_brief(
    *,
    gap: ContentGapRecord,
    tenant_id: uuid.UUID,
    campaign_id: str,
    competitor_benchmarks: list[CompetitorBenchmark],
    search_intent: SearchIntent,
    topic_cluster: str | None = None,
    content_type: ContentType = ContentType.BLOG_POST,
    recommended_headings: list[str] | None = None,
    recommended_schema_types: list[str] | None = None,
    suggested_publish_date: str = "2026-01-01",
) -> ContentBrief:
    """Assemble a ContentBrief from pipeline data.

    Args:
        gap: ContentGapRecord from F-006.
        tenant_id: Tenant UUID.
        campaign_id: Campaign identifier.
        competitor_benchmarks: Competitor data from F-005.
        search_intent: From F-003.
        topic_cluster: From F-002 (None if not run).
        content_type: From RecommendationEngine.
        recommended_headings: From RecommendationEngine.
        recommended_schema_types: From RecommendationEngine.
        suggested_publish_date: From PublishScheduler.

    Returns:
        Fully populated ContentBrief (validated by Pydantic on construction).
    """
    # Aggregate competitor benchmarks
    comp_word_counts = [b.word_count for b in competitor_benchmarks if b.word_count]
    avg_wc = sum(comp_word_counts) // len(comp_word_counts) if comp_word_counts else 0

    depth_scores = [
        b.depth_score for b in competitor_benchmarks if b.depth_score is not None
    ]

    schema_types_set: set[str] = set()
    has_faq = False
    for b in competitor_benchmarks:
        schema_types_set.update(b.schema_types)
        if b.has_faq_section:
            has_faq = True

    top_comp_url = None
    if competitor_benchmarks:
        best = min(competitor_benchmarks, key=lambda b: b.serp_position)
        top_comp_url = best.url

    # Supporting keywords from gap context
    supporting_kw: list[str] = []

    # Compute derived fields
    rec_wc = _compute_recommended_word_count(avg_wc)
    include_faq = _determine_include_faq(has_faq, search_intent)

    # Existing page URL only for thin content
    existing_url = gap.our_page_url if gap.gap_type.value == "thin_content" else None

    # Map gap_type to ContentBrief's GapType
    gap_type_map = {
        "own_gap": GapType.OWN_GAP,
        "thin_content": GapType.THIN_CONTENT,
        "new_opportunity": GapType.NEW_OPPORTUNITY,
    }
    brief_gap_type = gap_type_map.get(gap.gap_type.value, GapType.NEW_OPPORTUNITY)

    # Competitor best position for rationale
    comp_best_pos = gap.competitor_best_position

    rationale = _build_rationale(gap, comp_best_pos)

    return ContentBrief(
        tenant_id=tenant_id,
        schema_version=SCHEMA_VERSION,
        status=BriefStatus.PENDING_REVIEW,
        target_keyword=gap.keyword_text,
        target_language=gap.language,
        target_country=gap.language.upper()[:2] if len(gap.language) >= 2 else "XX",
        supporting_keywords=supporting_kw,
        search_intent=search_intent,
        topic_cluster=topic_cluster,
        content_type=content_type,
        keyword_volume=gap.score_inputs.volume if gap.score_inputs else 0,
        keyword_difficulty=gap.score_inputs.difficulty if gap.score_inputs else 0,
        opportunity_score=gap.opportunity_score or 0.0,
        opportunity_score_rationale=rationale,
        gap_type=brief_gap_type,
        existing_page_url=existing_url,
        competitor_avg_word_count=avg_wc,
        competitor_depth_scores=depth_scores,
        top_competitor_url=top_comp_url,
        competitor_schema_types=sorted(schema_types_set),
        competitors_have_faq=has_faq,
        recommended_word_count=rec_wc,
        recommended_headings=recommended_headings or [],
        recommended_schema_types=recommended_schema_types or [],
        include_faq=include_faq,
        suggested_publish_date=suggested_publish_date,
    )
