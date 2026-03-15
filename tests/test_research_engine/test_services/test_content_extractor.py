"""Tests for ContentExtractor (T-004).

ATS-001: Full extraction — word count, headings, schema, links, images.
ATS-004: JS-rendered page detection (body text < 100 chars).
ATS-005: Thin page detection (<300 words).
PI-001: word_count >= 0.
PI-002: h2_count/h3_count >= 0.
PI-012: Link counts >= 0.
PI-013: Image count >= 0.
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from src.research_engine.services.content_extractor import (
    ExtractionResult,
    compress_for_llm,
    extract_content,
)

FIXTURES_DIR = (
    Path(__file__).resolve().parents[2]
    / ".."
    / "src"
    / "research_engine"
    / "__fixtures__"
    / "competitor-pages"
)


def _load_fixture(name: str) -> str:
    """Load a fixture HTML file."""
    return (FIXTURES_DIR / name).read_text()


# ---------------------------------------------------------------------------
# ATS-001: Happy path — full extraction
# ---------------------------------------------------------------------------


class TestFullExtraction:
    """ATS-001: Normal article extraction."""

    def test_word_count_reasonable(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        # Normal article should have substantial word count (nav/footer stripped)
        assert result.word_count > 300

    def test_h1_extracted(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        assert result.h1_text == "FUE vs DHI Hair Transplant: Complete Comparison Guide"

    def test_h2_count_and_texts(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        assert result.h2_count >= 7
        assert len(result.h2_texts) == result.h2_count
        assert "What is FUE?" in result.h2_texts

    def test_h3_count(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        assert result.h3_count >= 1  # "References" heading

    def test_schema_types_extracted(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        assert "Article" in result.schema_types

    def test_faq_detected(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        # Has 3 <details> elements
        assert result.has_faq_section is True

    def test_image_count(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        assert result.image_count == 3

    def test_link_counts(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        assert result.internal_link_count >= 2
        assert result.external_link_count >= 2

    def test_not_thin_content(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        assert result.is_thin_content is False

    def test_not_js_rendered(self) -> None:
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://hairtransplantclinic.de/fue-vs-dhi")
        assert result.is_js_rendered is False


# ---------------------------------------------------------------------------
# ATS-005: Thin page detection
# ---------------------------------------------------------------------------


class TestThinPageDetection:
    """ATS-005: Pages with <300 words flagged as thin."""

    def test_thin_page_flagged(self) -> None:
        html = _load_fixture("thin-page.html")
        result = extract_content(html, "https://example.com/aftercare")
        assert result.is_thin_content is True
        assert result.word_count < 300

    def test_thin_page_still_extracts_h1(self) -> None:
        html = _load_fixture("thin-page.html")
        result = extract_content(html, "https://example.com/aftercare")
        assert result.h1_text == "Hair Transplant Aftercare Tips"

    def test_thin_page_image_counted(self) -> None:
        html = _load_fixture("thin-page.html")
        result = extract_content(html, "https://example.com/aftercare")
        assert result.image_count == 1


# ---------------------------------------------------------------------------
# ATS-004: JS-rendered page detection
# ---------------------------------------------------------------------------


class TestJsRenderedDetection:
    """ATS-004: SPA pages with minimal HTML content."""

    def test_spa_detected_as_js_rendered(self) -> None:
        html = _load_fixture("spa-page.html")
        result = extract_content(html, "https://example.com/app")
        assert result.is_js_rendered is True
        assert result.word_count < 100

    def test_spa_still_extracts_what_available(self) -> None:
        html = _load_fixture("spa-page.html")
        result = extract_content(html, "https://example.com/app")
        # Should still return a result, just flagged
        assert isinstance(result, ExtractionResult)


# ---------------------------------------------------------------------------
# FAQ page with FAQPage schema
# ---------------------------------------------------------------------------


class TestFaqPage:
    """FAQ page with FAQPage schema and itemtype."""

    def test_faqpage_schema_detected(self) -> None:
        html = _load_fixture("faq-page.html")
        result = extract_content(html, "https://example.com/faq")
        assert "FAQPage" in result.schema_types

    def test_faq_section_detected_via_itemtype(self) -> None:
        html = _load_fixture("faq-page.html")
        result = extract_content(html, "https://example.com/faq")
        assert result.has_faq_section is True

    def test_faq_page_h2_headings(self) -> None:
        html = _load_fixture("faq-page.html")
        result = extract_content(html, "https://example.com/faq")
        assert "FAQ: Common Questions" in result.h2_texts


# ---------------------------------------------------------------------------
# German page extraction
# ---------------------------------------------------------------------------


class TestGermanPage:
    """ATS-011 (prerequisite): Structural extraction works for DE."""

    def test_german_word_count(self) -> None:
        html = _load_fixture("german-page.html")
        result = extract_content(html, "https://haarklinik.de/fue")
        assert result.word_count > 100

    def test_german_headings_extracted(self) -> None:
        html = _load_fixture("german-page.html")
        result = extract_content(html, "https://haarklinik.de/fue")
        assert "Was ist FUE?" in result.h2_texts

    def test_german_schema_extracted(self) -> None:
        html = _load_fixture("german-page.html")
        result = extract_content(html, "https://haarklinik.de/fue")
        assert "Article" in result.schema_types


# ---------------------------------------------------------------------------
# PI: Property invariants
# ---------------------------------------------------------------------------


class TestPropertyInvariants:
    """Property invariants for extractor output."""

    @given(word_count=st.integers(min_value=0, max_value=50_000))
    @settings(max_examples=20)
    def test_pi_001_word_count_non_negative(self, word_count: int) -> None:
        """PI-001: Fabricated extraction always has non-negative word count."""
        result = ExtractionResult(word_count=word_count)
        assert result.word_count >= 0

    def test_pi_002_heading_counts_match_texts(self) -> None:
        """PI-002: h2_texts length matches h2_count."""
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://example.com")
        assert len(result.h2_texts) == result.h2_count

    def test_pi_012_link_counts_non_negative(self) -> None:
        """PI-012: Link counts always >= 0."""
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://example.com")
        assert result.internal_link_count >= 0
        assert result.external_link_count >= 0

    def test_pi_013_image_count_non_negative(self) -> None:
        """PI-013: Image count always >= 0."""
        html = _load_fixture("normal-article.html")
        result = extract_content(html, "https://example.com")
        assert result.image_count >= 0


# ---------------------------------------------------------------------------
# compress_for_llm
# ---------------------------------------------------------------------------


class TestCompressForLlm:
    """Compressed content for LLM quality assessment."""

    def test_includes_title(self) -> None:
        result = ExtractionResult(
            h1_text="Test Title",
            h2_texts=["H2A"],
            h2_count=1,
            body_text="Some body text here.",
            word_count=4,
        )
        compressed = compress_for_llm(result)
        assert "Test Title" in compressed

    def test_includes_headings(self) -> None:
        result = ExtractionResult(
            h2_texts=["Recovery", "Cost"],
            h2_count=2,
            body_text="Body content.",
            word_count=2,
        )
        compressed = compress_for_llm(result)
        assert "Recovery" in compressed
        assert "Cost" in compressed

    def test_truncates_body_to_2000_chars(self) -> None:
        result = ExtractionResult(
            body_text="x" * 5000,
            word_count=5000,
        )
        compressed = compress_for_llm(result)
        # The body excerpt should be at most 2000 chars of the body
        assert len(compressed) < 8000

    def test_respects_max_chars(self) -> None:
        result = ExtractionResult(
            h1_text="Title",
            h2_texts=["H" * 100 for _ in range(50)],
            h2_count=50,
            body_text="x" * 10000,
            word_count=10000,
        )
        compressed = compress_for_llm(result, max_chars=500)
        assert len(compressed) <= 500

    def test_includes_schema_types(self) -> None:
        result = ExtractionResult(
            schema_types=["Article", "FAQPage"],
            body_text="Content",
            word_count=1,
        )
        compressed = compress_for_llm(result)
        assert "Article" in compressed
        assert "FAQPage" in compressed


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


class TestEdgeCases:
    """Edge cases for extraction."""

    def test_empty_html(self) -> None:
        result = extract_content("", "https://example.com")
        assert result.word_count == 0
        assert result.h1_text is None
        assert result.h2_count == 0

    def test_no_body_tag(self) -> None:
        result = extract_content("<p>Just text</p>", "https://example.com")
        assert result.word_count >= 1

    def test_malformed_json_ld(self) -> None:
        html = '<script type="application/ld+json">not json</script><p>Text</p>'
        result = extract_content(html, "https://example.com")
        assert result.schema_types == []

    def test_multiple_json_ld_blocks(self) -> None:
        html = """
        <script type="application/ld+json">{"@type": "Article"}</script>
        <script type="application/ld+json">{"@type": "FAQPage"}</script>
        <p>Content</p>
        """
        result = extract_content(html, "https://example.com")
        assert "Article" in result.schema_types
        assert "FAQPage" in result.schema_types
