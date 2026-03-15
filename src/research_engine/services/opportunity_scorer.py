"""Opportunity scoring for F-006 Content Gap Identification.

Pure functions that calculate scores from inputs (ADR-F006-002).
No side effects, no I/O. Configurable via ScoringConfig.

TypeScript equivalent: modules/content-engine/research/services/opportunity-scorer.ts
"""

from __future__ import annotations

from dataclasses import dataclass

from src.research_engine.models.content_gap import ScoreInputs
from src.research_engine.scoring_config import ScoringConfig


@dataclass(frozen=True)
class OpportunityScoreResult:
    """Result of opportunity scoring calculation.

    Attributes:
        score: Opportunity score 0.0-1.0 (clamped).
        rationale: Human-readable score explanation.
        inputs: Formula inputs for reproducibility.
    """

    score: float
    rationale: str
    inputs: ScoreInputs


@dataclass(frozen=True)
class ThinContentScoreResult:
    """Result of thin content priority scoring.

    Attributes:
        score: Priority score 0.0-1.0 (clamped).
        rationale: Human-readable explanation.
    """

    score: float
    rationale: str


def calculate_gap_score(competitor_best_position: int | None) -> float:
    """Calculate gap_score component based on competitor positioning.

    Args:
        competitor_best_position: Best competitor position (1-50+), or None.

    Returns:
        Gap score: 1.0 (no competitor top 5), 0.7 (positions 6-10), 0.4 (top 5).
    """
    if competitor_best_position is None:
        return 1.0
    if competitor_best_position > 10:
        return 1.0
    if competitor_best_position > 5:
        return 0.7
    return 0.4


def calculate_opportunity_score(
    volume: int,
    difficulty: int,
    competitor_best_position: int | None,
    max_volume: int,
    is_universal_gap: bool,
    config: ScoringConfig,
) -> OpportunityScoreResult:
    """Calculate opportunity score for a gap/opportunity keyword.

    Formula: (volume_norm × 0.4) + (difficulty_inverse × 0.3) + (gap_score × 0.3)
    Universal gap bonus: +0.1, clamped to 1.0.

    Args:
        volume: Monthly search volume.
        difficulty: Keyword difficulty (0-100).
        competitor_best_position: Best competitor SERP position, or None.
        max_volume: Maximum volume in keyword set (for normalisation).
        is_universal_gap: Whether this is a universal gap across languages.
        config: Scoring formula weights.

    Returns:
        OpportunityScoreResult with score, rationale, and inputs.
    """
    # Normalise inputs
    volume_normalised = volume / max_volume if max_volume > 0 else 0.0
    difficulty_inverse = (100 - difficulty) / 100
    gap_score = calculate_gap_score(competitor_best_position)

    # Calculate composite score
    score = (
        (volume_normalised * config.volume_weight)
        + (difficulty_inverse * config.difficulty_weight)
        + (gap_score * config.gap_weight)
    )

    # Universal gap bonus
    bonus = config.universal_gap_bonus if is_universal_gap else 0.0
    score += bonus

    # Clamp to 1.0
    score = min(score, 1.0)

    # Build inputs for reproducibility
    inputs = ScoreInputs(
        volume=volume,
        volume_normalised=round(volume_normalised, 4),
        difficulty=difficulty,
        difficulty_inverse_normalised=round(difficulty_inverse, 4),
        gap_score=gap_score,
        universal_gap_bonus=bonus,
    )

    # Generate rationale
    rationale = _build_opportunity_rationale(
        score=score,
        volume=volume,
        difficulty=difficulty,
        competitor_best_position=competitor_best_position,
        is_universal_gap=is_universal_gap,
    )

    return OpportunityScoreResult(
        score=round(score, 2),
        rationale=rationale,
        inputs=inputs,
    )


def calculate_thin_content_priority_score(
    current_position: int,
    our_word_count: int,
    competitor_avg_word_count: int,
    max_word_count_gap: int,
    config: ScoringConfig,
) -> ThinContentScoreResult:
    """Calculate thin content priority score.

    Formula: (position_bucket × 0.5) + (word_count_gap_norm × 0.5)
    Where position_bucket = (50 - position) / 50

    Args:
        current_position: Our current ranking position (11-50).
        our_word_count: Our page's word count.
        competitor_avg_word_count: Top-3 competitor average word count.
        max_word_count_gap: Max word count gap in the dataset.
        config: Scoring formula weights.

    Returns:
        ThinContentScoreResult with score and rationale.
    """
    # Position bucket: higher position = more urgent (closer to page 1)
    position_bucket = (50 - current_position) / 50

    # Word count gap
    word_count_gap = max(0, competitor_avg_word_count - our_word_count)
    gap_normalised = (
        word_count_gap / max_word_count_gap if max_word_count_gap > 0 else 0.0
    )

    score = (position_bucket * config.thin_position_weight) + (
        gap_normalised * config.thin_wordcount_weight
    )

    # Clamp to 1.0
    score = min(score, 1.0)

    # Calculate percentage below competitor average
    pct_below = (
        round((1 - our_word_count / competitor_avg_word_count) * 100)
        if competitor_avg_word_count > 0
        else 0
    )

    rationale = (
        f"Ranking at #{current_position} (improvable). "
        f"Content gap: {word_count_gap:,} words below competitor average. "
        f"Our page: {our_word_count:,} words. "
        f"Competitor average: {competitor_avg_word_count:,} words. "
        f"{pct_below}% below competitor average."
    )

    return ThinContentScoreResult(
        score=round(score, 2),
        rationale=rationale,
    )


def _build_opportunity_rationale(
    score: float,
    volume: int,
    difficulty: int,
    competitor_best_position: int | None,
    is_universal_gap: bool,
) -> str:
    """Build human-readable rationale for an opportunity score.

    Args:
        score: Calculated opportunity score.
        volume: Monthly search volume.
        difficulty: Keyword difficulty.
        competitor_best_position: Best competitor position.
        is_universal_gap: Whether universal across languages.

    Returns:
        Formatted rationale string.
    """
    # Volume description
    if volume >= 5000:
        vol_desc = "High volume"
    elif volume >= 1000:
        vol_desc = "Medium volume"
    elif volume > 0:
        vol_desc = "Low volume"
    else:
        vol_desc = "Zero volume"

    # Difficulty description
    if difficulty <= 30:
        diff_desc = "easy to rank"
    elif difficulty <= 60:
        diff_desc = "moderate difficulty"
    else:
        diff_desc = "hard to rank"

    # Competitor description
    if competitor_best_position is None or competitor_best_position > 10:
        comp_desc = "no competitor in top 5"
    elif competitor_best_position > 5:
        comp_desc = f"competitor at position {competitor_best_position}"
    else:
        comp_desc = f"competitor at position {competitor_best_position}"

    parts = [
        f"Score: {score:.2f}",
        f"{vol_desc} ({volume:,}/mo)",
        f"{diff_desc} ({difficulty}/100)",
        comp_desc,
    ]

    if is_universal_gap:
        parts.append("universal gap bonus applied")

    if volume == 0:
        parts.append("AISO value only")

    return " — ".join([parts[0], ", ".join(parts[1:])])
