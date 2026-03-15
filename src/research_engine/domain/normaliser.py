"""Keyword normalisation and deduplication.

Pure functions for cleaning and deduplicating keyword lists.
No side effects — suitable for direct TypeScript translation.
"""

from __future__ import annotations

import re

from src.research_engine.models.keyword import Keyword

_WHITESPACE_RE = re.compile(r"\s+")


def normalise(term: str) -> str:
    """Normalise a keyword term.

    Lowercases, strips leading/trailing whitespace, and collapses
    multiple internal whitespace characters to a single space.

    Args:
        term: Raw keyword term.

    Returns:
        Normalised keyword string.
    """
    return _WHITESPACE_RE.sub(" ", term.strip().lower())


def make_dedup_key(term: str) -> str:
    """Create a sorted-token dedup key from a term.

    Normalises the term, then sorts tokens alphabetically.
    Two terms with the same tokens in different order produce
    the same dedup key.

    Args:
        term: Raw or normalised keyword term.

    Returns:
        Sorted-token dedup key.
    """
    normalised = normalise(term)
    if not normalised:
        return ""
    tokens = sorted(normalised.split())
    return " ".join(tokens)


def dedup(keywords: list[Keyword]) -> list[Keyword]:
    """Deduplicate a list of keywords using sorted-token keys.

    Two-phase deduplication:
    1. Compute sorted-token key for each keyword.
    2. Group by key; keep the first occurrence per key.

    When multiple keywords share the same key, the first one
    in the input list is kept as canonical.

    Args:
        keywords: List of Keyword models to deduplicate.

    Returns:
        Deduplicated list (order preserved, subset of input).
    """
    seen: dict[str, Keyword] = {}
    for kw in keywords:
        key = make_dedup_key(kw.term)
        if key not in seen:
            seen[key] = kw
    return list(seen.values())
