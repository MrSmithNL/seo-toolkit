"""End-to-end test for the F-001 keyword research pipeline.

Runs the full pipeline with mock adapters and fixture data,
verifying the output schema matches the KeywordRecord contract.
"""

from __future__ import annotations

import uuid
from unittest.mock import patch

import pytest

from src.research_engine.commands.run_keyword_research import (
    RunKeywordResearchCommand,
    run_keyword_research,
)
from src.research_engine.config import ResearchConfig
from src.research_engine.models.contracts import KeywordRecord
from src.research_engine.models.result import Ok
from tests.test_research_engine.conftest import (
    MockAutocomplete,
    MockStorage,
    MockVolumeSource,
)


@pytest.fixture()
def e2e_config() -> ResearchConfig:
    """Config for E2E test."""
    return ResearchConfig(
        environment="test",
        feature_keyword_research=True,
        max_crawl_pages=3,
    )


@pytest.fixture()
def e2e_cmd() -> RunKeywordResearchCommand:
    """Full E2E command with seed keywords and competitors."""
    return RunKeywordResearchCommand(
        tenant_id=uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee"),
        campaign_id="e2e_test",
        target_url="https://example.com",
        locales=["en"],
        seed_keywords=["hair transplant", "fue surgery", "hair loss treatment"],
        competitors=["competitor.com"],
    )


class TestE2EPipeline:
    """End-to-end pipeline test with all adapters."""

    def test_full_pipeline_success(
        self,
        e2e_cmd: RunKeywordResearchCommand,
        e2e_config: ResearchConfig,
    ) -> None:
        """Full pipeline produces valid result with all steps."""
        storage = MockStorage()
        autocomplete = MockAutocomplete()
        volume = MockVolumeSource()

        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(
                e2e_cmd,
                e2e_config,
                storage,
                autocomplete=autocomplete,
                volume_source=volume,
            )

        assert isinstance(result, Ok)
        res = result.value

        # Pipeline produces a result
        assert res.run_id.startswith("run_")
        assert res.keywords_discovered > 0
        assert res.duration_ms >= 0

        # Keywords were persisted
        assert len(storage.keywords) == res.keywords_discovered

    def test_output_converts_to_keyword_record(
        self,
        e2e_cmd: RunKeywordResearchCommand,
        e2e_config: ResearchConfig,
    ) -> None:
        """Pipeline output keywords can be converted to KeywordRecord contract."""
        storage = MockStorage()

        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result = run_keyword_research(e2e_cmd, e2e_config, storage)

        assert isinstance(result, Ok)
        assert len(storage.keywords) > 0

        # Each persisted keyword should be convertible to a KeywordRecord
        for kw in storage.keywords:
            record = KeywordRecord(
                id=kw.id,
                tenant_id=kw.tenant_id,
                campaign_id=kw.campaign_id,
                term=kw.term,
                source=kw.source,
                locale="en",
                difficulty=kw.difficulty,
            )
            assert record.id.startswith("kw_")
            assert record.tenant_id == e2e_cmd.tenant_id
            assert len(record.term) > 0

    def test_pipeline_idempotent_run_ids(
        self,
        e2e_cmd: RunKeywordResearchCommand,
        e2e_config: ResearchConfig,
    ) -> None:
        """Two pipeline runs produce different run_ids."""
        storage1 = MockStorage()
        storage2 = MockStorage()

        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            result1 = run_keyword_research(e2e_cmd, e2e_config, storage1)
            result2 = run_keyword_research(e2e_cmd, e2e_config, storage2)

        assert result1.value.run_id != result2.value.run_id

    def test_all_keywords_have_tenant_id(
        self,
        e2e_cmd: RunKeywordResearchCommand,
        e2e_config: ResearchConfig,
    ) -> None:
        """Every persisted keyword has the correct tenant_id."""
        storage = MockStorage()

        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            run_keyword_research(e2e_cmd, e2e_config, storage)

        for kw in storage.keywords:
            assert kw.tenant_id == e2e_cmd.tenant_id

    def test_all_keywords_have_normalized_key(
        self,
        e2e_cmd: RunKeywordResearchCommand,
        e2e_config: ResearchConfig,
    ) -> None:
        """Every persisted keyword has a non-empty normalized_key."""
        storage = MockStorage()

        with patch(
            "src.research_engine.commands.run_keyword_research.crawl_site"
        ) as mock_crawl:
            mock_crawl.return_value = Ok([])
            run_keyword_research(e2e_cmd, e2e_config, storage)

        for kw in storage.keywords:
            assert kw.normalized_key != ""
            assert kw.normalized_key == kw.normalized_key.lower()
