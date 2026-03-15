"""Tests for intent classification prompt builder.

Covers:
- Prompt construction from keyword list
- Keyword escaping (control chars stripped, quoted)
- JSON schema injection
- Prompt versioning
"""

from __future__ import annotations

from src.research_engine.domain.intent_prompt_builder import build_intent_prompt


class TestBuildIntentPrompt:
    """Prompt builder constructs valid classification prompts."""

    def test_includes_all_keywords(self) -> None:
        """All input keywords appear in the prompt."""
        keywords = ["hair transplant", "best clinic", "FUE procedure"]
        prompt = build_intent_prompt(keywords)
        for kw in keywords:
            assert kw in prompt

    def test_includes_json_schema(self) -> None:
        """Prompt includes the structured output schema."""
        prompt = build_intent_prompt(["test keyword"])
        assert '"classifications"' in prompt
        assert '"intent"' in prompt
        assert '"confidence"' in prompt
        assert '"recommended_format"' in prompt

    def test_includes_intent_definitions(self) -> None:
        """Prompt includes all 4 intent type definitions."""
        prompt = build_intent_prompt(["test"])
        assert "informational" in prompt
        assert "commercial" in prompt
        assert "transactional" in prompt
        assert "navigational" in prompt

    def test_includes_ambiguity_rule(self) -> None:
        """Prompt includes the commercial > informational ambiguity rule."""
        prompt = build_intent_prompt(["test"])
        assert "commercial" in prompt.lower()
        assert "ambiguous" in prompt.lower() or "Ambiguity" in prompt

    def test_includes_format_signals(self) -> None:
        """Prompt includes format signal detection guidance."""
        prompt = build_intent_prompt(["test"])
        assert "how to" in prompt
        assert "best" in prompt
        assert "vs" in prompt
        assert "what is" in prompt

    def test_strips_control_characters(self) -> None:
        """Control characters in keyword text are stripped."""
        keywords = ["hair\x00transplant", "best\nclinic\ttips"]
        prompt = build_intent_prompt(keywords)
        assert "\x00" not in prompt
        # Newlines and tabs within keyword text should be replaced
        assert "hair transplant" in prompt or "hairtransplant" in prompt

    def test_keywords_are_quoted(self) -> None:
        """Keywords are wrapped in quotes in the prompt."""
        keywords = ["hair transplant cost"]
        prompt = build_intent_prompt(keywords)
        assert '"hair transplant cost"' in prompt

    def test_empty_keyword_list(self) -> None:
        """Empty keyword list produces a valid prompt with no keywords."""
        prompt = build_intent_prompt([])
        assert "classifications" in prompt

    def test_large_batch_50_keywords(self) -> None:
        """50 keywords (max batch size) all appear in prompt."""
        keywords = [f"keyword {i}" for i in range(50)]
        prompt = build_intent_prompt(keywords)
        for kw in keywords:
            assert kw in prompt
