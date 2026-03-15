"""Tests for F-006 OpportunityScorer.

Covers: ATS-011, ATS-012, ATS-013, ATS-014, ATS-015,
PI-003, PI-004, PI-006, PI-011.
"""

from __future__ import annotations

import math

from hypothesis import given
from hypothesis import strategies as st

from src.research_engine.scoring_config import ScoringConfig
from src.research_engine.services.opportunity_scorer import (
    calculate_gap_score,
    calculate_opportunity_score,
    calculate_thin_content_priority_score,
)

DEFAULT_CONFIG = ScoringConfig()


# ---------------------------------------------------------------------------
# ATS-011: High-value gap scored
# ---------------------------------------------------------------------------


class TestHighValueGap:
    """ATS-011: High volume, low difficulty, no competitor in top 5."""

    def test_high_value_score(self) -> None:
        result = calculate_opportunity_score(
            volume=8100,
            difficulty=32,
            competitor_best_position=None,
            max_volume=8100,
            is_universal_gap=False,
            config=DEFAULT_CONFIG,
        )

        # volume_norm=1.0, diff_inv=0.68, gap=1.0
        # (1.0 × 0.4) + (0.68 × 0.3) + (1.0 × 0.3) = 0.4 + 0.204 + 0.3 = 0.904
        # Rounded: 0.90
        assert 0.85 <= result.score <= 0.95
        assert "High volume" in result.rationale
        assert "8,100" in result.rationale
        assert result.inputs.volume == 8100


# ---------------------------------------------------------------------------
# ATS-012: Low-value gap scored
# ---------------------------------------------------------------------------


class TestLowValueGap:
    """ATS-012: Low volume, low difficulty, competitor at #3."""

    def test_low_value_score(self) -> None:
        result = calculate_opportunity_score(
            volume=40,
            difficulty=15,
            competitor_best_position=3,
            max_volume=8100,
            is_universal_gap=False,
            config=DEFAULT_CONFIG,
        )

        # volume_norm=40/8100≈0.005, diff_inv=0.85, gap=0.4
        # (0.005 × 0.4) + (0.85 × 0.3) + (0.4 × 0.3) ≈ 0.002 + 0.255 + 0.12 = 0.377
        assert result.score < 0.5
        assert "Low volume" in result.rationale
        assert result.inputs.gap_score == 0.4


# ---------------------------------------------------------------------------
# ATS-013: Thin content priority scoring
# ---------------------------------------------------------------------------


class TestThinContentPriority:
    """ATS-013: Thin content ranked #22, 380 words vs 2900 avg."""

    def test_thin_content_priority(self) -> None:
        result = calculate_thin_content_priority_score(
            current_position=22,
            our_word_count=380,
            competitor_avg_word_count=2900,
            max_word_count_gap=2520,
            config=DEFAULT_CONFIG,
        )

        # position_bucket = (50-22)/50 = 0.56
        # gap = 2520, normalised = 2520/2520 = 1.0
        # score = (0.56 × 0.5) + (1.0 × 0.5) = 0.28 + 0.5 = 0.78
        assert 0.75 <= result.score <= 0.85
        assert "Ranking at #22" in result.rationale
        assert "2,520" in result.rationale or "2520" in result.rationale


# ---------------------------------------------------------------------------
# ATS-014: Zero volume keyword
# ---------------------------------------------------------------------------


class TestZeroVolume:
    """ATS-014: Zero volume keyword scored."""

    def test_zero_volume_score(self) -> None:
        result = calculate_opportunity_score(
            volume=0,
            difficulty=20,
            competitor_best_position=None,
            max_volume=8100,
            is_universal_gap=False,
            config=DEFAULT_CONFIG,
        )

        assert result.inputs.volume_normalised == 0.0
        # Score non-zero: diff_inv=0.8, gap=1.0
        # (0 × 0.4) + (0.8 × 0.3) + (1.0 × 0.3) = 0 + 0.24 + 0.3 = 0.54
        assert result.score > 0
        assert "Zero volume" in result.rationale
        assert "AISO value only" in result.rationale


# ---------------------------------------------------------------------------
# ATS-015: Score components stored for transparency
# ---------------------------------------------------------------------------


class TestScoreTransparency:
    """ATS-015: Score components stored for reproducibility."""

    def test_score_inputs_present(self) -> None:
        result = calculate_opportunity_score(
            volume=5000,
            difficulty=45,
            competitor_best_position=8,
            max_volume=10000,
            is_universal_gap=False,
            config=DEFAULT_CONFIG,
        )

        inputs = result.inputs
        assert inputs.volume == 5000
        assert inputs.volume_normalised == 0.5
        assert inputs.difficulty == 45
        assert inputs.difficulty_inverse_normalised == 0.55
        assert inputs.gap_score == 0.7  # position 8 = 6-10 range
        assert inputs.universal_gap_bonus == 0.0

    def test_score_reproducible_from_inputs(self) -> None:
        """PI-011: Score is reproducible from inputs + formula."""
        result = calculate_opportunity_score(
            volume=3000,
            difficulty=50,
            competitor_best_position=None,
            max_volume=6000,
            is_universal_gap=False,
            config=DEFAULT_CONFIG,
        )

        inputs = result.inputs
        reproduced = (
            (inputs.volume_normalised * DEFAULT_CONFIG.volume_weight)
            + (inputs.difficulty_inverse_normalised * DEFAULT_CONFIG.difficulty_weight)
            + (inputs.gap_score * DEFAULT_CONFIG.gap_weight)
            + inputs.universal_gap_bonus
        )
        reproduced = min(reproduced, 1.0)

        assert abs(result.score - round(reproduced, 2)) < 0.01


# ---------------------------------------------------------------------------
# PI-003: Score always 0.0-1.0 (clamped)
# ---------------------------------------------------------------------------


class TestScoreRange:
    """PI-003: Opportunity score always 0.0-1.0."""

    def test_max_score_with_universal_bonus_clamped(self) -> None:
        """Score with max inputs + universal bonus should be clamped to 1.0."""
        result = calculate_opportunity_score(
            volume=10000,
            difficulty=0,
            competitor_best_position=None,
            max_volume=10000,
            is_universal_gap=True,
            config=DEFAULT_CONFIG,
        )

        # (1.0×0.4) + (1.0×0.3) + (1.0×0.3) + 0.1 = 1.1 → clamped to 1.0
        assert result.score <= 1.0

    @given(
        volume=st.integers(min_value=0, max_value=100000),
        difficulty=st.integers(min_value=0, max_value=100),
        position=st.one_of(
            st.none(),
            st.integers(min_value=1, max_value=50),
        ),
        is_universal=st.booleans(),
    )
    def test_score_always_in_range(
        self,
        volume: int,
        difficulty: int,
        position: int | None,
        is_universal: bool,
    ) -> None:
        max_vol = max(volume, 1)
        result = calculate_opportunity_score(
            volume=volume,
            difficulty=difficulty,
            competitor_best_position=position,
            max_volume=max_vol,
            is_universal_gap=is_universal,
            config=DEFAULT_CONFIG,
        )

        assert 0.0 <= result.score <= 1.0
        assert not math.isnan(result.score)
        assert not math.isinf(result.score)


# ---------------------------------------------------------------------------
# PI-006: Rationale non-empty
# ---------------------------------------------------------------------------


class TestRationale:
    """PI-006: Every scored row has a non-empty rationale."""

    def test_opportunity_rationale_non_empty(self) -> None:
        result = calculate_opportunity_score(
            volume=100,
            difficulty=50,
            competitor_best_position=None,
            max_volume=1000,
            is_universal_gap=False,
            config=DEFAULT_CONFIG,
        )
        assert len(result.rationale) > 0

    def test_thin_content_rationale_non_empty(self) -> None:
        result = calculate_thin_content_priority_score(
            current_position=30,
            our_word_count=200,
            competitor_avg_word_count=1500,
            max_word_count_gap=1300,
            config=DEFAULT_CONFIG,
        )
        assert len(result.rationale) > 0


# ---------------------------------------------------------------------------
# Gap score component
# ---------------------------------------------------------------------------


class TestGapScore:
    """Gap score calculation based on competitor position."""

    def test_no_competitor(self) -> None:
        assert calculate_gap_score(None) == 1.0

    def test_competitor_beyond_10(self) -> None:
        assert calculate_gap_score(15) == 1.0

    def test_competitor_position_6_to_10(self) -> None:
        assert calculate_gap_score(6) == 0.7
        assert calculate_gap_score(10) == 0.7

    def test_competitor_position_1_to_5(self) -> None:
        assert calculate_gap_score(1) == 0.4
        assert calculate_gap_score(5) == 0.4


# ---------------------------------------------------------------------------
# Custom config
# ---------------------------------------------------------------------------


class TestCustomConfig:
    """Scoring with custom configuration weights."""

    def test_custom_weights(self) -> None:
        config = ScoringConfig(
            volume_weight=0.5,
            difficulty_weight=0.2,
            gap_weight=0.3,
        )
        result = calculate_opportunity_score(
            volume=5000,
            difficulty=50,
            competitor_best_position=None,
            max_volume=5000,
            is_universal_gap=False,
            config=config,
        )
        # (1.0 × 0.5) + (0.5 × 0.2) + (1.0 × 0.3) = 0.5 + 0.1 + 0.3 = 0.9
        assert abs(result.score - 0.9) < 0.01
