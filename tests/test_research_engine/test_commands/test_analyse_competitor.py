"""Tests for AnalyseCompetitorPage + BatchAnalyseCompetitors (T-008).

ATS-001: Happy path — full extraction + quality assessment.
ATS-002: robots.txt blocked → skipped, logged.
ATS-003: 404 → crawl_failed, pipeline continues.
ATS-006: 429 → retry → crawl_failed, pipeline continues.
INT-001: F-004 output as input (SERP URLs).
INT-002: F-005 output consumable by F-006.
INT-006: Token budget compliance.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from src.research_engine.commands.analyse_competitor import (
    AnalyseCompetitorPageCommand,
    BatchAnalyseCompetitorsCommand,
    analyse_competitor_page,
    batch_analyse_competitors,
)
from src.research_engine.config import ResearchConfig
from src.research_engine.models.competitor import (
    CompetitorBenchmark,
    CompetitorSnapshot,
    CrawlStatus,
    QualityAssessmentStatus,
)
from src.research_engine.models.result import Err, Ok

# ---------------------------------------------------------------------------
# Mock dependencies
# ---------------------------------------------------------------------------

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")


class MockPageDownloader:
    """Fake downloader returning canned responses."""

    def __init__(
        self,
        responses: dict[str, tuple[bool, int, str, str]] | None = None,
    ) -> None:
        """responses: {url: (success, status, html, hash)}."""
        self._responses = responses or {}
        self.calls: list[str] = []

    def download(self, url: str):
        self.calls.append(url)
        if url in self._responses:
            success, status, html, html_hash = self._responses[url]
            return _FakeDownloadResult(
                success=success,
                http_status_code=status,
                html=html,
                raw_html_hash=html_hash,
                is_robots_blocked=False,
                retries_attempted=0,
                error=None if success else f"HTTP {status}",
            )
        # Default: 404
        return _FakeDownloadResult(
            success=False,
            http_status_code=404,
            html="",
            raw_html_hash="",
            is_robots_blocked=False,
            retries_attempted=0,
            error="HTTP 404",
        )


class MockRobotsBlockedDownloader:
    """Downloader that always reports robots blocked."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def download(self, url: str):
        self.calls.append(url)
        return _FakeDownloadResult(
            success=False,
            http_status_code=0,
            html="",
            raw_html_hash="",
            is_robots_blocked=True,
            retries_attempted=0,
            error="Blocked by robots.txt",
        )


class MockRetryFailDownloader:
    """Downloader that simulates 429 with retries."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def download(self, url: str):
        self.calls.append(url)
        return _FakeDownloadResult(
            success=False,
            http_status_code=429,
            html="",
            raw_html_hash="",
            is_robots_blocked=False,
            retries_attempted=3,
            error="HTTP 429 after 3 retries",
        )


@dataclass
class _FakeDownloadResult:
    success: bool
    http_status_code: int
    html: str
    raw_html_hash: str
    is_robots_blocked: bool
    retries_attempted: int
    error: str | None


class MockContentExtractor:
    """Returns canned extraction results."""

    def __init__(
        self,
        word_count: int = 2500,
        h1_text: str = "Test Title",
        h2_count: int = 7,
        h2_texts: list[str] | None = None,
        h3_count: int = 3,
        schema_types: list[str] | None = None,
    ) -> None:
        self.word_count = word_count
        self.h1_text = h1_text
        self.h2_count = h2_count
        self.h2_texts = h2_texts or ["H2 One", "H2 Two"]
        self.h3_count = h3_count
        self.schema_types = schema_types or ["Article"]
        self.calls: list[str] = []

    def extract(self, html: str, url: str):
        self.calls.append(url)
        return _FakeExtractionResult(
            word_count=self.word_count,
            h1_text=self.h1_text,
            h2_count=self.h2_count,
            h2_texts=self.h2_texts,
            h3_count=self.h3_count,
            schema_types=self.schema_types,
            has_faq_section=False,
            internal_link_count=5,
            external_link_count=3,
            image_count=2,
            is_thin_content=self.word_count < 300,
            is_js_rendered=False,
            body_text="Test body text content.",
        )


@dataclass
class _FakeExtractionResult:
    word_count: int
    h1_text: str | None
    h2_count: int
    h2_texts: list[str]
    h3_count: int
    schema_types: list[str]
    has_faq_section: bool
    internal_link_count: int
    external_link_count: int
    image_count: int
    is_thin_content: bool
    is_js_rendered: bool
    body_text: str


class MockQualityAssessor:
    """Returns canned quality assessment."""

    def __init__(
        self,
        depth_score: int = 4,
        fail: bool = False,
    ) -> None:
        self.depth_score = depth_score
        self.fail = fail
        self.calls: list[str] = []

    def assess_single(self, compressed_text: str, url: str):
        self.calls.append(url)
        if self.fail:
            return _FakeAssessmentResult(
                status=QualityAssessmentStatus.FAILED,
                profile=None,
                error="LLM unavailable",
                tokens_used=0,
            )
        return _FakeAssessmentResult(
            status=QualityAssessmentStatus.COMPLETED,
            profile=_FakeQualityProfile(
                depth_score=self.depth_score,
                topics_covered=["topic1", "topic2"],
                has_original_data=self.depth_score >= 4,
                has_author_credentials=self.depth_score >= 4,
                eeat_signals=["author_bio"] if self.depth_score >= 4 else [],
                quality_rationale="Solid quality assessment.",
                llm_assessed_fields=[
                    "depth_score",
                    "topics_covered",
                    "has_original_data",
                    "has_author_credentials",
                    "eeat_signals",
                    "quality_rationale",
                ],
            ),
            error=None,
            tokens_used=350,
        )


@dataclass
class _FakeAssessmentResult:
    status: QualityAssessmentStatus
    profile: _FakeQualityProfile | None
    error: str | None
    tokens_used: int


@dataclass
class _FakeQualityProfile:
    depth_score: int
    topics_covered: list[str]
    has_original_data: bool
    has_author_credentials: bool
    eeat_signals: list[str]
    quality_rationale: str
    llm_assessed_fields: list[str]


class MockSnapshotRepo:
    """In-memory snapshot repository."""

    def __init__(self) -> None:
        self.snapshots: list[CompetitorSnapshot] = []

    def save_snapshot(self, snapshot: CompetitorSnapshot) -> str:
        self.snapshots.append(snapshot)
        return snapshot.id

    def get_latest(self, url: str, tenant_id: str) -> CompetitorSnapshot | None:
        matches = [
            s for s in self.snapshots if s.url == url and str(s.tenant_id) == tenant_id
        ]
        if not matches:
            return None
        return max(matches, key=lambda s: s.crawled_at)

    def get_by_keyword(
        self, keyword_id: str, tenant_id: str
    ) -> list[CompetitorBenchmark]:
        return []


class MockEventEmitter:
    """Captures emitted events."""

    def __init__(self) -> None:
        self.events: list = []

    def emit(self, event) -> None:
        self.events.append(event)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _config(enabled: bool = True) -> ResearchConfig:
    return ResearchConfig(
        feature_competitor_analysis=enabled,
        crawl_min_delay_ms=0,
        crawl_max_concurrent=2,
        crawl_max_retries=2,
    )


def _make_deps(
    downloader=None,
    extractor=None,
    assessor=None,
    repo=None,
    events=None,
):
    """Build dependency dict for command."""
    return {
        "downloader": downloader
        or MockPageDownloader(
            {
                "https://example.com/page": (
                    True,
                    200,
                    "<html>Content</html>",
                    "abc123",
                ),
            }
        ),
        "extractor": extractor or MockContentExtractor(),
        "assessor": assessor or MockQualityAssessor(),
        "repo": repo or MockSnapshotRepo(),
        "events": events or MockEventEmitter(),
    }


# ---------------------------------------------------------------------------
# ATS-001: Happy path — full extraction + quality assessment
# ---------------------------------------------------------------------------


class TestHappyPath:
    """ATS-001: Full pipeline success."""

    def test_single_page_analysis(self) -> None:
        deps = _make_deps()
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        result = analyse_competitor_page(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.crawl_status == CrawlStatus.SUCCESS
        assert result.value.word_count == 2500
        assert result.value.depth_score == 4
        assert result.value.content_changed is False

    def test_snapshot_persisted(self) -> None:
        repo = MockSnapshotRepo()
        deps = _make_deps(repo=repo)
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        analyse_competitor_page(cmd, _config(), **deps)
        assert len(repo.snapshots) == 1
        snap = repo.snapshots[0]
        assert snap.url == "https://example.com/page"
        assert snap.word_count == 2500
        assert snap.crawl_status == CrawlStatus.SUCCESS

    def test_event_emitted(self) -> None:
        events = MockEventEmitter()
        deps = _make_deps(events=events)
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        analyse_competitor_page(cmd, _config(), **deps)
        assert len(events.events) == 1
        assert events.events[0].type == "research.competitor.analysed"


# ---------------------------------------------------------------------------
# ATS-002: robots.txt blocked
# ---------------------------------------------------------------------------


class TestRobotsBlocked:
    """ATS-002: robots.txt blocks → skipped, logged."""

    def test_robots_blocked_returns_result(self) -> None:
        deps = _make_deps(downloader=MockRobotsBlockedDownloader())
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/private/page",
            domain="example.com",
            serp_position=3,
        )
        result = analyse_competitor_page(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.crawl_status == CrawlStatus.ROBOTS_BLOCKED

    def test_robots_blocked_snapshot_saved(self) -> None:
        repo = MockSnapshotRepo()
        deps = _make_deps(
            downloader=MockRobotsBlockedDownloader(),
            repo=repo,
        )
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/private/page",
            domain="example.com",
            serp_position=3,
        )
        analyse_competitor_page(cmd, _config(), **deps)
        assert len(repo.snapshots) == 1
        assert repo.snapshots[0].crawl_status == CrawlStatus.ROBOTS_BLOCKED


# ---------------------------------------------------------------------------
# ATS-003: 404 → crawl_failed, pipeline continues
# ---------------------------------------------------------------------------


class TestHttp404:
    """ATS-003: 404 → crawl_failed, pipeline continues."""

    def test_404_returns_crawl_failed(self) -> None:
        deps = _make_deps(downloader=MockPageDownloader({}))
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/missing",
            domain="example.com",
            serp_position=3,
        )
        result = analyse_competitor_page(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.crawl_status == CrawlStatus.CRAWL_FAILED

    def test_404_snapshot_saved_with_failed_status(self) -> None:
        repo = MockSnapshotRepo()
        deps = _make_deps(downloader=MockPageDownloader({}), repo=repo)
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/missing",
            domain="example.com",
            serp_position=3,
        )
        analyse_competitor_page(cmd, _config(), **deps)
        assert len(repo.snapshots) == 1
        assert repo.snapshots[0].crawl_status == CrawlStatus.CRAWL_FAILED


# ---------------------------------------------------------------------------
# ATS-006: 429 → retry → crawl_failed
# ---------------------------------------------------------------------------


class TestRateLimit429:
    """ATS-006: 429 with retries → crawl_failed, pipeline continues."""

    def test_429_returns_crawl_failed(self) -> None:
        deps = _make_deps(downloader=MockRetryFailDownloader())
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        result = analyse_competitor_page(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.crawl_status == CrawlStatus.CRAWL_FAILED


# ---------------------------------------------------------------------------
# Feature flag check
# ---------------------------------------------------------------------------


class TestFeatureFlag:
    """Feature flag FEATURE_COMPETITOR_ANALYSIS gated."""

    def test_disabled_returns_error(self) -> None:
        deps = _make_deps()
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        result = analyse_competitor_page(cmd, _config(enabled=False), **deps)
        assert isinstance(result, Err)
        assert "disabled" in result.error.lower()


# ---------------------------------------------------------------------------
# Change detection
# ---------------------------------------------------------------------------


class TestChangeDetection:
    """Content change detection via raw_html_hash."""

    def test_first_crawl_content_changed_false(self) -> None:
        repo = MockSnapshotRepo()
        deps = _make_deps(repo=repo)
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        result = analyse_competitor_page(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.content_changed is False

    def test_second_crawl_different_hash_detects_change(self) -> None:
        repo = MockSnapshotRepo()
        # First crawl
        deps1 = _make_deps(
            downloader=MockPageDownloader(
                {
                    "https://example.com/page": (
                        True,
                        200,
                        "<html>V1</html>",
                        "hash_v1",
                    ),
                }
            ),
            repo=repo,
        )
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        analyse_competitor_page(cmd, _config(), **deps1)

        # Second crawl with different hash
        deps2 = _make_deps(
            downloader=MockPageDownloader(
                {
                    "https://example.com/page": (
                        True,
                        200,
                        "<html>V2</html>",
                        "hash_v2",
                    ),
                }
            ),
            repo=repo,
        )
        result = analyse_competitor_page(cmd, _config(), **deps2)
        assert isinstance(result, Ok)
        assert result.value.content_changed is True


# ---------------------------------------------------------------------------
# LLM failure graceful degradation
# ---------------------------------------------------------------------------


class TestLlmFailure:
    """LLM failure → quality skipped, snapshot still saved."""

    def test_llm_failure_saves_snapshot_without_quality(self) -> None:
        repo = MockSnapshotRepo()
        deps = _make_deps(
            assessor=MockQualityAssessor(fail=True),
            repo=repo,
        )
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        result = analyse_competitor_page(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.crawl_status == CrawlStatus.SUCCESS
        assert len(repo.snapshots) == 1
        assert (
            repo.snapshots[0].quality_assessment_status
            == QualityAssessmentStatus.FAILED
        )


# ---------------------------------------------------------------------------
# Batch analysis
# ---------------------------------------------------------------------------


class TestBatchAnalysis:
    """BatchAnalyseCompetitors — processes URLs from SERP."""

    def test_batch_processes_all_urls(self) -> None:
        urls = [
            {
                "url": f"https://site{i}.com/page",
                "domain": f"site{i}.com",
                "serp_position": i + 1,
            }
            for i in range(5)
        ]
        downloader = MockPageDownloader(
            {
                u["url"]: (True, 200, f"<html>Content {i}</html>", f"hash_{i}")
                for i, u in enumerate(urls)
            }
        )
        deps = _make_deps(downloader=downloader)
        cmd = BatchAnalyseCompetitorsCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            urls=urls,
            pipeline_run_id="run_001",
        )
        result = batch_analyse_competitors(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.succeeded == 5
        assert result.value.failed == 0
        assert result.value.robots_blocked == 0

    def test_batch_counts_failures(self) -> None:
        urls = [
            {"url": "https://good.com/page", "domain": "good.com", "serp_position": 1},
            {"url": "https://bad.com/page", "domain": "bad.com", "serp_position": 2},
        ]
        downloader = MockPageDownloader(
            {
                "https://good.com/page": (True, 200, "<html>OK</html>", "hash_ok"),
                # bad.com will get default 404
            }
        )
        deps = _make_deps(downloader=downloader)
        cmd = BatchAnalyseCompetitorsCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            urls=urls,
            pipeline_run_id="run_002",
        )
        result = batch_analyse_competitors(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.succeeded == 1
        assert (
            result.value.failed == 1
        )  # 404 is a crawl failure, still "succeeded" for pipeline

    def test_batch_counts_robots_blocked(self) -> None:
        urls = [
            {
                "url": "https://blocked.com/page",
                "domain": "blocked.com",
                "serp_position": 1,
            },
        ]
        deps = _make_deps(downloader=MockRobotsBlockedDownloader())
        cmd = BatchAnalyseCompetitorsCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            urls=urls,
            pipeline_run_id="run_003",
        )
        result = batch_analyse_competitors(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.robots_blocked == 1

    def test_batch_emits_batch_event(self) -> None:
        events = MockEventEmitter()
        urls = [
            {
                "url": "https://example.com/page",
                "domain": "example.com",
                "serp_position": 1,
            },
        ]
        deps = _make_deps(
            downloader=MockPageDownloader(
                {
                    "https://example.com/page": (
                        True,
                        200,
                        "<html>Content</html>",
                        "hash1",
                    ),
                }
            ),
            events=events,
        )
        cmd = BatchAnalyseCompetitorsCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            urls=urls,
            pipeline_run_id="run_004",
        )
        batch_analyse_competitors(cmd, _config(), **deps)
        # Should have per-page events + 1 batch event
        batch_events = [
            e for e in events.events if e.type == "research.competitor.batch_completed"
        ]
        assert len(batch_events) == 1
        assert batch_events[0].succeeded == 1

    def test_partial_failures_dont_halt_batch(self) -> None:
        """Partial failures don't stop remaining URLs."""
        urls = [
            {"url": "https://fail.com/page", "domain": "fail.com", "serp_position": 1},
            {"url": "https://ok.com/page", "domain": "ok.com", "serp_position": 2},
            {
                "url": "https://also-ok.com/page",
                "domain": "also-ok.com",
                "serp_position": 3,
            },
        ]
        downloader = MockPageDownloader(
            {
                "https://ok.com/page": (True, 200, "<html>OK</html>", "hash1"),
                "https://also-ok.com/page": (
                    True,
                    200,
                    "<html>Also OK</html>",
                    "hash2",
                ),
                # fail.com defaults to 404
            }
        )
        deps = _make_deps(downloader=downloader)
        cmd = BatchAnalyseCompetitorsCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            urls=urls,
            pipeline_run_id="run_005",
        )
        result = batch_analyse_competitors(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        # All 3 URLs processed (2 ok, 1 crawl_failed)
        assert result.value.total == 3

    def test_batch_feature_flag_disabled(self) -> None:
        deps = _make_deps()
        cmd = BatchAnalyseCompetitorsCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            urls=[],
            pipeline_run_id="run_006",
        )
        result = batch_analyse_competitors(cmd, _config(enabled=False), **deps)
        assert isinstance(result, Err)


# ---------------------------------------------------------------------------
# INT-001: F-004 output as input
# ---------------------------------------------------------------------------


class TestIntF004Input:
    """INT-001: SERP result URLs from F-004 are accepted."""

    def test_serp_urls_accepted(self) -> None:
        """URLs from F-004 SerpSnapshot organic_results are valid batch input."""
        serp_urls = [
            {
                "url": "https://example.com/fue-vs-dhi",
                "domain": "example.com",
                "serp_position": 1,
            },
            {
                "url": "https://clinic.de/hair-guide",
                "domain": "clinic.de",
                "serp_position": 2,
            },
        ]
        downloader = MockPageDownloader(
            {
                url["url"]: (True, 200, f"<html>{url['domain']}</html>", f"h_{i}")
                for i, url in enumerate(serp_urls)
            }
        )
        deps = _make_deps(downloader=downloader)
        cmd = BatchAnalyseCompetitorsCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            urls=serp_urls,
            pipeline_run_id="run_int001",
        )
        result = batch_analyse_competitors(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.total == 2
        assert result.value.succeeded >= 1


# ---------------------------------------------------------------------------
# INT-002: F-005 output consumable by F-006
# ---------------------------------------------------------------------------


class TestIntF006Output:
    """INT-002: Snapshots contain fields needed by F-006 gap analysis."""

    def test_snapshot_has_f006_fields(self) -> None:
        repo = MockSnapshotRepo()
        deps = _make_deps(repo=repo)
        cmd = AnalyseCompetitorPageCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
        )
        analyse_competitor_page(cmd, _config(), **deps)

        snap = repo.snapshots[0]
        # F-006 needs: word_count, depth_score, h2_texts
        assert snap.word_count > 0
        assert snap.depth_score is not None
        assert snap.depth_score >= 1
        assert snap.depth_score <= 5
        assert isinstance(snap.h2_texts, list)


# ---------------------------------------------------------------------------
# INT-006: Token budget compliance
# ---------------------------------------------------------------------------


class TestTokenBudget:
    """INT-006: LLM token budget tracking."""

    def test_batch_tracks_total_tokens(self) -> None:
        urls = [
            {
                "url": f"https://site{i}.com/page",
                "domain": f"site{i}.com",
                "serp_position": i + 1,
            }
            for i in range(3)
        ]
        downloader = MockPageDownloader(
            {
                u["url"]: (True, 200, f"<html>Content {i}</html>", f"hash_{i}")
                for i, u in enumerate(urls)
            }
        )
        deps = _make_deps(downloader=downloader)
        cmd = BatchAnalyseCompetitorsCommand(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            serp_snapshot_id="ss_def456",
            urls=urls,
            pipeline_run_id="run_token",
        )
        result = batch_analyse_competitors(cmd, _config(), **deps)
        assert isinstance(result, Ok)
        assert result.value.llm_tokens_total > 0
        # 3 pages × 350 tokens mock = 1050
        assert result.value.llm_tokens_total == 1050
