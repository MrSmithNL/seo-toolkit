"""Tests for QualityAssessor (T-006).

ATS-008: Authoritative page → depth_score=5, E-E-AT signals.
ATS-009: Thin page → depth_score=2, no E-E-AT.
ATS-010: Medium quality → depth_score=3.
ATS-012: Crawl-failed → quality skipped.
ATS-013: 12 pages → 3 LLM batch calls (5+5+2).
ATS-014: Depth score rubric adherence.
PI-003: Depth score always 1-5.
PI-008: LLM fields flagged.
PI-011: Rationale present when scored.
"""

from __future__ import annotations

import json

from src.research_engine.models.competitor import QualityAssessmentStatus
from src.research_engine.services.quality_assessor import (
    QualityAssessor,
)

# ---------------------------------------------------------------------------
# Mock LLM
# ---------------------------------------------------------------------------


class MockLlm:
    """Mock LLM returning canned quality assessment responses."""

    def __init__(self, response: str = "") -> None:
        self.response = response
        self.calls: list[str] = []

    def complete(self, prompt: str) -> str:
        """Return canned response, tracking calls."""
        self.calls.append(prompt)
        return self.response


class FailingLlm:
    """LLM that always raises an exception."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        raise ConnectionError("LLM service unavailable")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

AUTHORITATIVE_RESPONSE = json.dumps(
    {
        "depth_score": 5,
        "topics_covered": ["FUE procedure", "recovery timeline", "cost comparison"],
        "has_original_data": True,
        "has_author_credentials": True,
        "eeat_signals": ["author_bio", "medical_review", "citations"],
        "quality_rationale": "Comprehensive 4200-word article by a surgeon.",
    }
)

THIN_RESPONSE = json.dumps(
    {
        "depth_score": 2,
        "topics_covered": ["aftercare basics"],
        "has_original_data": False,
        "has_author_credentials": False,
        "eeat_signals": [],
        "quality_rationale": "Brief 350-word overview, no credentials.",
    }
)

MEDIUM_RESPONSE = json.dumps(
    {
        "depth_score": 3,
        "topics_covered": [
            "recovery timeline",
            "washing instructions",
            "activity restrictions",
        ],
        "has_original_data": False,
        "has_author_credentials": False,
        "eeat_signals": [],
        "quality_rationale": "Solid 1800-word guide, no citations.",
    }
)

BATCH_RESPONSE = json.dumps(
    [
        {
            "depth_score": 5,
            "topics_covered": ["topic1"],
            "has_original_data": True,
            "has_author_credentials": True,
            "eeat_signals": ["author_bio"],
            "quality_rationale": "Authoritative content.",
        },
        {
            "depth_score": 3,
            "topics_covered": ["topic2"],
            "has_original_data": False,
            "has_author_credentials": False,
            "eeat_signals": [],
            "quality_rationale": "Solid content.",
        },
    ]
)


# ---------------------------------------------------------------------------
# ATS-008: Authoritative competitor page
# ---------------------------------------------------------------------------


class TestAuthoritativePage:
    """ATS-008: Authoritative page assessment."""

    def test_depth_score_5(self) -> None:
        llm = MockLlm(response=AUTHORITATIVE_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single(
            "Long authoritative content...", "https://example.com"
        )
        assert result.status == QualityAssessmentStatus.COMPLETED
        assert result.profile is not None
        assert result.profile.depth_score == 5

    def test_eeat_signals_present(self) -> None:
        llm = MockLlm(response=AUTHORITATIVE_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Content...", "https://example.com")
        assert "author_bio" in result.profile.eeat_signals
        assert "citations" in result.profile.eeat_signals

    def test_has_original_data(self) -> None:
        llm = MockLlm(response=AUTHORITATIVE_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Content...", "https://example.com")
        assert result.profile.has_original_data is True


# ---------------------------------------------------------------------------
# ATS-009: Thin competitor page
# ---------------------------------------------------------------------------


class TestThinPage:
    """ATS-009: Thin page assessment."""

    def test_depth_score_2(self) -> None:
        llm = MockLlm(response=THIN_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Brief content.", "https://example.com")
        assert result.profile.depth_score == 2

    def test_no_eeat_signals(self) -> None:
        llm = MockLlm(response=THIN_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Brief content.", "https://example.com")
        assert result.profile.eeat_signals == []

    def test_no_original_data(self) -> None:
        llm = MockLlm(response=THIN_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Brief content.", "https://example.com")
        assert result.profile.has_original_data is False


# ---------------------------------------------------------------------------
# ATS-010: Medium quality page
# ---------------------------------------------------------------------------


class TestMediumQuality:
    """ATS-010: Medium quality assessment."""

    def test_depth_score_3(self) -> None:
        llm = MockLlm(response=MEDIUM_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Medium content.", "https://example.com")
        assert result.profile.depth_score == 3

    def test_topics_covered(self) -> None:
        llm = MockLlm(response=MEDIUM_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Content.", "https://example.com")
        assert "recovery timeline" in result.profile.topics_covered


# ---------------------------------------------------------------------------
# ATS-012: Crawl-failed → quality skipped
# ---------------------------------------------------------------------------


class TestCrawlFailedSkipped:
    """ATS-012: Empty content results in skipped assessment."""

    def test_empty_content_skipped(self) -> None:
        llm = MockLlm()
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("", "https://example.com")
        assert result.status == QualityAssessmentStatus.SKIPPED
        assert len(llm.calls) == 0  # No LLM call made

    def test_whitespace_only_skipped(self) -> None:
        llm = MockLlm()
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("   ", "https://example.com")
        assert result.status == QualityAssessmentStatus.SKIPPED


# ---------------------------------------------------------------------------
# ATS-013: Batch processing — 5 pages per LLM batch
# ---------------------------------------------------------------------------


class TestBatchProcessing:
    """ATS-013: Batch processing with configurable batch size."""

    def test_12_pages_makes_3_calls(self) -> None:
        """12 pages with batch_size=5 → 3 LLM calls (5+5+2)."""
        llm = MockLlm(response=BATCH_RESPONSE)
        assessor = QualityAssessor(llm, batch_size=5)
        pages = [
            {"url": f"https://example.com/page{i}", "content": f"Content {i}"}
            for i in range(12)
        ]
        result = assessor.assess_batch(pages)
        assert result.llm_calls_made == 3
        assert len(result.results) == 12

    def test_5_pages_makes_1_call(self) -> None:
        llm = MockLlm(response=BATCH_RESPONSE)
        assessor = QualityAssessor(llm, batch_size=5)
        pages = [
            {"url": f"https://example.com/page{i}", "content": f"Content {i}"}
            for i in range(5)
        ]
        result = assessor.assess_batch(pages)
        assert result.llm_calls_made == 1

    def test_batch_tracks_total_tokens(self) -> None:
        llm = MockLlm(response=AUTHORITATIVE_RESPONSE)
        assessor = QualityAssessor(llm, batch_size=5)
        pages = [{"url": "https://example.com", "content": "Content"}]
        result = assessor.assess_batch(pages)
        assert result.total_tokens > 0


# ---------------------------------------------------------------------------
# LLM failure handling
# ---------------------------------------------------------------------------


class TestLlmFailure:
    """LLM failure → status=failed, pipeline continues."""

    def test_llm_failure_returns_failed_status(self) -> None:
        llm = FailingLlm()
        assessor = QualityAssessor(llm, max_retries=2)
        result = assessor.assess_single("Content", "https://example.com")
        assert result.status == QualityAssessmentStatus.FAILED
        assert "unavailable" in result.error.lower()

    def test_llm_retries_on_failure(self) -> None:
        llm = FailingLlm()
        assessor = QualityAssessor(llm, max_retries=2)
        assessor.assess_single("Content", "https://example.com")
        # Initial attempt + 2 retries = 3 calls
        assert len(llm.calls) == 3

    def test_batch_llm_failure_marks_all_pages_failed(self) -> None:
        llm = FailingLlm()
        assessor = QualityAssessor(llm, batch_size=5)
        pages = [
            {"url": f"https://example.com/page{i}", "content": f"Content {i}"}
            for i in range(3)
        ]
        result = assessor.assess_batch(pages)
        assert all(r.status == QualityAssessmentStatus.FAILED for r in result.results)


# ---------------------------------------------------------------------------
# PI-008: LLM fields flagged
# ---------------------------------------------------------------------------


class TestLlmFieldsFlagged:
    """PI-008: All AI-assessed fields tagged."""

    def test_profile_has_llm_assessed_fields(self) -> None:
        llm = MockLlm(response=AUTHORITATIVE_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Content", "https://example.com")
        assert "depth_score" in result.profile.llm_assessed_fields
        assert "quality_rationale" in result.profile.llm_assessed_fields


# ---------------------------------------------------------------------------
# PI-011: Rationale present when scored
# ---------------------------------------------------------------------------


class TestRationalePresent:
    """PI-011: Rationale accompanies every depth score."""

    def test_rationale_always_present(self) -> None:
        llm = MockLlm(response=AUTHORITATIVE_RESPONSE)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Content", "https://example.com")
        assert result.profile.quality_rationale
        assert len(result.profile.quality_rationale) > 0


# ---------------------------------------------------------------------------
# Response parsing edge cases
# ---------------------------------------------------------------------------


class TestResponseParsing:
    """Edge cases in LLM response parsing."""

    def test_markdown_code_block_extracted(self) -> None:
        response = f"```json\n{AUTHORITATIVE_RESPONSE}\n```"
        llm = MockLlm(response=response)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Content", "https://example.com")
        assert result.status == QualityAssessmentStatus.COMPLETED

    def test_invalid_json_returns_failed(self) -> None:
        llm = MockLlm(response="This is not JSON at all")
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Content", "https://example.com")
        assert result.status == QualityAssessmentStatus.FAILED

    def test_profiles_wrapper_key(self) -> None:
        """Response with {"profiles": [...]} wrapper."""
        response = json.dumps({"profiles": [json.loads(AUTHORITATIVE_RESPONSE)]})
        llm = MockLlm(response=response)
        assessor = QualityAssessor(llm)
        result = assessor.assess_single("Content", "https://example.com")
        assert result.status == QualityAssessmentStatus.COMPLETED
