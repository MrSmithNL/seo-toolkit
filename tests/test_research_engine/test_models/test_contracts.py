"""Tests for the KeywordRecord downstream contract.

TDD: These tests are written BEFORE the implementation.
Covers: T-001 (KeywordRecord contract for F-002, F-003, F-007)
"""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from src.research_engine.models.contracts import KeywordRecord
from src.research_engine.models.keyword import (
    DifficultySource,
    GapStatus,
    KeywordIntent,
    KeywordSource,
)


def _make_record(**overrides: object) -> KeywordRecord:
    """Helper to create a valid KeywordRecord with defaults."""
    defaults: dict = {
        "id": "kw_test123",
        "tenant_id": uuid.uuid4(),
        "campaign_id": "camp_test",
        "term": "hair transplant cost",
        "locale": "en",
        "volume": 5000,
        "cpc": 3.50,
        "difficulty": 45,
        "difficulty_source": DifficultySource.HEURISTIC,
        "intent": None,
        "gap_status": GapStatus.NEW_OPPORTUNITY,
        "source": KeywordSource.URL_EXTRACTION,
    }
    defaults.update(overrides)
    return KeywordRecord(**defaults)


class TestKeywordRecord:
    """Tests for the KeywordRecord contract type."""

    def test_creates_valid_record(self) -> None:
        """A valid KeywordRecord with all fields succeeds."""
        record = _make_record()
        assert record.term == "hair transplant cost"
        assert record.volume == 5000
        assert record.gap_status == GapStatus.NEW_OPPORTUNITY

    def test_f002_can_read_cluster_fields(self) -> None:
        """F-002 needs: id, term, locale, volume for clustering."""
        record = _make_record()
        assert record.id is not None
        assert record.term is not None
        assert record.locale is not None
        assert record.volume is not None

    def test_f003_can_read_intent_fields(self) -> None:
        """F-003 needs: id, term to classify intent."""
        record = _make_record()
        assert record.id is not None
        assert record.term is not None
        assert record.intent is None  # not yet classified

    def test_f007_can_read_calendar_fields(self) -> None:
        """F-007 needs: id, term, volume, difficulty, gap_status for prioritisation."""
        record = _make_record()
        assert record.id is not None
        assert record.volume is not None
        assert record.difficulty is not None
        assert record.gap_status is not None

    def test_intent_is_optional(self) -> None:
        """Intent is None until F-003 populates it."""
        record = _make_record(intent=None)
        assert record.intent is None

    def test_intent_accepts_valid_value(self) -> None:
        """Intent accepts valid KeywordIntent enum value."""
        record = _make_record(intent=KeywordIntent.INFORMATIONAL)
        assert record.intent == KeywordIntent.INFORMATIONAL

    def test_serialises_to_dict(self) -> None:
        """Record must serialise to dict for JSON output."""
        record = _make_record()
        data = record.model_dump()
        assert isinstance(data, dict)
        assert data["term"] == "hair transplant cost"
        assert data["source"] == "url_extraction"

    def test_serialises_to_json(self) -> None:
        """Record must serialise to JSON string."""
        record = _make_record()
        json_str = record.model_dump_json()
        assert isinstance(json_str, str)
        assert "hair transplant cost" in json_str

    def test_rejects_invalid_locale(self) -> None:
        """Locale must be from supported set."""
        with pytest.raises(ValidationError):
            _make_record(locale="xx")

    def test_difficulty_range_enforced(self) -> None:
        """Difficulty must be 0-100 when set."""
        with pytest.raises(ValidationError):
            _make_record(difficulty=150)
