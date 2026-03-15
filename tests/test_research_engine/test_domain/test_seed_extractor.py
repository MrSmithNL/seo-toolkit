"""Tests for seed keyword extraction from HTML.

TDD: Tests written BEFORE implementation.
Covers: T-004 (Seed Extractor portion)
"""

from __future__ import annotations

from pathlib import Path

from src.research_engine.domain.seed_extractor import SeedKeyword, extract_seeds

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_fixture(name: str) -> str:
    """Load a fixture file as string."""
    return (FIXTURES_DIR / name).read_text()


class TestExtractSeeds:
    """Tests for extract_seeds() function."""

    def test_extracts_from_title(self) -> None:
        """Extracts keywords from <title> tag."""
        html = _load_fixture("sample-page.html")
        seeds = extract_seeds(html, "https://example.com/cost")
        terms = [s.term for s in seeds]
        assert any("hair transplant cost" in t.lower() for t in terms)

    def test_extracts_from_meta_description(self) -> None:
        """Extracts keywords from <meta name='description'>."""
        html = _load_fixture("sample-page.html")
        seeds = extract_seeds(html, "https://example.com/cost")
        terms = [s.term for s in seeds]
        # Meta description mentions "hair transplant prices", "FUE clinics"
        assert any("hair transplant" in t.lower() for t in terms)

    def test_extracts_from_h1(self) -> None:
        """Extracts keywords from <h1> tags."""
        html = _load_fixture("sample-page.html")
        seeds = extract_seeds(html, "https://example.com/cost")
        elements = [s.source_element for s in seeds]
        assert "h1" in elements

    def test_extracts_from_h2(self) -> None:
        """Extracts keywords from <h2> tags."""
        html = _load_fixture("sample-page.html")
        seeds = extract_seeds(html, "https://example.com/cost")
        elements = [s.source_element for s in seeds]
        assert "h2" in elements

    def test_extracts_from_h3(self) -> None:
        """Extracts keywords from <h3> tags."""
        html = _load_fixture("sample-page.html")
        seeds = extract_seeds(html, "https://example.com/cost")
        elements = [s.source_element for s in seeds]
        assert "h3" in elements

    def test_extracts_from_breadcrumbs(self) -> None:
        """Extracts keywords from breadcrumb navigation."""
        html = _load_fixture("sample-page.html")
        seeds = extract_seeds(html, "https://example.com/cost")
        elements = [s.source_element for s in seeds]
        assert "breadcrumb" in elements

    def test_returns_seed_keyword_objects(self) -> None:
        """Each result is a SeedKeyword with term, source_url, source_element."""
        html = _load_fixture("sample-page.html")
        seeds = extract_seeds(html, "https://example.com/cost")
        assert len(seeds) > 0
        for seed in seeds:
            assert isinstance(seed, SeedKeyword)
            assert seed.term
            assert seed.source_url == "https://example.com/cost"
            assert seed.source_element

    def test_empty_html_returns_empty_list(self) -> None:
        """Empty HTML returns empty list (not an error)."""
        seeds = extract_seeds("", "https://example.com")
        assert seeds == []

    def test_html_without_relevant_tags(self) -> None:
        """HTML with no title/meta/headings returns empty list."""
        html = "<html><body><p>Just a paragraph</p></body></html>"
        seeds = extract_seeds(html, "https://example.com")
        assert seeds == []

    def test_deduplicates_extracted_seeds(self) -> None:
        """Same text appearing in multiple elements is not duplicated."""
        html = (
            "<html><head><title>Hair Transplant</title></head>"
            "<body><h1>Hair Transplant</h1></body></html>"
        )
        seeds = extract_seeds(html, "https://example.com")
        terms = [s.term.lower() for s in seeds]
        # The term appears in both title and h1, but should be deduped
        assert terms.count("hair transplant") == 1
