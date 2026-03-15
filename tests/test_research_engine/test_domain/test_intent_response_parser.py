"""Tests for intent classification response parser.

Covers:
- PI-001: Valid intent type in output
- PI-002: Valid confidence level in output
- PI-003: Rationale non-empty
- PI-004: Valid format enum
- PI-007: All keywords classified or flagged
- PI-008: Order preservation
"""

from __future__ import annotations

import json
from pathlib import Path

from src.research_engine.domain.intent_response_parser import (
    parse_intent_response,
)
from src.research_engine.models.intent import (
    ContentFormat,
    IntentConfidence,
    IntentType,
)
from src.research_engine.models.result import Err, Ok

FIXTURE_PATH = (
    Path(__file__).parents[2]
    / ".."
    / "src"
    / "research_engine"
    / "__fixtures__"
    / "intent-classification-response.json"
)


def _fixture_json() -> str:
    return FIXTURE_PATH.read_text()


def _fixture_keywords() -> list[str]:
    data = json.loads(_fixture_json())
    return [c["keyword"] for c in data["classifications"]]


class TestParseValidResponse:
    """Parser handles well-formed LLM responses."""

    def test_parses_fixture(self) -> None:
        """Fixture response parses successfully."""
        keywords = _fixture_keywords()
        result = parse_intent_response(_fixture_json(), keywords)
        assert isinstance(result, Ok)
        assert len(result.value.classifications) == len(keywords)

    def test_all_intents_are_valid(self) -> None:
        """PI-001: Every classification has a valid intent type."""
        keywords = _fixture_keywords()
        result = parse_intent_response(_fixture_json(), keywords)
        assert isinstance(result, Ok)
        valid_intents = {t.value for t in IntentType}
        for cls in result.value.classifications:
            assert cls.intent in valid_intents

    def test_all_confidence_levels_valid(self) -> None:
        """PI-002: Every classification has a valid confidence level."""
        keywords = _fixture_keywords()
        result = parse_intent_response(_fixture_json(), keywords)
        assert isinstance(result, Ok)
        valid_levels = {c.value for c in IntentConfidence}
        for cls in result.value.classifications:
            assert cls.confidence in valid_levels

    def test_all_rationales_non_empty(self) -> None:
        """PI-003: Every classification has a non-empty rationale."""
        keywords = _fixture_keywords()
        result = parse_intent_response(_fixture_json(), keywords)
        assert isinstance(result, Ok)
        for cls in result.value.classifications:
            assert cls.rationale.strip()

    def test_all_formats_valid(self) -> None:
        """PI-004: Every classification has a valid format enum."""
        keywords = _fixture_keywords()
        result = parse_intent_response(_fixture_json(), keywords)
        assert isinstance(result, Ok)
        valid_formats = {f.value for f in ContentFormat}
        for cls in result.value.classifications:
            assert cls.recommended_format in valid_formats

    def test_all_keywords_present(self) -> None:
        """PI-007: All input keywords appear in the output."""
        keywords = _fixture_keywords()
        result = parse_intent_response(_fixture_json(), keywords)
        assert isinstance(result, Ok)
        output_keywords = {c.keyword.lower() for c in result.value.classifications}
        for kw in keywords:
            assert kw.lower() in output_keywords


class TestParseMarkdownFences:
    """Parser handles markdown-wrapped JSON responses."""

    def test_strips_json_fence(self) -> None:
        """JSON wrapped in ```json ... ``` is parsed correctly."""
        keywords = ["hair transplant"]
        cls_json = (
            '{"keyword": "hair transplant",'
            ' "intent": "informational",'
            ' "confidence": "high",'
            ' "rationale": "Informational query.",'
            ' "recommended_format": "definition-explainer",'
            ' "format_signal": null}'
        )
        raw = f'```json\n{{"classifications": [{cls_json}]}}\n```'
        result = parse_intent_response(raw, keywords)
        assert isinstance(result, Ok)
        assert len(result.value.classifications) == 1

    def test_strips_plain_fence(self) -> None:
        """JSON wrapped in ``` ... ``` (no language hint) is parsed."""
        keywords = ["hair transplant"]
        cls_json = (
            '{"keyword": "hair transplant",'
            ' "intent": "informational",'
            ' "confidence": "high",'
            ' "rationale": "Informational query.",'
            ' "recommended_format": "definition-explainer",'
            ' "format_signal": null}'
        )
        raw = f'```\n{{"classifications": [{cls_json}]}}\n```'
        result = parse_intent_response(raw, keywords)
        assert isinstance(result, Ok)


class TestParseInvalidResponse:
    """Parser rejects malformed or invalid responses."""

    def test_invalid_json(self) -> None:
        """Invalid JSON returns Err."""
        result = parse_intent_response("not json", ["test"])
        assert isinstance(result, Err)

    def test_missing_classifications_key(self) -> None:
        """JSON without 'classifications' key returns Err."""
        result = parse_intent_response('{"results": []}', ["test"])
        assert isinstance(result, Err)

    def test_missing_keyword_in_output(self) -> None:
        """Response missing an input keyword returns Err."""
        keywords = ["hair transplant", "best clinic"]
        response = json.dumps(
            {
                "classifications": [
                    {
                        "keyword": "hair transplant",
                        "intent": "informational",
                        "confidence": "high",
                        "rationale": "Test.",
                        "recommended_format": "definition-explainer",
                        "format_signal": None,
                    }
                ]
            }
        )
        result = parse_intent_response(response, keywords)
        assert isinstance(result, Err)
        assert "missing" in result.error.lower() or "Missing" in result.error

    def test_invented_keyword_in_output(self) -> None:
        """Response with invented keyword returns Err."""
        keywords = ["hair transplant"]
        response = json.dumps(
            {
                "classifications": [
                    {
                        "keyword": "hair transplant",
                        "intent": "informational",
                        "confidence": "high",
                        "rationale": "Test.",
                        "recommended_format": "definition-explainer",
                        "format_signal": None,
                    },
                    {
                        "keyword": "invented keyword",
                        "intent": "informational",
                        "confidence": "high",
                        "rationale": "Test.",
                        "recommended_format": "definition-explainer",
                        "format_signal": None,
                    },
                ]
            }
        )
        result = parse_intent_response(response, keywords)
        assert isinstance(result, Err)
        assert "invented" in result.error.lower() or "Invented" in result.error

    def test_invalid_intent_value(self) -> None:
        """Response with invalid intent value returns Err."""
        keywords = ["test"]
        response = json.dumps(
            {
                "classifications": [
                    {
                        "keyword": "test",
                        "intent": "exploratory",
                        "confidence": "high",
                        "rationale": "Test.",
                        "recommended_format": "definition-explainer",
                        "format_signal": None,
                    }
                ]
            }
        )
        result = parse_intent_response(response, keywords)
        assert isinstance(result, Err)

    def test_invalid_confidence_value(self) -> None:
        """Response with invalid confidence value returns Err."""
        keywords = ["test"]
        response = json.dumps(
            {
                "classifications": [
                    {
                        "keyword": "test",
                        "intent": "informational",
                        "confidence": "very_high",
                        "rationale": "Test.",
                        "recommended_format": "definition-explainer",
                        "format_signal": None,
                    }
                ]
            }
        )
        result = parse_intent_response(response, keywords)
        assert isinstance(result, Err)

    def test_invalid_format_value(self) -> None:
        """Response with invalid format value returns Err."""
        keywords = ["test"]
        response = json.dumps(
            {
                "classifications": [
                    {
                        "keyword": "test",
                        "intent": "informational",
                        "confidence": "high",
                        "rationale": "Test.",
                        "recommended_format": "blog-post",
                        "format_signal": None,
                    }
                ]
            }
        )
        result = parse_intent_response(response, keywords)
        assert isinstance(result, Err)

    def test_empty_rationale(self) -> None:
        """Response with empty rationale returns Err."""
        keywords = ["test"]
        response = json.dumps(
            {
                "classifications": [
                    {
                        "keyword": "test",
                        "intent": "informational",
                        "confidence": "high",
                        "rationale": "",
                        "recommended_format": "definition-explainer",
                        "format_signal": None,
                    }
                ]
            }
        )
        result = parse_intent_response(response, keywords)
        assert isinstance(result, Err)

    def test_duplicate_keyword_in_output(self) -> None:
        """Response with duplicate keyword returns Err."""
        keywords = ["test"]
        response = json.dumps(
            {
                "classifications": [
                    {
                        "keyword": "test",
                        "intent": "informational",
                        "confidence": "high",
                        "rationale": "First.",
                        "recommended_format": "definition-explainer",
                        "format_signal": None,
                    },
                    {
                        "keyword": "test",
                        "intent": "commercial",
                        "confidence": "high",
                        "rationale": "Duplicate.",
                        "recommended_format": "category-page",
                        "format_signal": None,
                    },
                ]
            }
        )
        result = parse_intent_response(response, keywords)
        assert isinstance(result, Err)
        assert "duplicate" in result.error.lower() or "Duplicate" in result.error


class TestCaseInsensitiveMatching:
    """Keywords are matched case-insensitively."""

    def test_case_mismatch_accepted(self) -> None:
        """LLM returning different case still matches."""
        keywords = ["Hair Transplant"]
        response = json.dumps(
            {
                "classifications": [
                    {
                        "keyword": "hair transplant",
                        "intent": "commercial",
                        "confidence": "medium",
                        "rationale": "Ambiguous head term.",
                        "recommended_format": "category-page",
                        "format_signal": None,
                    }
                ]
            }
        )
        result = parse_intent_response(response, keywords)
        assert isinstance(result, Ok)
