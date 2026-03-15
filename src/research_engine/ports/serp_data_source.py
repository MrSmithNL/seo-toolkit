"""SerpDataSource protocol for SERP data providers.

Implements the Adapter pattern from ADR-F004-001 and ADR-E001-002.
Each SERP provider (DataForSEO, Google scraper) implements this protocol.

TypeScript equivalent: modules/content-engine/research/ports/serp-data-source.ts
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from src.research_engine.models.serp import SerpFeatures


@dataclass(frozen=True)
class RawSerpResult:
    """Raw organic result from a SERP data source.

    Adapters map their API response into this common format.
    The command layer then enriches into a full SerpResult model.
    """

    position: int
    url: str
    domain: str
    title: str | None = None
    meta_description: str | None = None
    estimated_word_count: int | None = None
    content_type: str | None = None


@dataclass(frozen=True)
class RawSerpResponse:
    """Raw response from a SERP data source.

    Contains organic results and feature flags in a provider-agnostic format.
    """

    organic_results: list[RawSerpResult] = field(default_factory=list)
    features: SerpFeatures = field(default_factory=SerpFeatures)
    no_organic_results: bool = False
    api_source: str = "mock"


@runtime_checkable
class SerpDataSource(Protocol):
    """Protocol for SERP data providers.

    Each adapter (DataForSEO, Google scraper, Mock) implements this protocol.
    The command layer calls fetch_serp() and receives a provider-agnostic response.
    """

    def fetch_serp(
        self,
        keyword: str,
        language: str,
        country: str,
    ) -> RawSerpResponse:
        """Fetch SERP data for a keyword.

        Args:
            keyword: The search query.
            language: BCP 47 language code (e.g., 'de', 'en').
            country: ISO 3166-1 country code (e.g., 'DE', 'US').

        Returns:
            Raw SERP response with organic results and feature flags.

        Raises:
            SerpApiError: On persistent API failure after retries.
        """
        ...
