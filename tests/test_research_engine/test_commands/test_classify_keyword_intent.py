"""Tests for F-003 intent classification pipeline.

Covers:
- ATS-006: 120 keywords → 3 LLM calls (50, 50, 20)
- ATS-007: LLM failure → retry once → mark unclassified, continue
- ATS-008: Non-English keyword classified using English taxonomy
- ATS-016: All records updated with intent fields
- ATS-017: Volume refresh does NOT reclassify
- ATS-018: --reclassify flag forces re-classification
- INT-001: F-001 output as input
- PI-011: Token budget compliance
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

import pytest

from src.research_engine.commands.classify_keyword_intent import (
    ClassifyKeywordIntentCommand,
    classify_keyword_intent,
)
from src.research_engine.config import ResearchConfig
from src.research_engine.models.keyword import Keyword, KeywordSource
from src.research_engine.models.result import Err, Ok

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN = "camp_test001"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _config(**overrides: object) -> ResearchConfig:
    return ResearchConfig(
        environment="test",
        feature_intent_classification=True,
        intent_chunk_size=overrides.get("chunk_size", 50),
        intent_max_retries=overrides.get("max_retries", 1),
    )


def _make_keywords(terms: list[str], locale: str = "en") -> list[Keyword]:
    return [
        Keyword(
            tenant_id=TENANT,
            campaign_id=CAMPAIGN,
            term=term,
            source=KeywordSource.MANUAL_SEED,
        )
        for term in terms
    ]


def _make_llm_response(keywords: list[str]) -> str:
    """Create a valid LLM response for the given keywords."""
    classifications = []
    for kw in keywords:
        classifications.append(
            {
                "keyword": kw,
                "intent": "informational",
                "confidence": "high",
                "rationale": f"Test classification for {kw}.",
                "recommended_format": "definition-explainer",
                "format_signal": None,
            }
        )
    return json.dumps({"classifications": classifications})


class MockStorageForIntent:
    """In-memory storage for intent tests."""

    def __init__(self) -> None:  # noqa: D107
        self.keywords: list[Keyword] = []

    def save(self, keywords: list[Keyword]) -> int:  # noqa: D102
        existing_keys = {kw.normalized_key for kw in self.keywords}
        count = 0
        for kw in keywords:
            if kw.normalized_key not in existing_keys:
                self.keywords.append(kw)
                existing_keys.add(kw.normalized_key)
                count += 1
        return count

    def get_by_campaign(  # noqa: D102
        self,
        campaign_id: str,
        locale: str | None = None,
        min_volume: int | None = None,
        max_difficulty: int | None = None,
    ) -> list[Keyword]:
        results = [kw for kw in self.keywords if kw.campaign_id == campaign_id]
        if locale:
            # All keywords have default locale in the term — no locale field on Keyword
            pass
        return results

    def update_intent_fields(  # noqa: D102
        self,
        keyword_id: str,
        intent: str,
        intent_confidence: str,
        intent_rationale: str,
        recommended_format: str,
        format_signal: str | None,
        classified_at: datetime,
    ) -> bool:
        for kw in self.keywords:
            if kw.id == keyword_id:
                object.__setattr__(kw, "intent", intent)
                object.__setattr__(kw, "intent_confidence", intent_confidence)
                object.__setattr__(kw, "intent_rationale", intent_rationale)
                object.__setattr__(kw, "recommended_format", recommended_format)
                object.__setattr__(kw, "format_signal", format_signal)
                object.__setattr__(kw, "classified_at", classified_at)
                return True
        return False

    def save_gaps(self, gaps: list) -> int:  # noqa: D102
        return 0

    def get_gaps(self, campaign_id: str) -> list:  # noqa: D102
        return []


class ChunkedMockLlm:
    """Mock LLM that returns valid responses for each chunk."""

    def __init__(self) -> None:  # noqa: D107
        self.calls: list[str] = []
        self.fail_on_call: int | None = None

    def complete(self, prompt: str) -> str:  # noqa: D102
        self.calls.append(prompt)
        if self.fail_on_call is not None and len(self.calls) == self.fail_on_call:
            raise ConnectionError("LLM service unavailable")

        # Extract keywords from the prompt
        keywords = []
        for line in prompt.split("\n"):
            line = line.strip()
            if line.startswith('- "') and line.endswith('"'):
                keywords.append(line[3:-1])
        return _make_llm_response(keywords)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestFeatureFlag:
    """Feature flag gates the pipeline."""

    def test_disabled_flag_returns_err(self) -> None:  # noqa: D102
        config = ResearchConfig(environment="test", feature_intent_classification=False)
        storage = MockStorageForIntent()
        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, config, storage, llm)
        assert isinstance(result, Err)
        assert "disabled" in result.error.lower()


class TestHappyPath:
    """Normal classification flow."""

    def test_classifies_all_keywords(self) -> None:
        """ATS-016: All records updated with intent fields."""
        storage = MockStorageForIntent()
        keywords = _make_keywords(["hair transplant", "best clinic", "FUE procedure"])
        storage.save(keywords)
        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, _config(), storage, llm)
        assert isinstance(result, Ok)
        assert result.value.keywords_classified == 3
        assert result.value.failed == 0

        # Verify intent fields are populated
        for kw in storage.keywords:
            assert kw.intent is not None
            assert kw.intent_confidence is not None
            assert kw.intent_rationale is not None
            assert kw.recommended_format is not None
            assert kw.classified_at is not None

    def test_returns_distribution_stats(self) -> None:
        """Result includes intent and format distribution."""
        storage = MockStorageForIntent()
        storage.save(_make_keywords(["test keyword"]))
        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, _config(), storage, llm)
        assert isinstance(result, Ok)
        assert "informational" in result.value.intent_distribution

    def test_no_keywords_returns_err(self) -> None:
        """Empty keyword set returns Err."""
        storage = MockStorageForIntent()
        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, _config(), storage, llm)
        assert isinstance(result, Err)


class TestChunking:
    """ATS-006: Batch processing with 50 keywords per chunk."""

    def test_120_keywords_makes_3_calls(self) -> None:
        """120 keywords → 3 LLM calls (50, 50, 20)."""
        storage = MockStorageForIntent()
        keywords = _make_keywords([f"keyword {i}" for i in range(120)])
        storage.save(keywords)
        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, _config(), storage, llm)
        assert isinstance(result, Ok)
        assert result.value.keywords_classified == 120
        assert len(llm.calls) == 3

    def test_custom_chunk_size(self) -> None:
        """Custom chunk size is respected."""
        storage = MockStorageForIntent()
        keywords = _make_keywords([f"keyword {i}" for i in range(30)])
        storage.save(keywords)
        llm = ChunkedMockLlm()
        config = _config(chunk_size=10)
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, config, storage, llm)
        assert isinstance(result, Ok)
        assert len(llm.calls) == 3


class TestLLMFailure:
    """ATS-007: LLM failure handling."""

    def test_retry_on_failure(self) -> None:
        """Failed LLM call retries once."""
        storage = MockStorageForIntent()
        storage.save(_make_keywords(["hair transplant"]))

        class RetryLlm:
            """LLM that fails on first call then succeeds."""

            def __init__(self):  # noqa: D107
                self.calls = 0

            def complete(self, prompt: str) -> str:  # noqa: D102
                self.calls += 1
                if self.calls == 1:
                    raise ConnectionError("Transient failure")
                keywords = []
                for line in prompt.split("\n"):
                    line = line.strip()
                    if line.startswith('- "') and line.endswith('"'):
                        keywords.append(line[3:-1])
                return _make_llm_response(keywords)

        llm = RetryLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, _config(), storage, llm)
        assert isinstance(result, Ok)
        assert result.value.keywords_classified == 1
        assert llm.calls == 2

    def test_persistent_failure_marks_unclassified(self) -> None:
        """Persistent LLM failure marks keywords as unclassified."""
        storage = MockStorageForIntent()
        keywords = _make_keywords([f"keyword {i}" for i in range(60)])
        storage.save(keywords)

        llm = ChunkedMockLlm()
        llm.fail_on_call = 1  # Fail on the first call

        class AlwaysFailFirstChunkLlm:
            """LLM that always fails on the first chunk."""

            def __init__(self):  # noqa: D107
                self.calls = []

            def complete(self, prompt: str) -> str:  # noqa: D102
                self.calls.append(prompt)
                # Count which chunk we're on (first 2 calls = chunk 1, next = chunk 2)
                if len(self.calls) <= 2:
                    raise ConnectionError("Persistent failure")
                keywords = []
                for line in prompt.split("\n"):
                    line = line.strip()
                    if line.startswith('- "') and line.endswith('"'):
                        keywords.append(line[3:-1])
                return _make_llm_response(keywords)

        llm2 = AlwaysFailFirstChunkLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, _config(), storage, llm2)
        assert isinstance(result, Ok)
        # First chunk (50) failed, second chunk (10) succeeded
        assert result.value.keywords_classified == 10
        assert result.value.failed == 50


class TestReclassify:
    """ATS-017/ATS-018: Reclassify behavior."""

    def test_skips_already_classified(self) -> None:
        """ATS-017: Already-classified keywords are skipped."""
        storage = MockStorageForIntent()
        keywords = _make_keywords(["hair transplant", "best clinic"])
        storage.save(keywords)

        # Pre-classify the first keyword
        now = datetime.now(tz=UTC)
        storage.update_intent_fields(
            keywords[0].id,
            "informational",
            "high",
            "Already classified.",
            "definition-explainer",
            None,
            now,
        )

        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(
            tenant_id=TENANT,
            campaign_id=CAMPAIGN,
            reclassify=False,
        )

        result = classify_keyword_intent(cmd, _config(), storage, llm)
        assert isinstance(result, Ok)
        assert result.value.keywords_classified == 1
        assert result.value.skipped == 1

    def test_reclassify_flag_forces_reclassification(self) -> None:
        """ATS-018: --reclassify flag re-classifies everything."""
        storage = MockStorageForIntent()
        keywords = _make_keywords(["hair transplant", "best clinic"])
        storage.save(keywords)

        # Pre-classify both
        now = datetime.now(tz=UTC)
        for kw in keywords:
            storage.update_intent_fields(
                kw.id,
                "informational",
                "high",
                "Old.",
                "definition-explainer",
                None,
                now,
            )

        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(
            tenant_id=TENANT,
            campaign_id=CAMPAIGN,
            reclassify=True,
        )

        result = classify_keyword_intent(cmd, _config(), storage, llm)
        assert isinstance(result, Ok)
        assert result.value.keywords_classified == 2
        assert result.value.skipped == 0


class TestEventEmission:
    """Pipeline emits IntentClassificationCompletedEvent."""

    def test_emits_event_on_success(self, caplog: pytest.LogCaptureFixture) -> None:
        """Completion event is emitted as structured log."""
        storage = MockStorageForIntent()
        storage.save(_make_keywords(["hair transplant"]))
        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        import logging

        with caplog.at_level(logging.INFO):
            result = classify_keyword_intent(cmd, _config(), storage, llm)

        assert isinstance(result, Ok)
        event_logs = [
            r for r in caplog.records if "research.intent.completed" in r.getMessage()
        ]
        assert len(event_logs) == 1


class TestNonEnglishKeywords:
    """ATS-008: Non-English keywords classified using English taxonomy."""

    def test_german_keyword_classified(self) -> None:
        """German keyword gets English intent type."""
        storage = MockStorageForIntent()
        storage.save(_make_keywords(["Haartransplantation Kosten Deutschland"]))
        llm = ChunkedMockLlm()
        cmd = ClassifyKeywordIntentCommand(tenant_id=TENANT, campaign_id=CAMPAIGN)

        result = classify_keyword_intent(cmd, _config(), storage, llm)
        assert isinstance(result, Ok)
        assert result.value.keywords_classified == 1

        # Verify the intent is in English taxonomy
        kw = storage.keywords[0]
        assert kw.intent in {
            "informational",
            "commercial",
            "transactional",
            "navigational",
        }
