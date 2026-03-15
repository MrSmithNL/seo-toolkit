"""Tests for LanguageScheduler.

Covers: INT-006, PI-009 (no scheduling collisions).
"""

from __future__ import annotations

import uuid

from src.research_engine.models.content_brief import (
    ContentBrief,
    ContentType,
    GapType,
    SearchIntent,
)
from src.research_engine.services.language_scheduler import stagger_languages

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _make_brief(keyword: str, language: str, pub_date: str) -> ContentBrief:
    return ContentBrief(
        tenant_id=TENANT,
        target_keyword=keyword,
        target_language=language,
        target_country=language.upper()[:2],
        search_intent=SearchIntent.COMMERCIAL,
        content_type=ContentType.BLOG_POST,
        keyword_volume=1000,
        keyword_difficulty=30,
        opportunity_score=0.7,
        opportunity_score_rationale="Test rationale",
        gap_type=GapType.OWN_GAP,
        competitor_avg_word_count=2000,
        recommended_word_count=2200,
        suggested_publish_date=pub_date,
    )


class TestStaggerLanguages:
    """INT-006: Multi-language calendar with staggering."""

    def test_single_language_unchanged(self) -> None:
        """Single-language briefs are not modified."""
        briefs = [_make_brief("hair transplant", "en", "2026-03-16")]
        result = stagger_languages(briefs)
        assert result[0].suggested_publish_date == "2026-03-16"

    def test_two_languages_staggered(self) -> None:
        """EN stays at week 1, DE moves to week 2."""
        briefs = [
            _make_brief("hair transplant", "en", "2026-03-16"),
            _make_brief("hair transplant", "de", "2026-03-16"),
        ]
        result = stagger_languages(briefs, primary_language="en")

        en_brief = [b for b in result if b.target_language == "en"][0]
        de_brief = [b for b in result if b.target_language == "de"][0]

        assert en_brief.suggested_publish_date == "2026-03-16"
        assert de_brief.suggested_publish_date == "2026-03-23"  # +1 week

    def test_three_languages_staggered(self) -> None:
        """EN week 1, DE week 2, FR week 3."""
        briefs = [
            _make_brief("FUE vs DHI", "en", "2026-03-16"),
            _make_brief("FUE vs DHI", "de", "2026-03-16"),
            _make_brief("FUE vs DHI", "fr", "2026-03-16"),
        ]
        result = stagger_languages(briefs, primary_language="en")

        dates = {b.target_language: b.suggested_publish_date for b in result}
        assert dates["en"] == "2026-03-16"
        assert dates["de"] == "2026-03-23"
        assert dates["fr"] == "2026-03-30"

    def test_no_collision_same_keyword_language_date(self) -> None:
        """PI-009: No two briefs share same (keyword, language, date)."""
        briefs = [
            _make_brief("hair cost", "en", "2026-03-16"),
            _make_brief("hair cost", "de", "2026-03-16"),
            _make_brief("hair cost", "fr", "2026-03-16"),
        ]
        result = stagger_languages(briefs)

        combos = [
            (b.target_keyword, b.target_language, b.suggested_publish_date)
            for b in result
        ]
        assert len(combos) == len(set(combos))

    def test_empty_briefs(self) -> None:
        result = stagger_languages([])
        assert result == []

    def test_different_keywords_not_staggered(self) -> None:
        """Different keywords with same language should not be staggered."""
        briefs = [
            _make_brief("hair cost", "en", "2026-03-16"),
            _make_brief("FUE vs DHI", "en", "2026-03-16"),
        ]
        result = stagger_languages(briefs)
        # Both keep their original date (different keywords)
        assert all(b.suggested_publish_date == "2026-03-16" for b in result)
