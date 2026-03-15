"""Tests for F-003 intent classification enums and contract types.

Covers:
- PI-001: Valid intent type (always one of 4 values)
- PI-002: Valid confidence level (always one of 3 values)
- PI-004: Valid format enum (always one of 9 values)
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.research_engine.models.intent import (
    ContentFormat,
    IntentClassification,
    IntentConfidence,
    IntentType,
)


class TestIntentType:
    """PI-001: Valid intent type (always one of 4 values)."""

    def test_has_four_values(self) -> None:
        """IntentType has exactly 4 members."""
        assert len(IntentType) == 4

    def test_informational_value(self) -> None:
        """Informational intent maps to correct string."""
        assert IntentType.INFORMATIONAL == "informational"

    def test_commercial_value(self) -> None:
        """Commercial intent maps to correct string."""
        assert IntentType.COMMERCIAL == "commercial"

    def test_transactional_value(self) -> None:
        """Transactional intent maps to correct string."""
        assert IntentType.TRANSACTIONAL == "transactional"

    def test_navigational_value(self) -> None:
        """Navigational intent maps to correct string."""
        assert IntentType.NAVIGATIONAL == "navigational"

    def test_is_string_enum(self) -> None:
        """IntentType values are strings (StrEnum)."""
        for member in IntentType:
            assert isinstance(member.value, str)

    def test_invalid_value_raises(self) -> None:
        """Invalid intent type string raises ValueError."""
        with pytest.raises(ValueError):
            IntentType("invalid_intent")


class TestIntentConfidence:
    """PI-002: Valid confidence level (always one of 3 values)."""

    def test_has_three_values(self) -> None:
        """IntentConfidence has exactly 3 members."""
        assert len(IntentConfidence) == 3

    def test_high_value(self) -> None:
        """High confidence maps correctly."""
        assert IntentConfidence.HIGH == "high"

    def test_medium_value(self) -> None:
        """Medium confidence maps correctly."""
        assert IntentConfidence.MEDIUM == "medium"

    def test_low_value(self) -> None:
        """Low confidence maps correctly."""
        assert IntentConfidence.LOW == "low"

    def test_invalid_value_raises(self) -> None:
        """Invalid confidence string raises ValueError."""
        with pytest.raises(ValueError):
            IntentConfidence("very_high")


class TestContentFormat:
    """PI-004: Valid format enum (always one of 9 values)."""

    def test_has_nine_values(self) -> None:
        """ContentFormat has exactly 9 members."""
        assert len(ContentFormat) == 9

    def test_all_format_values(self) -> None:
        """All 9 content format values are present."""
        expected = {
            "how-to-guide",
            "definition-explainer",
            "comparison-article",
            "listicle",
            "faq-page",
            "product-landing-page",
            "category-page",
            "location-page",
            "brand-navigational-page",
        }
        actual = {f.value for f in ContentFormat}
        assert actual == expected

    def test_is_string_enum(self) -> None:
        """ContentFormat values are strings."""
        for member in ContentFormat:
            assert isinstance(member.value, str)

    def test_invalid_value_raises(self) -> None:
        """Invalid format string raises ValueError."""
        with pytest.raises(ValueError):
            ContentFormat("blog-post")


class TestIntentClassification:
    """IntentClassification Pydantic model for a single keyword classification."""

    def test_creates_valid_classification(self) -> None:
        """Valid classification with all required fields."""
        cls = IntentClassification(
            keyword="hair transplant cost",
            intent=IntentType.INFORMATIONAL,
            confidence=IntentConfidence.HIGH,
            rationale="User wants pricing information",
            recommended_format=ContentFormat.DEFINITION_EXPLAINER,
            format_signal=None,
        )
        assert cls.keyword == "hair transplant cost"
        assert cls.intent == IntentType.INFORMATIONAL
        assert cls.confidence == IntentConfidence.HIGH
        assert cls.recommended_format == ContentFormat.DEFINITION_EXPLAINER

    def test_format_signal_optional(self) -> None:
        """format_signal can be None."""
        cls = IntentClassification(
            keyword="hair growth serum",
            intent=IntentType.COMMERCIAL,
            confidence=IntentConfidence.HIGH,
            rationale="Commercial investigation",
            recommended_format=ContentFormat.CATEGORY_PAGE,
            format_signal=None,
        )
        assert cls.format_signal is None

    def test_format_signal_with_value(self) -> None:
        """format_signal can contain a detected signal string."""
        cls = IntentClassification(
            keyword="how to care for hair after transplant",
            intent=IntentType.INFORMATIONAL,
            confidence=IntentConfidence.HIGH,
            rationale="How-to query",
            recommended_format=ContentFormat.HOW_TO_GUIDE,
            format_signal="how to",
        )
        assert cls.format_signal == "how to"

    def test_rejects_empty_rationale(self) -> None:
        """PI-003: Rationale must be non-empty."""
        with pytest.raises(ValueError):
            IntentClassification(
                keyword="test",
                intent=IntentType.INFORMATIONAL,
                confidence=IntentConfidence.HIGH,
                rationale="",
                recommended_format=ContentFormat.DEFINITION_EXPLAINER,
                format_signal=None,
            )

    def test_rejects_whitespace_rationale(self) -> None:
        """Rationale of only whitespace is rejected."""
        with pytest.raises(ValueError):
            IntentClassification(
                keyword="test",
                intent=IntentType.INFORMATIONAL,
                confidence=IntentConfidence.HIGH,
                rationale="   ",
                recommended_format=ContentFormat.DEFINITION_EXPLAINER,
                format_signal=None,
            )

    def test_rejects_empty_keyword(self) -> None:
        """Keyword must be non-empty."""
        with pytest.raises(ValueError):
            IntentClassification(
                keyword="",
                intent=IntentType.INFORMATIONAL,
                confidence=IntentConfidence.HIGH,
                rationale="Test rationale",
                recommended_format=ContentFormat.DEFINITION_EXPLAINER,
                format_signal=None,
            )


class TestIntentClassificationProperties:
    """Property-based tests for intent classification invariants."""

    @given(
        intent=st.sampled_from(list(IntentType)),
        confidence=st.sampled_from(list(IntentConfidence)),
        fmt=st.sampled_from(list(ContentFormat)),
    )
    @settings(max_examples=50)
    def test_any_valid_enum_combination_accepted(
        self,
        intent: IntentType,
        confidence: IntentConfidence,
        fmt: ContentFormat,
    ) -> None:
        """Any combination of valid enum values is accepted."""
        cls = IntentClassification(
            keyword="test keyword",
            intent=intent,
            confidence=confidence,
            rationale="Test rationale for property test",
            recommended_format=fmt,
            format_signal=None,
        )
        assert cls.intent in IntentType
        assert cls.confidence in IntentConfidence
        assert cls.recommended_format in ContentFormat
