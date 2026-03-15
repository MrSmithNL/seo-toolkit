"""Pipeline orchestrator for F-003 Search Intent Classification.

Orchestrates: load keywords -> filter unclassified -> chunk -> build prompt
-> call LLM -> parse response -> validate -> write intent fields -> emit event.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from src.research_engine.config import ResearchConfig
from src.research_engine.domain.intent_prompt_builder import build_intent_prompt
from src.research_engine.domain.intent_response_parser import parse_intent_response
from src.research_engine.events.intent_events import (
    IntentClassificationCompletedEvent,
    emit_intent_event,
)
from src.research_engine.models.keyword import Keyword
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.ports.llm_gateway import LlmGateway
from src.research_engine.ports.storage import KeywordStoragePort

logger = logging.getLogger(__name__)


@dataclass
class ClassifyKeywordIntentCommand:
    """Input for the intent classification pipeline.

    Attributes:
        tenant_id: Tenant identifier.
        campaign_id: Campaign identifier.
        locale: Classify keywords for this locale.
        reclassify: Re-run even if already classified.
    """

    tenant_id: uuid.UUID
    campaign_id: str
    locale: str = "en"
    reclassify: bool = False


@dataclass
class ClassifyKeywordIntentResult:
    """Output from the intent classification pipeline.

    Attributes:
        run_id: Unique pipeline run identifier.
        keywords_classified: Number of keywords classified.
        skipped: Already classified and reclassify=false.
        failed: LLM failures, marked as unclassified.
        intent_distribution: Count per intent type.
        confidence_distribution: Count per confidence level.
        format_distribution: Count per content format.
        llm_tokens_used: Estimated total tokens consumed.
        duration_ms: Pipeline duration in milliseconds.
    """

    run_id: str
    keywords_classified: int
    skipped: int
    failed: int
    intent_distribution: dict[str, int]
    confidence_distribution: dict[str, int]
    format_distribution: dict[str, int]
    llm_tokens_used: int
    duration_ms: int


def _chunk_list(items: list, chunk_size: int) -> list[list]:
    """Split a list into chunks of specified size."""
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def classify_keyword_intent(  # noqa: C901
    cmd: ClassifyKeywordIntentCommand,
    config: ResearchConfig,
    storage: KeywordStoragePort,
    llm: LlmGateway,
) -> Result[ClassifyKeywordIntentResult, str]:
    """Execute the F-003 intent classification pipeline.

    Steps:
    1. Feature flag check
    2. Load keywords from storage
    3. Filter to unclassified (unless reclassify=True)
    4. Chunk into batches
    5. For each chunk: build prompt, call LLM, parse response
    6. Write intent fields to keyword records
    7. Emit completion event

    Args:
        cmd: Pipeline command with parameters.
        config: Research engine configuration.
        storage: Keyword storage adapter.
        llm: LLM gateway for classification.

    Returns:
        Ok(result) on success, Err(message) on failure.
    """
    start_time = time.monotonic()
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    # Step 1: Feature flag
    if not config.feature_intent_classification:
        return Err("Feature flag FEATURE_INTENT_CLASSIFICATION is disabled")

    # Step 2: Load keywords
    logger.info("Step 2: Loading keywords for %s/%s", cmd.campaign_id, cmd.locale)
    all_keywords = storage.get_by_campaign(cmd.campaign_id)
    if not all_keywords:
        return Err("No keywords found for intent classification")

    # Step 3: Filter unclassified (unless reclassify)
    if cmd.reclassify:
        to_classify = all_keywords
        skipped = 0
    else:
        to_classify = [kw for kw in all_keywords if kw.classified_at is None]
        skipped = len(all_keywords) - len(to_classify)

    if not to_classify:
        duration_ms = int((time.monotonic() - start_time) * 1000)
        return Ok(
            ClassifyKeywordIntentResult(
                run_id=run_id,
                keywords_classified=0,
                skipped=skipped,
                failed=0,
                intent_distribution={},
                confidence_distribution={},
                format_distribution={},
                llm_tokens_used=0,
                duration_ms=duration_ms,
            )
        )

    logger.info(
        "Loaded %d keywords (%d to classify, %d skipped)",
        len(all_keywords),
        len(to_classify),
        skipped,
    )

    # Build term-to-keyword mapping
    term_to_keyword: dict[str, Keyword] = {kw.term.lower(): kw for kw in to_classify}
    terms = [kw.term for kw in to_classify]

    # Step 4: Chunk
    chunk_size = config.intent_chunk_size
    chunks = _chunk_list(terms, chunk_size)
    logger.info("Split into %d chunk(s) of max %d", len(chunks), chunk_size)

    # Step 5: Process chunks
    classified_count = 0
    failed_count = 0
    intent_dist: dict[str, int] = {}
    confidence_dist: dict[str, int] = {}
    format_dist: dict[str, int] = {}
    estimated_tokens = 0

    for i, chunk in enumerate(chunks):
        prompt = build_intent_prompt(chunk)
        logger.info("Chunk %d: calling LLM with %d keywords", i + 1, len(chunk))

        # Estimate tokens
        estimated_tokens += len(prompt.split()) + len(chunk) * 40

        # LLM call with retry
        raw_response = None
        for attempt in range(config.intent_max_retries + 1):
            try:
                raw_response = llm.complete(prompt)
                break
            except Exception:  # noqa: BLE001
                if attempt < config.intent_max_retries:
                    logger.warning(
                        "LLM call failed (attempt %d), retrying", attempt + 1
                    )
                else:
                    logger.error(
                        "LLM call failed after %d retries",
                        config.intent_max_retries + 1,
                    )

        if raw_response is None:
            logger.warning(
                "LLM unavailable — marking %d keywords as unclassified", len(chunk)
            )
            failed_count += len(chunk)
            continue

        # Parse and validate
        parsed = parse_intent_response(raw_response, chunk)
        if isinstance(parsed, Err):
            logger.warning("Parse failed: %s — retrying once", parsed.error)
            # Retry the LLM call
            try:
                raw_response = llm.complete(prompt)
                parsed = parse_intent_response(raw_response, chunk)
            except Exception:  # noqa: BLE001
                logger.warning("LLM retry also failed")

            if isinstance(parsed, Err):
                logger.warning(
                    "Parse failed after retry: %s — marking chunk as unclassified",
                    parsed.error,
                )
                failed_count += len(chunk)
                continue

        # Step 6: Write intent fields
        now = datetime.now(tz=UTC)
        for cls in parsed.value.classifications:
            kw = term_to_keyword.get(cls.keyword.lower())
            if kw is None:
                continue

            storage.update_intent_fields(
                keyword_id=kw.id,
                intent=cls.intent,
                intent_confidence=cls.confidence,
                intent_rationale=cls.rationale,
                recommended_format=cls.recommended_format,
                format_signal=cls.format_signal,
                classified_at=now,
            )
            classified_count += 1

            # Update distributions
            intent_dist[cls.intent] = intent_dist.get(cls.intent, 0) + 1
            confidence_dist[cls.confidence] = confidence_dist.get(cls.confidence, 0) + 1
            format_dist[cls.recommended_format] = (
                format_dist.get(cls.recommended_format, 0) + 1
            )

    # Step 7: Emit event
    duration_ms = int((time.monotonic() - start_time) * 1000)

    if classified_count > 0:
        event = IntentClassificationCompletedEvent(
            tenant_id=cmd.tenant_id,
            campaign_id=cmd.campaign_id,
            run_id=run_id,
            locale=cmd.locale,
            keywords_classified=classified_count,
            intent_distribution=intent_dist,
        )
        emit_intent_event(event)

    logger.info(
        "Intent classification complete: %d classified, %d skipped, %d failed in %dms",
        classified_count,
        skipped,
        failed_count,
        duration_ms,
    )

    return Ok(
        ClassifyKeywordIntentResult(
            run_id=run_id,
            keywords_classified=classified_count,
            skipped=skipped,
            failed=failed_count,
            intent_distribution=intent_dist,
            confidence_distribution=confidence_dist,
            format_distribution=format_dist,
            llm_tokens_used=estimated_tokens,
            duration_ms=duration_ms,
        )
    )
