"""Shared test fixtures for the Research Engine test suite.

Provides mock adapters, sample config, and reusable fixtures.
"""

from __future__ import annotations

import uuid

import pytest

from src.research_engine.config import ResearchConfig
from src.research_engine.models.keyword import Keyword, KeywordGap
from src.research_engine.ports.data_source import KeywordVolumeResult

# ---------------------------------------------------------------------------
# Test config
# ---------------------------------------------------------------------------


@pytest.fixture()
def test_config() -> ResearchConfig:
    """ResearchConfig with environment='test' and feature flag enabled."""
    return ResearchConfig(
        environment="test",
        feature_keyword_research=True,
        storage_mode="json",
        max_crawl_pages=5,
        autocomplete_daily_limit=100,
        autocomplete_delay_seconds=0.0,
    )


@pytest.fixture()
def tenant_id() -> uuid.UUID:
    """Fixed tenant_id for tests."""
    return uuid.UUID("12345678-1234-1234-1234-123456789abc")


# ---------------------------------------------------------------------------
# Mock storage adapter (in-memory)
# ---------------------------------------------------------------------------


class MockStorage:
    """In-memory storage implementing KeywordStoragePort."""

    def __init__(self) -> None:  # noqa: D107
        self.keywords: list[Keyword] = []
        self.gaps: list[KeywordGap] = []

    def save(self, keywords: list[Keyword]) -> int:
        """Save keywords, deduping by normalized_key."""
        existing_keys = {kw.normalized_key for kw in self.keywords}
        count = 0
        for kw in keywords:
            if kw.normalized_key not in existing_keys:
                self.keywords.append(kw)
                existing_keys.add(kw.normalized_key)
                count += 1
        return count

    def get_by_campaign(
        self,
        campaign_id: str,
        locale: str | None = None,
        min_volume: int | None = None,
        max_difficulty: int | None = None,
    ) -> list[Keyword]:
        """Query keywords by campaign."""
        return [kw for kw in self.keywords if kw.campaign_id == campaign_id]

    def save_gaps(self, gaps: list[KeywordGap]) -> int:
        """Save gap records."""
        self.gaps.extend(gaps)
        return len(gaps)

    def get_gaps(self, campaign_id: str) -> list[KeywordGap]:
        """Get gaps by campaign."""
        return [g for g in self.gaps if g.campaign_id == campaign_id]


@pytest.fixture()
def mock_storage() -> MockStorage:
    """In-memory mock storage."""
    return MockStorage()


# ---------------------------------------------------------------------------
# Mock autocomplete adapter
# ---------------------------------------------------------------------------


class MockAutocomplete:
    """Mock autocomplete data source."""

    @property
    def capabilities(self) -> set[str]:
        """Return supported capabilities."""
        return {"suggestions"}

    def get_keyword_volume(
        self, keywords: list[str], locale: str, country: str
    ) -> list[KeywordVolumeResult]:
        """Not supported."""
        raise NotImplementedError

    def get_keyword_suggestions(self, seed: str, locale: str) -> list[str]:
        """Return canned suggestions based on seed."""
        return [f"{seed} cost", f"{seed} results", f"best {seed}"]


@pytest.fixture()
def mock_autocomplete() -> MockAutocomplete:
    """Mock autocomplete adapter."""
    return MockAutocomplete()


# ---------------------------------------------------------------------------
# Mock volume source adapter
# ---------------------------------------------------------------------------


class MockVolumeSource:
    """Mock volume data source."""

    @property
    def capabilities(self) -> set[str]:
        """Return supported capabilities."""
        return {"volume", "suggestions", "trends"}

    def get_keyword_volume(
        self, keywords: list[str], locale: str, country: str
    ) -> list[KeywordVolumeResult]:
        """Return mock volume data."""
        return [
            KeywordVolumeResult(keyword=kw, volume=1000 + i * 100, cpc=1.5)
            for i, kw in enumerate(keywords)
        ]

    def get_keyword_suggestions(self, seed: str, locale: str) -> list[str]:
        """Return suggestions."""
        return [f"{seed} tips"]


@pytest.fixture()
def mock_volume_source() -> MockVolumeSource:
    """Mock volume data source."""
    return MockVolumeSource()


# ---------------------------------------------------------------------------
# Failing adapters (for partial failure tests)
# ---------------------------------------------------------------------------


class FailingAutocomplete:
    """Autocomplete adapter that always fails."""

    @property
    def capabilities(self) -> set[str]:
        """Return supported capabilities."""
        return {"suggestions"}

    def get_keyword_volume(
        self, keywords: list[str], locale: str, country: str
    ) -> list[KeywordVolumeResult]:
        """Not supported."""
        raise NotImplementedError

    def get_keyword_suggestions(self, seed: str, locale: str) -> list[str]:
        """Always fails."""
        raise ConnectionError("Autocomplete service down")


class FailingVolumeSource:
    """Volume source that always fails."""

    @property
    def capabilities(self) -> set[str]:
        """Return supported capabilities."""
        return {"volume"}

    def get_keyword_volume(
        self, keywords: list[str], locale: str, country: str
    ) -> list[KeywordVolumeResult]:
        """Always fails."""
        raise ConnectionError("Volume service down")

    def get_keyword_suggestions(self, seed: str, locale: str) -> list[str]:
        """Not supported."""
        raise NotImplementedError


@pytest.fixture()
def failing_autocomplete() -> FailingAutocomplete:
    """Autocomplete adapter that always fails."""
    return FailingAutocomplete()


@pytest.fixture()
def failing_volume_source() -> FailingVolumeSource:
    """Volume source that always fails."""
    return FailingVolumeSource()
