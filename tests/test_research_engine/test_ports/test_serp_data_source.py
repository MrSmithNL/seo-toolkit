"""Tests for SerpDataSource protocol and MockSerpDataSource.

TDD: Tests for T-002 covering ATS-013 and PI-004.
"""

from __future__ import annotations

from src.research_engine.adapters.mock_serp_data_source import (
    MockSerpDataSource,
    make_feature_rich_response,
    make_happy_path_response,
    make_purely_organic_response,
    make_video_heavy_response,
    make_zero_results_response,
)
from src.research_engine.ports.serp_data_source import RawSerpResponse, SerpDataSource


class TestMockSerpDataSource:
    """Tests for MockSerpDataSource adapter."""

    def test_implements_protocol(self) -> None:
        """MockSerpDataSource implements SerpDataSource protocol."""
        mock = MockSerpDataSource()
        assert isinstance(mock, SerpDataSource)

    def test_default_response_has_10_results(self) -> None:
        """Unregistered keyword returns default 10-result fixture."""
        mock = MockSerpDataSource()
        response = mock.fetch_serp("unknown keyword", "de", "DE")
        assert len(response.organic_results) == 10

    def test_registered_response_returned(self) -> None:
        """Registered keyword returns its specific response."""
        mock = MockSerpDataSource()
        custom = RawSerpResponse(organic_results=[], no_organic_results=True)
        mock.set_response("test keyword", custom)
        response = mock.fetch_serp("test keyword", "en", "US")
        assert response.no_organic_results is True
        assert len(response.organic_results) == 0

    def test_case_insensitive_lookup(self) -> None:
        """Keyword lookup is case-insensitive."""
        mock = MockSerpDataSource()
        custom = RawSerpResponse(organic_results=[], no_organic_results=True)
        mock.set_response("Test Keyword", custom)
        response = mock.fetch_serp("test keyword", "en", "US")
        assert response.no_organic_results is True

    def test_calls_tracked(self) -> None:
        """All fetch_serp calls are tracked."""
        mock = MockSerpDataSource()
        mock.fetch_serp("kw1", "de", "DE")
        mock.fetch_serp("kw2", "en", "US")
        assert len(mock.calls) == 2
        assert mock.calls[0] == ("kw1", "de", "DE")
        assert mock.calls[1] == ("kw2", "en", "US")


class TestFixtures:
    """Tests for fixture data completeness."""

    def test_happy_path_fixture(self) -> None:
        """Happy path has 10 results and some features."""
        response = make_happy_path_response()
        assert len(response.organic_results) == 10
        assert response.features.featured_snippet is True
        assert response.features.people_also_ask is True
        assert len(response.features.paa_questions) == 3

    def test_video_heavy_fixture(self) -> None:
        """Video-heavy SERP has mix of blog and video."""
        response = make_video_heavy_response()
        assert len(response.organic_results) == 10
        content_types = [r.content_type for r in response.organic_results]
        assert "blog" in content_types
        assert "video" in content_types
        assert response.features.video_carousel is True

    def test_zero_results_fixture(self) -> None:
        """Zero results fixture is flagged correctly."""
        response = make_zero_results_response()
        assert len(response.organic_results) == 0
        assert response.no_organic_results is True
        assert response.features.ai_overview is True

    def test_feature_rich_fixture(self) -> None:
        """Feature-rich fixture has all features set."""
        response = make_feature_rich_response()
        assert len(response.organic_results) == 10
        assert response.features.ai_overview is True
        assert response.features.featured_snippet is True
        assert response.features.people_also_ask is True
        assert response.features.knowledge_panel is True
        assert response.features.image_pack is True
        assert response.features.video_carousel is True
        assert response.features.local_pack is True
        assert response.features.shopping_results is True
        assert len(response.features.paa_questions) == 5

    def test_purely_organic_fixture(self) -> None:
        """ATS-013: Purely organic SERP — all feature flags false."""
        response = make_purely_organic_response()
        assert len(response.organic_results) == 10
        f = response.features
        assert f.ai_overview is False
        assert f.featured_snippet is False
        assert f.people_also_ask is False
        assert f.knowledge_panel is False
        assert f.image_pack is False
        assert f.video_carousel is False
        assert f.local_pack is False
        assert f.shopping_results is False
        assert f.paa_questions == []

    def test_all_fixtures_have_valid_positions(self) -> None:
        """PI-001: All fixture results have valid positions 1-10."""
        fixtures = [
            make_happy_path_response(),
            make_video_heavy_response(),
            make_feature_rich_response(),
            make_purely_organic_response(),
        ]
        for fixture in fixtures:
            for result in fixture.organic_results:
                assert 1 <= result.position <= 10

    def test_all_fixtures_have_nonempty_urls(self) -> None:
        """PI-002: All fixture results have non-empty URLs."""
        fixtures = [
            make_happy_path_response(),
            make_video_heavy_response(),
            make_feature_rich_response(),
            make_purely_organic_response(),
        ]
        for fixture in fixtures:
            for result in fixture.organic_results:
                assert result.url
                assert len(result.url) > 0
