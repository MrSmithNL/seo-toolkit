"""Tests for F-004 SerpFeatureDetector.

TDD: Tests for T-004 covering ATS-008 to ATS-013, PI-004, PI-005.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from src.research_engine.models.serp import SerpFeatures
from src.research_engine.services.serp_feature_detector import SerpFeatureDetector

# ---------------------------------------------------------------------------
# ATS-008: AI Overview detected
# ---------------------------------------------------------------------------


class TestAiOverviewDetection:
    """ATS-008: AI Overview detection and warning flag."""

    def test_ai_overview_detected(self) -> None:
        """AI Overview flag is normalized to True."""
        raw = {"ai_overview": True}
        features = SerpFeatureDetector.normalize(raw)
        assert features.ai_overview is True

    def test_ai_overview_not_detected(self) -> None:
        """AI Overview flag defaults to False when absent."""
        raw = {}
        features = SerpFeatureDetector.normalize(raw)
        assert features.ai_overview is False

    def test_ai_overview_warning_flag(self) -> None:
        """AI Overview warning is generated when detected."""
        features = SerpFeatures(ai_overview=True)
        warnings = SerpFeatureDetector.get_warnings(features)
        assert "ai_overview_detected" in warnings

    def test_no_warning_when_no_ai_overview(self) -> None:
        """No AI Overview warning when not detected."""
        features = SerpFeatures(ai_overview=False)
        warnings = SerpFeatureDetector.get_warnings(features)
        assert "ai_overview_detected" not in warnings


# ---------------------------------------------------------------------------
# ATS-009: Featured snippet detected
# ---------------------------------------------------------------------------


class TestFeaturedSnippetDetection:
    """ATS-009: Featured snippet detection."""

    def test_featured_snippet_detected(self) -> None:
        """Featured snippet flag is normalized."""
        raw = {"featured_snippet": True}
        features = SerpFeatureDetector.normalize(raw)
        assert features.featured_snippet is True


# ---------------------------------------------------------------------------
# ATS-010: PAA extraction (up to 5 questions)
# ---------------------------------------------------------------------------


class TestPaaExtraction:
    """ATS-010: People Also Ask extraction."""

    def test_paa_questions_extracted(self) -> None:
        """PAA questions are extracted as strings."""
        raw = {
            "people_also_ask": True,
            "paa_questions": ["Q1", "Q2", "Q3"],
        }
        features = SerpFeatureDetector.normalize(raw)
        assert features.people_also_ask is True
        assert features.paa_questions == ["Q1", "Q2", "Q3"]

    def test_paa_truncated_to_5(self) -> None:
        """PAA questions are truncated to 5 max."""
        raw = {
            "people_also_ask": True,
            "paa_questions": [f"Q{i}" for i in range(8)],
        }
        features = SerpFeatureDetector.normalize(raw)
        assert len(features.paa_questions) == 5

    def test_paa_empty_when_not_present(self) -> None:
        """PAA questions are empty when not present."""
        raw = {}
        features = SerpFeatureDetector.normalize(raw)
        assert features.paa_questions == []


# ---------------------------------------------------------------------------
# ATS-011: Local pack detected
# ---------------------------------------------------------------------------


class TestLocalPackDetection:
    """ATS-011: Local pack detection."""

    def test_local_pack_detected(self) -> None:
        """Local pack flag is normalized."""
        raw = {"local_pack": True}
        features = SerpFeatureDetector.normalize(raw)
        assert features.local_pack is True


# ---------------------------------------------------------------------------
# ATS-012: Image pack and video carousel
# ---------------------------------------------------------------------------


class TestImageVideoDetection:
    """ATS-012: Image pack and video carousel detection."""

    def test_image_pack_detected(self) -> None:
        """Image pack flag is normalized."""
        raw = {"image_pack": True}
        features = SerpFeatureDetector.normalize(raw)
        assert features.image_pack is True

    def test_video_carousel_detected(self) -> None:
        """Video carousel flag is normalized."""
        raw = {"video_carousel": True}
        features = SerpFeatureDetector.normalize(raw)
        assert features.video_carousel is True


# ---------------------------------------------------------------------------
# ATS-013: Purely organic SERP — all flags false
# ---------------------------------------------------------------------------


class TestPurelyOrganicSerp:
    """ATS-013: No SERP features detected."""

    def test_all_flags_false(self) -> None:
        """All feature flags are False when no features present."""
        raw = {}
        features = SerpFeatureDetector.normalize(raw)
        assert features.ai_overview is False
        assert features.featured_snippet is False
        assert features.people_also_ask is False
        assert features.knowledge_panel is False
        assert features.image_pack is False
        assert features.video_carousel is False
        assert features.local_pack is False
        assert features.shopping_results is False
        assert features.paa_questions == []


# ---------------------------------------------------------------------------
# PI-004: All feature fields are boolean (property test)
# ---------------------------------------------------------------------------


class TestFeatureFlagProperties:
    """PI-004: Property-based tests for feature flag invariants."""

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
    def test_normalize_always_returns_booleans(
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
        """Property: normalize always returns boolean feature flags."""
        raw = {
            "ai_overview": ai_overview,
            "featured_snippet": featured_snippet,
            "people_also_ask": people_also_ask,
            "knowledge_panel": knowledge_panel,
            "image_pack": image_pack,
            "video_carousel": video_carousel,
            "local_pack": local_pack,
            "shopping_results": shopping_results,
        }
        features = SerpFeatureDetector.normalize(raw)
        assert isinstance(features.ai_overview, bool)
        assert isinstance(features.featured_snippet, bool)
        assert isinstance(features.people_also_ask, bool)
        assert isinstance(features.knowledge_panel, bool)
        assert isinstance(features.image_pack, bool)
        assert isinstance(features.video_carousel, bool)
        assert isinstance(features.local_pack, bool)
        assert isinstance(features.shopping_results, bool)


# ---------------------------------------------------------------------------
# DataForSEO response format normalization
# ---------------------------------------------------------------------------


class TestDataForSeoNormalization:
    """DataForSEO-specific feature mapping."""

    def test_dataforseo_feature_format(self) -> None:
        """DataForSEO uses different key names in items."""
        raw = {
            "ai_overview": True,
            "featured_snippet": True,
            "people_also_ask": True,
            "knowledge_panel": False,
            "image_pack": True,
            "video_carousel": False,
            "local_pack": True,
            "shopping_results": False,
            "paa_questions": ["Q1", "Q2"],
        }
        features = SerpFeatureDetector.normalize(raw)
        assert features.ai_overview is True
        assert features.featured_snippet is True
        assert features.people_also_ask is True
        assert features.knowledge_panel is False
        assert features.image_pack is True
        assert features.video_carousel is False
        assert features.local_pack is True
        assert features.shopping_results is False
        assert features.paa_questions == ["Q1", "Q2"]

    def test_truthy_values_normalized_to_bool(self) -> None:
        """Non-boolean truthy values are coerced to bool."""
        raw = {
            "ai_overview": 1,
            "featured_snippet": "yes",
        }
        features = SerpFeatureDetector.normalize(raw)
        assert features.ai_overview is True
        assert features.featured_snippet is True

    def test_falsy_values_normalized_to_bool(self) -> None:
        """Non-boolean falsy values are coerced to bool."""
        raw = {
            "ai_overview": 0,
            "featured_snippet": "",
            "local_pack": None,
        }
        features = SerpFeatureDetector.normalize(raw)
        assert features.ai_overview is False
        assert features.featured_snippet is False
        assert features.local_pack is False
