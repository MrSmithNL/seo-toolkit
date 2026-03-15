"""Rationale string builder for ContentBrief opportunity scores.

Generates human-readable, one-line rationale strings per US-002.

TypeScript equivalent:
  modules/content-engine/research/services/rationale-builder.ts
"""

from __future__ import annotations


def _volume_label(volume: int) -> str:
    """Return human-readable volume label."""
    if volume > 5000:
        return "High volume"
    if volume >= 500:
        return "Medium volume"
    return "Low volume"


def _difficulty_label(difficulty: int) -> str:
    """Return human-readable difficulty label."""
    if difficulty < 30:
        return "easy to rank"
    if difficulty <= 60:
        return "moderate competition"
    return "hard to rank"


def build_new_content_rationale(
    *,
    score: float,
    volume: int,
    difficulty: int,
    competitor_best_position: int | None,
) -> str:
    """Build rationale for own_gap or new_opportunity briefs."""
    vol_label = _volume_label(volume)
    diff_label = _difficulty_label(difficulty)

    if competitor_best_position is None:
        gap_label = "no competitor in top 5"
    else:
        gap_label = f"competitor at position {competitor_best_position}"

    return (
        f"Score: {score:.2f} — "
        f"{vol_label} ({volume:,}/mo), "
        f"{diff_label} ({difficulty}/100), "
        f"{gap_label}."
    )


def build_thin_content_rationale(
    *,
    score: float,
    our_position: int,
    our_word_count: int,
    competitor_avg_word_count: int,
) -> str:
    """Build rationale for thin_content briefs."""
    avg = f"{competitor_avg_word_count:,}"
    return (
        f"Priority: {score:.2f} — "
        f"We rank #{our_position}. "
        f"Our page is {our_word_count:,} words "
        f"vs competitor average of {avg}. "
        "Strong update opportunity."
    )


def build_aiso_only_rationale(
    *,
    score: float,
    difficulty: int,
) -> str:
    """Build rationale for zero-volume AISO-only topics."""
    diff_label = _difficulty_label(difficulty)
    return (
        f"Score: {score:.2f} (AISO only) — "
        f"Zero search volume. "
        f"{diff_label.capitalize()} ({difficulty}/100). "
        "Recommended for AI citation only, not organic traffic."
    )
