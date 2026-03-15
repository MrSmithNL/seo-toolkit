"""Tests for keyword gap analysis.

TDD: Tests written BEFORE implementation.
Covers: T-008 (Keyword Gap Analyser)
"""

from __future__ import annotations

import uuid

from src.research_engine.domain.gap_analyser import CompetitorKeyword, analyse_gaps


class TestAnalyseGaps:
    """Tests for analyse_gaps() function."""

    def test_identifies_competitor_gaps(self) -> None:
        """ATS-014: Keywords competitors rank for that we don't."""
        our_keywords = {"hair transplant", "fue transplant"}
        competitor_keywords = [
            CompetitorKeyword(
                domain="competitor.com",
                keyword="hair loss treatment",
                position=5,
            ),
            CompetitorKeyword(
                domain="competitor.com",
                keyword="hair transplant",
                position=3,
            ),
        ]
        tenant_id = uuid.uuid4()
        gaps = analyse_gaps(
            our_keywords=our_keywords,
            competitor_keywords=competitor_keywords,
            campaign_id="camp_1",
            tenant_id=tenant_id,
        )
        # "hair loss treatment" is a gap (competitor ranks, we don't)
        # "hair transplant" is NOT a gap (we rank for it)
        assert len(gaps) == 1
        assert gaps[0].competitor_domain == "competitor.com"

    def test_no_gaps_returns_empty(self) -> None:
        """ATS-016: When we rank for everything, return empty."""
        our_keywords = {"hair transplant", "fue transplant"}
        competitor_keywords = [
            CompetitorKeyword(
                domain="competitor.com", keyword="hair transplant", position=5
            ),
        ]
        gaps = analyse_gaps(
            our_keywords=our_keywords,
            competitor_keywords=competitor_keywords,
            campaign_id="camp_1",
            tenant_id=uuid.uuid4(),
        )
        assert gaps == []

    def test_multiple_competitors_deduped(self) -> None:
        """ATS-017: Same keyword gap from multiple competitors is deduped."""
        our_keywords: set[str] = set()
        competitor_keywords = [
            CompetitorKeyword(
                domain="competitor1.com", keyword="hair loss", position=3
            ),
            CompetitorKeyword(
                domain="competitor2.com", keyword="hair loss", position=7
            ),
        ]
        gaps = analyse_gaps(
            our_keywords=our_keywords,
            competitor_keywords=competitor_keywords,
            campaign_id="camp_1",
            tenant_id=uuid.uuid4(),
        )
        # "hair loss" from 2 competitors — one gap per competitor
        assert len(gaps) == 2
        domains = {g.competitor_domain for g in gaps}
        assert domains == {"competitor1.com", "competitor2.com"}

    def test_gap_includes_position(self) -> None:
        """Gap records include competitor position data."""
        gaps = analyse_gaps(
            our_keywords=set(),
            competitor_keywords=[
                CompetitorKeyword(domain="competitor.com", keyword="test", position=4),
            ],
            campaign_id="camp_1",
            tenant_id=uuid.uuid4(),
        )
        assert len(gaps) == 1
        assert gaps[0].competitor_position == 4

    def test_empty_competitors_returns_empty(self) -> None:
        """No competitor data returns empty gaps."""
        gaps = analyse_gaps(
            our_keywords={"hair transplant"},
            competitor_keywords=[],
            campaign_id="camp_1",
            tenant_id=uuid.uuid4(),
        )
        assert gaps == []

    def test_gap_has_correct_tenant(self) -> None:
        """Gap records inherit the correct tenant_id."""
        tenant_id = uuid.uuid4()
        gaps = analyse_gaps(
            our_keywords=set(),
            competitor_keywords=[
                CompetitorKeyword(domain="competitor.com", keyword="test", position=1),
            ],
            campaign_id="camp_1",
            tenant_id=tenant_id,
        )
        assert gaps[0].tenant_id == tenant_id
