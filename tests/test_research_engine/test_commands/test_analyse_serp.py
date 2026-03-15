"""Tests for F-004 AnalyseSerpCommand and BatchAnalyseSerpCommand.

TDD: Tests for T-007 covering ATS-001, ATS-004, ATS-005, ATS-006,
ATS-014, INT-003, NFR-4, NFR-17.
"""

from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from src.research_engine.adapters.mock_serp_data_source import (
    MockSerpDataSource,
    make_feature_rich_response,
    make_zero_results_response,
)
from src.research_engine.commands.analyse_serp import (
    AnalyseSerpCommand,
    BatchAnalyseSerpCommand,
    analyse_serp,
    batch_analyse_serp,
)
from src.research_engine.config import ResearchConfig
from src.research_engine.models.result import Err, Ok
from src.research_engine.models.serp import SerpFeatures
from src.research_engine.repos.file_serp_snapshot_repo import FileSerpSnapshotRepo
from src.research_engine.services.serp_rate_limiter import SerpRateLimiter

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")


@pytest.fixture()
def config() -> ResearchConfig:
    """Config with SERP analysis enabled."""
    return ResearchConfig(
        feature_serp_analysis=True,
        serp_daily_limit=50,
        serp_cache_days=7,
    )


@pytest.fixture()
def mock_source() -> MockSerpDataSource:
    """Mock SERP data source."""
    return MockSerpDataSource()


@pytest.fixture()
def rate_limiter() -> SerpRateLimiter:
    """Rate limiter with default limits."""
    return SerpRateLimiter(daily_limits={"mock": 50, "dataforseo": 50})


@pytest.fixture()
def repo(tmp_path: Path) -> FileSerpSnapshotRepo:
    """File-based snapshot repo."""
    return FileSerpSnapshotRepo(data_dir=tmp_path / "serp")


@pytest.fixture()
def cmd() -> AnalyseSerpCommand:
    """Standard analyse command."""
    return AnalyseSerpCommand(
        tenant_id=TENANT_ID,
        keyword_id="kw_abc123",
        keyword_text="FUE hair transplant",
        language="de",
        country="DE",
    )


# ---------------------------------------------------------------------------
# Feature flag
# ---------------------------------------------------------------------------


class TestFeatureFlag:
    """Feature flag gating."""

    def test_disabled_flag_returns_error(
        self,
        cmd: AnalyseSerpCommand,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Returns Err when feature flag is disabled."""
        config = ResearchConfig(feature_serp_analysis=False)
        result = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Err)
        assert "disabled" in result.error.lower()


# ---------------------------------------------------------------------------
# ATS-001: Happy path — standard SERP retrieval
# ---------------------------------------------------------------------------


class TestHappyPath:
    """ATS-001: End-to-end SERP analysis."""

    def test_returns_ok_with_snapshot(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Happy path returns Ok with snapshot details."""
        result = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        output = result.value
        assert output.snapshot_id.startswith("ss_")
        assert output.result_count == 10
        assert output.from_cache is False

    def test_snapshot_persisted(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Snapshot is persisted in the repo after analysis."""
        result = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        latest = repo.get_latest("FUE hair transplant", "de", str(TENANT_ID))
        assert latest is not None
        assert latest.id == result.value.snapshot_id

    def test_rate_limiter_incremented(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Rate limiter counter is incremented after a fetch."""
        analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert rate_limiter.get_daily_count("mock") == 1

    def test_serp_features_populated(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """SERP features are populated in the output."""
        result = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        assert isinstance(result.value.serp_features, SerpFeatures)


# ---------------------------------------------------------------------------
# ATS-016: Cache hit — snapshot within TTL
# ---------------------------------------------------------------------------


class TestCacheHit:
    """ATS-016: Cached snapshot served when within TTL."""

    def test_cached_snapshot_returned(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Second call returns from_cache=True and same snapshot_id."""
        result1 = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result1, Ok)
        result2 = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result2, Ok)
        assert result2.value.from_cache is True
        assert result2.value.snapshot_id == result1.value.snapshot_id
        # Rate limiter should only have 1 call (second was cached)
        assert rate_limiter.get_daily_count("mock") == 1

    def test_force_refresh_bypasses_cache(
        self,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """force_refresh=True bypasses the cache."""
        cmd = AnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            keyword_text="FUE hair transplant",
            language="de",
            country="DE",
            force_refresh=True,
        )
        result1 = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result1, Ok)
        result2 = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result2, Ok)
        assert result2.value.from_cache is False
        assert result2.value.snapshot_id != result1.value.snapshot_id
        assert rate_limiter.get_daily_count("mock") == 2


# ---------------------------------------------------------------------------
# ATS-004: Daily rate limit enforcement
# ---------------------------------------------------------------------------


class TestDailyLimit:
    """ATS-004: Daily rate limit blocks requests."""

    def test_limit_reached_returns_error(
        self,
        cmd: AnalyseSerpCommand,
        mock_source: MockSerpDataSource,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Returns Err when daily limit is reached."""
        config = ResearchConfig(feature_serp_analysis=True, serp_daily_limit=2)
        limiter = SerpRateLimiter(daily_limits={"mock": 2})
        # Exhaust the limit
        limiter.record_request("mock")
        limiter.record_request("mock")
        result = analyse_serp(cmd, config, mock_source, limiter, repo)
        assert isinstance(result, Err)
        assert "daily limit" in result.error.lower()

    def test_no_api_call_when_limited(
        self,
        cmd: AnalyseSerpCommand,
        mock_source: MockSerpDataSource,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """No API call is made when daily limit is reached."""
        config = ResearchConfig(feature_serp_analysis=True, serp_daily_limit=1)
        limiter = SerpRateLimiter(daily_limits={"mock": 1})
        limiter.record_request("mock")
        analyse_serp(cmd, config, mock_source, limiter, repo)
        assert len(mock_source.calls) == 0


# ---------------------------------------------------------------------------
# ATS-005: API failure with graceful degradation
# ---------------------------------------------------------------------------


class TestApiFailure:
    """ATS-005: API failure handling."""

    def test_api_error_returns_err(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Returns Err when SERP data source raises an exception."""
        mock = MockSerpDataSource()
        mock.set_error("FUE hair transplant", ConnectionError("API down"))
        result = analyse_serp(cmd, config, mock, rate_limiter, repo)
        assert isinstance(result, Err)
        assert (
            "serp_unavailable" in result.error.lower() or "api" in result.error.lower()
        )

    def test_failure_does_not_increment_rate_limiter(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Rate limiter is not incremented on API failure."""
        mock = MockSerpDataSource()
        mock.set_error("FUE hair transplant", ConnectionError("API down"))
        analyse_serp(cmd, config, mock, rate_limiter, repo)
        # Rate limiter should not be incremented on failure
        assert rate_limiter.get_daily_count("mock") == 0


# ---------------------------------------------------------------------------
# ATS-006: Zero organic results
# ---------------------------------------------------------------------------


class TestZeroOrganic:
    """ATS-006: Zero organic results flagged."""

    def test_zero_results_flagged(
        self,
        config: ResearchConfig,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Zero organic results sets no_organic_results flag."""
        mock = MockSerpDataSource()
        mock.set_response("zero kw", make_zero_results_response())
        cmd = AnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_zero",
            keyword_text="zero kw",
            language="en",
            country="US",
        )
        result = analyse_serp(cmd, config, mock, rate_limiter, repo)
        assert isinstance(result, Ok)
        assert result.value.result_count == 0
        # Features still captured
        assert result.value.serp_features.ai_overview is True


# ---------------------------------------------------------------------------
# ATS-014: AI Overview warning propagates
# ---------------------------------------------------------------------------


class TestAiOverviewWarning:
    """ATS-014: AI Overview warning propagates to output."""

    def test_ai_overview_warning_in_output(
        self,
        config: ResearchConfig,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """AI Overview detection produces warning in output."""
        mock = MockSerpDataSource()
        mock.set_response("ai kw", make_feature_rich_response())
        cmd = AnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_ai",
            keyword_text="ai kw",
            language="en",
            country="US",
        )
        result = analyse_serp(cmd, config, mock, rate_limiter, repo)
        assert isinstance(result, Ok)
        assert "ai_overview_detected" in result.value.warnings


# ---------------------------------------------------------------------------
# INT-003: F-001 output as input
# ---------------------------------------------------------------------------


class TestF001Integration:
    """INT-003: F-001 output as input pipeline."""

    def test_keyword_fields_used(
        self,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Command accepts keyword fields from F-001 output."""
        cmd = AnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_from_f001",
            keyword_text="keyword from F-001",
            language="en",
            country="US",
        )
        result = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        # Verify the snapshot stores the keyword text
        latest = repo.get_latest("keyword from F-001", "en", str(TENANT_ID))
        assert latest is not None
        assert latest.keyword_text == "keyword from F-001"


# ---------------------------------------------------------------------------
# BatchAnalyseSerpCommand tests
# ---------------------------------------------------------------------------


class TestBatchAnalyse:
    """Batch SERP analysis tests."""

    def test_batch_processes_all_keywords(
        self,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Batch processes all keywords and returns counts."""
        cmd = BatchAnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keywords=[
                {
                    "keyword_id": "kw1",
                    "keyword_text": "keyword one",
                    "language": "en",
                    "country": "US",
                },
                {
                    "keyword_id": "kw2",
                    "keyword_text": "keyword two",
                    "language": "en",
                    "country": "US",
                },
                {
                    "keyword_id": "kw3",
                    "keyword_text": "keyword three",
                    "language": "en",
                    "country": "US",
                },
            ],
            pipeline_run_id="run_test123",
        )
        result = batch_analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        output = result.value
        assert output.completed == 3
        assert output.cached == 0
        assert output.failed == 0
        assert output.queued_for_tomorrow == 0
        assert len(output.snapshots) == 3

    def test_batch_cached_keyword_counted(
        self,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Cached keywords are counted separately in batch."""
        # First: analyse one keyword
        single_cmd = AnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw1",
            keyword_text="keyword one",
            language="en",
            country="US",
        )
        analyse_serp(single_cmd, config, mock_source, rate_limiter, repo)

        # Now batch with the same keyword
        batch_cmd = BatchAnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keywords=[
                {
                    "keyword_id": "kw1",
                    "keyword_text": "keyword one",
                    "language": "en",
                    "country": "US",
                },
                {
                    "keyword_id": "kw2",
                    "keyword_text": "keyword two",
                    "language": "en",
                    "country": "US",
                },
            ],
            pipeline_run_id="run_test456",
        )
        result = batch_analyse_serp(batch_cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        assert result.value.completed == 2
        assert result.value.cached == 1

    def test_batch_daily_limit_queues_remaining(
        self,
        mock_source: MockSerpDataSource,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """NFR-17: Remaining keywords queued when daily limit reached."""
        config = ResearchConfig(feature_serp_analysis=True, serp_daily_limit=2)
        limiter = SerpRateLimiter(daily_limits={"mock": 2})

        batch_cmd = BatchAnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keywords=[
                {
                    "keyword_id": "kw1",
                    "keyword_text": "keyword one",
                    "language": "en",
                    "country": "US",
                },
                {
                    "keyword_id": "kw2",
                    "keyword_text": "keyword two",
                    "language": "en",
                    "country": "US",
                },
                {
                    "keyword_id": "kw3",
                    "keyword_text": "keyword three",
                    "language": "en",
                    "country": "US",
                },
                {
                    "keyword_id": "kw4",
                    "keyword_text": "keyword four",
                    "language": "en",
                    "country": "US",
                },
            ],
            pipeline_run_id="run_limit",
        )
        result = batch_analyse_serp(batch_cmd, config, mock_source, limiter, repo)
        assert isinstance(result, Ok)
        assert result.value.completed == 2
        assert result.value.queued_for_tomorrow == 2

    def test_batch_api_failure_counted(
        self,
        config: ResearchConfig,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """NFR-4: API failure doesn't halt pipeline, counted as failed."""
        mock = MockSerpDataSource()
        mock.set_error("keyword two", ConnectionError("API down"))

        batch_cmd = BatchAnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keywords=[
                {
                    "keyword_id": "kw1",
                    "keyword_text": "keyword one",
                    "language": "en",
                    "country": "US",
                },
                {
                    "keyword_id": "kw2",
                    "keyword_text": "keyword two",
                    "language": "en",
                    "country": "US",
                },
                {
                    "keyword_id": "kw3",
                    "keyword_text": "keyword three",
                    "language": "en",
                    "country": "US",
                },
            ],
            pipeline_run_id="run_fail",
        )
        result = batch_analyse_serp(batch_cmd, config, mock, rate_limiter, repo)
        assert isinstance(result, Ok)
        assert result.value.completed == 2
        assert result.value.failed == 1
        assert len(result.value.errors) == 1
        assert result.value.errors[0]["keyword_id"] == "kw2"

    def test_batch_feature_flag_disabled(
        self,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Batch returns Err when feature flag is disabled."""
        config = ResearchConfig(feature_serp_analysis=False)
        batch_cmd = BatchAnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keywords=[
                {
                    "keyword_id": "kw1",
                    "keyword_text": "kw",
                    "language": "en",
                    "country": "US",
                },
            ],
            pipeline_run_id="run_off",
        )
        result = batch_analyse_serp(batch_cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Err)

    def test_batch_empty_keywords(
        self,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Batch with empty keyword list returns Ok with zero counts."""
        batch_cmd = BatchAnalyseSerpCommand(
            tenant_id=TENANT_ID,
            keywords=[],
            pipeline_run_id="run_empty",
        )
        result = batch_analyse_serp(batch_cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        assert result.value.completed == 0


# ---------------------------------------------------------------------------
# Cost estimate
# ---------------------------------------------------------------------------


class TestCostEstimate:
    """Cost tracking in output."""

    def test_cost_estimate_populated(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Cost estimate is included in output."""
        result = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        assert result.value.cost_estimate_usd is not None

    def test_cached_result_zero_cost(
        self,
        cmd: AnalyseSerpCommand,
        config: ResearchConfig,
        mock_source: MockSerpDataSource,
        rate_limiter: SerpRateLimiter,
        repo: FileSerpSnapshotRepo,
    ) -> None:
        """Cached result has zero cost."""
        analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        result = analyse_serp(cmd, config, mock_source, rate_limiter, repo)
        assert isinstance(result, Ok)
        assert result.value.cost_estimate_usd == "0.0000"
