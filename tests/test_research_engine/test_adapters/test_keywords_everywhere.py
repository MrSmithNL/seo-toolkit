"""Tests for Keywords Everywhere adapter.

TDD: Tests written BEFORE implementation.
Covers: T-006 (Keywords Everywhere Adapter)
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import SecretStr

from src.research_engine.adapters.keywords_everywhere import KeywordsEverywhereAdapter
from src.research_engine.ports.data_source import KeywordDataSource

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_fixture_json(name: str) -> dict:
    """Load a JSON fixture file."""
    return json.loads((FIXTURES_DIR / name).read_text())


class TestKeywordsEverywhereAdapter:
    """Tests for the KeywordsEverywhereAdapter."""

    def test_implements_data_source_protocol(self) -> None:
        """Adapter must implement KeywordDataSource protocol."""
        adapter = KeywordsEverywhereAdapter(api_key=SecretStr("test-key"))
        assert isinstance(adapter, KeywordDataSource)

    def test_capabilities(self) -> None:
        """Capabilities must include volume, suggestions, trends."""
        adapter = KeywordsEverywhereAdapter(api_key=SecretStr("test-key"))
        assert adapter.capabilities == {"volume", "suggestions", "trends"}

    def test_happy_path_returns_volume_data(self, httpx_mock: pytest.fixture) -> None:
        """ATS-006: Valid response returns volume, CPC, trend."""
        fixture = _load_fixture_json("keywords-everywhere-response.json")
        httpx_mock.add_response(json=fixture)  # type: ignore[attr-defined]

        adapter = KeywordsEverywhereAdapter(api_key=SecretStr("test-key"))
        results = adapter.get_keyword_volume(
            ["hair transplant cost", "hair transplant turkey"],
            locale="en",
            country="US",
        )

        assert len(results) >= 2
        first = next(r for r in results if r.keyword == "hair transplant cost")
        assert first.volume == 12100
        assert first.cpc == 4.52
        assert first.trend is not None
        assert len(first.trend) == 12

    def test_zero_volume_retained(self, httpx_mock: pytest.fixture) -> None:
        """ATS-008: Keywords with zero volume are NOT filtered out."""
        fixture = _load_fixture_json("keywords-everywhere-response.json")
        httpx_mock.add_response(json=fixture)  # type: ignore[attr-defined]

        adapter = KeywordsEverywhereAdapter(api_key=SecretStr("test-key"))
        results = adapter.get_keyword_volume(
            ["hair transplant near me"], locale="en", country="US"
        )

        zero_vol = [r for r in results if r.volume == 0]
        assert len(zero_vol) >= 1

    def test_batch_size_100(self, httpx_mock: pytest.fixture) -> None:
        """ATS-009: 150 keywords should produce 2 API calls."""
        fixture = _load_fixture_json("keywords-everywhere-response.json")
        httpx_mock.add_response(json=fixture)  # type: ignore[attr-defined]
        httpx_mock.add_response(json=fixture)  # type: ignore[attr-defined]

        adapter = KeywordsEverywhereAdapter(api_key=SecretStr("test-key"))
        keywords = [f"keyword_{i}" for i in range(150)]
        adapter.get_keyword_volume(keywords, locale="en", country="US")

        requests = httpx_mock.get_requests()  # type: ignore[attr-defined]
        assert len(requests) == 2

    def test_retry_on_429(self, httpx_mock: pytest.fixture) -> None:
        """ATS-010: Retries on 429 with exponential backoff."""
        fixture = _load_fixture_json("keywords-everywhere-response.json")
        httpx_mock.add_response(status_code=429)  # type: ignore[attr-defined]
        httpx_mock.add_response(json=fixture)  # type: ignore[attr-defined]

        adapter = KeywordsEverywhereAdapter(
            api_key=SecretStr("test-key"), base_retry_delay=0.0
        )
        results = adapter.get_keyword_volume(
            ["hair transplant cost"], locale="en", country="US"
        )
        assert len(results) > 0

    def test_retry_exhausted_returns_empty(self, httpx_mock: pytest.fixture) -> None:
        """After max retries, returns empty list."""
        httpx_mock.add_response(status_code=500)  # type: ignore[attr-defined]
        httpx_mock.add_response(status_code=500)  # type: ignore[attr-defined]
        httpx_mock.add_response(status_code=500)  # type: ignore[attr-defined]
        httpx_mock.add_response(status_code=500)  # type: ignore[attr-defined]

        adapter = KeywordsEverywhereAdapter(
            api_key=SecretStr("test-key"), base_retry_delay=0.0
        )
        results = adapter.get_keyword_volume(["test"], locale="en", country="US")
        assert results == []

    def test_api_key_not_in_repr(self) -> None:
        """API key must not appear in repr."""
        adapter = KeywordsEverywhereAdapter(api_key=SecretStr("super-secret"))
        assert "super-secret" not in repr(adapter)

    @given(count=st.integers(min_value=1, max_value=500))
    @settings(max_examples=20)
    def test_property_batch_efficiency(self, count: int) -> None:
        """Property: API calls <= ceil(keywords / 100)."""
        expected_calls = math.ceil(count / 100)
        adapter = KeywordsEverywhereAdapter(api_key=SecretStr("test-key"))
        batches = adapter._compute_batches([f"kw_{i}" for i in range(count)])
        assert len(batches) == expected_calls
