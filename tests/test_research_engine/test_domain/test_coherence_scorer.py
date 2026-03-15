"""Tests for coherence score validation.

TDD: Tests written BEFORE implementation.
Covers: F-002 T-005 (Coherence Score Post-Processing)
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from src.research_engine.domain.coherence_scorer import validate_coherence
from src.research_engine.models.result import Err, Ok


class TestValidateCoherence:
    """Tests for coherence score validation."""

    def test_high_score_no_warning(self) -> None:
        """Score 8 is valid with no warning."""
        result = validate_coherence(8, "Tight cluster.")
        assert isinstance(result, Ok)
        assert result.value.score == 8
        assert result.value.low_coherence_warning is None

    def test_low_score_sets_warning(self) -> None:
        """Score 3 triggers low-coherence warning."""
        result = validate_coherence(3, "Loose cluster.")
        assert isinstance(result, Ok)
        assert result.value.low_coherence_warning is not None
        assert "3" in result.value.low_coherence_warning

    def test_score_4_no_warning(self) -> None:
        """Score 4 is at threshold boundary — no warning."""
        result = validate_coherence(4, "Moderate.")
        assert isinstance(result, Ok)
        assert result.value.low_coherence_warning is None

    def test_score_zero_returns_err(self) -> None:
        """Score 0 is below minimum, returns Err."""
        result = validate_coherence(0, "Invalid.")
        assert isinstance(result, Err)

    def test_score_eleven_returns_err(self) -> None:
        """Score 11 is above maximum, returns Err."""
        result = validate_coherence(11, "Invalid.")
        assert isinstance(result, Err)

    def test_empty_rationale_returns_err(self) -> None:
        """Empty rationale returns Err."""
        result = validate_coherence(7, "")
        assert isinstance(result, Err)

    def test_rationale_preserved(self) -> None:
        """Rationale is preserved in result."""
        result = validate_coherence(9, "Very tight cluster.")
        assert isinstance(result, Ok)
        assert result.value.rationale == "Very tight cluster."

    @given(score=st.integers(min_value=1, max_value=10))
    def test_valid_range_always_ok(self, score: int) -> None:
        """Any score 1-10 with non-empty rationale returns Ok."""
        result = validate_coherence(score, "Valid.")
        assert isinstance(result, Ok)
        assert result.value.score == score
