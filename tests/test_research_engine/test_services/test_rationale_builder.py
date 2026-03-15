"""Tests for rationale string builder.

Covers: ATS-008, ATS-009, ATS-010, ATS-011.
"""

from __future__ import annotations

from src.research_engine.services.rationale_builder import (
    build_aiso_only_rationale,
    build_new_content_rationale,
    build_thin_content_rationale,
)


class TestNewContentRationale:
    """ATS-008, ATS-009: Rationale for new content."""

    def test_high_priority_no_competitor(self) -> None:
        """ATS-008: High volume, easy, no competitor."""
        result = build_new_content_rationale(
            score=0.74,
            volume=8100,
            difficulty=25,
            competitor_best_position=None,
        )
        assert "Score: 0.74" in result
        assert "High volume (8,100/mo)" in result
        assert "easy to rank (25/100)" in result
        assert "no competitor in top 5" in result

    def test_medium_priority_with_competitor(self) -> None:
        """ATS-009: Medium volume, moderate, competitor at #7."""
        result = build_new_content_rationale(
            score=0.52,
            volume=2400,
            difficulty=48,
            competitor_best_position=7,
        )
        assert "Medium volume (2,400/mo)" in result
        assert "moderate competition (48/100)" in result
        assert "competitor at position 7" in result


class TestThinContentRationale:
    """ATS-010: Rationale for thin content upgrades."""

    def test_thin_content_rationale(self) -> None:
        result = build_thin_content_rationale(
            score=0.82,
            our_position=18,
            our_word_count=420,
            competitor_avg_word_count=2800,
        )
        assert "Priority: 0.82" in result
        assert "We rank #18" in result
        assert "420 words" in result
        assert "2,800" in result
        assert "Strong update opportunity" in result


class TestAisoOnlyRationale:
    """ATS-011: Zero-volume AISO topic."""

    def test_aiso_rationale(self) -> None:
        result = build_aiso_only_rationale(score=0.15, difficulty=18)
        assert "AISO only" in result
        assert "Zero search volume" in result
        assert "AI citation only" in result
