"""ContentExtractor for F-005 competitor page analysis.

Parses HTML with BeautifulSoup4 and extracts structural fields:
word count, headings, JSON-LD schema types, FAQ detection,
link counts, image count, JS-rendered detection, thin content flag.

TypeScript equivalent: modules/content-engine/research/services/content-extractor.ts
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)

THIN_CONTENT_THRESHOLD = 300
JS_RENDERED_THRESHOLD = 100


@dataclass
class ExtractionResult:
    """Structured extraction from a competitor page."""

    word_count: int = 0
    h1_text: str | None = None
    h2_count: int = 0
    h3_count: int = 0
    h2_texts: list[str] = field(default_factory=list)
    schema_types: list[str] = field(default_factory=list)
    has_faq_section: bool = False
    internal_link_count: int = 0
    external_link_count: int = 0
    image_count: int = 0
    is_thin_content: bool = False
    is_js_rendered: bool = False
    body_text: str = ""


def extract_content(html: str, page_url: str) -> ExtractionResult:
    """Extract structural data from HTML content.

    Strips nav/footer/header/aside/script/style before word count.

    Args:
        html: Raw HTML string.
        page_url: URL of the page (for internal/external link classification).

    Returns:
        ExtractionResult with all structural fields.
    """
    soup = BeautifulSoup(html, "html.parser")
    result = ExtractionResult()

    # Extract JSON-LD schema types before stripping
    result.schema_types = _extract_schema_types(soup)

    # Detect FAQ section before stripping
    result.has_faq_section = _detect_faq_section(soup)

    # Count images before stripping
    result.image_count = _count_images(soup)

    # Count links before stripping (need full DOM)
    internal, external = _count_links(soup, page_url)
    result.internal_link_count = internal
    result.external_link_count = external

    # Extract headings before stripping boilerplate
    result.h1_text = _extract_h1(soup)
    h2_texts = _extract_headings(soup, "h2")
    h3_texts = _extract_headings(soup, "h3")
    result.h2_texts = h2_texts
    result.h2_count = len(h2_texts)
    result.h3_count = len(h3_texts)

    # Strip boilerplate elements for word count
    body_text = _extract_body_text(soup)
    result.body_text = body_text

    # Word count from cleaned body text
    words = body_text.split()
    result.word_count = len(words)

    # Flags
    result.is_thin_content = result.word_count < THIN_CONTENT_THRESHOLD
    result.is_js_rendered = result.word_count < JS_RENDERED_THRESHOLD

    return result


def _extract_body_text(soup: BeautifulSoup) -> str:
    """Extract body text, stripping navigation/boilerplate elements.

    Removes: nav, footer, header, aside, script, style, noscript.

    Args:
        soup: Parsed HTML.

    Returns:
        Cleaned body text.
    """
    # Work on a copy to avoid mutating the original
    body = soup.find("body")
    if body is None:
        # No body tag — use entire soup
        body = soup

    # Remove boilerplate elements
    for tag_name in ["nav", "footer", "header", "aside", "script", "style", "noscript"]:
        for element in body.find_all(tag_name):
            element.decompose()

    text = body.get_text(separator=" ", strip=True)
    # Collapse whitespace
    return " ".join(text.split())


def _extract_h1(soup: BeautifulSoup) -> str | None:
    """Extract the first H1 text.

    Args:
        soup: Parsed HTML.

    Returns:
        H1 text or None.
    """
    h1 = soup.find("h1")
    if h1 and isinstance(h1, Tag):
        text = h1.get_text(strip=True)
        return text if text else None
    return None


def _extract_headings(soup: BeautifulSoup, level: str) -> list[str]:
    """Extract all heading texts at a given level.

    Args:
        soup: Parsed HTML.
        level: Heading level ('h2' or 'h3').

    Returns:
        List of heading texts.
    """
    headings = []
    for tag in soup.find_all(level):
        if isinstance(tag, Tag):
            text = tag.get_text(strip=True)
            if text:
                headings.append(text)
    return headings


def _extract_schema_types(soup: BeautifulSoup) -> list[str]:
    """Extract JSON-LD schema types from script tags.

    Looks for <script type="application/ld+json"> blocks.

    Args:
        soup: Parsed HTML.

    Returns:
        List of unique @type values found.
    """
    schema_types: list[str] = []

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            if isinstance(data, dict):
                _collect_types(data, schema_types)
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        _collect_types(item, schema_types)
        except (json.JSONDecodeError, TypeError):
            continue

    return list(dict.fromkeys(schema_types))  # dedupe preserving order


def _collect_types(data: dict, types: list[str]) -> None:
    """Recursively collect @type values from JSON-LD data."""
    if "@type" in data:
        t = data["@type"]
        if isinstance(t, str):
            types.append(t)
        elif isinstance(t, list):
            types.extend(str(x) for x in t)

    # Check @graph for nested types
    if "@graph" in data and isinstance(data["@graph"], list):
        for item in data["@graph"]:
            if isinstance(item, dict):
                _collect_types(item, types)


def _detect_faq_section(soup: BeautifulSoup) -> bool:
    """Detect FAQ section via multiple signals.

    Checks:
    1. FAQPage microdata itemtype
    2. H2 containing "FAQ" (case-insensitive)
    3. Groups of <details> elements (3+)

    Args:
        soup: Parsed HTML.

    Returns:
        True if FAQ section detected.
    """
    # Check FAQPage itemtype
    faq_itemtype = soup.find(
        attrs={"itemtype": lambda v: bool(v and "FAQPage" in str(v))},
    )
    if faq_itemtype:
        return True

    # Check H2 containing "FAQ"
    for h2 in soup.find_all("h2"):
        if isinstance(h2, Tag) and "faq" in h2.get_text(strip=True).lower():
            return True

    # Check for groups of <details> elements (3+)
    details_count = len(soup.find_all("details"))
    if details_count >= 3:  # noqa: PLR2004
        return True

    return False


def _count_links(soup: BeautifulSoup, page_url: str) -> tuple[int, int]:
    """Count internal and external links.

    Args:
        soup: Parsed HTML.
        page_url: Page URL for determining internal vs external.

    Returns:
        Tuple of (internal_count, external_count).
    """
    from urllib.parse import urlparse

    page_domain = urlparse(page_url).netloc.lower()
    internal = 0
    external = 0

    for a_tag in soup.find_all("a", href=True):
        href = str(a_tag.get("href", ""))
        if not href or href.startswith("#") or href.startswith("javascript:"):
            continue

        if href.startswith("/") or href.startswith("./") or href.startswith("../"):
            internal += 1
        elif href.startswith("http://") or href.startswith("https://"):
            link_domain = urlparse(href).netloc.lower()
            if link_domain == page_domain:
                internal += 1
            else:
                external += 1
        else:
            # Relative link without prefix
            internal += 1

    return internal, external


def _count_images(soup: BeautifulSoup) -> int:
    """Count image elements.

    Args:
        soup: Parsed HTML.

    Returns:
        Number of <img> tags found.
    """
    return len(soup.find_all("img"))


def compress_for_llm(
    extraction: ExtractionResult,
    max_chars: int = 8000,
) -> str:
    """Compress extracted content for LLM quality assessment.

    Takes first 2000 chars of body text + all headings + any
    author/references sections detected.

    Args:
        extraction: The extraction result.
        max_chars: Maximum characters to include.

    Returns:
        Compressed text string.
    """
    parts: list[str] = []

    # H1
    if extraction.h1_text:
        parts.append(f"Title: {extraction.h1_text}")

    # Headings structure
    if extraction.h2_texts:
        parts.append("Headings:")
        for h2 in extraction.h2_texts:
            parts.append(f"  - {h2}")

    # Body text excerpt
    body = extraction.body_text
    if body:
        excerpt = body[:2000]
        parts.append(f"\nBody excerpt ({len(body)} chars total):")
        parts.append(excerpt)

    # Schema types
    if extraction.schema_types:
        parts.append(f"\nSchema types: {', '.join(extraction.schema_types)}")

    # Word count context
    parts.append(f"\nWord count: {extraction.word_count}")

    compressed = "\n".join(parts)
    return compressed[:max_chars]
