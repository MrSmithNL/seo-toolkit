"""Tests for F-004 DataForSEO adapter.

TDD: Tests for T-005 covering ATS-001, ATS-005, ATS-006, INT-001, INT-007.
Uses recorded responses (no live API calls).
"""

# ruff: noqa: S105, S106

from __future__ import annotations

from unittest.mock import patch

import pytest

from src.research_engine.adapters.dataforseo_adapter import DataForSeoAdapter
from src.research_engine.ports.serp_data_source import SerpDataSource

# ---------------------------------------------------------------------------
# Recorded API response fixtures
# ---------------------------------------------------------------------------


def _standard_response() -> dict:
    """DataForSEO standard response with 10 organic results."""
    items = []
    for i in range(10):
        items.append(
            {
                "type": "organic",
                "rank_group": i + 1,
                "rank_absolute": i + 1,
                "url": f"https://example{i}.com/fue-transplant",
                "domain": f"example{i}.com",
                "title": f"FUE Hair Transplant Guide #{i + 1}",
                "description": f"Meta description for page #{i + 1}",
                "breadcrumb": f"example{i}.com > fue",
            }
        )
    return {
        "status_code": 20000,
        "tasks": [
            {
                "result": [
                    {
                        "keyword": "FUE hair transplant",
                        "items_count": 10,
                        "items": items,
                        "item_types": [
                            "organic",
                            "people_also_ask",
                            "featured_snippet",
                        ],
                    }
                ],
            }
        ],
    }


def _response_with_features() -> dict:
    """Response with SERP features detected via item_types."""
    items = [
        {
            "type": "organic",
            "rank_group": 1,
            "rank_absolute": 1,
            "url": "https://example.com",
            "domain": "example.com",
            "title": "Test",
            "description": "Test desc",
        }
    ]
    return {
        "status_code": 20000,
        "tasks": [
            {
                "result": [
                    {
                        "keyword": "test",
                        "items_count": 1,
                        "items": items
                        + [
                            {"type": "featured_snippet", "title": "Snippet"},
                            {
                                "type": "people_also_ask",
                                "items": [
                                    {"title": "Q1"},
                                    {"title": "Q2"},
                                    {"title": "Q3"},
                                ],
                            },
                            {"type": "ai_overview"},
                            {"type": "knowledge_graph"},
                            {"type": "images"},
                            {"type": "video"},
                            {"type": "local_pack"},
                            {"type": "shopping"},
                        ],
                        "item_types": [
                            "organic",
                            "featured_snippet",
                            "people_also_ask",
                            "ai_overview",
                            "knowledge_graph",
                            "images",
                            "video",
                            "local_pack",
                            "shopping",
                        ],
                    }
                ],
            }
        ],
    }


def _empty_results_response() -> dict:
    """Response with no organic results (only SERP features)."""
    return {
        "status_code": 20000,
        "tasks": [
            {
                "result": [
                    {
                        "keyword": "test",
                        "items_count": 0,
                        "items": [{"type": "ai_overview"}],
                        "item_types": ["ai_overview"],
                    }
                ],
            }
        ],
    }


def _error_response() -> dict:
    """DataForSEO error response."""
    return {
        "status_code": 50000,
        "tasks": [
            {
                "status_code": 50000,
                "status_message": "Internal Server Error",
                "result": None,
            }
        ],
    }


# ---------------------------------------------------------------------------
# ATS-001: Happy path — 10 organic results returned
# ---------------------------------------------------------------------------


class TestHappyPath:
    """ATS-001: Standard SERP retrieval."""

    def test_returns_10_organic_results(self) -> None:
        """10 organic results parsed from DataForSEO response."""
        adapter = DataForSeoAdapter(login="test", password="test")
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.return_value = _standard_response()
            response = adapter.fetch_serp("FUE hair transplant", "de", "DE")

        assert len(response.organic_results) == 10
        assert response.api_source == "dataforseo"
        assert response.no_organic_results is False

    def test_result_positions_correct(self) -> None:
        """Results have correct positions 1-10."""
        adapter = DataForSeoAdapter(login="test", password="test")
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.return_value = _standard_response()
            response = adapter.fetch_serp("FUE hair transplant", "de", "DE")

        for i, result in enumerate(response.organic_results):
            assert result.position == i + 1

    def test_result_fields_populated(self) -> None:
        """Results have URL, domain, title, meta_description."""
        adapter = DataForSeoAdapter(login="test", password="test")
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.return_value = _standard_response()
            response = adapter.fetch_serp("FUE hair transplant", "de", "DE")

        first = response.organic_results[0]
        assert first.url == "https://example0.com/fue-transplant"
        assert first.domain == "example0.com"
        assert first.title == "FUE Hair Transplant Guide #1"
        assert first.meta_description == "Meta description for page #1"

    def test_implements_protocol(self) -> None:
        """DataForSeoAdapter implements SerpDataSource protocol."""
        adapter = DataForSeoAdapter(login="test", password="test")
        assert isinstance(adapter, SerpDataSource)


# ---------------------------------------------------------------------------
# Feature detection from item_types
# ---------------------------------------------------------------------------


class TestFeatureDetection:
    """SERP features parsed from DataForSEO item_types."""

    def test_features_detected_from_item_types(self) -> None:
        """Feature flags are set based on item_types array."""
        adapter = DataForSeoAdapter(login="test", password="test")
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.return_value = _response_with_features()
            response = adapter.fetch_serp("test", "en", "US")

        f = response.features
        assert f.ai_overview is True
        assert f.featured_snippet is True
        assert f.people_also_ask is True
        assert f.knowledge_panel is True
        assert f.image_pack is True
        assert f.video_carousel is True
        assert f.local_pack is True
        assert f.shopping_results is True

    def test_paa_questions_extracted(self) -> None:
        """PAA questions extracted from people_also_ask items."""
        adapter = DataForSeoAdapter(login="test", password="test")
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.return_value = _response_with_features()
            response = adapter.fetch_serp("test", "en", "US")

        assert len(response.features.paa_questions) == 3
        assert response.features.paa_questions[0] == "Q1"


# ---------------------------------------------------------------------------
# ATS-005: API failure with retry and graceful degradation
# ---------------------------------------------------------------------------


class TestApiFailure:
    """ATS-005: Retry and graceful degradation."""

    def test_raises_on_persistent_failure(self) -> None:
        """Raises SerpApiError after all retries exhausted."""
        adapter = DataForSeoAdapter(
            login="test",
            password="test",
            max_retries=3,
            retry_delays=(0.0, 0.0, 0.0),
        )
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.side_effect = ConnectionError("API down")
            with pytest.raises(ConnectionError):
                adapter.fetch_serp("test", "en", "US")

        assert mock_post.call_count == 4  # 1 original + 3 retries

    def test_retries_on_error_response(self) -> None:
        """Retries when DataForSEO returns error status code."""
        adapter = DataForSeoAdapter(
            login="test",
            password="test",
            max_retries=2,
            retry_delays=(0.0, 0.0),
        )
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.side_effect = [
                _error_response(),
                _error_response(),
                _standard_response(),
            ]
            response = adapter.fetch_serp("test", "en", "US")

        assert len(response.organic_results) == 10
        assert mock_post.call_count == 3


# ---------------------------------------------------------------------------
# ATS-006: Zero organic results
# ---------------------------------------------------------------------------


class TestZeroOrganic:
    """ATS-006: Zero organic results handling."""

    def test_zero_organic_flagged(self) -> None:
        """SERP with no organic results sets no_organic_results flag."""
        adapter = DataForSeoAdapter(login="test", password="test")
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.return_value = _empty_results_response()
            response = adapter.fetch_serp("test", "en", "US")

        assert len(response.organic_results) == 0
        assert response.no_organic_results is True

    def test_features_still_captured(self) -> None:
        """SERP features are still captured when no organic results."""
        adapter = DataForSeoAdapter(login="test", password="test")
        with patch.object(adapter, "_post_api") as mock_post:
            mock_post.return_value = _empty_results_response()
            response = adapter.fetch_serp("test", "en", "US")

        assert response.features.ai_overview is True


# ---------------------------------------------------------------------------
# INT-007: Credential security
# ---------------------------------------------------------------------------


class TestCredentialSecurity:
    """INT-007: Credentials read from constructor, not hardcoded."""

    def test_credentials_stored_in_instance(self) -> None:
        """Login and password are instance attributes, not hardcoded."""
        adapter = DataForSeoAdapter(login="my_login", password="my_pass")
        assert adapter._login == "my_login"
        assert adapter._password == "my_pass"

    def test_no_hardcoded_api_keys(self) -> None:
        """No actual API keys or passwords hardcoded in adapter source."""
        import inspect

        from src.research_engine.adapters import dataforseo_adapter

        source = inspect.getsource(dataforseo_adapter)
        # Should not contain environment variable reads directly
        assert "os.environ" not in source
        # Should not contain actual credential values (passwords, tokens)
        assert "password123" not in source
        assert "secret" not in source.lower().replace("secretstr", "")
