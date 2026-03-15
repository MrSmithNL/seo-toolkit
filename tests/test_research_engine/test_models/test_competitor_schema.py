"""Schema validation tests for CompetitorSnapshot model (T-001).

Tests property invariants PI-001 through PI-013 and structural validation.
TDD: these tests are written BEFORE implementation is complete.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from src.research_engine.models.competitor import (
    CompetitorBenchmark,
    CompetitorSnapshot,
    CrawlStatus,
    QualityProfile,
)

TENANT_ID = uuid.UUID("12345678-1234-1234-1234-123456789abc")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_snapshot(**overrides: object) -> CompetitorSnapshot:
    """Create a valid CompetitorSnapshot with defaults."""
    defaults: dict = {
        "tenant_id": TENANT_ID,
        "keyword_id": "kw_abc123",
        "serp_snapshot_id": "ss_def456",
        "url": "https://example.com/page",
        "domain": "example.com",
        "serp_position": 3,
        "crawl_status": CrawlStatus.SUCCESS,
        "word_count": 2500,
        "h1_text": "Example Title",
        "h2_count": 5,
        "h3_count": 3,
        "h2_texts": ["Heading 1", "Heading 2", "Heading 3", "Heading 4", "Heading 5"],
        "schema_types": ["Article"],
        "has_faq_section": False,
        "internal_link_count": 10,
        "external_link_count": 5,
        "image_count": 3,
        "raw_html_hash": "d41d8cd98f00b204e9800998ecf8427e",
        "crawled_at": datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC),
    }
    defaults.update(overrides)
    return CompetitorSnapshot(**defaults)


# ---------------------------------------------------------------------------
# PI-001: Word count non-negative
# ---------------------------------------------------------------------------


class TestWordCountNonNegative:
    """PI-001: word_count is always >= 0."""

    def test_zero_word_count_valid(self) -> None:
        snap = _make_snapshot(word_count=0)
        assert snap.word_count == 0

    def test_positive_word_count_valid(self) -> None:
        snap = _make_snapshot(word_count=3200)
        assert snap.word_count == 3200

    def test_negative_word_count_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(word_count=-1)

    def test_none_word_count_allowed(self) -> None:
        snap = _make_snapshot(word_count=None)
        assert snap.word_count is None

    @given(wc=st.integers(min_value=0, max_value=100_000))
    @settings(max_examples=50)
    def test_property_word_count_non_negative(self, wc: int) -> None:
        snap = _make_snapshot(word_count=wc)
        assert snap.word_count >= 0


# ---------------------------------------------------------------------------
# PI-002: Heading counts non-negative
# ---------------------------------------------------------------------------


class TestHeadingCountsNonNegative:
    """PI-002: h2_count and h3_count are always >= 0."""

    def test_zero_heading_counts_valid(self) -> None:
        snap = _make_snapshot(h2_count=0, h3_count=0, h2_texts=[])
        assert snap.h2_count == 0
        assert snap.h3_count == 0

    def test_negative_h2_count_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(h2_count=-1)

    def test_negative_h3_count_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(h3_count=-1)

    @given(
        h2=st.integers(min_value=0, max_value=100),
        h3=st.integers(min_value=0, max_value=100),
    )
    @settings(max_examples=50)
    def test_property_heading_counts_non_negative(self, h2: int, h3: int) -> None:
        texts = [f"H{i}" for i in range(h2)]
        snap = _make_snapshot(h2_count=h2, h3_count=h3, h2_texts=texts)
        assert snap.h2_count >= 0
        assert snap.h3_count >= 0


# ---------------------------------------------------------------------------
# PI-003: Depth score range 1-5
# ---------------------------------------------------------------------------


class TestDepthScoreRange:
    """PI-003: depth_score is always 1-5 inclusive."""

    @pytest.mark.parametrize("score", [1, 2, 3, 4, 5])
    def test_valid_depth_scores(self, score: int) -> None:
        snap = _make_snapshot(depth_score=score)
        assert snap.depth_score == score

    def test_zero_depth_score_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(depth_score=0)

    def test_six_depth_score_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(depth_score=6)

    def test_null_depth_score_allowed(self) -> None:
        snap = _make_snapshot(depth_score=None)
        assert snap.depth_score is None

    @given(score=st.integers(min_value=1, max_value=5))
    @settings(max_examples=20)
    def test_property_depth_score_in_range(self, score: int) -> None:
        snap = _make_snapshot(depth_score=score)
        assert 1 <= snap.depth_score <= 5


# ---------------------------------------------------------------------------
# PI-004: Schema types valid
# ---------------------------------------------------------------------------


class TestSchemaTypesValid:
    """PI-004: schema_types is an array of strings (may be empty)."""

    def test_empty_schema_types(self) -> None:
        snap = _make_snapshot(schema_types=[])
        assert snap.schema_types == []

    def test_multiple_schema_types(self) -> None:
        snap = _make_snapshot(schema_types=["Article", "FAQPage"])
        assert snap.schema_types == ["Article", "FAQPage"]


# ---------------------------------------------------------------------------
# PI-005: Crawled_at present
# ---------------------------------------------------------------------------


class TestCrawledAtPresent:
    """PI-005: Every CompetitorSnapshot has a non-null crawled_at."""

    def test_crawled_at_set_automatically(self) -> None:
        snap = _make_snapshot()
        assert snap.crawled_at is not None
        assert snap.crawled_at.tzinfo is not None  # UTC-aware

    def test_crawled_at_accepts_explicit_value(self) -> None:
        ts = datetime(2026, 3, 15, 12, 0, 0, tzinfo=UTC)
        snap = _make_snapshot(crawled_at=ts)
        assert snap.crawled_at == ts


# ---------------------------------------------------------------------------
# PI-006: Tenant isolation
# ---------------------------------------------------------------------------


class TestTenantIsolation:
    """PI-006: Every CompetitorSnapshot has a non-null tenant_id."""

    def test_tenant_id_required(self) -> None:
        snap = _make_snapshot()
        assert snap.tenant_id is not None
        assert isinstance(snap.tenant_id, uuid.UUID)

    def test_tenant_id_is_uuid(self) -> None:
        snap = _make_snapshot(tenant_id=TENANT_ID)
        assert snap.tenant_id == TENANT_ID


# ---------------------------------------------------------------------------
# PI-007: Hash non-empty
# ---------------------------------------------------------------------------


class TestHashNonEmpty:
    """PI-007: raw_html_hash is always a non-empty string (MD5) when set."""

    def test_hash_is_valid_md5_string(self) -> None:
        snap = _make_snapshot(raw_html_hash="d41d8cd98f00b204e9800998ecf8427e")
        assert len(snap.raw_html_hash) == 32

    def test_hash_none_allowed_for_failed_crawl(self) -> None:
        snap = _make_snapshot(
            crawl_status=CrawlStatus.CRAWL_FAILED,
            raw_html_hash=None,
            word_count=None,
        )
        assert snap.raw_html_hash is None


# ---------------------------------------------------------------------------
# PI-008: LLM fields flagged
# ---------------------------------------------------------------------------


class TestLlmFieldsFlagged:
    """PI-008: All AI-assessed fields tagged in llm_assessed_fields."""

    def test_quality_profile_flags_all_fields(self) -> None:
        profile = QualityProfile(
            depth_score=3,
            topics_covered=["topic1"],
            quality_rationale="Test rationale",
        )
        expected_fields = [
            "depth_score",
            "topics_covered",
            "has_original_data",
            "has_author_credentials",
            "eeat_signals",
            "quality_rationale",
        ]
        assert profile.llm_assessed_fields == expected_fields


# ---------------------------------------------------------------------------
# PI-009: Snapshots append-only
# ---------------------------------------------------------------------------


class TestSnapshotsAppendOnly:
    """PI-009: Each snapshot gets a unique ID (append-only verification)."""

    def test_different_ids_generated(self) -> None:
        snap1 = _make_snapshot()
        snap2 = _make_snapshot()
        assert snap1.id != snap2.id

    def test_id_has_cs_prefix(self) -> None:
        snap = _make_snapshot()
        assert snap.id.startswith("cs_")


# ---------------------------------------------------------------------------
# PI-011: Rationale present when scored
# ---------------------------------------------------------------------------


class TestRationalePresentWhenScored:
    """PI-011: Every non-null depth_score has a non-empty quality_rationale."""

    def test_quality_profile_requires_rationale(self) -> None:
        with pytest.raises(ValueError):
            QualityProfile(
                depth_score=3,
                topics_covered=[],
                quality_rationale="",
            )


# ---------------------------------------------------------------------------
# PI-012: Link counts non-negative
# ---------------------------------------------------------------------------


class TestLinkCountsNonNegative:
    """PI-012: internal_link_count and external_link_count >= 0."""

    def test_zero_link_counts(self) -> None:
        snap = _make_snapshot(internal_link_count=0, external_link_count=0)
        assert snap.internal_link_count == 0
        assert snap.external_link_count == 0

    def test_negative_internal_link_count_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(internal_link_count=-1)

    def test_negative_external_link_count_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(external_link_count=-1)


# ---------------------------------------------------------------------------
# PI-013: Image count non-negative
# ---------------------------------------------------------------------------


class TestImageCountNonNegative:
    """PI-013: image_count is always >= 0."""

    def test_zero_image_count(self) -> None:
        snap = _make_snapshot(image_count=0)
        assert snap.image_count == 0

    def test_negative_image_count_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(image_count=-1)


# ---------------------------------------------------------------------------
# Serialisation / round-trip
# ---------------------------------------------------------------------------


class TestSerialisation:
    """Ensure model serialises and deserialises correctly."""

    def test_json_round_trip(self) -> None:
        snap = _make_snapshot()
        json_str = snap.model_dump_json()
        restored = CompetitorSnapshot.model_validate_json(json_str)
        assert restored.url == snap.url
        assert restored.word_count == snap.word_count
        assert restored.tenant_id == snap.tenant_id

    def test_dict_round_trip(self) -> None:
        snap = _make_snapshot()
        data = snap.model_dump(mode="json")
        restored = CompetitorSnapshot.model_validate(data)
        assert restored.id == snap.id


# ---------------------------------------------------------------------------
# CompetitorBenchmark
# ---------------------------------------------------------------------------


class TestCompetitorBenchmark:
    """Test the lightweight benchmark view."""

    def test_from_snapshot_fields(self) -> None:
        bench = CompetitorBenchmark(
            url="https://example.com/page",
            domain="example.com",
            serp_position=3,
            word_count=2500,
            depth_score=4,
            h2_texts=["H1", "H2"],
            schema_types=["Article"],
            has_faq_section=True,
            topics_covered=["topic1", "topic2"],
        )
        assert bench.url == "https://example.com/page"
        assert bench.depth_score == 4
        assert bench.has_faq_section is True

    def test_defaults_for_missing_data(self) -> None:
        bench = CompetitorBenchmark(
            url="https://example.com",
            domain="example.com",
            serp_position=1,
        )
        assert bench.word_count is None
        assert bench.depth_score is None
        assert bench.h2_texts == []
        assert bench.schema_types == []
        assert bench.topics_covered == []


# ---------------------------------------------------------------------------
# CrawlStatus enum
# ---------------------------------------------------------------------------


class TestCrawlStatus:
    """Test crawl status enum values."""

    def test_all_statuses_match_spec(self) -> None:
        assert CrawlStatus.SUCCESS == "success"
        assert CrawlStatus.CRAWL_FAILED == "crawl_failed"
        assert CrawlStatus.ROBOTS_BLOCKED == "robots_blocked"
        assert CrawlStatus.JS_RENDERED == "js_rendered"

    def test_crawl_failed_snapshot(self) -> None:
        snap = _make_snapshot(
            crawl_status=CrawlStatus.CRAWL_FAILED,
            http_status_code=404,
            word_count=None,
            h2_count=None,
            h3_count=None,
            h2_texts=[],
            raw_html_hash=None,
            internal_link_count=None,
            external_link_count=None,
            image_count=None,
        )
        assert snap.crawl_status == CrawlStatus.CRAWL_FAILED
        assert snap.word_count is None


# ---------------------------------------------------------------------------
# Serp position validation
# ---------------------------------------------------------------------------


class TestSerpPosition:
    """Serp position must be 1-10."""

    def test_position_1_valid(self) -> None:
        snap = _make_snapshot(serp_position=1)
        assert snap.serp_position == 1

    def test_position_10_valid(self) -> None:
        snap = _make_snapshot(serp_position=10)
        assert snap.serp_position == 10

    def test_position_0_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(serp_position=0)

    def test_position_11_rejected(self) -> None:
        with pytest.raises(ValueError):
            _make_snapshot(serp_position=11)
