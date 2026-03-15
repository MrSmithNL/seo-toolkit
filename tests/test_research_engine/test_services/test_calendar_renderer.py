"""Tests for CalendarRenderer.

Covers: ATS-013, ATS-014, PI-015.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from src.research_engine.models.content_brief import (
    ContentBrief,
    ContentType,
    GapType,
    SearchIntent,
)
from src.research_engine.services.calendar_renderer import (
    render_calendar_json,
    render_calendar_markdown,
    write_calendar_files,
)

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _make_brief(
    keyword: str,
    score: float,
    gap_type: str = "own_gap",
    volume: int = 1000,
    difficulty: int = 30,
) -> ContentBrief:
    existing_url = "https://example.com/page" if gap_type == "thin_content" else None
    return ContentBrief(
        tenant_id=TENANT,
        target_keyword=keyword,
        target_language="en",
        target_country="DE",
        search_intent=SearchIntent.COMMERCIAL,
        content_type=ContentType.BLOG_POST,
        keyword_volume=volume,
        keyword_difficulty=difficulty,
        opportunity_score=score,
        opportunity_score_rationale=f"Score: {score}",
        gap_type=GapType(gap_type),
        existing_page_url=existing_url,
        competitor_avg_word_count=2000,
        competitor_depth_scores=[3, 4, 3],
        top_competitor_url="https://example.com/comp",
        recommended_word_count=2200,
        recommended_headings=["Heading A", "Heading B"],
        recommended_schema_types=["Article"],
        suggested_publish_date="2026-03-16",
    )


class TestRenderCalendarMarkdown:
    """ATS-014: Markdown format — correct structure."""

    def test_markdown_contains_keyword_and_volume(self) -> None:
        briefs = [_make_brief("hair transplant", 0.9, volume=8100)]
        md = render_calendar_markdown(briefs, "2026-03-16")
        assert "hair transplant" in md
        assert "8,100" in md

    def test_markdown_contains_headings(self) -> None:
        briefs = [_make_brief("FUE cost", 0.8)]
        md = render_calendar_markdown(briefs, "2026-03-16")
        assert "Heading A" in md
        assert "Heading B" in md

    def test_markdown_contains_action_checkboxes(self) -> None:
        """ATS-014: Action checkboxes present."""
        briefs = [_make_brief("hair cost", 0.7)]
        md = render_calendar_markdown(briefs, "2026-03-16")
        assert "Approve" in md
        assert "Reject" in md
        assert "Edit" in md

    def test_markdown_new_content_before_thin(self) -> None:
        """PI-015: New content section appears before update section."""
        briefs = [
            _make_brief("thin topic", 0.9, "thin_content"),
            _make_brief("new topic", 0.5, "own_gap"),
        ]
        md = render_calendar_markdown(briefs, "2026-03-16")
        new_idx = md.index("New Content")
        update_idx = md.index("Content to Update")
        assert new_idx < update_idx

    def test_markdown_sorted_by_score_within_section(self) -> None:
        """PI-015: Calendar entries sorted by opportunity_score descending."""
        briefs = [
            _make_brief("kw-low-priority", 0.3),
            _make_brief("kw-high-priority", 0.9),
            _make_brief("kw-mid-priority", 0.6),
        ]
        md = render_calendar_markdown(briefs, "2026-03-16")
        # Highest score first
        assert (
            md.index("kw-high-priority")
            < md.index("kw-mid-priority")
            < md.index("kw-low-priority")
        )

    def test_markdown_empty_briefs(self) -> None:
        md = render_calendar_markdown([], "2026-03-16")
        assert "No content topics generated" in md

    def test_markdown_header_shows_counts(self) -> None:
        briefs = [
            _make_brief("new1", 0.9, "own_gap"),
            _make_brief("new2", 0.8, "own_gap"),
            _make_brief("thin1", 0.7, "thin_content"),
        ]
        md = render_calendar_markdown(briefs, "2026-03-16")
        assert "Total topics:** 3" in md
        assert "New content:** 2" in md
        assert "Updates:** 1" in md


class TestRenderCalendarJson:
    """ATS-013: JSON output."""

    def test_json_is_valid_array(self) -> None:
        briefs = [_make_brief("hair transplant", 0.9)]
        result = render_calendar_json(briefs)
        data = json.loads(result)
        assert isinstance(data, list)
        assert len(data) == 1

    def test_json_contains_all_fields(self) -> None:
        briefs = [_make_brief("hair transplant", 0.9)]
        result = render_calendar_json(briefs)
        data = json.loads(result)
        entry = data[0]
        assert entry["target_keyword"] == "hair transplant"
        assert entry["opportunity_score"] == 0.9
        assert "id" in entry
        assert "schema_version" in entry

    def test_json_empty_array(self) -> None:
        result = render_calendar_json([])
        data = json.loads(result)
        assert data == []


class TestWriteCalendarFiles:
    """ATS-013, INT-005: Dual file output to disk."""

    def test_creates_both_files(self, tmp_path: Path) -> None:
        """ATS-013: Both md and json files created."""
        briefs = [_make_brief("hair transplant", 0.9)]
        md_path, json_path = write_calendar_files(briefs, tmp_path, "2026-03-16")

        assert md_path.exists()
        assert json_path.exists()
        assert md_path.name == "calendar-2026-03-16.md"
        assert json_path.name == "calendar-2026-03-16.json"

    def test_json_file_valid(self, tmp_path: Path) -> None:
        briefs = [_make_brief("hair cost", 0.8)]
        _, json_path = write_calendar_files(briefs, tmp_path, "2026-03-16")
        data = json.loads(json_path.read_text())
        assert len(data) == 1
        assert data[0]["target_keyword"] == "hair cost"

    def test_md_file_contains_content(self, tmp_path: Path) -> None:
        briefs = [_make_brief("FUE cost", 0.7)]
        md_path, _ = write_calendar_files(briefs, tmp_path, "2026-03-16")
        content = md_path.read_text()
        assert "FUE cost" in content

    def test_creates_output_dir_if_missing(self, tmp_path: Path) -> None:
        """INT-005: Output dir created automatically."""
        nested = tmp_path / "data" / "calendar" / "example.com"
        briefs = [_make_brief("test", 0.5)]
        md_path, json_path = write_calendar_files(briefs, nested, "2026-03-16")
        assert md_path.exists()
        assert json_path.exists()
