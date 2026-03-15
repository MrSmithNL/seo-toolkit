"""Coverage data source port for F-006 Content Gap Identification.

Defines the interface for determining whether the user's site
covers a given keyword. Two implementations: GSC (primary) and
SERP fallback (ADR-F006-001).

TypeScript equivalent: modules/content-engine/research/ports/coverage-data-source.ts
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.research_engine.models.content_gap import GscQueryData


@runtime_checkable
class CoverageDataSource(Protocol):
    """Interface for coverage data lookup.

    Implementations:
    - GscCoverageSource: Google Search Console API (primary)
    - SerpCoverageSource: SERP top-50 check (fallback)
    """

    def get_coverage(
        self,
        keyword_text: str,
        language: str,
    ) -> GscQueryData | None:
        """Check if user's site has coverage for this keyword.

        Args:
            keyword_text: The keyword to check coverage for.
            language: BCP 47 language code.

        Returns:
            GscQueryData with impressions/clicks data, or None if no coverage.
        """
        ...

    def is_available(self) -> bool:
        """Check whether this data source is accessible.

        Returns:
            True if data source is connected and responding.
        """
        ...
