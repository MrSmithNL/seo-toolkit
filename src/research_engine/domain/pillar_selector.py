"""Pillar keyword selection for topic clusters.

Validates and optionally overrides the LLM's pillar choice
using volume data and intent signals.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.research_engine.models.keyword import Keyword, KeywordIntent

# Intent broadness ranking (lower = broader)
_INTENT_RANK: dict[KeywordIntent | None, int] = {
    KeywordIntent.INFORMATIONAL: 0,
    KeywordIntent.COMMERCIAL: 1,
    KeywordIntent.NAVIGATIONAL: 2,
    KeywordIntent.TRANSACTIONAL: 3,
    None: 1,  # Unknown treated as mid-range
}


@dataclass(frozen=True)
class PillarResult:
    """Result of pillar selection for a cluster.

    Attributes:
        keyword_id: ID of the selected pillar keyword.
        term: The pillar keyword term.
        rationale: Explanation of why this keyword was selected.
        no_pillar_flag: Warning if cluster has no suitable pillar.
    """

    keyword_id: str
    term: str
    rationale: str
    no_pillar_flag: str | None = None


def _is_all_transactional(keywords: list[Keyword]) -> bool:
    """Check if all keywords in a cluster are transactional."""
    return all(
        kw.intent in (KeywordIntent.TRANSACTIONAL, KeywordIntent.NAVIGATIONAL)
        for kw in keywords
        if kw.intent is not None
    ) and any(kw.intent is not None for kw in keywords)


def select_pillar(
    cluster_keywords: list[Keyword],
    llm_pillar_term: str,
    volume_map: dict[str, int],
) -> PillarResult:
    """Select the pillar keyword for a cluster.

    Uses volume data to validate/override the LLM's choice.
    If no volume data exists, trusts the LLM's selection.

    Args:
        cluster_keywords: Keywords in this cluster.
        llm_pillar_term: The pillar keyword chosen by the LLM.
        volume_map: Mapping of keyword_id to search volume.

    Returns:
        PillarResult with selected pillar and rationale.
    """
    if not cluster_keywords:
        return PillarResult(
            keyword_id="",
            term="",
            rationale="Empty cluster, no pillar available.",
        )

    # Check all-transactional flag
    no_pillar_flag: str | None = None
    if _is_all_transactional(cluster_keywords):
        no_pillar_flag = "No suitable pillar — consider informational expansion"

    # If no volume data, trust LLM
    if not volume_map:
        llm_match = next(
            (
                kw
                for kw in cluster_keywords
                if kw.term.lower() == llm_pillar_term.lower()
            ),
            None,
        )
        if llm_match:
            return PillarResult(
                keyword_id=llm_match.id,
                term=llm_match.term,
                rationale=f"LLM selected '{llm_match.term}' (no volume data).",
                no_pillar_flag=no_pillar_flag,
            )
        # LLM term not found, use first keyword
        fallback = cluster_keywords[0]
        return PillarResult(
            keyword_id=fallback.id,
            term=fallback.term,
            rationale=(
                f"Fallback to '{fallback.term}' "
                f"(LLM choice not found, no volume data)."
            ),
            no_pillar_flag=no_pillar_flag,
        )

    # Sort by volume (desc), then by intent broadness (asc) for tie-breaking
    def sort_key(kw: Keyword) -> tuple[int, int]:
        vol = volume_map.get(kw.id, 0)
        intent_rank = _INTENT_RANK.get(kw.intent, 1)
        return (-vol, intent_rank)

    sorted_kws = sorted(cluster_keywords, key=sort_key)
    best = sorted_kws[0]
    best_vol = volume_map.get(best.id, 0)

    # Check if LLM's choice matches
    llm_match = next(
        (kw for kw in cluster_keywords if kw.term.lower() == llm_pillar_term.lower()),
        None,
    )

    if llm_match and llm_match.id == best.id:
        rationale = (
            f"LLM selected '{best.term}' confirmed as highest volume " f"({best_vol})."
        )
    elif llm_match:
        llm_vol = volume_map.get(llm_match.id, 0)
        rationale = (
            f"Overrode LLM choice '{llm_match.term}' (vol={llm_vol}) "
            f"with '{best.term}' (vol={best_vol})."
        )
    else:
        rationale = (
            f"LLM pillar '{llm_pillar_term}' not found in cluster. "
            f"Selected '{best.term}' (vol={best_vol})."
        )

    return PillarResult(
        keyword_id=best.id,
        term=best.term,
        rationale=rationale,
        no_pillar_flag=no_pillar_flag,
    )
