"""Tests for F-004 SerpSnapshotRepo (file-based storage).

TDD: Tests for T-006 covering ATS-015 to ATS-020, INT-008, PI-011.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from src.research_engine.models.serp import (
    ApiSource,
    ContentType,
    SerpFeatures,
    SerpResult,
    SerpSnapshot,
)
from src.research_engine.ports.serp_snapshot_port import SerpSnapshotPort
from src.research_engine.repos.file_serp_snapshot_repo import FileSerpSnapshotRepo

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")
TENANT_STR = str(TENANT_ID)


def _make_snapshot(
    *,
    keyword_text: str = "FUE hair transplant",
    language: str = "de",
    fetched_at: datetime | None = None,
    **overrides: object,
) -> SerpSnapshot:
    """Create a test snapshot."""
    defaults: dict = {
        "tenant_id": TENANT_ID,
        "keyword_id": "kw_abc123",
        "keyword_text": keyword_text,
        "language": language,
        "country": "DE",
        "api_source": ApiSource.MOCK,
        "result_count": 10,
        "serp_features": SerpFeatures(ai_overview=True),
    }
    if fetched_at:
        defaults["fetched_at"] = fetched_at
    defaults.update(overrides)
    return SerpSnapshot(**defaults)


def _make_results(snapshot_id: str, count: int = 3) -> list[SerpResult]:
    """Create test SERP results."""
    return [
        SerpResult(
            tenant_id=TENANT_ID,
            snapshot_id=snapshot_id,
            position=i + 1,
            url=f"https://example{i}.com/page",
            domain=f"example{i}.com",
            title=f"Page {i + 1}",
            content_type=ContentType.BLOG,
        )
        for i in range(count)
    ]


@pytest.fixture()
def repo(tmp_path: Path) -> FileSerpSnapshotRepo:
    """File-based repo using tmp directory."""
    return FileSerpSnapshotRepo(data_dir=tmp_path / "serp")


# ---------------------------------------------------------------------------
# Protocol check
# ---------------------------------------------------------------------------


class TestProtocol:
    """FileSerpSnapshotRepo implements SerpSnapshotPort."""

    def test_implements_protocol(self, repo: FileSerpSnapshotRepo) -> None:
        """Repo implements the port protocol."""
        assert isinstance(repo, SerpSnapshotPort)


# ---------------------------------------------------------------------------
# ATS-015: First snapshot created with all fields
# ---------------------------------------------------------------------------


class TestSnapshotCreation:
    """ATS-015: First snapshot created and persisted."""

    def test_save_and_retrieve(self, repo: FileSerpSnapshotRepo) -> None:
        """Snapshot saved and retrieved with all fields intact."""
        snapshot = _make_snapshot()
        results = _make_results(snapshot.id)
        repo.save_snapshot(snapshot, results)

        latest = repo.get_latest("FUE hair transplant", "de", TENANT_STR)
        assert latest is not None
        assert latest.id == snapshot.id
        assert latest.keyword_text == "FUE hair transplant"
        assert latest.language == "de"
        assert latest.country == "DE"
        assert latest.api_source == ApiSource.MOCK
        assert latest.result_count == 10
        assert latest.serp_features.ai_overview is True

    def test_results_retrievable(self, repo: FileSerpSnapshotRepo) -> None:
        """Results for a snapshot can be retrieved."""
        snapshot = _make_snapshot()
        results = _make_results(snapshot.id, count=5)
        repo.save_snapshot(snapshot, results)

        retrieved = repo.get_results_for_snapshot(snapshot.id)
        assert len(retrieved) == 5
        assert retrieved[0].position == 1
        assert retrieved[0].url == "https://example0.com/page"

    def test_returns_snapshot_id(self, repo: FileSerpSnapshotRepo) -> None:
        """save_snapshot returns the snapshot ID."""
        snapshot = _make_snapshot()
        sid = repo.save_snapshot(snapshot, [])
        assert sid == snapshot.id


# ---------------------------------------------------------------------------
# ATS-016: Cache hit — snapshot within 7 days
# ---------------------------------------------------------------------------


class TestCacheHit:
    """ATS-016: Cached snapshot served when within TTL."""

    def test_recent_snapshot_returned(self, repo: FileSerpSnapshotRepo) -> None:
        """3-day-old snapshot is returned (within 7-day TTL)."""
        three_days_ago = datetime.now(tz=UTC) - timedelta(days=3)
        snapshot = _make_snapshot(fetched_at=three_days_ago)
        repo.save_snapshot(snapshot, [])

        latest = repo.get_latest("FUE hair transplant", "de", TENANT_STR)
        assert latest is not None
        assert latest.id == snapshot.id


# ---------------------------------------------------------------------------
# ATS-017: Cache miss — snapshot older than 7 days
# ---------------------------------------------------------------------------


class TestCacheMiss:
    """ATS-017: Stale snapshot returns None."""

    def test_old_snapshot_returns_none(self, repo: FileSerpSnapshotRepo) -> None:
        """10-day-old snapshot returns None (exceeds 7-day TTL)."""
        ten_days_ago = datetime.now(tz=UTC) - timedelta(days=10)
        snapshot = _make_snapshot(fetched_at=ten_days_ago)
        repo.save_snapshot(snapshot, [])

        latest = repo.get_latest("FUE hair transplant", "de", TENANT_STR)
        assert latest is None


# ---------------------------------------------------------------------------
# ATS-018: Trend comparison across multiple snapshots
# ---------------------------------------------------------------------------


class TestTrendComparison:
    """ATS-018: Historical snapshots for trend analysis."""

    def test_multiple_snapshots_returned(self, repo: FileSerpSnapshotRepo) -> None:
        """3 snapshots over 3 months are all returned."""
        now = datetime.now(tz=UTC)
        for i in range(3):
            ts = now - timedelta(days=30 * i)
            snapshot = _make_snapshot(
                fetched_at=ts,
                serp_features=SerpFeatures(ai_overview=(i > 0)),
            )
            repo.save_snapshot(snapshot, [])

        history = repo.get_history("FUE hair transplant", "de", TENANT_STR)
        assert len(history) == 3

    def test_history_ordered_newest_first(self, repo: FileSerpSnapshotRepo) -> None:
        """History is ordered by fetched_at descending."""
        now = datetime.now(tz=UTC)
        timestamps = [now - timedelta(days=d) for d in [60, 30, 0]]
        for ts in timestamps:
            snapshot = _make_snapshot(fetched_at=ts)
            repo.save_snapshot(snapshot, [])

        history = repo.get_history("FUE hair transplant", "de", TENANT_STR)
        assert len(history) == 3
        # Newest first
        assert history[0].fetched_at >= history[1].fetched_at
        assert history[1].fetched_at >= history[2].fetched_at

    def test_history_limit(self, repo: FileSerpSnapshotRepo) -> None:
        """History respects limit parameter."""
        now = datetime.now(tz=UTC)
        for i in range(5):
            snapshot = _make_snapshot(fetched_at=now - timedelta(days=i))
            repo.save_snapshot(snapshot, [])

        history = repo.get_history("FUE hair transplant", "de", TENANT_STR, limit=2)
        assert len(history) == 2

    def test_detect_ai_overview_change(self, repo: FileSerpSnapshotRepo) -> None:
        """Can detect AI Overview changing from false to true."""
        now = datetime.now(tz=UTC)
        snap1 = _make_snapshot(
            fetched_at=now - timedelta(days=60),
            serp_features=SerpFeatures(ai_overview=False),
        )
        snap2 = _make_snapshot(
            fetched_at=now - timedelta(days=30),
            serp_features=SerpFeatures(ai_overview=True),
        )
        repo.save_snapshot(snap1, [])
        repo.save_snapshot(snap2, [])

        history = repo.get_history("FUE hair transplant", "de", TENANT_STR)
        assert len(history) == 2
        # Newest first: snap2 has ai_overview=True, snap1 has False
        assert history[0].serp_features.ai_overview is True
        assert history[1].serp_features.ai_overview is False


# ---------------------------------------------------------------------------
# ATS-019: Standalone file mode
# ---------------------------------------------------------------------------


class TestStandaloneFileMode:
    """ATS-019: Files saved with correct path structure."""

    def test_file_created(self, repo: FileSerpSnapshotRepo) -> None:
        """Snapshot file is created in expected directory."""
        snapshot = _make_snapshot()
        repo.save_snapshot(snapshot, [])

        expected_dir = repo._data_dir / TENANT_STR / "de"
        json_files = list(expected_dir.glob("*.json"))
        assert len(json_files) == 1
        assert "fue-hair-transplant" in json_files[0].name

    def test_filename_includes_timestamp(self, repo: FileSerpSnapshotRepo) -> None:
        """Filename includes ISO timestamp."""
        ts = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
        snapshot = _make_snapshot(fetched_at=ts)
        repo.save_snapshot(snapshot, [])

        expected_dir = repo._data_dir / TENANT_STR / "de"
        json_files = list(expected_dir.glob("*.json"))
        assert "20260315T120000" in json_files[0].name


# ---------------------------------------------------------------------------
# ATS-020: Configurable cache TTL
# ---------------------------------------------------------------------------


class TestConfigurableCacheTtl:
    """ATS-020: Cache TTL is configurable via max_age_days."""

    def test_14_day_ttl(self, repo: FileSerpSnapshotRepo) -> None:
        """10-day-old snapshot is served with 14-day TTL."""
        ten_days_ago = datetime.now(tz=UTC) - timedelta(days=10)
        snapshot = _make_snapshot(fetched_at=ten_days_ago)
        repo.save_snapshot(snapshot, [])

        latest = repo.get_latest(
            "FUE hair transplant",
            "de",
            TENANT_STR,
            max_age_days=14,
        )
        assert latest is not None

    def test_3_day_ttl(self, repo: FileSerpSnapshotRepo) -> None:
        """5-day-old snapshot is NOT served with 3-day TTL."""
        five_days_ago = datetime.now(tz=UTC) - timedelta(days=5)
        snapshot = _make_snapshot(fetched_at=five_days_ago)
        repo.save_snapshot(snapshot, [])

        latest = repo.get_latest(
            "FUE hair transplant",
            "de",
            TENANT_STR,
            max_age_days=3,
        )
        assert latest is None


# ---------------------------------------------------------------------------
# PI-011: Snapshots append-only (never overwrite)
# ---------------------------------------------------------------------------


class TestAppendOnly:
    """PI-011: Subsequent fetches create new records."""

    def test_two_snapshots_both_retained(self, repo: FileSerpSnapshotRepo) -> None:
        """Two saves for the same keyword create two separate files."""
        now = datetime.now(tz=UTC)
        snap1 = _make_snapshot(fetched_at=now - timedelta(hours=1))
        snap2 = _make_snapshot(fetched_at=now)
        repo.save_snapshot(snap1, [])
        repo.save_snapshot(snap2, [])

        history = repo.get_history("FUE hair transplant", "de", TENANT_STR)
        assert len(history) == 2
        ids = {s.id for s in history}
        assert snap1.id in ids
        assert snap2.id in ids


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge case handling."""

    def test_no_snapshots_returns_none(self, repo: FileSerpSnapshotRepo) -> None:
        """get_latest returns None when no snapshots exist."""
        latest = repo.get_latest("nonexistent", "de", TENANT_STR)
        assert latest is None

    def test_no_history_returns_empty(self, repo: FileSerpSnapshotRepo) -> None:
        """get_history returns empty list when no snapshots exist."""
        history = repo.get_history("nonexistent", "de", TENANT_STR)
        assert history == []

    def test_results_for_unknown_snapshot(self, repo: FileSerpSnapshotRepo) -> None:
        """get_results_for_snapshot returns empty for unknown ID."""
        results = repo.get_results_for_snapshot("ss_unknown")
        assert results == []

    def test_different_keywords_isolated(self, repo: FileSerpSnapshotRepo) -> None:
        """Different keywords don't interfere with each other."""
        snap1 = _make_snapshot(keyword_text="FUE hair transplant")
        snap2 = _make_snapshot(keyword_text="DHI hair transplant")
        repo.save_snapshot(snap1, [])
        repo.save_snapshot(snap2, [])

        fue_history = repo.get_history("FUE hair transplant", "de", TENANT_STR)
        dhi_history = repo.get_history("DHI hair transplant", "de", TENANT_STR)
        assert len(fue_history) == 1
        assert len(dhi_history) == 1

    def test_different_languages_isolated(self, repo: FileSerpSnapshotRepo) -> None:
        """Different languages don't interfere."""
        snap_de = _make_snapshot(language="de", country="DE")
        snap_en = _make_snapshot(language="en", country="US")
        repo.save_snapshot(snap_de, [])
        repo.save_snapshot(snap_en, [])

        de_history = repo.get_history("FUE hair transplant", "de", TENANT_STR)
        en_history = repo.get_history("FUE hair transplant", "en", TENANT_STR)
        assert len(de_history) == 1
        assert len(en_history) == 1
