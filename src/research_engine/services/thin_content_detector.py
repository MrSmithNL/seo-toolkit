"""Thin content detector for F-006 Content Gap Identification.

Identifies keywords where our site has coverage but content is
significantly weaker than competitors (word count < 50% of avg).

TypeScript equivalent: modules/content-engine/research/services/thin-content-detector.ts
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from src.research_engine.models.content_gap import CompetitorEntry
from src.research_engine.scoring_config import ScoringConfig

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ThinContentResult:
    """Result of thin content detection for a keyword.

    Attributes:
        is_thin: Whether the content is thin.
        our_word_count: Our page's word count.
        competitor_avg_word_count: Top-3 competitor average.
        word_count_gap: Words needed to reach competitor average.
        rationale: Human-readable explanation.
        insufficient_data: True if not enough competitor data.
    """

    is_thin: bool
    our_word_count: int
    competitor_avg_word_count: int
    word_count_gap: int
    rationale: str
    insufficient_data: bool = False


def detect_thin_content(
    our_ranking_position: int | None,
    our_word_count: int | None,
    competitors: list[CompetitorEntry],
    config: ScoringConfig,
) -> ThinContentResult:
    """Detect whether our content is thin compared to competitors.

    Rules:
    1. Only applies to keywords where we rank 11-50 (underperforming).
    2. Top-10 rankings are NEVER flagged as thin (ranking well despite fewer words).
    3. Non-ranking keywords are NOT thin content (they're own_gap).
    4. Compare our word count vs top-3 competitor average.
    5. If our word count < threshold (50%) of competitor average → thin.
    6. Competitors with crawl_failed are excluded from the average.

    Args:
        our_ranking_position: Our SERP position (None if not ranking).
        our_word_count: Our page's word count (None if unknown).
        competitors: Competitor data with word counts.
        config: Scoring config with thin_content_threshold.

    Returns:
        ThinContentResult with detection outcome and metadata.
    """
    # Rule 3: Not ranking → not a thin content case
    if our_ranking_position is None:
        return ThinContentResult(
            is_thin=False,
            our_word_count=0,
            competitor_avg_word_count=0,
            word_count_gap=0,
            rationale="Not ranking — classified as own_gap, not thin content.",
        )

    # Rule 2: Top 10 → never thin
    if our_ranking_position <= 10:
        return ThinContentResult(
            is_thin=False,
            our_word_count=our_word_count or 0,
            competitor_avg_word_count=0,
            word_count_gap=0,
            rationale=(
                f"Ranking at #{our_ranking_position} (top 10) "
                "— not flagged as thin regardless of word count."
            ),
        )

    # Sort by position to get top-3 competitors
    valid_competitors = sorted(
        [
            c
            for c in competitors
            if not c.crawl_failed and c.word_count is not None and c.word_count > 0
        ],
        key=lambda c: c.position,
    )
    top_3_counts = [
        c.word_count for c in valid_competitors[:3] if c.word_count is not None
    ]

    # Rule 6: Not enough data
    if not top_3_counts:
        return ThinContentResult(
            is_thin=False,
            our_word_count=our_word_count or 0,
            competitor_avg_word_count=0,
            word_count_gap=0,
            rationale="Insufficient competitor data — thin content assessment skipped.",
            insufficient_data=True,
        )

    # Our word count unknown
    if our_word_count is None:
        return ThinContentResult(
            is_thin=False,
            our_word_count=0,
            competitor_avg_word_count=0,
            word_count_gap=0,
            rationale="Our word count unknown — thin content assessment skipped.",
            insufficient_data=True,
        )

    competitor_avg = sum(top_3_counts) // len(top_3_counts)

    # Rule 4: Check threshold
    threshold = config.thin_content_threshold
    is_thin = competitor_avg > 0 and our_word_count < (competitor_avg * threshold)

    word_count_gap = max(0, competitor_avg - our_word_count)

    if is_thin:
        pct_below = (
            round((1 - our_word_count / competitor_avg) * 100)
            if competitor_avg > 0
            else 0
        )
        rationale = (
            f"Ranks #{our_ranking_position}. "
            f"Competitor average: {competitor_avg:,} words. "
            f"Our page: {our_word_count:,} words. "
            f"{pct_below}% below competitor average."
        )
    else:
        rationale = (
            f"Ranks #{our_ranking_position}. "
            f"Our page: {our_word_count:,} words. "
            f"Competitor average: {competitor_avg:,} words. "
            f"Above thin content threshold ({threshold:.0%})."
        )

    return ThinContentResult(
        is_thin=is_thin,
        our_word_count=our_word_count,
        competitor_avg_word_count=competitor_avg,
        word_count_gap=word_count_gap,
        rationale=rationale,
    )
