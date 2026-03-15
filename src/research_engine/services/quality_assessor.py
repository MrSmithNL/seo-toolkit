"""QualityAssessor for F-005 LLM-based content quality benchmarking.

Sends compressed page content to LLM for quality assessment.
Produces depth_score (1-5), topics, E-E-A-T signals.
Batches pages per LLM call. Graceful fallback on failure.

TypeScript equivalent: modules/content-engine/research/services/quality-assessor.ts
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol, runtime_checkable

from src.research_engine.models.competitor import (
    QualityAssessmentStatus,
    QualityProfile,
)

logger = logging.getLogger(__name__)

PROMPT_DIR = (
    Path(__file__).resolve().parent.parent / "prompts" / "competitor-quality-assessment"
)


@runtime_checkable
class LlmGateway(Protocol):
    """Protocol for LLM API calls."""

    def complete(self, prompt: str) -> str:
        """Send prompt to LLM and return response text."""
        ...


@dataclass
class QualityAssessmentResult:
    """Result of quality assessment for a single page."""

    status: QualityAssessmentStatus
    profile: QualityProfile | None = None
    tokens_used: int = 0
    error: str | None = None


@dataclass
class BatchQualityResult:
    """Result of batch quality assessment."""

    results: list[QualityAssessmentResult] = field(default_factory=list)
    total_tokens: int = 0
    llm_calls_made: int = 0


class QualityAssessor:
    """LLM-based content quality assessor.

    Uses compressed page content to produce quality profiles
    with depth scores, topic lists, and E-E-A-T signal detection.
    """

    def __init__(
        self,
        llm: LlmGateway,
        *,
        batch_size: int = 5,
        max_retries: int = 2,
    ) -> None:
        """Initialise with LLM gateway.

        Args:
            llm: LLM gateway for quality assessment calls.
            batch_size: Pages per LLM batch call.
            max_retries: Max retries on LLM failure.
        """
        self._llm = llm
        self._batch_size = batch_size
        self._max_retries = max_retries
        self._prompt_template = self._load_prompt()

    def assess_single(self, compressed_text: str, url: str) -> QualityAssessmentResult:
        """Assess quality of a single page.

        Args:
            compressed_text: Compressed page content (from compress_for_llm).
            url: URL of the page (for context).

        Returns:
            QualityAssessmentResult with profile or error.
        """
        if not compressed_text.strip():
            return QualityAssessmentResult(
                status=QualityAssessmentStatus.SKIPPED,
                error="No content to assess",
            )

        prompt = self._build_prompt([{"url": url, "content": compressed_text}])

        for attempt in range(self._max_retries + 1):
            try:
                response = self._llm.complete(prompt)
                profiles = self._parse_response(response)
                if profiles:
                    return QualityAssessmentResult(
                        status=QualityAssessmentStatus.COMPLETED,
                        profile=profiles[0],
                        tokens_used=len(prompt.split()) + len(response.split()),
                    )
                return QualityAssessmentResult(
                    status=QualityAssessmentStatus.FAILED,
                    error="Failed to parse LLM response",
                )
            except Exception as exc:  # noqa: BLE001
                if attempt < self._max_retries:
                    logger.warning(
                        "LLM call failed (attempt %d/%d): %s",
                        attempt + 1,
                        self._max_retries,
                        exc,
                    )
                    continue
                return QualityAssessmentResult(
                    status=QualityAssessmentStatus.FAILED,
                    error=(
                        f"LLM unavailable after "
                        f"{self._max_retries + 1} attempts: {exc}"
                    ),
                )

        return QualityAssessmentResult(
            status=QualityAssessmentStatus.FAILED,
            error="Unexpected: exhausted retries",
        )

    def assess_batch(
        self,
        pages: list[dict[str, str]],
    ) -> BatchQualityResult:
        """Assess quality of multiple pages in batches.

        Args:
            pages: List of {"url": str, "content": str} dicts.

        Returns:
            BatchQualityResult with per-page results.
        """
        batch_result = BatchQualityResult()

        for i in range(0, len(pages), self._batch_size):
            batch = pages[i : i + self._batch_size]
            prompt = self._build_prompt(batch)
            batch_result.llm_calls_made += 1

            try:
                response = self._llm.complete(prompt)
                profiles = self._parse_response(response)
                tokens = len(prompt.split()) + len(response.split())
                batch_result.total_tokens += tokens

                for j, _page in enumerate(batch):
                    if j < len(profiles):
                        batch_result.results.append(
                            QualityAssessmentResult(
                                status=QualityAssessmentStatus.COMPLETED,
                                profile=profiles[j],
                                tokens_used=tokens // len(batch),
                            ),
                        )
                    else:
                        batch_result.results.append(
                            QualityAssessmentResult(
                                status=QualityAssessmentStatus.FAILED,
                                error="LLM returned fewer profiles than pages",
                            ),
                        )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Batch LLM call failed: %s", exc)
                for _ in batch:
                    batch_result.results.append(
                        QualityAssessmentResult(
                            status=QualityAssessmentStatus.FAILED,
                            error=f"LLM batch call failed: {exc}",
                        ),
                    )

        return batch_result

    def _build_prompt(self, pages: list[dict[str, str]]) -> str:
        """Build the quality assessment prompt.

        Args:
            pages: List of {"url": str, "content": str} dicts.

        Returns:
            Formatted prompt string.
        """
        page_sections = []
        for i, page in enumerate(pages, 1):
            page_sections.append(f"--- Page {i}: {page['url']} ---\n{page['content']}")

        pages_text = "\n\n".join(page_sections)
        return self._prompt_template.format(
            page_count=len(pages),
            pages=pages_text,
        )

    def _parse_response(self, response: str) -> list[QualityProfile]:
        """Parse LLM response into QualityProfile list.

        Expects JSON array or single JSON object.

        Args:
            response: Raw LLM response text.

        Returns:
            List of parsed QualityProfile objects.
        """
        # Try to extract JSON from the response
        text = response.strip()

        # Find JSON content (may be wrapped in markdown code blocks)
        if "```json" in text:
            start = text.index("```json") + 7
            end = text.index("```", start)
            text = text[start:end].strip()
        elif "```" in text:
            start = text.index("```") + 3
            end = text.index("```", start)
            text = text[start:end].strip()

        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM response as JSON: %s", text[:200])
            return []

        if isinstance(data, dict):
            data = data.get("profiles", [data])

        if not isinstance(data, list):
            return []

        profiles = []
        for item in data:
            try:
                profile = QualityProfile(
                    depth_score=item.get("depth_score", 3),
                    topics_covered=item.get("topics_covered", []),
                    has_original_data=item.get("has_original_data", False),
                    has_author_credentials=item.get("has_author_credentials", False),
                    eeat_signals=item.get("eeat_signals", []),
                    quality_rationale=item.get(
                        "quality_rationale", "No rationale provided"
                    ),
                )
                profiles.append(profile)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to parse quality profile: %s", exc)
                continue

        return profiles

    def _load_prompt(self) -> str:
        """Load the quality assessment prompt template.

        Returns:
            Prompt template string with {page_count} and {pages} placeholders.
        """
        prompt_file = PROMPT_DIR / "v1.txt"
        if prompt_file.exists():
            return prompt_file.read_text()

        # Fallback inline prompt if file not yet created
        return _DEFAULT_PROMPT


_DEFAULT_PROMPT = """You are a content quality assessor for SEO competitor analysis.

Assess the quality of {page_count} competitor page(s) below.
For each page, produce a JSON quality profile.

## Depth Score Rubric
1 = Surface: topic mentioned, no detail
2 = Introductory: definitions and overview only
3 = Solid: covers main subtopics, some practical content
4 = In-depth: comprehensive treatment, addresses edge cases
5 = Authoritative: original data, expert credentials, cited research

## E-E-A-T Signals to Detect
- "author_bio" — named author with credentials
- "medical_review" — reviewed by a medical professional
- "citations" — references to studies, research, or data sources
- "first_person_experience" — personal experience or case studies

## Output Format
Return ONLY valid JSON. For multiple pages, return a JSON array.
Each element must have exactly these fields:
{{
  "depth_score": <1-5 integer>,
  "topics_covered": [<list of main subtopics>],
  "has_original_data": <boolean>,
  "has_author_credentials": <boolean>,
  "eeat_signals": [<list of detected signals>],
  "quality_rationale": "<1-2 sentences explaining the score>"
}}

## Pages to Assess

{pages}"""
