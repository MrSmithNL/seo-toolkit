"""Tests for FileCompetitorSnapshotRepo (T-007).

ATS-015: First crawl → content_changed=false.
ATS-016: Second crawl, content changed → content_changed=true, new snapshot.
ATS-017: Second crawl, unchanged → content_changed=false.
ATS-018: getLatest returns most recent snapshot.
INT-005: Standalone file output validates.
PI-009: Append-only (never overwrite).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from pathlib import Path

from src.research_engine.models.competitor import (
    CompetitorSnapshot,
    CrawlStatus,
)
from src.research_engine.repos.file_competitor_snapshot_repo import (
    FileCompetitorSnapshotRepo,
)

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _make_snapshot(
    url: str = "https://example.com/fue-vs-dhi",
    crawled_at: datetime | None = None,
    raw_html_hash: str = "abc123def456",
    content_changed: bool = False,
    **overrides: object,
) -> CompetitorSnapshot:
    """Create a valid snapshot for testing."""
    defaults: dict = {
        "tenant_id": TENANT_ID,
        "keyword_id": "kw_abc123",
        "serp_snapshot_id": "ss_def456",
        "url": url,
        "domain": "example.com",
        "serp_position": 3,
        "crawl_status": CrawlStatus.SUCCESS,
        "word_count": 2500,
        "h1_text": "Test Title",
        "h2_count": 5,
        "h3_count": 2,
        "h2_texts": ["H1", "H2", "H3", "H4", "H5"],
        "schema_types": ["Article"],
        "internal_link_count": 10,
        "external_link_count": 5,
        "image_count": 3,
        "raw_html_hash": raw_html_hash,
        "content_changed": content_changed,
        "crawled_at": crawled_at or datetime.now(tz=UTC),
    }
    defaults.update(overrides)
    return CompetitorSnapshot(**defaults)


# ---------------------------------------------------------------------------
# ATS-015: First crawl snapshot
# ---------------------------------------------------------------------------


class TestFirstCrawl:
    """ATS-015: First crawl stores snapshot with content_changed=false."""

    def test_save_and_retrieve(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)
        snap = _make_snapshot(content_changed=False)
        snap_id = repo.save_snapshot(snap)
        assert snap_id == snap.id

        latest = repo.get_latest(snap.url, str(TENANT_ID))
        assert latest is not None
        assert latest.id == snap.id
        assert latest.content_changed is False

    def test_file_created_on_disk(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)
        snap = _make_snapshot()
        repo.save_snapshot(snap)

        json_files = list(tmp_path.rglob("*.json"))
        assert len(json_files) == 1


# ---------------------------------------------------------------------------
# ATS-016: Second crawl — content changed
# ---------------------------------------------------------------------------


class TestContentChanged:
    """ATS-016: Hash difference detected, new snapshot created."""

    def test_different_hash_marks_content_changed(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)

        snap1 = _make_snapshot(
            raw_html_hash="hash_v1",
            crawled_at=datetime(2026, 3, 14, 10, 0, 0, tzinfo=UTC),
            content_changed=False,
        )
        repo.save_snapshot(snap1)

        snap2 = _make_snapshot(
            raw_html_hash="hash_v2",
            crawled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
            content_changed=True,
        )
        repo.save_snapshot(snap2)

        latest = repo.get_latest(snap2.url, str(TENANT_ID))
        assert latest.content_changed is True
        assert latest.raw_html_hash == "hash_v2"

    def test_previous_snapshot_preserved(self, tmp_path: Path) -> None:
        """PI-009: Previous snapshot not overwritten."""
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)

        snap1 = _make_snapshot(
            crawled_at=datetime(2026, 3, 14, 10, 0, 0, tzinfo=UTC),
        )
        snap2 = _make_snapshot(
            crawled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
        )

        repo.save_snapshot(snap1)
        repo.save_snapshot(snap2)

        # Both files exist
        json_files = list(tmp_path.rglob("*.json"))
        assert len(json_files) == 2


# ---------------------------------------------------------------------------
# ATS-017: Second crawl — unchanged
# ---------------------------------------------------------------------------


class TestContentUnchanged:
    """ATS-017: Same hash → content_changed=false."""

    def test_same_hash_no_change(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)

        snap1 = _make_snapshot(
            raw_html_hash="same_hash",
            crawled_at=datetime(2026, 3, 14, 10, 0, 0, tzinfo=UTC),
            content_changed=False,
        )
        snap2 = _make_snapshot(
            raw_html_hash="same_hash",
            crawled_at=datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
            content_changed=False,
        )

        repo.save_snapshot(snap1)
        repo.save_snapshot(snap2)

        latest = repo.get_latest(snap2.url, str(TENANT_ID))
        assert latest.content_changed is False


# ---------------------------------------------------------------------------
# ATS-018: Query most recent snapshot
# ---------------------------------------------------------------------------


class TestGetLatest:
    """ATS-018: getLatest returns most recent snapshot."""

    def test_returns_most_recent(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)

        for i in range(3):
            snap = _make_snapshot(
                crawled_at=datetime(2026, 3, 13 + i, 10, 0, 0, tzinfo=UTC),
                raw_html_hash=f"hash_{i}",
            )
            repo.save_snapshot(snap)

        latest = repo.get_latest(
            "https://example.com/fue-vs-dhi",
            str(TENANT_ID),
        )
        assert latest is not None
        assert latest.raw_html_hash == "hash_2"

    def test_returns_none_when_no_snapshots(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)
        result = repo.get_latest("https://nonexistent.com/page", str(TENANT_ID))
        assert result is None


# ---------------------------------------------------------------------------
# get_by_keyword (F-006 consumer)
# ---------------------------------------------------------------------------


class TestGetByKeyword:
    """Get benchmarks for a keyword — F-006 consumption."""

    def test_returns_benchmarks_for_keyword(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)

        for i in range(3):
            snap = _make_snapshot(
                url=f"https://site{i}.com/page",
                domain=f"site{i}.com",
                serp_position=i + 1,
                word_count=1000 * (i + 1),
                keyword_id="kw_abc123",
            )
            repo.save_snapshot(snap)

        benchmarks = repo.get_by_keyword("kw_abc123", str(TENANT_ID))
        assert len(benchmarks) == 3
        assert benchmarks[0].serp_position == 1
        assert benchmarks[0].word_count == 1000

    def test_returns_empty_for_unknown_keyword(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)
        benchmarks = repo.get_by_keyword("kw_nonexistent", str(TENANT_ID))
        assert benchmarks == []


# ---------------------------------------------------------------------------
# get_history
# ---------------------------------------------------------------------------


class TestGetHistory:
    """Historical snapshots for a URL."""

    def test_returns_newest_first(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)

        for i in range(5):
            snap = _make_snapshot(
                crawled_at=datetime(2026, 3, 11 + i, 10, 0, 0, tzinfo=UTC),
                raw_html_hash=f"hash_{i}",
            )
            repo.save_snapshot(snap)

        history = repo.get_history(
            "https://example.com/fue-vs-dhi",
            str(TENANT_ID),
            limit=3,
        )
        assert len(history) == 3
        assert history[0].raw_html_hash == "hash_4"
        assert history[1].raw_html_hash == "hash_3"

    def test_respects_limit(self, tmp_path: Path) -> None:
        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)

        for i in range(10):
            snap = _make_snapshot(
                crawled_at=datetime(2026, 3, 1 + i, 10, 0, 0, tzinfo=UTC),
                raw_html_hash=f"h_{i}",
            )
            repo.save_snapshot(snap)

        history = repo.get_history(
            "https://example.com/fue-vs-dhi",
            str(TENANT_ID),
            limit=5,
        )
        assert len(history) == 5


# ---------------------------------------------------------------------------
# INT-005: Standalone file output validates
# ---------------------------------------------------------------------------


class TestFileOutput:
    """INT-005: Files validate against CompetitorSnapshot schema."""

    def test_saved_file_validates(self, tmp_path: Path) -> None:
        import json as json_mod

        repo = FileCompetitorSnapshotRepo(data_dir=tmp_path)
        snap = _make_snapshot()
        repo.save_snapshot(snap)

        json_files = list(tmp_path.rglob("*.json"))
        assert len(json_files) == 1

        data = json_mod.loads(json_files[0].read_text())
        restored = CompetitorSnapshot.model_validate(data)
        assert restored.url == snap.url
        assert restored.word_count == snap.word_count
