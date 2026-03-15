"""Tests for Google Autocomplete adapter.

TDD: Tests written BEFORE implementation.
Covers: T-005 (Google Autocomplete Adapter)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.research_engine.adapters.autocomplete import GoogleAutocompleteAdapter
from src.research_engine.ports.data_source import KeywordDataSource

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_fixture(name: str) -> str:
    """Load a fixture file as string."""
    return (FIXTURES_DIR / name).read_text()


class TestGoogleAutocompleteAdapter:
    """Tests for the GoogleAutocompleteAdapter."""

    def test_implements_data_source_protocol(self) -> None:
        """Adapter must implement KeywordDataSource protocol."""
        adapter = GoogleAutocompleteAdapter()
        assert isinstance(adapter, KeywordDataSource)

    def test_capabilities_include_suggestions(self) -> None:
        """Capabilities must include 'suggestions'."""
        adapter = GoogleAutocompleteAdapter()
        assert "suggestions" in adapter.capabilities
        assert "volume" not in adapter.capabilities

    def test_parses_valid_xml_response(self, httpx_mock: pytest.fixture) -> None:
        """Valid autocomplete XML parsed into suggestion strings."""
        xml = _load_fixture("autocomplete-response.xml")
        httpx_mock.add_response(text=xml)  # type: ignore[attr-defined]

        adapter = GoogleAutocompleteAdapter()
        suggestions = adapter.get_keyword_suggestions("hair transplant", "en")

        assert len(suggestions) == 8
        assert "hair transplant cost" in suggestions
        assert "hair transplant turkey" in suggestions

    def test_empty_response_returns_empty_list(
        self, httpx_mock: pytest.fixture
    ) -> None:
        """Empty XML response returns empty list."""
        httpx_mock.add_response(  # type: ignore[attr-defined]
            text='<?xml version="1.0"?><toplevel></toplevel>'
        )
        adapter = GoogleAutocompleteAdapter()
        suggestions = adapter.get_keyword_suggestions("obscure query", "en")
        assert suggestions == []

    def test_http_error_returns_empty_list(self, httpx_mock: pytest.fixture) -> None:
        """HTTP error returns empty list (graceful degradation)."""
        httpx_mock.add_response(status_code=500)  # type: ignore[attr-defined]
        adapter = GoogleAutocompleteAdapter()
        suggestions = adapter.get_keyword_suggestions("test", "en")
        assert suggestions == []

    def test_get_keyword_volume_raises(self) -> None:
        """get_keyword_volume is not supported."""
        adapter = GoogleAutocompleteAdapter()
        with pytest.raises(NotImplementedError):
            adapter.get_keyword_volume(["test"], "en", "US")

    def test_rate_limiter_tracks_calls(self, httpx_mock: pytest.fixture) -> None:
        """Rate limiter tracks number of calls made."""
        xml = _load_fixture("autocomplete-response.xml")
        httpx_mock.add_response(text=xml)  # type: ignore[attr-defined]
        httpx_mock.add_response(text=xml)  # type: ignore[attr-defined]

        adapter = GoogleAutocompleteAdapter(daily_limit=100, delay_seconds=0.0)
        adapter.get_keyword_suggestions("query1", "en")
        adapter.get_keyword_suggestions("query2", "en")
        assert adapter.calls_today == 2

    def test_daily_limit_enforced(self) -> None:
        """After hitting daily limit, returns empty list."""
        adapter = GoogleAutocompleteAdapter(daily_limit=0, delay_seconds=0.0)
        result = adapter.get_keyword_suggestions("test", "en")
        assert result == []
