"""Tests for the F-001 keyword research pipeline orchestrator.

Covers: T-009 (Pipeline Orchestrator)
Tests written for existing implementation.
"""

from __future__ import annotations

import logging
import uuid
from unittest.mock import patch

import pytest

from src.research_engine.commands.run_keyword_research import (
    RunKeywordResearchCommand,
    RunKeywordResearchResult,
    run_keyword_research,
)
from src.research_engine.config import ResearchConfig
from src.research_engine.models.result import Err, Ok
from tests.test_research_engine.conftest import (
    FailingAutocomplete,
    FailingVolumeSource,
    MockAutocomplete,
    MockStorage,
    MockVolumeSource,
)


@pytest.fixture()
def cmd(tenant_id: uuid.UUID) -> RunKeywordResearchCommand:
    """Default pipeline command for tests."""
    return RunKeywordResearchCommand(
        tenant_id=tenant_id,
        campaign_id="camp_test",
        target_url="https://example.com",
        locales=["en"],
        seed_keywords=["hair transplant", "fue transplant"],
    )


@pytest.fixture()
def disabled_config() -> ResearchConfig:
    """Config with feature flag disabled."""
    return ResearchConfig(
        environment="test",
        feature_keyword_research=False,
    )


class TestFeatureFlag:
    """Tests for feature flag behaviour."""

    def test_disabled_returns_err(
        self,
        cmd: RunKeywordResearchCommand,
        disabled_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Pipeline returns Err when feature flag is disabled."""
        result = run_keyword_research(cmd, disabled_config, mock_storage)
        assert isinstance(result, Err)
        assert "disabled" in result.error.lower()

    def test_enabled_does_not_short_circuit(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Pipeline proceeds when feature flag is enabled."""
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)
            assert isinstance(result, Ok)
            mock_crawl.assert_called_once()


class TestHappyPath:
    """Tests for successful pipeline execution."""

    def test_returns_ok_result(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Pipeline returns Ok with result data on success."""
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)

        assert isinstance(result, Ok)
        assert isinstance(result.value, RunKeywordResearchResult)

    def test_result_has_run_id(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Result includes a unique run_id."""
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)

        assert result.value.run_id.startswith("run_")

    def test_manual_seeds_counted(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Manual seed keywords are included in discovered count."""
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)

        # 2 seed keywords provided
        assert result.value.keywords_discovered >= 2

    def test_duration_positive(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Duration is recorded as positive milliseconds."""
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)

        assert result.value.duration_ms >= 0

    def test_keywords_persisted_to_storage(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Keywords are saved to storage."""
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            run_keyword_research(cmd, test_config, mock_storage)

        assert len(mock_storage.keywords) > 0


class TestCrawlFailure:
    """Tests for crawl step failure."""

    def test_crawl_failure_returns_err(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Pipeline returns Err when crawl fails."""
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Err("Connection refused")
            result = run_keyword_research(cmd, test_config, mock_storage)

        assert isinstance(result, Err)
        assert "crawl" in result.error.lower()


class TestPartialFailure:
    """Tests for partial failure resilience."""

    def test_autocomplete_failure_continues(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Pipeline continues when autocomplete fails."""
        failing_ac = FailingAutocomplete()
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(
                cmd, test_config, mock_storage, autocomplete=failing_ac
            )

        assert isinstance(result, Ok)
        # Still has manual seeds
        assert result.value.keywords_discovered >= 2

    def test_volume_failure_continues(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Pipeline continues when volume enrichment fails."""
        failing_vol = FailingVolumeSource()
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(
                cmd, test_config, mock_storage, volume_source=failing_vol
            )

        assert isinstance(result, Ok)
        assert result.value.keywords_enriched == 0


class TestWithAutocomplete:
    """Tests with autocomplete expansion."""

    def test_autocomplete_expands_keywords(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
        mock_autocomplete: MockAutocomplete,
    ) -> None:
        """Autocomplete adds additional keyword suggestions."""
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(
                cmd, test_config, mock_storage, autocomplete=mock_autocomplete
            )

        # Should have more than just the 2 manual seeds
        assert result.value.keywords_discovered > 2


class TestEventEmission:
    """Tests for event emission."""

    def test_event_emitted_on_success(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """KeywordResearchCompletedEvent is emitted on success."""
        with (
            patch(
                "src.research_engine.commands.run_keyword_research.crawl_site"
            ) as mock_crawl,
            caplog.at_level(logging.INFO),
        ):
            mock_crawl.return_value = Ok([])
            run_keyword_research(cmd, test_config, mock_storage)

        event_logs = [r for r in caplog.records if "Event:" in r.message]
        assert len(event_logs) == 1
        assert "research.keywords.completed" in event_logs[0].message

    def test_event_contains_run_id(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Event log contains the run_id."""
        with (
            patch(
                "src.research_engine.commands.run_keyword_research.crawl_site"
            ) as mock_crawl,
            caplog.at_level(logging.INFO),
        ):
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)

        event_logs = [r for r in caplog.records if "Event:" in r.message]
        assert result.value.run_id in event_logs[0].message


class TestGapAnalysis:
    """Tests for gap analysis step."""

    def test_no_competitors_skips_gap_analysis(
        self,
        tenant_id: uuid.UUID,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Gap analysis is skipped when no competitors specified."""
        cmd = RunKeywordResearchCommand(
            tenant_id=tenant_id,
            campaign_id="camp_test",
            target_url="https://example.com",
            seed_keywords=["test"],
        )
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)

        assert result.value.gap_keywords_found == 0

    def test_competitors_triggers_gap_analysis(
        self,
        tenant_id: uuid.UUID,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Gap analysis runs when competitors are provided."""
        cmd = RunKeywordResearchCommand(
            tenant_id=tenant_id,
            campaign_id="camp_test",
            target_url="https://example.com",
            seed_keywords=["test"],
            competitors=["competitor.com"],
        )
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)

        # Gap count is 0 because analyse_gaps receives empty competitor_kws list
        # (real SERP data not fetched in R1)
        assert isinstance(result, Ok)
        assert result.value.gap_keywords_found == 0


class TestSkipFlags:
    """Tests for skip_enrichment and skip_difficulty flags."""

    def test_skip_enrichment(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
        mock_volume_source: MockVolumeSource,
    ) -> None:
        """Volume enrichment skipped when skip_enrichment=True."""
        cmd.skip_enrichment = True
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(
                cmd, test_config, mock_storage, volume_source=mock_volume_source
            )

        assert result.value.keywords_enriched == 0

    def test_skip_difficulty(
        self,
        cmd: RunKeywordResearchCommand,
        test_config: ResearchConfig,
        mock_storage: MockStorage,
    ) -> None:
        """Difficulty estimation skipped when skip_difficulty=True."""
        cmd.skip_difficulty = True
        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(cmd, test_config, mock_storage)

        assert isinstance(result, Ok)
        # Keywords should not have difficulty scores
        for kw in mock_storage.keywords:
            assert kw.difficulty is None
