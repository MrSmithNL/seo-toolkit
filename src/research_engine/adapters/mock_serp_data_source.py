"""Mock SERP data source for testing.

Returns configurable fixture data. Used in unit and integration tests
so tests run without API keys (NFR-11).

TypeScript equivalent:
    modules/content-engine/research/adapters/__mocks__/mock-serp-data-source.ts
"""

from __future__ import annotations

from src.research_engine.models.serp import SerpFeatures
from src.research_engine.ports.serp_data_source import (
    RawSerpResponse,
    RawSerpResult,
    SerpDataSource,
)


class MockSerpDataSource:
    """Mock implementation of SerpDataSource.

    Configurable responses per keyword for testing different scenarios.
    Implements SerpDataSource protocol.
    """

    def __init__(self) -> None:
        """Initialise with empty response registry."""
        self._responses: dict[str, RawSerpResponse] = {}
        self._errors: dict[str, Exception] = {}
        self.calls: list[tuple[str, str, str]] = []

    def set_response(self, keyword: str, response: RawSerpResponse) -> None:
        """Register a canned response for a keyword.

        Args:
            keyword: The keyword to match.
            response: The response to return.
        """
        self._responses[keyword.lower()] = response

    def set_error(self, keyword: str, error: Exception) -> None:
        """Register an error to raise for a keyword.

        Args:
            keyword: The keyword to match.
            error: The exception to raise.
        """
        self._errors[keyword.lower()] = error

    def fetch_serp(
        self,
        keyword: str,
        language: str,
        country: str,
    ) -> RawSerpResponse:
        """Return registered response or default fixture.

        Args:
            keyword: The search query.
            language: BCP 47 language code.
            country: ISO 3166-1 country code.

        Returns:
            Registered response or default 10-result fixture.

        Raises:
            Exception: If an error is registered for this keyword.
        """
        self.calls.append((keyword, language, country))
        key = keyword.lower()
        if key in self._errors:
            raise self._errors[key]
        if key in self._responses:
            return self._responses[key]
        return _default_response()


# ---------------------------------------------------------------------------
# Fixture generators
# ---------------------------------------------------------------------------


def make_happy_path_response() -> RawSerpResponse:
    """Standard 10-result SERP with mixed content types.

    Scenario: "FUE hair transplant", DE — happy path.
    """
    results = [
        RawSerpResult(
            position=i + 1,
            url=f"https://example{i}.com/fue-hair-transplant",
            domain=f"example{i}.com",
            title=f"FUE Hair Transplant Guide #{i + 1}",
            meta_description=f"About FUE hair transplant #{i + 1}.",
            estimated_word_count=1500 + i * 200,
            content_type="blog" if i < 7 else "product_page",
        )
        for i in range(10)
    ]
    return RawSerpResponse(
        organic_results=results,
        features=SerpFeatures(
            featured_snippet=True,
            people_also_ask=True,
            paa_questions=["How long does FUE take?", "Is FUE permanent?", "FUE cost?"],
        ),
        api_source="mock",
    )


def make_video_heavy_response() -> RawSerpResponse:
    """SERP with mix of blog and video results.

    Scenario: "hair transplant before after results".
    """
    results = []
    for i in range(10):
        ct = "blog" if i < 4 else "video"
        results.append(
            RawSerpResult(
                position=i + 1,
                url=f"https://site{i}.com/before-after",
                domain=f"site{i}.com",
                title=f"Hair Transplant Before After #{i + 1}",
                content_type=ct,
            ),
        )
    return RawSerpResponse(
        organic_results=results,
        features=SerpFeatures(image_pack=True, video_carousel=True),
        api_source="mock",
    )


def make_zero_results_response() -> RawSerpResponse:
    """SERP with no organic results (AI Overview only).

    Scenario: Query triggers only AI Overview.
    """
    return RawSerpResponse(
        organic_results=[],
        features=SerpFeatures(ai_overview=True),
        no_organic_results=True,
        api_source="mock",
    )


def make_feature_rich_response() -> RawSerpResponse:
    """SERP with all feature types detected.

    Scenario: Informational query with many SERP features.
    """
    results = [
        RawSerpResult(
            position=i + 1,
            url=f"https://info{i}.com/fue",
            domain=f"info{i}.com",
            title=f"FUE Info #{i + 1}",
            content_type="blog",
        )
        for i in range(10)
    ]
    return RawSerpResponse(
        organic_results=results,
        features=SerpFeatures(
            ai_overview=True,
            featured_snippet=True,
            people_also_ask=True,
            knowledge_panel=True,
            image_pack=True,
            video_carousel=True,
            local_pack=True,
            shopping_results=True,
            paa_questions=[
                "What is FUE?",
                "Is FUE painful?",
                "How much does FUE cost?",
                "FUE recovery time?",
                "FUE vs FUT?",
            ],
        ),
        api_source="mock",
    )


def make_purely_organic_response() -> RawSerpResponse:
    """SERP with only organic results, no features.

    Scenario: "FUE vs DHI recovery comparison" — clean organic SERP.
    """
    results = [
        RawSerpResult(
            position=i + 1,
            url=f"https://blog{i}.com/fue-vs-dhi",
            domain=f"blog{i}.com",
            title=f"FUE vs DHI Comparison #{i + 1}",
            content_type="blog",
            estimated_word_count=2000 + i * 100,
        )
        for i in range(10)
    ]
    return RawSerpResponse(
        organic_results=results,
        features=SerpFeatures(),
        api_source="mock",
    )


def _default_response() -> RawSerpResponse:
    """Default response for unregistered keywords."""
    return make_happy_path_response()


# Protocol check (runtime only, suppressed for linting)
assert isinstance(MockSerpDataSource(), SerpDataSource)  # noqa: S101
