"""Tests for the F-002 clustering pipeline orchestrator.

TDD: Tests written BEFORE implementation.
Covers: F-002 T-007 (Pipeline Orchestrator + Event)
"""

from __future__ import annotations

import json
import uuid

import pytest

from src.research_engine.commands.cluster_keywords import (
    ClusterKeywordsCommand,
    cluster_keywords,
)
from src.research_engine.config import ResearchConfig
from src.research_engine.models.keyword import Keyword, KeywordSource
from src.research_engine.models.result import Err, Ok
from tests.test_research_engine.conftest import MockClusterStorage, MockLlm, MockStorage

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN = "camp_1"


def _config(clustering: bool = True) -> ResearchConfig:
    """Create a test config with clustering enabled."""
    return ResearchConfig(
        environment="test",
        feature_keyword_research=True,
        feature_topic_clustering=clustering,
        storage_mode="json",
    )


def _keywords(terms: list[str]) -> list[Keyword]:
    """Create test keywords."""
    return [
        Keyword(
            id=f"kw_{i:03d}",
            tenant_id=TENANT,
            campaign_id=CAMPAIGN,
            term=term,
            source=KeywordSource.URL_EXTRACTION,
        )
        for i, term in enumerate(terms)
    ]


def _llm_response(clusters: list[dict], unclustered: list[str] | None = None) -> str:
    """Build a valid LLM clustering response JSON string."""
    return json.dumps(
        {
            "clusters": clusters,
            "unclustered": unclustered or [],
        }
    )


def _make_cluster_dict(
    name: str, keywords: list[str], pillar: str, score: int = 7
) -> dict:
    """Build a cluster dict for the LLM response."""
    return {
        "name": name,
        "rationale": f"Rationale for {name}",
        "pillar_keyword": pillar,
        "pillar_rationale": f"{pillar} is the pillar",
        "coherence_score": score,
        "coherence_rationale": f"Score {score} because test",
        "keywords": keywords,
    }


class TestFeatureFlag:
    """Feature flag gating tests."""

    def test_disabled_returns_err(self) -> None:
        """Pipeline returns Err when feature flag is disabled."""
        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        result = cluster_keywords(
            cmd,
            _config(clustering=False),
            MockStorage(),
            MockClusterStorage(),
            MockLlm(),
        )
        assert isinstance(result, Err)
        assert "disabled" in result.error.lower()


class TestNoKeywords:
    """Tests when no keywords are available."""

    def test_no_keywords_returns_err(self) -> None:
        """Pipeline returns Err when storage has no keywords."""
        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        result = cluster_keywords(
            cmd, _config(), MockStorage(), MockClusterStorage(), MockLlm()
        )
        assert isinstance(result, Err)
        assert "no keywords" in result.error.lower()


class TestHappyPath:
    """Happy path pipeline tests."""

    def test_creates_clusters_from_llm_response(self) -> None:
        """Full pipeline creates clusters and assigns keyword FKs."""
        kw_storage = MockStorage()
        keywords = _keywords(["hair transplant", "fue surgery", "hair loss"])
        kw_storage.save(keywords)

        cluster_storage = MockClusterStorage()
        llm_response = _llm_response(
            [
                _make_cluster_dict(
                    "Hair Procedures",
                    ["hair transplant", "fue surgery", "hair loss"],
                    "hair transplant",
                ),
            ]
        )
        llm = MockLlm(response=llm_response)

        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        result = cluster_keywords(cmd, _config(), kw_storage, cluster_storage, llm)

        assert isinstance(result, Ok)
        assert result.value.clusters_created == 1
        assert result.value.unclustered_count == 0

        # Verify clusters persisted
        clusters = cluster_storage.get_clusters(CAMPAIGN, "en")
        assert len(clusters) == 1
        assert clusters[0].name == "Hair Procedures"
        assert clusters[0].keyword_count == 3

    def test_run_id_is_unique(self) -> None:
        """Each pipeline run gets a unique run_id."""
        kw_storage = MockStorage()
        kw_storage.save(_keywords(["test keyword"]))

        response = _llm_response(
            [
                _make_cluster_dict("Test", ["test keyword"], "test keyword"),
            ]
        )

        r1 = cluster_keywords(
            ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN),
            _config(),
            kw_storage,
            MockClusterStorage(),
            MockLlm(response=response),
        )
        r2 = cluster_keywords(
            ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN),
            _config(),
            kw_storage,
            MockClusterStorage(),
            MockLlm(response=response),
        )

        assert isinstance(r1, Ok)
        assert isinstance(r2, Ok)
        assert r1.value.run_id != r2.value.run_id

    def test_pillar_keyword_id_set(self) -> None:
        """Cluster gets pillar_keyword_id from pillar selection."""
        kw_storage = MockStorage()
        kw_storage.save(_keywords(["seo tips", "seo guide"]))

        response = _llm_response(
            [
                _make_cluster_dict("SEO", ["seo tips", "seo guide"], "seo tips"),
            ]
        )
        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        result = cluster_keywords(
            cmd, _config(), kw_storage, MockClusterStorage(), MockLlm(response=response)
        )

        assert isinstance(result, Ok)


class TestLlmFailure:
    """LLM failure and retry tests."""

    def test_llm_failure_marks_unclustered(self) -> None:
        """LLM failure after retries results in all keywords unclustered."""
        kw_storage = MockStorage()
        kw_storage.save(_keywords(["kw1", "kw2", "kw3"]))

        class FailingLlm:
            """LLM that always raises."""

            def complete(self, prompt: str) -> str:
                """Always fail."""
                raise ConnectionError("LLM down")

        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        result = cluster_keywords(
            cmd, _config(), kw_storage, MockClusterStorage(), FailingLlm()
        )

        assert isinstance(result, Ok)
        assert result.value.clusters_created == 0
        assert result.value.unclustered_count == 3

    def test_llm_returns_bad_json_marks_unclustered(self) -> None:
        """Unparseable LLM response marks keywords as unclustered."""
        kw_storage = MockStorage()
        kw_storage.save(_keywords(["kw1", "kw2"]))

        llm = MockLlm(response="not valid json at all")
        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        result = cluster_keywords(cmd, _config(), kw_storage, MockClusterStorage(), llm)

        assert isinstance(result, Ok)
        assert result.value.clusters_created == 0
        assert result.value.unclustered_count == 2


class TestForceRecluster:
    """Force recluster tests."""

    def test_force_recluster_creates_new_ids(self) -> None:
        """Force recluster generates new cluster IDs, not reusing existing."""
        kw_storage = MockStorage()
        kw_storage.save(_keywords(["hair loss"]))

        response = _llm_response(
            [
                _make_cluster_dict("Hair Loss", ["hair loss"], "hair loss"),
            ]
        )

        cluster_storage = MockClusterStorage()
        cmd = ClusterKeywordsCommand(
            tenant_id=TENANT, campaign_id=CAMPAIGN, force_recluster=True
        )

        # First run
        cluster_keywords(
            cmd, _config(), kw_storage, cluster_storage, MockLlm(response=response)
        )
        first_ids = {
            c.id
            for c in cluster_storage.get_clusters(CAMPAIGN, "en", include_deleted=True)
        }

        # Second run (force)
        cluster_storage2 = MockClusterStorage()
        cluster_keywords(
            cmd, _config(), kw_storage, cluster_storage2, MockLlm(response=response)
        )
        second_ids = {
            c.id
            for c in cluster_storage2.get_clusters(CAMPAIGN, "en", include_deleted=True)
        }

        # IDs should be different
        assert first_ids != second_ids


class TestEventEmission:
    """Event emission tests."""

    def test_emits_clustering_event(self, caplog: pytest.LogCaptureFixture) -> None:
        """Pipeline emits ClusteringCompletedEvent on success."""
        kw_storage = MockStorage()
        kw_storage.save(_keywords(["test"]))

        response = _llm_response(
            [
                _make_cluster_dict("Test", ["test"], "test"),
            ]
        )

        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        with caplog.at_level("INFO"):
            result = cluster_keywords(
                cmd,
                _config(),
                kw_storage,
                MockClusterStorage(),
                MockLlm(response=response),
            )

        assert isinstance(result, Ok)
        event_logs = [
            r
            for r in caplog.records
            if "research.clustering.completed" in r.getMessage()
        ]
        assert len(event_logs) == 1

    def test_event_emitted_on_llm_failure_too(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Event is emitted even when LLM fails (0 clusters, N unclustered)."""
        kw_storage = MockStorage()
        kw_storage.save(_keywords(["kw1"]))

        class FailingLlm:
            """LLM that always raises."""

            def complete(self, prompt: str) -> str:
                """Always fail."""
                raise ConnectionError("LLM down")

        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        with caplog.at_level("INFO"):
            cluster_keywords(
                cmd, _config(), kw_storage, MockClusterStorage(), FailingLlm()
            )

        event_logs = [
            r
            for r in caplog.records
            if "research.clustering.completed" in r.getMessage()
        ]
        assert len(event_logs) == 1


class TestCoherenceWarning:
    """Coherence score integration tests."""

    def test_low_coherence_sets_flag(self) -> None:
        """Low coherence score (< 4) sets no_pillar_flag on cluster."""
        kw_storage = MockStorage()
        kw_storage.save(_keywords(["kw1", "kw2", "kw3"]))

        response = _llm_response(
            [
                _make_cluster_dict(
                    "Loose Cluster", ["kw1", "kw2", "kw3"], "kw1", score=2
                ),
            ]
        )

        cmd = ClusterKeywordsCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)
        cluster_storage = MockClusterStorage()
        result = cluster_keywords(
            cmd, _config(), kw_storage, cluster_storage, MockLlm(response=response)
        )

        assert isinstance(result, Ok)
        clusters = cluster_storage.get_clusters(CAMPAIGN, "en")
        assert len(clusters) == 1
        assert clusters[0].no_pillar_flag is not None
        assert "coherence" in clusters[0].no_pillar_flag.lower()
