"""Scoring configuration for F-006 Content Gap Identification.

Loaded from environment variables with sensible defaults.
Formula weights are named constants, not inline (ADR-F006-002).

TypeScript equivalent: modules/content-engine/research/config/scoring-config.ts
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ScoringConfig:
    """Configurable scoring formula weights and thresholds.

    All weights are loaded from env vars with defaults.
    Changing weights = env var update, no code change.
    """

    # Opportunity score formula weights (must sum to 1.0)
    volume_weight: float = 0.4
    difficulty_weight: float = 0.3
    gap_weight: float = 0.3

    # Universal gap bonus
    universal_gap_bonus: float = 0.1

    # Thin content thresholds
    thin_content_threshold: float = 0.5  # 50% of competitor avg

    # Thin content priority score weights (must sum to 1.0)
    thin_position_weight: float = 0.5
    thin_wordcount_weight: float = 0.5

    # Volume threshold for calendar inclusion
    min_volume_threshold: int = 50


def load_scoring_config() -> ScoringConfig:
    """Load scoring config from environment variables.

    Env vars (all optional, defaults used if not set):
    - GAP_SCORE_VOLUME_WEIGHT
    - GAP_SCORE_DIFFICULTY_WEIGHT
    - GAP_SCORE_GAP_WEIGHT
    - GAP_SCORE_UNIVERSAL_BONUS
    - GAP_THIN_CONTENT_THRESHOLD
    - GAP_THIN_POSITION_WEIGHT
    - GAP_THIN_WORDCOUNT_WEIGHT
    - GAP_MIN_VOLUME_THRESHOLD

    Returns:
        ScoringConfig with values from env or defaults.
    """
    return ScoringConfig(
        volume_weight=float(os.environ.get("GAP_SCORE_VOLUME_WEIGHT", "0.4")),
        difficulty_weight=float(os.environ.get("GAP_SCORE_DIFFICULTY_WEIGHT", "0.3")),
        gap_weight=float(os.environ.get("GAP_SCORE_GAP_WEIGHT", "0.3")),
        universal_gap_bonus=float(os.environ.get("GAP_SCORE_UNIVERSAL_BONUS", "0.1")),
        thin_content_threshold=float(
            os.environ.get("GAP_THIN_CONTENT_THRESHOLD", "0.5")
        ),
        thin_position_weight=float(os.environ.get("GAP_THIN_POSITION_WEIGHT", "0.5")),
        thin_wordcount_weight=float(os.environ.get("GAP_THIN_WORDCOUNT_WEIGHT", "0.5")),
        min_volume_threshold=int(os.environ.get("GAP_MIN_VOLUME_THRESHOLD", "50")),
    )
