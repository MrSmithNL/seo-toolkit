"""Tests for keyword models, enums, and validation rules.

TDD: These tests are written BEFORE the implementation.
Covers: T-001 (Keyword Schema & Models)
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from src.research_engine.models.keyword import (
    DifficultySource,
    GapStatus,
    Keyword,
    KeywordGap,
    KeywordIntent,
    KeywordMetric,
    KeywordSource,
)

# ---------------------------------------------------------------------------
# Strategies for property-based tests
# ---------------------------------------------------------------------------

SUPPORTED_LOCALES = ["de", "fr", "nl", "es", "it", "pt", "pl", "tr", "en"]
SUPPORTED_COUNTRIES = ["DE", "FR", "NL", "ES", "IT", "PT", "PL", "TR", "US", "GB"]


def _make_keyword(**overrides: object) -> Keyword:
    """Helper to create a valid Keyword with sensible defaults."""
    defaults: dict = {
        "tenant_id": uuid.uuid4(),
        "campaign_id": "camp_test",
        "term": "hair transplant",
        "source": KeywordSource.URL_EXTRACTION,
    }
    defaults.update(overrides)
    return Keyword(**defaults)


def _make_metric(**overrides: object) -> KeywordMetric:
    """Helper to create a valid KeywordMetric with sensible defaults."""
    defaults: dict = {
        "keyword_id": "kw_test",
        "tenant_id": uuid.uuid4(),
        "locale": "en",
        "country": "US",
        "volume": 1000,
        "cpc": 2.50,
        "trend": [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210],
        "data_source": "keywords_everywhere",
        "fetched_at": datetime.now(tz=UTC),
    }
    defaults.update(overrides)
    return KeywordMetric(**defaults)


# ===========================================================================
# Enum Tests
# ===========================================================================


class TestKeywordSourceEnum:
    """Tests for KeywordSource enum values."""

    def test_has_four_values(self) -> None:
        """KeywordSource must have exactly 4 values."""
        assert len(KeywordSource) == 4
        assert KeywordSource.URL_EXTRACTION == "url_extraction"
        assert KeywordSource.AUTOCOMPLETE == "autocomplete"
        assert KeywordSource.MANUAL_SEED == "manual_seed"
        assert KeywordSource.GAP_ANALYSIS == "gap_analysis"

    def test_string_representation(self) -> None:
        """Enum values are strings usable in serialisation."""
        assert KeywordSource.URL_EXTRACTION.value == "url_extraction"
        assert isinstance(KeywordSource.URL_EXTRACTION, str)


class TestGapStatusEnum:
    """Tests for GapStatus enum values."""

    def test_has_three_values(self) -> None:
        """GapStatus must have exactly 3 values."""
        assert len(GapStatus) == 3
        assert GapStatus.OWN_KEYWORD == "own_keyword"
        assert GapStatus.COMPETITOR_GAP == "competitor_gap"
        assert GapStatus.NEW_OPPORTUNITY == "new_opportunity"


class TestDifficultySourceEnum:
    """Tests for DifficultySource enum values."""

    def test_has_two_values(self) -> None:
        """DifficultySource must have exactly 2 values."""
        assert len(DifficultySource) == 2
        assert DifficultySource.HEURISTIC == "heuristic"
        assert DifficultySource.DATAFOR_SEO == "datafor_seo"


class TestKeywordIntentEnum:
    """Tests for KeywordIntent enum values."""

    def test_has_four_values(self) -> None:
        """KeywordIntent must have exactly 4 values."""
        assert len(KeywordIntent) == 4
        assert KeywordIntent.INFORMATIONAL == "informational"
        assert KeywordIntent.COMMERCIAL == "commercial"
        assert KeywordIntent.TRANSACTIONAL == "transactional"
        assert KeywordIntent.NAVIGATIONAL == "navigational"


# ===========================================================================
# Keyword Model Tests
# ===========================================================================


class TestKeywordModel:
    """Tests for the Keyword Pydantic model."""

    def test_creates_valid_keyword(self) -> None:
        """PI-001: Valid keyword with required fields succeeds."""
        kw = _make_keyword()
        assert kw.term == "hair transplant"
        assert kw.source == KeywordSource.URL_EXTRACTION
        assert kw.gap_status == GapStatus.NEW_OPPORTUNITY
        assert kw.id.startswith("kw_")

    def test_auto_generates_id(self) -> None:
        """Keyword id is auto-generated with kw_ prefix."""
        kw1 = _make_keyword()
        kw2 = _make_keyword()
        assert kw1.id.startswith("kw_")
        assert kw1.id != kw2.id

    def test_auto_generates_normalized_key(self) -> None:
        """Normalized key is computed from term (lowercase, sorted tokens)."""
        kw = _make_keyword(term="Cost Of Hair Transplant")
        assert kw.normalized_key == "cost hair of transplant"

    def test_rejects_empty_term(self) -> None:
        """PI-001: Empty term must be rejected."""
        with pytest.raises(ValidationError) as exc_info:
            _make_keyword(term="")
        assert "term" in str(exc_info.value)

    def test_rejects_whitespace_only_term(self) -> None:
        """Whitespace-only term must be rejected after stripping."""
        with pytest.raises(ValidationError):
            _make_keyword(term="   ")

    def test_tenant_id_required(self) -> None:
        """PI-008: tenant_id must not be null."""
        with pytest.raises(ValidationError):
            Keyword(
                campaign_id="camp_1",
                term="test",
                source=KeywordSource.URL_EXTRACTION,
                tenant_id=None,  # type: ignore[arg-type]
            )

    def test_difficulty_in_range(self) -> None:
        """PI-004: Difficulty must be 0-100 when set."""
        kw = _make_keyword(difficulty=50, difficulty_source=DifficultySource.HEURISTIC)
        assert kw.difficulty == 50
        assert kw.difficulty_source == DifficultySource.HEURISTIC

    def test_difficulty_rejects_negative(self) -> None:
        """PI-004: Difficulty below 0 must be rejected."""
        with pytest.raises(ValidationError):
            _make_keyword(difficulty=-1)

    def test_difficulty_rejects_over_100(self) -> None:
        """PI-004: Difficulty above 100 must be rejected."""
        with pytest.raises(ValidationError):
            _make_keyword(difficulty=101)

    def test_difficulty_none_is_valid(self) -> None:
        """Difficulty can be None (not yet estimated)."""
        kw = _make_keyword(difficulty=None)
        assert kw.difficulty is None

    def test_default_gap_status(self) -> None:
        """Default gap_status is new_opportunity."""
        kw = _make_keyword()
        assert kw.gap_status == GapStatus.NEW_OPPORTUNITY

    def test_timestamps_auto_set(self) -> None:
        """Timestamps are auto-populated."""
        kw = _make_keyword()
        assert isinstance(kw.created_at, datetime)
        assert isinstance(kw.updated_at, datetime)
        assert isinstance(kw.discovered_at, datetime)

    def test_intent_fields_default_none(self) -> None:
        """Intent fields are None until F-003 populates them."""
        kw = _make_keyword()
        assert kw.intent is None
        assert kw.intent_confidence is None
        assert kw.classified_at is None

    def test_cluster_id_default_none(self) -> None:
        """Cluster id is None until F-002 populates it."""
        kw = _make_keyword()
        assert kw.cluster_id is None

    @given(
        term=st.text(min_size=1, max_size=200).filter(lambda s: s.strip()),
    )
    @settings(max_examples=50)
    def test_property_non_empty_term_always_accepted(self, term: str) -> None:
        """PI-001 property: any non-empty stripped string is a valid term."""
        kw = _make_keyword(term=term)
        assert len(kw.term) > 0

    @given(
        difficulty=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=50)
    def test_property_difficulty_range(self, difficulty: int) -> None:
        """PI-004 property: difficulty in [0,100] always accepted."""
        kw = _make_keyword(
            difficulty=difficulty, difficulty_source=DifficultySource.HEURISTIC
        )
        assert 0 <= kw.difficulty <= 100  # type: ignore[operator]


class TestKeywordDedupDetection:
    """PI-009: Detect duplicate keywords by campaign_id + normalized_key."""

    def test_same_normalized_key_detected(self) -> None:
        """Two keywords with same campaign + normalized_key are duplicates."""
        kw1 = _make_keyword(term="hair transplant cost")
        kw2 = _make_keyword(term="cost hair transplant")
        assert kw1.normalized_key == kw2.normalized_key
        assert kw1.campaign_id == kw2.campaign_id

    def test_different_campaigns_not_duplicate(self) -> None:
        """Same term in different campaigns are NOT duplicates."""
        kw1 = _make_keyword(term="hair transplant", campaign_id="camp_1")
        kw2 = _make_keyword(term="hair transplant", campaign_id="camp_2")
        assert kw1.normalized_key == kw2.normalized_key
        assert kw1.campaign_id != kw2.campaign_id

    def test_case_insensitive_dedup(self) -> None:
        """'Hair Transplant' and 'hair transplant' produce same key."""
        kw1 = _make_keyword(term="Hair Transplant")
        kw2 = _make_keyword(term="hair transplant")
        assert kw1.normalized_key == kw2.normalized_key


# ===========================================================================
# KeywordMetric Model Tests
# ===========================================================================


class TestKeywordMetricModel:
    """Tests for the KeywordMetric Pydantic model."""

    def test_creates_valid_metric(self) -> None:
        """Valid metric with all fields succeeds."""
        m = _make_metric()
        assert m.volume == 1000
        assert m.cpc == 2.50
        assert m.id.startswith("km_")
        assert len(m.trend) == 12

    def test_auto_generates_id(self) -> None:
        """Metric id is auto-generated with km_ prefix."""
        m = _make_metric()
        assert m.id.startswith("km_")

    def test_volume_non_negative(self) -> None:
        """PI-003: Volume must be >= 0."""
        m = _make_metric(volume=0)
        assert m.volume == 0

    def test_volume_rejects_negative(self) -> None:
        """PI-003: Negative volume must be rejected."""
        with pytest.raises(ValidationError):
            _make_metric(volume=-1)

    def test_volume_none_is_valid(self) -> None:
        """Volume can be None (not yet fetched)."""
        m = _make_metric(volume=None)
        assert m.volume is None

    def test_cpc_non_negative(self) -> None:
        """PI-012: CPC must be >= 0."""
        m = _make_metric(cpc=0.0)
        assert m.cpc == 0.0

    def test_cpc_rejects_negative(self) -> None:
        """PI-012: Negative CPC must be rejected."""
        with pytest.raises(ValidationError):
            _make_metric(cpc=-0.50)

    def test_trend_must_have_12_elements(self) -> None:
        """PI-005: Trend array must have exactly 12 elements."""
        m = _make_metric()
        assert len(m.trend) == 12

    def test_trend_rejects_wrong_length(self) -> None:
        """PI-005: Trend with != 12 elements must be rejected."""
        with pytest.raises(ValidationError):
            _make_metric(trend=[100, 200, 300])

    def test_trend_rejects_empty(self) -> None:
        """PI-005: Empty trend must be rejected."""
        with pytest.raises(ValidationError):
            _make_metric(trend=[])

    def test_locale_validated(self) -> None:
        """PI-002: Locale must be from supported set."""
        m = _make_metric(locale="de")
        assert m.locale == "de"

    def test_locale_rejects_unsupported(self) -> None:
        """PI-002: Unsupported locale must be rejected."""
        with pytest.raises(ValidationError):
            _make_metric(locale="xx")

    def test_country_validated(self) -> None:
        """Country must be from supported set."""
        m = _make_metric(country="DE")
        assert m.country == "DE"

    def test_tenant_id_required(self) -> None:
        """PI-008: tenant_id must not be null."""
        with pytest.raises(ValidationError):
            _make_metric(tenant_id=None)

    @given(volume=st.integers(min_value=0, max_value=10_000_000))
    @settings(max_examples=50)
    def test_property_volume_non_negative(self, volume: int) -> None:
        """PI-003 property: any non-negative volume accepted."""
        m = _make_metric(volume=volume)
        assert m.volume >= 0


# ===========================================================================
# KeywordGap Model Tests
# ===========================================================================


class TestKeywordGapModel:
    """Tests for the KeywordGap Pydantic model."""

    def test_creates_valid_gap(self) -> None:
        """Valid gap record with required fields succeeds."""
        gap = KeywordGap(
            tenant_id=uuid.uuid4(),
            campaign_id="camp_1",
            keyword_id="kw_test",
            competitor_domain="competitor.com",
        )
        assert gap.id.startswith("kg_")
        assert gap.competitor_domain == "competitor.com"
        assert gap.competitor_position is None
        assert gap.our_position is None

    def test_positions_positive_when_set(self) -> None:
        """Positions must be >= 1 when set."""
        gap = KeywordGap(
            tenant_id=uuid.uuid4(),
            campaign_id="camp_1",
            keyword_id="kw_test",
            competitor_domain="competitor.com",
            competitor_position=3,
            our_position=15,
        )
        assert gap.competitor_position == 3
        assert gap.our_position == 15

    def test_position_rejects_zero(self) -> None:
        """Position 0 is invalid (SERP positions start at 1)."""
        with pytest.raises(ValidationError):
            KeywordGap(
                tenant_id=uuid.uuid4(),
                campaign_id="camp_1",
                keyword_id="kw_test",
                competitor_domain="competitor.com",
                competitor_position=0,
            )

    def test_position_rejects_negative(self) -> None:
        """Negative position must be rejected."""
        with pytest.raises(ValidationError):
            KeywordGap(
                tenant_id=uuid.uuid4(),
                campaign_id="camp_1",
                keyword_id="kw_test",
                competitor_domain="competitor.com",
                our_position=-1,
            )

    def test_competitor_domain_required(self) -> None:
        """Competitor domain must not be empty."""
        with pytest.raises(ValidationError):
            KeywordGap(
                tenant_id=uuid.uuid4(),
                campaign_id="camp_1",
                keyword_id="kw_test",
                competitor_domain="",
            )

    def test_tenant_id_required(self) -> None:
        """PI-008: tenant_id must not be null."""
        with pytest.raises(ValidationError):
            KeywordGap(
                tenant_id=None,  # type: ignore[arg-type]
                campaign_id="camp_1",
                keyword_id="kw_test",
                competitor_domain="competitor.com",
            )
