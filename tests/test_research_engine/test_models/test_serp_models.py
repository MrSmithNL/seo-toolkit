"""Tests for F-004 SERP models (SerpSnapshot, SerpResult, SerpFeatures).

TDD: Tests written first per spec requirements.md and tests.md.
Covers PI-001 to PI-012 property invariants and ATS-015 schema validation.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from src.research_engine.models.serp import (
    ApiSource,
    ContentType,
    SerpFeatures,
    SerpResult,
    SerpSnapshot,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _make_result(*, position: int = 1, **overrides: object) -> SerpResult:
    """Create a valid SerpResult with sensible defaults."""
    defaults: dict = {
        "id": f"sr_{uuid.uuid4().hex[:12]}",
        "tenant_id": TENANT_ID,
        "snapshot_id": "ss_abc123",
        "position": position,
        "url": f"https://example.com/page-{position}",
        "domain": "example.com",
        "title": f"Page {position} title",
        "content_type": ContentType.BLOG,
    }
    defaults.update(overrides)
    return SerpResult(**defaults)


def _make_snapshot(**overrides: object) -> SerpSnapshot:
    """Create a valid SerpSnapshot with sensible defaults."""
    defaults: dict = {
        "tenant_id": TENANT_ID,
        "keyword_id": "kw_abc123",
        "keyword_text": "FUE hair transplant",
        "language": "de",
        "country": "DE",
        "api_source": ApiSource.DATAFORSEO,
        "result_count": 10,
    }
    defaults.update(overrides)
    return SerpSnapshot(**defaults)


# ---------------------------------------------------------------------------
# PI-001: Position range — every organic result position is 1-10
# ---------------------------------------------------------------------------


class TestPositionRange:
    """PI-001: Position range validation."""

    def test_valid_positions(self) -> None:
        """Positions 1-10 are accepted."""
        for pos in range(1, 11):
            result = _make_result(position=pos)
            assert result.position == pos

    def test_position_zero_rejected(self) -> None:
        """Position 0 is rejected."""
        with pytest.raises(ValidationError, match="greater than or equal to 1"):
            _make_result(position=0)

    def test_position_11_rejected(self) -> None:
        """Position 11 is rejected."""
        with pytest.raises(ValidationError, match="less than or equal to 10"):
            _make_result(position=11)

    def test_negative_position_rejected(self) -> None:
        """Negative positions are rejected."""
        with pytest.raises(ValidationError):
            _make_result(position=-1)

    @given(pos=st.integers(min_value=1, max_value=10))
    @settings(max_examples=20)
    def test_any_valid_position_accepted(self, pos: int) -> None:
        """Property: any position 1-10 produces a valid result."""
        result = _make_result(position=pos)
        assert 1 <= result.position <= 10


# ---------------------------------------------------------------------------
# PI-002: URL non-empty
# ---------------------------------------------------------------------------


class TestUrlNonEmpty:
    """PI-002: Every organic result has a non-empty URL."""

    def test_empty_url_rejected(self) -> None:
        """Empty string URL is rejected."""
        with pytest.raises(ValidationError, match="too_short"):
            _make_result(url="")

    def test_whitespace_url_stripped_and_rejected(self) -> None:
        """Whitespace-only URL is rejected."""
        with pytest.raises(ValidationError):
            _make_result(url="   ")

    def test_valid_url_accepted(self) -> None:
        """Non-empty URL is accepted."""
        result = _make_result(url="https://example.com/page")
        assert result.url == "https://example.com/page"


# ---------------------------------------------------------------------------
# PI-003: Content type valid enum
# ---------------------------------------------------------------------------


class TestContentType:
    """PI-003: content_type must be a valid enum value."""

    @pytest.mark.parametrize(
        "ct",
        [
            ContentType.BLOG,
            ContentType.PRODUCT_PAGE,
            ContentType.CATEGORY_PAGE,
            ContentType.VIDEO,
            ContentType.TOOL,
            ContentType.NEWS,
            ContentType.OTHER,
        ],
    )
    def test_valid_content_types(self, ct: ContentType) -> None:
        """All defined content types are accepted."""
        result = _make_result(content_type=ct)
        assert result.content_type == ct

    def test_invalid_content_type_rejected(self) -> None:
        """Invalid content type is rejected."""
        with pytest.raises(ValidationError):
            _make_result(content_type="podcast")  # type: ignore[arg-type]

    def test_none_content_type_defaults_to_other(self) -> None:
        """None content type defaults to OTHER."""
        result = _make_result(content_type=None)
        assert result.content_type is None


# ---------------------------------------------------------------------------
# PI-004: Feature flags boolean
# ---------------------------------------------------------------------------


class TestFeatureFlagsBoolean:
    """PI-004: All SERP feature flags are boolean."""

    def test_default_features_all_false(self) -> None:
        """Default SerpFeatures has all flags as False."""
        features = SerpFeatures()
        assert features.ai_overview is False
        assert features.featured_snippet is False
        assert features.people_also_ask is False
        assert features.knowledge_panel is False
        assert features.image_pack is False
        assert features.video_carousel is False
        assert features.local_pack is False
        assert features.shopping_results is False

    def test_all_features_true(self) -> None:
        """All flags can be set to True."""
        features = SerpFeatures(
            ai_overview=True,
            featured_snippet=True,
            people_also_ask=True,
            knowledge_panel=True,
            image_pack=True,
            video_carousel=True,
            local_pack=True,
            shopping_results=True,
            paa_questions=["Q1", "Q2"],
        )
        assert features.ai_overview is True
        assert features.featured_snippet is True

    @given(
        ai_overview=st.booleans(),
        featured_snippet=st.booleans(),
        people_also_ask=st.booleans(),
        knowledge_panel=st.booleans(),
        image_pack=st.booleans(),
        video_carousel=st.booleans(),
        local_pack=st.booleans(),
        shopping_results=st.booleans(),
    )
    @settings(max_examples=20)
    def test_feature_flags_always_boolean(
        self,
        ai_overview: bool,
        featured_snippet: bool,
        people_also_ask: bool,
        knowledge_panel: bool,
        image_pack: bool,
        video_carousel: bool,
        local_pack: bool,
        shopping_results: bool,
    ) -> None:
        """Property: all feature flags are always boolean."""
        features = SerpFeatures(
            ai_overview=ai_overview,
            featured_snippet=featured_snippet,
            people_also_ask=people_also_ask,
            knowledge_panel=knowledge_panel,
            image_pack=image_pack,
            video_carousel=video_carousel,
            local_pack=local_pack,
            shopping_results=shopping_results,
        )
        assert isinstance(features.ai_overview, bool)
        assert isinstance(features.featured_snippet, bool)
        assert isinstance(features.people_also_ask, bool)
        assert isinstance(features.knowledge_panel, bool)
        assert isinstance(features.image_pack, bool)
        assert isinstance(features.video_carousel, bool)
        assert isinstance(features.local_pack, bool)
        assert isinstance(features.shopping_results, bool)


# ---------------------------------------------------------------------------
# PI-005: PAA array limit (0-5 elements)
# ---------------------------------------------------------------------------


class TestPaaArrayLimit:
    """PI-005: PAA questions array has 0-5 elements."""

    def test_empty_paa(self) -> None:
        """Empty PAA array is valid."""
        features = SerpFeatures(paa_questions=[])
        assert features.paa_questions == []

    def test_five_questions_accepted(self) -> None:
        """Exactly 5 PAA questions are accepted."""
        questions = [f"Question {i}" for i in range(5)]
        features = SerpFeatures(paa_questions=questions)
        assert len(features.paa_questions) == 5

    def test_six_questions_rejected(self) -> None:
        """More than 5 PAA questions are rejected."""
        questions = [f"Question {i}" for i in range(6)]
        with pytest.raises(ValidationError, match="too_long"):
            SerpFeatures(paa_questions=questions)

    @given(n=st.integers(min_value=0, max_value=5))
    @settings(max_examples=10)
    def test_any_valid_paa_count(self, n: int) -> None:
        """Property: 0-5 PAA questions always valid."""
        questions = [f"Q{i}" for i in range(n)]
        features = SerpFeatures(paa_questions=questions)
        assert 0 <= len(features.paa_questions) <= 5


# ---------------------------------------------------------------------------
# PI-006: Timestamp present
# ---------------------------------------------------------------------------


class TestTimestampPresent:
    """PI-006: Every SerpSnapshot has a non-null fetched_at timestamp."""

    def test_fetched_at_auto_generated(self) -> None:
        """fetched_at is auto-populated if not provided."""
        snapshot = _make_snapshot()
        assert snapshot.fetched_at is not None
        assert isinstance(snapshot.fetched_at, datetime)
        assert snapshot.fetched_at.tzinfo is not None  # timezone-aware

    def test_explicit_fetched_at_preserved(self) -> None:
        """Explicit fetched_at is preserved."""
        ts = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
        snapshot = _make_snapshot(fetched_at=ts)
        assert snapshot.fetched_at == ts


# ---------------------------------------------------------------------------
# PI-007: Tenant isolation
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    """PI-007: Every SerpSnapshot has a non-null tenant_id."""

    def test_tenant_id_required(self) -> None:
        """tenant_id is required on SerpSnapshot."""
        with pytest.raises(ValidationError):
            SerpSnapshot(
                keyword_id="kw_abc",
                keyword_text="test",
                language="de",
                country="DE",
                api_source=ApiSource.DATAFORSEO,
                result_count=0,
            )

    def test_tenant_id_on_result(self) -> None:
        """tenant_id is required on SerpResult."""
        with pytest.raises(ValidationError):
            SerpResult(
                snapshot_id="ss_abc",
                position=1,
                url="https://example.com",
                domain="example.com",
            )


# ---------------------------------------------------------------------------
# PI-008: API source valid
# ---------------------------------------------------------------------------


class TestApiSource:
    """PI-008: api_source must be a valid enum value."""

    @pytest.mark.parametrize(
        "source",
        [ApiSource.DATAFORSEO, ApiSource.GOOGLE_SCRAPE, ApiSource.MOCK],
    )
    def test_valid_sources(self, source: ApiSource) -> None:
        """Valid API sources are accepted."""
        snapshot = _make_snapshot(api_source=source)
        assert snapshot.api_source == source

    def test_invalid_source_rejected(self) -> None:
        """Invalid API source is rejected."""
        with pytest.raises(ValidationError):
            _make_snapshot(api_source="bing")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# PI-010: Result count matches
# ---------------------------------------------------------------------------


class TestResultCountMatches:
    """PI-010: result_count equals length of organic_results array."""

    def test_result_count_zero_for_no_results(self) -> None:
        """result_count=0 with no_organic_results flag."""
        snapshot = _make_snapshot(result_count=0, no_organic_results=True)
        assert snapshot.result_count == 0
        assert snapshot.no_organic_results is True

    def test_result_count_ten(self) -> None:
        """result_count=10 for standard SERP."""
        snapshot = _make_snapshot(result_count=10)
        assert snapshot.result_count == 10


# ---------------------------------------------------------------------------
# PI-012: Word count non-negative
# ---------------------------------------------------------------------------


class TestWordCountNonNegative:
    """PI-012: estimated_word_count is always >= 0."""

    def test_positive_word_count(self) -> None:
        """Positive word count accepted."""
        result = _make_result(estimated_word_count=1500)
        assert result.estimated_word_count == 1500

    def test_zero_word_count(self) -> None:
        """Zero word count accepted."""
        result = _make_result(estimated_word_count=0)
        assert result.estimated_word_count == 0

    def test_negative_word_count_rejected(self) -> None:
        """Negative word count rejected."""
        with pytest.raises(ValidationError, match="greater than or equal to 0"):
            _make_result(estimated_word_count=-1)

    def test_none_word_count_accepted(self) -> None:
        """None word count (unknown) accepted."""
        result = _make_result(estimated_word_count=None)
        assert result.estimated_word_count is None


# ---------------------------------------------------------------------------
# ATS-015: Snapshot created with all required fields
# ---------------------------------------------------------------------------


class TestSnapshotCreation:
    """ATS-015: SerpSnapshot created with all required fields."""

    def test_full_snapshot_creation(self) -> None:
        """Snapshot with all fields creates successfully."""
        features = SerpFeatures(
            ai_overview=True,
            featured_snippet=True,
            people_also_ask=True,
            paa_questions=["How long does FUE take?", "Is FUE permanent?"],
        )
        snapshot = SerpSnapshot(
            tenant_id=TENANT_ID,
            keyword_id="kw_abc123",
            keyword_text="FUE hair transplant",
            language="de",
            country="DE",
            api_source=ApiSource.DATAFORSEO,
            result_count=10,
            serp_features=features,
            pipeline_run_id="run_xyz789",
            cost_estimate_usd="0.0006",
        )
        assert snapshot.id.startswith("ss_")
        assert snapshot.tenant_id == TENANT_ID
        assert snapshot.keyword_text == "FUE hair transplant"
        assert snapshot.language == "de"
        assert snapshot.country == "DE"
        assert snapshot.api_source == ApiSource.DATAFORSEO
        assert snapshot.result_count == 10
        assert snapshot.serp_features.ai_overview is True
        assert len(snapshot.serp_features.paa_questions) == 2
        assert snapshot.fetched_at is not None
        assert snapshot.created_at is not None

    def test_snapshot_id_prefix(self) -> None:
        """Snapshot ID always starts with 'ss_'."""
        snapshot = _make_snapshot()
        assert snapshot.id.startswith("ss_")

    def test_result_id_prefix(self) -> None:
        """Result ID always starts with 'sr_'."""
        result = _make_result()
        assert result.id.startswith("sr_")

    def test_snapshot_serialization_roundtrip(self) -> None:
        """Snapshot can be serialized and deserialized."""
        snapshot = _make_snapshot(
            serp_features=SerpFeatures(ai_overview=True, paa_questions=["Q1"]),
        )
        data = snapshot.model_dump(mode="json")
        restored = SerpSnapshot.model_validate(data)
        assert restored.id == snapshot.id
        assert restored.serp_features.ai_overview is True
        assert restored.serp_features.paa_questions == ["Q1"]


# ---------------------------------------------------------------------------
# Locale / Country validation
# ---------------------------------------------------------------------------


class TestLocaleCountryValidation:
    """Locale and country validation on SerpSnapshot."""

    def test_supported_locale(self) -> None:
        """Supported locale is accepted."""
        snapshot = _make_snapshot(language="en", country="US")
        assert snapshot.language == "en"

    def test_unsupported_locale_rejected(self) -> None:
        """Unsupported locale is rejected."""
        with pytest.raises(ValidationError, match="Unsupported locale"):
            _make_snapshot(language="xx")

    def test_unsupported_country_rejected(self) -> None:
        """Unsupported country is rejected."""
        with pytest.raises(ValidationError, match="Unsupported country"):
            _make_snapshot(country="XX")
