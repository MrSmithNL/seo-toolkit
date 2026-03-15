"""Shared test fixtures for the Research Engine test suite.

Provides mock adapters, sample config, and reusable fixtures.
"""

from __future__ import annotations

import uuid
from datetime import datetime

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

    def update_intent_fields(
        self,
        keyword_id: str,
        intent: str,
        intent_confidence: str,
        intent_rationale: str,
        recommended_format: str,
        format_signal: str | None,
        classified_at: datetime,
    ) -> bool:
        """Update intent classification fields on a keyword."""
        for kw in self.keywords:
            if kw.id == keyword_id:
                object.__setattr__(kw, "intent", intent)
                object.__setattr__(kw, "intent_confidence", intent_confidence)
                object.__setattr__(kw, "intent_rationale", intent_rationale)
                object.__setattr__(kw, "recommended_format", recommended_format)
                object.__setattr__(kw, "format_signal", format_signal)
                object.__setattr__(kw, "classified_at", classified_at)
                return True
        return False


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


# ---------------------------------------------------------------------------
# Mock cluster storage adapter (F-002)
# ---------------------------------------------------------------------------


class MockClusterStorage:
    """In-memory storage implementing ClusterStoragePort."""

    def __init__(self) -> None:  # noqa: D107
        self.clusters: list[dict] = []
        self.keyword_assignments: dict[str, str | None] = {}
        self.deleted_ids: set[str] = set()

    def save_clusters(self, clusters: list) -> int:
        """Save clusters by upsert on id."""
        existing_ids = {c["id"] for c in self.clusters}
        count = 0
        for cluster in clusters:
            dumped = cluster.model_dump(mode="json")
            if dumped["id"] in existing_ids:
                self.clusters = [
                    dumped if c["id"] == dumped["id"] else c for c in self.clusters
                ]
            else:
                self.clusters.append(dumped)
            count += 1
        return count

    def get_clusters(
        self,
        campaign_id: str,
        locale: str,
        include_deleted: bool = False,
    ) -> list:
        """Query clusters."""
        from src.research_engine.models.cluster import KeywordCluster

        results = []
        for data in self.clusters:
            if data["campaign_id"] != campaign_id:
                continue
            if data["locale"] != locale:
                continue
            cluster = KeywordCluster.model_validate(data)
            if not include_deleted and cluster.deleted_at is not None:
                continue
            results.append(cluster)
        return results

    def soft_delete(self, cluster_ids: list[str]) -> int:
        """Soft-delete clusters."""
        from datetime import UTC, datetime

        count = 0
        for item in self.clusters:
            if item["id"] in cluster_ids and item.get("deleted_at") is None:
                item["deleted_at"] = datetime.now(tz=UTC).isoformat()
                self.deleted_ids.add(item["id"])
                count += 1
        return count

    def update_keyword_cluster_ids(
        self,
        assignments: dict[str, str | None],
        campaign_id: str,
    ) -> int:
        """Track keyword cluster assignments."""
        self.keyword_assignments.update(assignments)
        return len(assignments)


@pytest.fixture()
def mock_cluster_storage() -> MockClusterStorage:
    """In-memory mock cluster storage."""
    return MockClusterStorage()


# ---------------------------------------------------------------------------
# Mock LLM adapter (F-002)
# ---------------------------------------------------------------------------


class MockLlm:
    """Mock LLM that returns canned clustering responses."""

    def __init__(self, response: str = "") -> None:  # noqa: D107
        self.response = response
        self.calls: list[str] = []

    def complete(self, prompt: str) -> str:
        """Return canned response, tracking calls."""
        self.calls.append(prompt)
        return self.response


@pytest.fixture()
def mock_llm() -> MockLlm:
    """Mock LLM adapter."""
    return MockLlm()
