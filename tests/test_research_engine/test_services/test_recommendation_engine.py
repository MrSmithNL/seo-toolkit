"""Tests for RecommendationEngine.

Covers: ATS-002, ATS-003, ATS-004, ATS-007, INT-004.
"""

from __future__ import annotations

import json

from src.research_engine.models.content_brief import ContentType, SearchIntent
from src.research_engine.services.recommendation_engine import (
    _build_fallback_recommendation,
    _infer_content_type_from_intent,
    _parse_llm_response,
    get_recommendations,
)


class MockLlm:
    """Mock LLM for tests."""

    def __init__(self, response: str = "", fail: bool = False) -> None:
        self.response = response
        self.calls: list[str] = []
        self.fail = fail

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        if self.fail:
            raise ConnectionError("LLM service unavailable")
        return self.response


class TestContentTypeInference:
    """ATS-002: Content type inferred from intent."""

    def test_commercial_maps_to_comparison(self) -> None:
        assert (
            _infer_content_type_from_intent(SearchIntent.COMMERCIAL)
            == ContentType.COMPARISON
        )

    def test_informational_maps_to_how_to(self) -> None:
        assert (
            _infer_content_type_from_intent(SearchIntent.INFORMATIONAL)
            == ContentType.HOW_TO
        )

    def test_transactional_maps_to_product_page(self) -> None:
        assert (
            _infer_content_type_from_intent(SearchIntent.TRANSACTIONAL)
            == ContentType.PRODUCT_PAGE
        )


class TestParseLlmResponse:
    """Parse structured JSON from LLM."""

    def test_valid_json(self) -> None:
        response = json.dumps(
            {
                "content_type": "comparison",
                "recommended_headings": [
                    "What is FUE?",
                    "What is DHI?",
                    "Key differences",
                ],
                "recommended_schema_types": ["Article", "FAQPage"],
            }
        )
        rec = _parse_llm_response(response, SearchIntent.COMMERCIAL)
        assert rec.content_type == ContentType.COMPARISON
        assert len(rec.recommended_headings) == 3
        assert rec.source == "llm_recommended"

    def test_json_in_code_block(self) -> None:
        response = (
            '```json\n{"content_type": "how_to",'
            ' "recommended_headings": ["Step 1"],'
            ' "recommended_schema_types": ["HowTo"]}\n```'
        )
        rec = _parse_llm_response(response, SearchIntent.INFORMATIONAL)
        assert rec.content_type == ContentType.HOW_TO

    def test_invalid_content_type_falls_back(self) -> None:
        response = json.dumps(
            {
                "content_type": "infographic",
                "recommended_headings": [],
                "recommended_schema_types": [],
            }
        )
        rec = _parse_llm_response(response, SearchIntent.INFORMATIONAL)
        assert rec.content_type == ContentType.HOW_TO  # fallback from intent


class TestFallbackRecommendation:
    """ATS-007: LLM failure → fallback to competitor headings."""

    def test_uses_longest_competitor_headings(self) -> None:
        headings = [
            ["Heading A"],
            ["Heading B", "Heading C", "Heading D"],
            ["Heading E", "Heading F"],
        ]
        rec = _build_fallback_recommendation(
            SearchIntent.COMMERCIAL, headings, ["Article"]
        )
        assert rec.recommended_headings == ["Heading B", "Heading C", "Heading D"]
        assert rec.source == "extracted from competitor — LLM unavailable"

    def test_content_type_from_intent(self) -> None:
        rec = _build_fallback_recommendation(SearchIntent.INFORMATIONAL, [], [])
        assert rec.content_type == ContentType.HOW_TO


class TestGetRecommendations:
    """Integration: LLM call + retry + fallback."""

    def test_successful_llm_call(self) -> None:
        llm = MockLlm(
            response=json.dumps(
                {
                    "content_type": "comparison",
                    "recommended_headings": ["FUE overview", "DHI overview"],
                    "recommended_schema_types": ["Article"],
                }
            )
        )

        rec = get_recommendations(
            keyword="FUE vs DHI",
            intent=SearchIntent.COMMERCIAL,
            competitor_headings=[["Comp heading"]],
            competitor_schema_types=["Article"],
            llm=llm,
        )

        assert rec.content_type == ContentType.COMPARISON
        assert len(llm.calls) == 1  # only one call needed

    def test_llm_failure_triggers_fallback(self) -> None:
        """ATS-007: LLM fails → fallback after retries."""
        llm = MockLlm(fail=True)

        rec = get_recommendations(
            keyword="FUE vs DHI",
            intent=SearchIntent.COMMERCIAL,
            competitor_headings=[["Comp H1", "Comp H2"]],
            competitor_schema_types=["Article"],
            llm=llm,
            max_retries=2,
        )

        assert rec.source == "extracted from competitor — LLM unavailable"
        assert len(llm.calls) == 3  # initial + 2 retries
        assert rec.content_type == ContentType.COMPARISON

    def test_no_llm_provided(self) -> None:
        """No LLM → immediate fallback."""
        rec = get_recommendations(
            keyword="test",
            intent=SearchIntent.INFORMATIONAL,
            competitor_headings=[],
            competitor_schema_types=[],
            llm=None,
        )
        assert rec.source == "extracted from competitor — LLM unavailable"
