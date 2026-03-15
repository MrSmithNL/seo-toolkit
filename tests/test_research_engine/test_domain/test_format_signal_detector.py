"""Tests for format signal detector.

Covers:
- ATS-009: "how to" signal → how-to-guide
- ATS-010: "vs" signal → comparison-article
- ATS-011: "best" signal → listicle
- ATS-012: "what is" signal → definition-explainer
- ATS-013: Location + transactional → location-page
- ATS-014: Generic commercial, no signal → category-page
- ATS-015: Format is structured enum, not free text
"""

from __future__ import annotations

from src.research_engine.domain.format_signal_detector import detect_format_signal
from src.research_engine.models.intent import ContentFormat, IntentType


class TestHowToSignal:
    """ATS-009: 'how to' signal → how-to-guide."""

    def test_how_to_prefix(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "how to care for hair after transplant", IntentType.INFORMATIONAL
        )
        assert result.format == ContentFormat.HOW_TO_GUIDE
        assert result.signal == "how to"

    def test_how_do_i_prefix(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "how do I prepare for hair transplant", IntentType.INFORMATIONAL
        )
        assert result.format == ContentFormat.HOW_TO_GUIDE
        assert result.signal == "how do i"

    def test_case_insensitive(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "How To Wash Hair After Surgery", IntentType.INFORMATIONAL
        )
        assert result.format == ContentFormat.HOW_TO_GUIDE


class TestVsSignal:
    """ATS-010: 'vs' signal → comparison-article."""

    def test_vs_in_keyword(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "FUE vs DHI hair transplant", IntentType.COMMERCIAL
        )
        assert result.format == ContentFormat.COMPARISON_ARTICLE
        assert result.signal == "vs"

    def test_versus_in_keyword(self) -> None:  # noqa: D102
        result = detect_format_signal("FUE versus DHI", IntentType.COMMERCIAL)
        assert result.format == ContentFormat.COMPARISON_ARTICLE
        assert result.signal == "versus"

    def test_compared_to(self) -> None:  # noqa: D102
        result = detect_format_signal("FUE compared to DHI", IntentType.COMMERCIAL)
        assert result.format == ContentFormat.COMPARISON_ARTICLE
        assert result.signal == "compared to"


class TestBestSignal:
    """ATS-011: 'best' signal → listicle."""

    def test_best_prefix(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "best hair transplant clinics", IntentType.COMMERCIAL
        )
        assert result.format == ContentFormat.LISTICLE
        assert result.signal == "best"

    def test_top_prefix(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "top 10 hair clinics Germany", IntentType.COMMERCIAL
        )
        assert result.format == ContentFormat.LISTICLE
        assert result.signal == "top"


class TestWhatIsSignal:
    """ATS-012: 'what is' signal → definition-explainer."""

    def test_what_is_prefix(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "what is alopecia areata", IntentType.INFORMATIONAL
        )
        assert result.format == ContentFormat.DEFINITION_EXPLAINER
        assert result.signal == "what is"

    def test_what_are_prefix(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "what are the causes of hair loss", IntentType.INFORMATIONAL
        )
        assert result.format == ContentFormat.DEFINITION_EXPLAINER
        assert result.signal == "what are"


class TestLocationSignal:
    """ATS-013: Location + transactional → location-page."""

    def test_near_me(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "hair transplant near me", IntentType.TRANSACTIONAL
        )
        assert result.format == ContentFormat.LOCATION_PAGE
        assert result.signal == "near me"

    def test_city_with_transactional(self) -> None:  # noqa: D102
        result = detect_format_signal(
            "hair transplant consultation Berlin", IntentType.TRANSACTIONAL
        )
        assert result.format == ContentFormat.LOCATION_PAGE
        assert result.signal is not None


class TestDefaultFormats:
    """ATS-014: Default format when no signal detected."""

    def test_generic_commercial_no_signal(self) -> None:
        """Generic commercial keyword defaults to category-page."""
        result = detect_format_signal("hair growth serum", IntentType.COMMERCIAL)
        assert result.format == ContentFormat.CATEGORY_PAGE
        assert result.signal is None

    def test_generic_informational_no_signal(self) -> None:
        """Generic informational keyword defaults to definition-explainer."""
        result = detect_format_signal("alopecia causes", IntentType.INFORMATIONAL)
        assert result.format == ContentFormat.DEFINITION_EXPLAINER
        assert result.signal is None

    def test_generic_transactional_no_signal(self) -> None:
        """Generic transactional keyword defaults to product-landing-page."""
        result = detect_format_signal("book consultation", IntentType.TRANSACTIONAL)
        assert result.format == ContentFormat.PRODUCT_LANDING_PAGE
        assert result.signal is None

    def test_navigational_defaults_to_brand_page(self) -> None:
        """Navigational keyword defaults to brand-navigational-page."""
        result = detect_format_signal("hairgenetix", IntentType.NAVIGATIONAL)
        assert result.format == ContentFormat.BRAND_NAVIGATIONAL_PAGE
        assert result.signal is None


class TestFormatIsEnum:
    """ATS-015: Format is structured enum, not free text."""

    def test_all_outputs_are_enum_values(self) -> None:
        """Every detection result uses ContentFormat enum values."""
        test_cases = [
            ("how to wash hair", IntentType.INFORMATIONAL),
            ("best clinics", IntentType.COMMERCIAL),
            ("FUE vs DHI", IntentType.COMMERCIAL),
            ("what is FUE", IntentType.INFORMATIONAL),
            ("clinic near me", IntentType.TRANSACTIONAL),
            ("hair serum", IntentType.COMMERCIAL),
            ("hairgenetix", IntentType.NAVIGATIONAL),
        ]
        valid_formats = set(ContentFormat)
        for keyword, intent in test_cases:
            result = detect_format_signal(keyword, intent)
            assert result.format in valid_formats, f"Failed for: {keyword}"
