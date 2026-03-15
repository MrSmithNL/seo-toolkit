"""Tests for keyword normalisation and deduplication.

TDD: Tests written BEFORE implementation.
Covers: T-003 (Keyword Normalisation & Deduplication)
"""

from __future__ import annotations

import uuid

from hypothesis import given, settings
from hypothesis import strategies as st

from src.research_engine.domain.normaliser import dedup, make_dedup_key, normalise
from src.research_engine.models.keyword import Keyword, KeywordSource


def _kw(term: str, volume: int | None = None) -> Keyword:
    """Helper to create a keyword with a given term and volume."""
    return Keyword(
        tenant_id=uuid.uuid4(),
        campaign_id="camp_test",
        term=term,
        source=KeywordSource.URL_EXTRACTION,
        difficulty=volume,  # reuse difficulty field for simpler testing
    )


# ===========================================================================
# normalise() tests
# ===========================================================================


class TestNormalise:
    """Tests for the normalise() function."""

    def test_lowercases(self) -> None:
        """Converts to lowercase."""
        assert normalise("Hair Transplant") == "hair transplant"

    def test_strips_whitespace(self) -> None:
        """Strips leading and trailing whitespace."""
        assert normalise("  hair transplant  ") == "hair transplant"

    def test_collapses_internal_whitespace(self) -> None:
        """Collapses multiple internal spaces."""
        assert normalise("hair   transplant\tcost") == "hair transplant cost"

    def test_handles_empty_string(self) -> None:
        """Empty string normalises to empty string."""
        assert normalise("") == ""

    def test_handles_single_character(self) -> None:
        """Single character normalises correctly."""
        assert normalise("A") == "a"

    def test_handles_unicode_umlauts(self) -> None:
        """German umlauts are preserved (not stripped)."""
        assert normalise("Haarverpflanzung Türkei") == "haarverpflanzung türkei"

    @given(term=st.text(max_size=200))
    @settings(max_examples=100)
    def test_property_idempotent(self, term: str) -> None:
        """Property: normalise(normalise(x)) == normalise(x)."""
        once = normalise(term)
        twice = normalise(once)
        assert once == twice


# ===========================================================================
# make_dedup_key() tests
# ===========================================================================


class TestMakeDedupKey:
    """Tests for the make_dedup_key() function."""

    def test_sorts_tokens_alphabetically(self) -> None:
        """Tokens are sorted alphabetically."""
        assert make_dedup_key("cost of hair transplant") == "cost hair of transplant"

    def test_word_order_variants_match(self) -> None:
        """'hair transplant cost' and 'cost hair transplant' produce same key."""
        key1 = make_dedup_key("hair transplant cost")
        # Same tokens, different order → same key
        key3 = make_dedup_key("cost hair transplant")
        assert key1 == key3

    def test_case_insensitive(self) -> None:
        """Case differences produce the same key."""
        assert make_dedup_key("Hair Transplant") == make_dedup_key("hair transplant")

    def test_whitespace_insensitive(self) -> None:
        """Whitespace differences produce the same key."""
        assert make_dedup_key("hair  transplant") == make_dedup_key("hair transplant")

    def test_empty_string(self) -> None:
        """Empty string produces empty key."""
        assert make_dedup_key("") == ""

    def test_different_tokens_differ(self) -> None:
        """Different token sets produce different keys."""
        assert make_dedup_key("hair transplant") != make_dedup_key(
            "hair transplantation"
        )


# ===========================================================================
# dedup() tests
# ===========================================================================


class TestDedup:
    """Tests for the dedup() function."""

    def test_removes_exact_duplicates(self) -> None:
        """Exact same term appears once in output."""
        kws = [_kw("hair transplant"), _kw("hair transplant")]
        result = dedup(kws)
        assert len(result) == 1
        assert result[0].term == "hair transplant"

    def test_merges_word_order_variants(self) -> None:
        """Word-order variants merged (same sorted tokens)."""
        kws = [_kw("hair transplant cost"), _kw("cost hair transplant")]
        result = dedup(kws)
        assert len(result) == 1

    def test_keeps_different_keywords(self) -> None:
        """Genuinely different keywords are kept."""
        kws = [_kw("hair transplant"), _kw("hair transplantation")]
        result = dedup(kws)
        assert len(result) == 2

    def test_empty_list(self) -> None:
        """Empty input returns empty output."""
        assert dedup([]) == []

    def test_single_keyword(self) -> None:
        """Single keyword passes through unchanged."""
        kws = [_kw("hair transplant")]
        result = dedup(kws)
        assert len(result) == 1

    @given(
        terms=st.lists(
            st.text(min_size=1, max_size=50).filter(lambda s: s.strip()),
            min_size=0,
            max_size=20,
        )
    )
    @settings(max_examples=50)
    def test_property_never_grows(self, terms: list[str]) -> None:
        """Property: dedup(kws) length <= kws length (never grows)."""
        kws = [_kw(t) for t in terms]
        result = dedup(kws)
        assert len(result) <= len(kws)
