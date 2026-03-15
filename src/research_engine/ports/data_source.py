"""KeywordDataSource protocol for all keyword data providers.

All data source adapters implement this protocol using structural
typing (Protocol). Mirrors the TypeScript interface from ADR-E001-002.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class KeywordVolumeResult:
    """Volume data for a single keyword from an API.

    Attributes:
        keyword: The keyword term.
        volume: Monthly search volume (None if unavailable).
        cpc: Cost per click in USD (None if unavailable).
        trend: 12-month volume trend (empty if unavailable).
    """

    keyword: str
    volume: int | None = None
    cpc: float | None = None
    trend: list[int] | None = None


@runtime_checkable
class KeywordDataSource(Protocol):
    """Protocol for keyword data providers.

    Adapters implement a subset of capabilities.
    Check `capabilities` before calling a method.
    """

    @property
    def capabilities(self) -> set[str]:
        """Return supported capabilities.

        Possible values: 'volume', 'difficulty', 'serp',
        'suggestions', 'trends'.
        """
        ...

    def get_keyword_volume(
        self,
        keywords: list[str],
        locale: str,
        country: str,
    ) -> list[KeywordVolumeResult]:
        """Fetch volume, CPC, and trends for keywords.

        Args:
            keywords: List of keyword terms.
            locale: Language locale (e.g. 'en', 'de').
            country: Country code (e.g. 'US', 'DE').

        Returns:
            List of volume results.
        """
        ...

    def get_keyword_suggestions(
        self,
        seed: str,
        locale: str,
    ) -> list[str]:
        """Expand a seed keyword into suggestions.

        Args:
            seed: Seed keyword to expand.
            locale: Language locale.

        Returns:
            List of suggested keywords.
        """
        ...
