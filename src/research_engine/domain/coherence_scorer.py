"""Coherence score validation and post-processing.

Validates LLM-assigned coherence scores and adds warnings
for low-coherence clusters.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.research_engine.models.result import Err, Ok, Result

LOW_COHERENCE_THRESHOLD = 4


@dataclass(frozen=True)
class CoherenceResult:
    """Validated coherence score with optional warning.

    Attributes:
        score: Coherence score 1-10.
        rationale: LLM-provided explanation.
        low_coherence_warning: Warning if score is below threshold.
    """

    score: int
    rationale: str
    low_coherence_warning: str | None = None


def validate_coherence(
    score: int,
    rationale: str,
) -> Result[CoherenceResult, str]:
    """Validate and post-process a coherence score.

    Args:
        score: LLM-assigned coherence score.
        rationale: LLM-provided explanation.

    Returns:
        Ok(CoherenceResult) on valid input, Err(message) otherwise.
    """
    if not (1 <= score <= 10):
        return Err(f"Coherence score {score} out of range [1, 10]")

    if not rationale.strip():
        return Err("Coherence rationale is empty")

    warning: str | None = None
    if score < LOW_COHERENCE_THRESHOLD:
        warning = (
            f"Low coherence ({score}/10) — review cluster composition "
            f"before content planning"
        )

    return Ok(
        CoherenceResult(score=score, rationale=rationale, low_coherence_warning=warning)
    )
