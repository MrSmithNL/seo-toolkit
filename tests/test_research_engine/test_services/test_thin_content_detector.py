"""Tests for F-006 ThinContentDetector.

Covers: ATS-002, ATS-007, ATS-008, ATS-009, ATS-010,
PI-005, PI-012.
"""

from __future__ import annotations

from src.research_engine.models.content_gap import CompetitorEntry
from src.research_engine.scoring_config import ScoringConfig
from src.research_engine.services.thin_content_detector import detect_thin_content

DEFAULT_CONFIG = ScoringConfig()


# ---------------------------------------------------------------------------
# ATS-002 / ATS-007: Classic thin content
# ---------------------------------------------------------------------------


class TestClassicThinContent:
    """ATS-002, ATS-007: Rank 11-50 with much fewer words than competitors."""

    def test_rank_22_thin_content(self) -> None:
        """ATS-002: Ranks #22, 450 words vs 2800 avg."""
        competitors = [
            CompetitorEntry(
                url="https://c1.com/p", domain="c1.com", position=1, word_count=2800
            ),
            CompetitorEntry(
                url="https://c2.com/p", domain="c2.com", position=3, word_count=3000
            ),
            CompetitorEntry(
                url="https://c3.com/p", domain="c3.com", position=5, word_count=2600
            ),
        ]

        result = detect_thin_content(
            our_ranking_position=22,
            our_word_count=450,
            competitors=competitors,
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is True
        assert result.our_word_count == 450
        assert result.competitor_avg_word_count == 2800
        assert result.word_count_gap > 0

    def test_rank_18_thin_content(self) -> None:
        """ATS-007: Ranks #18, 400 words vs 2900 avg."""
        competitors = [
            CompetitorEntry(
                url="https://c1.com/p", domain="c1.com", position=2, word_count=2900
            ),
            CompetitorEntry(
                url="https://c2.com/p", domain="c2.com", position=4, word_count=3100
            ),
            CompetitorEntry(
                url="https://c3.com/p", domain="c3.com", position=6, word_count=2700
            ),
        ]

        result = detect_thin_content(
            our_ranking_position=18,
            our_word_count=400,
            competitors=competitors,
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is True
        assert result.word_count_gap == 2500  # 2900 - 400
        assert "Ranks #18" in result.rationale
        assert "86%" in result.rationale or "below" in result.rationale


# ---------------------------------------------------------------------------
# ATS-008: Ranking well despite fewer words — NOT thin
# ---------------------------------------------------------------------------


class TestRankingWellNotThin:
    """ATS-008: Ranks #4, fewer words but ranking well → not thin."""

    def test_top_10_not_flagged(self) -> None:
        competitors = [
            CompetitorEntry(
                url="https://c1.com/p", domain="c1.com", position=1, word_count=1200
            ),
            CompetitorEntry(
                url="https://c2.com/p", domain="c2.com", position=2, word_count=1400
            ),
            CompetitorEntry(
                url="https://c3.com/p", domain="c3.com", position=3, word_count=1000
            ),
        ]

        result = detect_thin_content(
            our_ranking_position=4,
            our_word_count=800,
            competitors=competitors,
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is False
        assert "top 10" in result.rationale

    def test_position_10_not_flagged(self) -> None:
        """Boundary: position 10 is still top 10."""
        result = detect_thin_content(
            our_ranking_position=10,
            our_word_count=100,
            competitors=[
                CompetitorEntry(
                    url="https://c1.com/p", domain="c1.com", position=1, word_count=5000
                ),
            ],
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is False

    def test_position_11_can_be_thin(self) -> None:
        """Boundary: position 11 is eligible for thin content detection."""
        result = detect_thin_content(
            our_ranking_position=11,
            our_word_count=100,
            competitors=[
                CompetitorEntry(
                    url="https://c1.com/p", domain="c1.com", position=1, word_count=5000
                ),
                CompetitorEntry(
                    url="https://c2.com/p", domain="c2.com", position=2, word_count=4000
                ),
                CompetitorEntry(
                    url="https://c3.com/p", domain="c3.com", position=3, word_count=6000
                ),
            ],
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is True


# ---------------------------------------------------------------------------
# ATS-009: Not ranking at all — not thin content
# ---------------------------------------------------------------------------


class TestNotRanking:
    """ATS-009: Not ranking → own_gap, not thin_content."""

    def test_non_ranking_not_thin(self) -> None:
        """PI-012: Non-ranking pages never classified as thin."""
        result = detect_thin_content(
            our_ranking_position=None,
            our_word_count=None,
            competitors=[
                CompetitorEntry(
                    url="https://c1.com/p", domain="c1.com", position=1, word_count=3000
                ),
            ],
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is False
        assert "own_gap" in result.rationale


# ---------------------------------------------------------------------------
# ATS-010: Competitor data missing
# ---------------------------------------------------------------------------


class TestMissingCompetitorData:
    """ATS-010: Competitor crawl_failed → skip assessment."""

    def test_all_competitors_crawl_failed(self) -> None:
        competitors = [
            CompetitorEntry(
                url="https://c1.com/p", domain="c1.com", position=1, crawl_failed=True
            ),
            CompetitorEntry(
                url="https://c2.com/p", domain="c2.com", position=2, crawl_failed=True
            ),
        ]

        result = detect_thin_content(
            our_ranking_position=22,
            our_word_count=400,
            competitors=competitors,
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is False
        assert result.insufficient_data is True
        assert "Insufficient" in result.rationale

    def test_some_competitors_crawl_failed(self) -> None:
        """Partial data: only use competitors with valid word counts."""
        competitors = [
            CompetitorEntry(
                url="https://c1.com/p", domain="c1.com", position=1, word_count=3000
            ),
            CompetitorEntry(
                url="https://c2.com/p", domain="c2.com", position=2, crawl_failed=True
            ),
            CompetitorEntry(
                url="https://c3.com/p", domain="c3.com", position=3, word_count=2500
            ),
        ]

        result = detect_thin_content(
            our_ranking_position=25,
            our_word_count=400,
            competitors=competitors,
            config=DEFAULT_CONFIG,
        )

        # Average of available: (3000 + 2500) / 2 = 2750
        assert result.is_thin is True
        assert result.competitor_avg_word_count == 2750

    def test_our_word_count_unknown(self) -> None:
        result = detect_thin_content(
            our_ranking_position=22,
            our_word_count=None,
            competitors=[
                CompetitorEntry(
                    url="https://c1.com/p", domain="c1.com", position=1, word_count=3000
                ),
            ],
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is False
        assert result.insufficient_data is True


# ---------------------------------------------------------------------------
# PI-005: Thin content threshold
# ---------------------------------------------------------------------------


class TestThreshold:
    """PI-005: thin_content only when rank 11-50 AND < 50% competitor avg."""

    def test_just_above_threshold_not_thin(self) -> None:
        """Word count at exactly 50% → not thin (boundary)."""
        competitors = [
            CompetitorEntry(
                url="https://c1.com/p", domain="c1.com", position=1, word_count=2000
            ),
            CompetitorEntry(
                url="https://c2.com/p", domain="c2.com", position=2, word_count=2000
            ),
            CompetitorEntry(
                url="https://c3.com/p", domain="c3.com", position=3, word_count=2000
            ),
        ]

        result = detect_thin_content(
            our_ranking_position=15,
            our_word_count=1000,  # exactly 50%
            competitors=competitors,
            config=DEFAULT_CONFIG,
        )

        # < 50% means strictly less than. 1000/2000 = 0.5 → not thin
        assert result.is_thin is False

    def test_just_below_threshold_is_thin(self) -> None:
        """Word count at 49% → thin."""
        competitors = [
            CompetitorEntry(
                url="https://c1.com/p", domain="c1.com", position=1, word_count=2000
            ),
            CompetitorEntry(
                url="https://c2.com/p", domain="c2.com", position=2, word_count=2000
            ),
            CompetitorEntry(
                url="https://c3.com/p", domain="c3.com", position=3, word_count=2000
            ),
        ]

        result = detect_thin_content(
            our_ranking_position=15,
            our_word_count=999,  # 49.95% < 50%
            competitors=competitors,
            config=DEFAULT_CONFIG,
        )

        assert result.is_thin is True

    def test_custom_threshold(self) -> None:
        """Custom 30% threshold."""
        config = ScoringConfig(thin_content_threshold=0.3)
        competitors = [
            CompetitorEntry(
                url="https://c1.com/p", domain="c1.com", position=1, word_count=1000
            ),
        ]

        # 400/1000 = 40% > 30% → not thin
        result = detect_thin_content(
            our_ranking_position=15,
            our_word_count=400,
            competitors=competitors,
            config=config,
        )
        assert result.is_thin is False

        # 200/1000 = 20% < 30% → thin
        result2 = detect_thin_content(
            our_ranking_position=15,
            our_word_count=200,
            competitors=competitors,
            config=config,
        )
        assert result2.is_thin is True
