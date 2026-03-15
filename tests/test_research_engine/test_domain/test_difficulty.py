"""Tests for keyword difficulty estimation.

TDD: Tests written BEFORE implementation.
Covers: T-007 (Keyword Difficulty Estimator)
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from src.research_engine.domain.difficulty import DifficultyResult, estimate_difficulty


class TestEstimateDifficulty:
    """Tests for the estimate_difficulty() function."""

    def test_low_difficulty_keyword(self) -> None:
        """ATS-011: Niche keyword with low volume scores low (~15)."""
        result = estimate_difficulty(
            volume=50,
            autocomplete_depth=2,
            llm_authority_score=10,
        )
        assert isinstance(result, DifficultyResult)
        assert result.score <= 30
        assert result.source == "heuristic"
        assert result.rationale

    def test_high_difficulty_keyword(self) -> None:
        """ATS-012: Head term with massive volume scores high (~85)."""
        result = estimate_difficulty(
            volume=100000,
            autocomplete_depth=8,
            llm_authority_score=90,
        )
        assert result.score >= 70
        assert result.source == "heuristic"

    def test_always_tagged_heuristic(self) -> None:
        """PI-006: All scores are tagged source='heuristic'."""
        result = estimate_difficulty(
            volume=5000,
            autocomplete_depth=5,
            llm_authority_score=50,
        )
        assert result.source == "heuristic"

    def test_rationale_not_empty(self) -> None:
        """Rationale must always be provided."""
        result = estimate_difficulty(
            volume=1000,
            autocomplete_depth=3,
            llm_authority_score=30,
        )
        assert len(result.rationale) > 0

    @given(
        volume=st.integers(min_value=0, max_value=1_000_000),
        depth=st.integers(min_value=0, max_value=10),
        authority=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=100)
    def test_property_score_in_range(
        self, volume: int, depth: int, authority: int
    ) -> None:
        """PI-004 property: difficulty always in [0, 100]."""
        result = estimate_difficulty(
            volume=volume,
            autocomplete_depth=depth,
            llm_authority_score=authority,
        )
        assert 0 <= result.score <= 100

    def test_zero_inputs(self) -> None:
        """All-zero inputs produce a low difficulty score."""
        result = estimate_difficulty(
            volume=0,
            autocomplete_depth=0,
            llm_authority_score=0,
        )
        assert result.score == 0
        assert result.source == "heuristic"
