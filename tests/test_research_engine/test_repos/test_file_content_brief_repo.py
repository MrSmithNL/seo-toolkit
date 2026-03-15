"""Tests for FileContentBriefRepo.

Covers: INT-005 (file-based persistence).
"""

from __future__ import annotations

import uuid
from pathlib import Path

from src.research_engine.models.content_brief import (
    BriefStatus,
    ContentBrief,
    ContentType,
    GapType,
    SearchIntent,
)
from src.research_engine.repos.file_content_brief_repo import FileContentBriefRepo

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _make_brief(keyword: str = "hair transplant", score: float = 0.7) -> ContentBrief:
    return ContentBrief(
        tenant_id=TENANT,
        target_keyword=keyword,
        target_language="en",
        target_country="DE",
        search_intent=SearchIntent.COMMERCIAL,
        content_type=ContentType.BLOG_POST,
        keyword_volume=1000,
        keyword_difficulty=30,
        opportunity_score=score,
        opportunity_score_rationale=f"Score: {score}",
        gap_type=GapType.OWN_GAP,
        competitor_avg_word_count=2000,
        recommended_word_count=2200,
        suggested_publish_date="2026-03-16",
    )


class TestFileContentBriefRepo:
    """File-based brief persistence."""

    def test_save_and_get(self, tmp_path: Path) -> None:
        repo = FileContentBriefRepo(tmp_path, "example.com")
        brief = _make_brief()
        repo.save_brief(brief)

        loaded = repo.get_brief(brief.id)
        assert loaded is not None
        assert loaded.id == brief.id
        assert loaded.target_keyword == "hair transplant"

    def test_get_nonexistent_returns_none(self, tmp_path: Path) -> None:
        repo = FileContentBriefRepo(tmp_path, "example.com")
        assert repo.get_brief("cb_nonexistent") is None

    def test_save_briefs_batch(self, tmp_path: Path) -> None:
        repo = FileContentBriefRepo(tmp_path, "example.com")
        briefs = [_make_brief("kw1", 0.9), _make_brief("kw2", 0.5)]
        count = repo.save_briefs(briefs)
        assert count == 2

        all_briefs = repo.get_by_batch()
        assert len(all_briefs) == 2

    def test_get_by_status(self, tmp_path: Path) -> None:
        repo = FileContentBriefRepo(tmp_path, "example.com")
        briefs = [_make_brief("kw1"), _make_brief("kw2")]
        repo.save_briefs(briefs)

        pending = repo.get_by_status(BriefStatus.PENDING_REVIEW)
        assert len(pending) == 2

        approved = repo.get_by_status(BriefStatus.APPROVED)
        assert len(approved) == 0

    def test_update_brief(self, tmp_path: Path) -> None:
        repo = FileContentBriefRepo(tmp_path, "example.com")
        brief = _make_brief()
        repo.save_brief(brief)

        # Update via model_copy
        updated = brief.model_copy(update={"target_keyword": "updated keyword"})
        repo.update_brief(updated)

        loaded = repo.get_brief(brief.id)
        assert loaded is not None
        assert loaded.target_keyword == "updated keyword"

    def test_delete_all(self, tmp_path: Path) -> None:
        repo = FileContentBriefRepo(tmp_path, "example.com")
        briefs = [_make_brief("kw1"), _make_brief("kw2"), _make_brief("kw3")]
        repo.save_briefs(briefs)
        assert len(repo.get_by_batch()) == 3

        count = repo.delete_all()
        assert count == 3
        assert len(repo.get_by_batch()) == 0

    def test_creates_directory_structure(self, tmp_path: Path) -> None:
        """INT-005: Directory created automatically."""
        FileContentBriefRepo(tmp_path, "hairgenetix.com")
        expected_dir = tmp_path / "calendar" / "hairgenetix.com" / "briefs"
        assert expected_dir.exists()

    def test_brief_roundtrip_preserves_all_fields(self, tmp_path: Path) -> None:
        repo = FileContentBriefRepo(tmp_path, "example.com")
        brief = _make_brief()
        repo.save_brief(brief)
        loaded = repo.get_brief(brief.id)

        assert loaded is not None
        assert loaded.tenant_id == brief.tenant_id
        assert loaded.opportunity_score == brief.opportunity_score
        assert loaded.gap_type == brief.gap_type
        assert loaded.schema_version == brief.schema_version
