"""Tests for intent distribution query.

Covers:
- ATS-019: Filter by intent type returns correct count
- ATS-020: Filter by minimum confidence
- INT-002: F-003 output consumable by F-007
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from src.research_engine.models.keyword import Keyword, KeywordSource
from src.research_engine.queries.get_intent_distribution import (
    GetIntentDistributionQuery,
    get_intent_distribution,
)
from tests.test_research_engine.conftest import MockStorage

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")
CAMPAIGN = "camp_test001"


def _make_classified_keyword(
    term: str,
    intent: str,
    confidence: str = "high",
    fmt: str = "definition-explainer",
) -> Keyword:
    """Create a keyword with intent fields populated."""
    kw = Keyword(
        tenant_id=TENANT,
        campaign_id=CAMPAIGN,
        term=term,
        source=KeywordSource.MANUAL_SEED,
    )
    now = datetime.now(tz=UTC)
    object.__setattr__(kw, "intent", intent)
    object.__setattr__(kw, "intent_confidence", confidence)
    object.__setattr__(kw, "intent_rationale", f"Test rationale for {term}")
    object.__setattr__(kw, "recommended_format", fmt)
    object.__setattr__(kw, "classified_at", now)
    return kw


def _seed_storage() -> MockStorage:
    """Create storage with a realistic distribution of classified keywords."""
    storage = MockStorage()
    # 12 transactional
    for i in range(12):
        storage.keywords.append(
            _make_classified_keyword(
                f"buy product {i}", "transactional", "high", "product-landing-page"
            )
        )
    # 80 informational
    for i in range(80):
        conf = "high" if i < 60 else "medium"
        storage.keywords.append(
            _make_classified_keyword(
                f"what is topic {i}", "informational", conf, "definition-explainer"
            )
        )
    # 50 commercial
    for i in range(50):
        conf = "high" if i < 30 else "medium"
        storage.keywords.append(
            _make_classified_keyword(
                f"best product {i}", "commercial", conf, "listicle"
            )
        )
    # 8 navigational
    for i in range(8):
        storage.keywords.append(
            _make_classified_keyword(
                f"brand {i}", "navigational", "high", "brand-navigational-page"
            )
        )
    return storage


class TestIntentDistribution:
    """Core distribution query tests."""

    def test_total_count(self) -> None:
        """Total matches seeded data."""
        storage = _seed_storage()
        query = GetIntentDistributionQuery(campaign_id=CAMPAIGN)
        result = get_intent_distribution(query, storage)
        assert result.total == 150
        assert result.classified == 150
        assert result.unclassified == 0

    def test_intent_breakdown(self) -> None:
        """ATS-019: Filter by intent type returns correct count."""
        storage = _seed_storage()
        query = GetIntentDistributionQuery(campaign_id=CAMPAIGN)
        result = get_intent_distribution(query, storage)
        assert result.by_intent["transactional"] == 12
        assert result.by_intent["informational"] == 80
        assert result.by_intent["commercial"] == 50
        assert result.by_intent["navigational"] == 8

    def test_confidence_breakdown(self) -> None:
        """ATS-020: Confidence distribution is correct."""
        storage = _seed_storage()
        query = GetIntentDistributionQuery(campaign_id=CAMPAIGN)
        result = get_intent_distribution(query, storage)
        # 12 trans (high) + 60 info (high) + 30 comm (high) + 8 nav (high) = 110
        assert result.by_confidence["high"] == 110
        # 20 info (medium) + 20 comm (medium) = 40
        assert result.by_confidence["medium"] == 40

    def test_format_breakdown(self) -> None:
        """Format distribution is correct."""
        storage = _seed_storage()
        query = GetIntentDistributionQuery(campaign_id=CAMPAIGN)
        result = get_intent_distribution(query, storage)
        assert result.by_format["product-landing-page"] == 12
        assert result.by_format["definition-explainer"] == 80
        assert result.by_format["listicle"] == 50
        assert result.by_format["brand-navigational-page"] == 8

    def test_unclassified_counted(self) -> None:
        """Keywords without intent are counted as unclassified."""
        storage = MockStorage()
        storage.keywords.append(
            Keyword(
                tenant_id=TENANT,
                campaign_id=CAMPAIGN,
                term="unclassified keyword",
                source=KeywordSource.MANUAL_SEED,
            )
        )
        storage.keywords.append(
            _make_classified_keyword("classified keyword", "informational")
        )
        query = GetIntentDistributionQuery(campaign_id=CAMPAIGN)
        result = get_intent_distribution(query, storage)
        assert result.total == 2
        assert result.classified == 1
        assert result.unclassified == 1

    def test_empty_campaign(self) -> None:
        """Empty campaign returns zero counts."""
        storage = MockStorage()
        query = GetIntentDistributionQuery(campaign_id=CAMPAIGN)
        result = get_intent_distribution(query, storage)
        assert result.total == 0
        assert result.classified == 0
