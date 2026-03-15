"""Tests for keyword cluster models.

TDD: Tests written BEFORE implementation.
Covers: F-002 T-001 (Cluster Model)
"""

from __future__ import annotations

import uuid

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from src.research_engine.models.cluster import KeywordCluster


def _make_cluster(**overrides: object) -> KeywordCluster:
    """Helper to create a valid KeywordCluster with defaults."""
    defaults: dict[str, object] = {
        "tenant_id": uuid.uuid4(),
        "campaign_id": "camp_1",
        "locale": "en",
        "name": "Hair Transplant Procedures",
        "rationale": "Keywords related to hair transplant types and methods.",
    }
    defaults.update(overrides)
    return KeywordCluster(**defaults)  # type: ignore[arg-type]


class TestKeywordClusterCreation:
    """Tests for basic model creation."""

    def test_creates_valid_cluster(self) -> None:
        """Valid inputs create a cluster with correct fields."""
        cluster = _make_cluster()
        assert cluster.name == "Hair Transplant Procedures"
        assert cluster.campaign_id == "camp_1"
        assert cluster.locale == "en"
        assert cluster.rationale is not None

    def test_auto_generates_id(self) -> None:
        """ID is auto-generated with tc_ prefix."""
        cluster = _make_cluster()
        assert cluster.id.startswith("tc_")
        assert len(cluster.id) == 15  # tc_ + 12 hex chars

    def test_two_clusters_have_unique_ids(self) -> None:
        """Each cluster gets a unique ID."""
        c1 = _make_cluster()
        c2 = _make_cluster()
        assert c1.id != c2.id

    def test_timestamps_set_automatically(self) -> None:
        """created_at and updated_at are set on creation."""
        cluster = _make_cluster()
        assert cluster.created_at is not None
        assert cluster.updated_at is not None

    def test_deleted_at_defaults_to_none(self) -> None:
        """Soft-delete field defaults to None (not deleted)."""
        cluster = _make_cluster()
        assert cluster.deleted_at is None

    def test_pillar_fields_default_to_none(self) -> None:
        """Pillar fields default to None before selection."""
        cluster = _make_cluster()
        assert cluster.pillar_keyword_id is None
        assert cluster.pillar_rationale is None

    def test_prompt_version_default(self) -> None:
        """Default prompt version is clustering-v1."""
        cluster = _make_cluster()
        assert cluster.prompt_version == "clustering-v1"


class TestKeywordClusterValidation:
    """Tests for field validation."""

    def test_name_required_non_empty(self) -> None:
        """Empty name is rejected."""
        with pytest.raises(ValidationError):
            _make_cluster(name="")

    def test_coherence_score_valid_range(self) -> None:
        """Score within 1-10 is accepted."""
        cluster = _make_cluster(coherence_score=8)
        assert cluster.coherence_score == 8

    def test_coherence_score_rejects_zero(self) -> None:
        """Score of 0 is rejected (min is 1)."""
        with pytest.raises(ValidationError):
            _make_cluster(coherence_score=0)

    def test_coherence_score_rejects_eleven(self) -> None:
        """Score of 11 is rejected (max is 10)."""
        with pytest.raises(ValidationError):
            _make_cluster(coherence_score=11)

    def test_coherence_score_none_is_valid(self) -> None:
        """None coherence score is valid (pre-scoring)."""
        cluster = _make_cluster(coherence_score=None)
        assert cluster.coherence_score is None

    def test_locale_validated(self) -> None:
        """Supported locales are accepted."""
        cluster = _make_cluster(locale="de")
        assert cluster.locale == "de"

    def test_locale_rejects_unsupported(self) -> None:
        """Unsupported locales are rejected."""
        with pytest.raises(ValidationError):
            _make_cluster(locale="xx")

    def test_tenant_id_required(self) -> None:
        """tenant_id is mandatory."""
        with pytest.raises(ValidationError):
            KeywordCluster(
                campaign_id="camp_1",
                locale="en",
                name="Test",
                rationale="Test rationale",
            )

    def test_keyword_count_defaults_to_zero(self) -> None:
        """keyword_count defaults to 0."""
        cluster = _make_cluster()
        assert cluster.keyword_count == 0


class TestKeywordClusterHypothesis:
    """Property-based tests for cluster model."""

    @given(score=st.integers(min_value=1, max_value=10))
    def test_valid_coherence_score_range(self, score: int) -> None:
        """Any integer 1-10 is a valid coherence score."""
        cluster = _make_cluster(coherence_score=score)
        assert 1 <= cluster.coherence_score <= 10

    @given(name=st.text(min_size=1, max_size=100).filter(lambda x: x.strip()))
    def test_non_empty_names_accepted(self, name: str) -> None:
        """Any non-empty string is a valid cluster name."""
        cluster = _make_cluster(name=name)
        assert len(cluster.name) > 0
