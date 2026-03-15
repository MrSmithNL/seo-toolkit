"""Tests for pillar keyword selection.

TDD: Tests written BEFORE implementation.
Covers: F-002 T-004 (Pillar Selection Rules)
"""

from __future__ import annotations

import uuid

from src.research_engine.domain.pillar_selector import select_pillar
from src.research_engine.models.keyword import Keyword, KeywordIntent, KeywordSource


def _kw(
    term: str,
    intent: KeywordIntent | None = None,
    keyword_id: str = "",
) -> Keyword:
    """Helper to create a keyword."""
    return Keyword(
        id=keyword_id or f"kw_{uuid.uuid4().hex[:12]}",
        tenant_id=uuid.uuid4(),
        campaign_id="camp_1",
        term=term,
        source=KeywordSource.URL_EXTRACTION,
        intent=intent,
    )


class TestSelectPillar:
    """Tests for pillar selection logic."""

    def test_llm_choice_accepted_when_highest_volume(self) -> None:
        """LLM's pillar choice is accepted if it has highest volume."""
        kws = [
            _kw("hair transplant", keyword_id="kw_1"),
            _kw("fue surgery", keyword_id="kw_2"),
        ]
        volume_map = {"kw_1": 5000, "kw_2": 1000}
        result = select_pillar(kws, "hair transplant", volume_map)
        assert result.keyword_id == "kw_1"
        assert result.term == "hair transplant"

    def test_overrides_llm_when_not_highest_volume(self) -> None:
        """Overrides LLM choice with highest-volume keyword."""
        kws = [
            _kw("fue surgery", keyword_id="kw_1"),
            _kw("hair transplant", keyword_id="kw_2"),
        ]
        volume_map = {"kw_1": 1000, "kw_2": 5000}
        result = select_pillar(kws, "fue surgery", volume_map)
        assert result.keyword_id == "kw_2"
        assert result.term == "hair transplant"

    def test_all_transactional_sets_flag(self) -> None:
        """All-transactional cluster sets no_pillar_flag."""
        kws = [
            _kw("buy hair transplant", KeywordIntent.TRANSACTIONAL, "kw_1"),
            _kw("hair transplant price", KeywordIntent.TRANSACTIONAL, "kw_2"),
        ]
        volume_map = {"kw_1": 1000, "kw_2": 2000}
        result = select_pillar(kws, "buy hair transplant", volume_map)
        assert result.no_pillar_flag is not None
        assert "informational" in result.no_pillar_flag.lower()

    def test_mixed_intents_no_flag(self) -> None:
        """Mixed-intent cluster does not set no_pillar_flag."""
        kws = [
            _kw("hair transplant info", KeywordIntent.INFORMATIONAL, "kw_1"),
            _kw("buy hair transplant", KeywordIntent.TRANSACTIONAL, "kw_2"),
        ]
        volume_map = {"kw_1": 3000, "kw_2": 1000}
        result = select_pillar(kws, "hair transplant info", volume_map)
        assert result.no_pillar_flag is None

    def test_volume_tie_prefers_broader_intent(self) -> None:
        """On volume tie, prefer informational over transactional."""
        kws = [
            _kw("hair transplant guide", KeywordIntent.INFORMATIONAL, "kw_1"),
            _kw("buy hair transplant", KeywordIntent.TRANSACTIONAL, "kw_2"),
        ]
        volume_map = {"kw_1": 3000, "kw_2": 3000}
        result = select_pillar(kws, "buy hair transplant", volume_map)
        assert result.keyword_id == "kw_1"

    def test_missing_pillar_term_falls_back(self) -> None:
        """If LLM's pillar term not found, fall back to highest volume."""
        kws = [_kw("hair transplant", keyword_id="kw_1"), _kw("fue", keyword_id="kw_2")]
        volume_map = {"kw_1": 5000, "kw_2": 1000}
        result = select_pillar(kws, "nonexistent keyword", volume_map)
        assert result.keyword_id == "kw_1"

    def test_no_volume_data_uses_llm_choice(self) -> None:
        """If no volume data, trust LLM's choice."""
        kws = [_kw("hair transplant", keyword_id="kw_1"), _kw("fue", keyword_id="kw_2")]
        result = select_pillar(kws, "fue", {})
        assert result.keyword_id == "kw_2"

    def test_result_has_rationale(self) -> None:
        """Result always includes a rationale string."""
        kws = [_kw("test", keyword_id="kw_1")]
        result = select_pillar(kws, "test", {"kw_1": 100})
        assert len(result.rationale) > 0
