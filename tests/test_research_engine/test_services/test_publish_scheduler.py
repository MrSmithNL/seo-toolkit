"""Tests for PublishScheduler.

Covers: ATS-005, ATS-006, PI-009.
"""

from __future__ import annotations

import uuid
from datetime import date

from src.research_engine.models.content_brief import (
    ContentBrief,
    ContentType,
    GapType,
    SearchIntent,
)
from src.research_engine.services.publish_scheduler import (
    _next_monday,
    schedule_publish_dates,
)

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _make_brief(score: float, gap_type: str = "own_gap") -> ContentBrief:
    """Create a minimal valid ContentBrief for scheduling tests."""
    existing_url = "https://example.com/page" if gap_type == "thin_content" else None
    return ContentBrief(
        tenant_id=TENANT,
        target_keyword=f"kw-{score}",
        target_language="en",
        target_country="DE",
        search_intent=SearchIntent.COMMERCIAL,
        content_type=ContentType.BLOG_POST,
        keyword_volume=1000,
        keyword_difficulty=30,
        opportunity_score=score,
        opportunity_score_rationale=f"Score: {score}",
        gap_type=GapType(gap_type),
        existing_page_url=existing_url,
        competitor_avg_word_count=2000,
        recommended_word_count=2200,
        suggested_publish_date="2026-01-01",  # placeholder
    )


class TestNextMonday:
    """Helper: find next Monday."""

    def test_sunday_to_monday(self) -> None:
        """2026-03-15 (Sunday) → 2026-03-16 (Monday)."""
        assert _next_monday(date(2026, 3, 15)) == date(2026, 3, 16)

    def test_monday_stays(self) -> None:
        """2026-03-16 (Monday) → stays 2026-03-16."""
        assert _next_monday(date(2026, 3, 16)) == date(2026, 3, 16)

    def test_wednesday_to_next_monday(self) -> None:
        """2026-03-18 (Wednesday) → 2026-03-23 (Monday)."""
        assert _next_monday(date(2026, 3, 18)) == date(2026, 3, 23)


class TestSchedulePublishDates:
    """ATS-005: Publish date assignment."""

    def test_15_topics_2_per_week(self) -> None:
        """ATS-005: 15 topics, 2/week, pipeline on 2026-03-15 (Sun)."""
        briefs = [_make_brief(0.9 - i * 0.05) for i in range(15)]
        scheduled = schedule_publish_dates(
            briefs,
            pipeline_run_date=date(2026, 3, 15),
            cadence_per_week=2,
        )

        # First topic: 2026-03-16 (Monday after Sunday)
        assert scheduled[0].suggested_publish_date == "2026-03-16"

        # Last topic: should be about 7 weeks out
        last_date = date.fromisoformat(scheduled[-1].suggested_publish_date)
        first_date = date.fromisoformat(scheduled[0].suggested_publish_date)
        weeks_span = (last_date - first_date).days / 7
        assert 6 <= weeks_span <= 8  # ~7.5 weeks for 15 topics at 2/week

    def test_sorted_by_priority(self) -> None:
        """PI-009: Highest score gets earliest date."""
        briefs = [
            _make_brief(0.3),
            _make_brief(0.9),
            _make_brief(0.6),
        ]
        scheduled = schedule_publish_dates(
            briefs,
            start_date=date(2026, 3, 16),
        )

        # Build a map of score → date for each scheduled brief
        score_date = {b.opportunity_score: b.suggested_publish_date for b in scheduled}

        # Highest score (0.9) should have the earliest date
        assert score_date[0.9] <= score_date[0.6]
        assert score_date[0.6] <= score_date[0.3]

    def test_only_thin_content(self) -> None:
        """ATS-006: 0 new content, 8 thin → only update section."""
        briefs = [_make_brief(0.5 + i * 0.05, "thin_content") for i in range(8)]
        scheduled = schedule_publish_dates(
            briefs,
            start_date=date(2026, 3, 16),
            cadence_per_week=2,
        )

        assert len(scheduled) == 8
        # All should have valid dates
        for b in scheduled:
            date.fromisoformat(b.suggested_publish_date)

    def test_new_content_before_thin(self) -> None:
        """New content scheduled before thin content updates."""
        new_briefs = [_make_brief(0.5, "own_gap"), _make_brief(0.4, "new_opportunity")]
        thin_briefs = [_make_brief(0.9, "thin_content")]

        all_briefs = thin_briefs + new_briefs  # intentionally mixed
        scheduled = schedule_publish_dates(
            all_briefs,
            start_date=date(2026, 3, 16),
            cadence_per_week=2,
        )

        # Find the thin content brief
        thin_dates = [
            b.suggested_publish_date
            for b in scheduled
            if b.gap_type == GapType.THIN_CONTENT
        ]
        new_dates = [
            b.suggested_publish_date
            for b in scheduled
            if b.gap_type != GapType.THIN_CONTENT
        ]

        # All thin dates should be after all new dates
        assert min(thin_dates) > max(new_dates)

    def test_empty_briefs(self) -> None:
        """Empty input returns empty."""
        result = schedule_publish_dates([])
        assert result == []
