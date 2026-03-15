"""Read query for intent classification distribution.

Thin query layer over keyword storage. Aggregates intent, confidence,
and format distributions for a campaign's classified keywords.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from src.research_engine.ports.storage import KeywordStoragePort


@dataclass
class GetIntentDistributionQuery:
    """Query for intent distribution by campaign.

    Attributes:
        campaign_id: Campaign to query.
    """

    campaign_id: str


@dataclass
class IntentDistributionResult:
    """Aggregated intent distribution for a campaign.

    Attributes:
        total: Total keyword count.
        classified: Keywords with intent classification.
        unclassified: Keywords without intent classification.
        by_intent: Count per intent type.
        by_confidence: Count per confidence level.
        by_format: Count per recommended format.
    """

    total: int = 0
    classified: int = 0
    unclassified: int = 0
    by_intent: dict[str, int] = field(default_factory=dict)
    by_confidence: dict[str, int] = field(default_factory=dict)
    by_format: dict[str, int] = field(default_factory=dict)


def get_intent_distribution(
    query: GetIntentDistributionQuery,
    storage: KeywordStoragePort,
) -> IntentDistributionResult:
    """Aggregate intent distribution for a campaign.

    Args:
        query: Query parameters.
        storage: Keyword storage adapter.

    Returns:
        IntentDistributionResult with counts and breakdowns.
    """
    keywords = storage.get_by_campaign(query.campaign_id)

    if not keywords:
        return IntentDistributionResult()

    intent_counter: Counter[str] = Counter()
    confidence_counter: Counter[str] = Counter()
    format_counter: Counter[str] = Counter()
    classified = 0

    for kw in keywords:
        if kw.intent is not None:
            classified += 1
            intent_counter[kw.intent] += 1
            if kw.intent_confidence is not None:
                confidence_counter[kw.intent_confidence] += 1
            if kw.recommended_format is not None:
                format_counter[kw.recommended_format] += 1

    return IntentDistributionResult(
        total=len(keywords),
        classified=classified,
        unclassified=len(keywords) - classified,
        by_intent=dict(intent_counter),
        by_confidence=dict(confidence_counter),
        by_format=dict(format_counter),
    )
