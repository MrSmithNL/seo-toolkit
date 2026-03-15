"""Keyword difficulty estimation using heuristic signals.

Pure function — no side effects. Uses three signals:
1. Volume bracket (higher volume = harder)
2. Autocomplete depth (more suggestions = more competitive)
3. LLM authority assessment (domain authority of top rankers)
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DifficultyResult:
    """Result of difficulty estimation.

    Attributes:
        score: Difficulty score 0-100.
        source: Always 'heuristic' for R1.
        rationale: Human-readable explanation of the score.
    """

    score: int
    source: str
    rationale: str


def _volume_to_score(volume: int) -> int:
    """Convert search volume to a difficulty signal (0-100).

    Args:
        volume: Monthly search volume.

    Returns:
        Score 0-100 based on volume bracket.
    """
    if volume == 0:
        return 0
    if volume < 100:
        return 10
    if volume < 1000:
        return 25
    if volume < 10000:
        return 50
    if volume < 100000:
        return 75
    return 95


def _depth_to_score(autocomplete_depth: int) -> int:
    """Convert autocomplete suggestion count to difficulty signal.

    Args:
        autocomplete_depth: Number of autocomplete suggestions.

    Returns:
        Score 0-100 based on depth.
    """
    return min(autocomplete_depth * 10, 100)


def estimate_difficulty(
    volume: int,
    autocomplete_depth: int,
    llm_authority_score: int,
) -> DifficultyResult:
    """Estimate keyword difficulty from three heuristic signals.

    Weighted average: volume 30%, autocomplete depth 20%, LLM authority 50%.

    Args:
        volume: Monthly search volume.
        autocomplete_depth: Number of autocomplete suggestions found.
        llm_authority_score: LLM-assessed domain authority of top rankers (0-100).

    Returns:
        DifficultyResult with score, source, and rationale.
    """
    volume_score = _volume_to_score(volume)
    depth_score = _depth_to_score(autocomplete_depth)
    authority_score = min(max(llm_authority_score, 0), 100)

    weighted = volume_score * 0.3 + depth_score * 0.2 + authority_score * 0.5
    score = min(max(int(round(weighted)), 0), 100)

    parts: list[str] = []
    parts.append(f"volume={volume} (signal: {volume_score})")
    parts.append(f"autocomplete_depth={autocomplete_depth} (signal: {depth_score})")
    parts.append(f"authority={llm_authority_score} (signal: {authority_score})")
    rationale = f"Heuristic: {', '.join(parts)}. Weighted score: {score}/100."

    return DifficultyResult(
        score=score,
        source="heuristic",
        rationale=rationale,
    )
