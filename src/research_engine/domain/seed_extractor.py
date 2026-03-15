"""Seed keyword extraction from HTML pages.

Extracts potential keywords from title, meta description, headings,
and breadcrumb navigation. Pure function — no HTTP calls.
"""

from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(frozen=True)
class SeedKeyword:
    """A keyword discovered from an HTML page.

    Attributes:
        term: The extracted keyword text.
        source_url: URL of the page it was found on.
        source_element: HTML element it was extracted from.
    """

    term: str
    source_url: str
    source_element: str


def extract_seeds(html: str, source_url: str) -> list[SeedKeyword]:  # noqa: C901
    """Extract seed keywords from an HTML page.

    Extracts text from: title, meta description, h1-h3, breadcrumbs.
    Deduplicates by lowercase term.

    Args:
        html: Raw HTML content.
        source_url: URL of the page.

    Returns:
        Deduplicated list of SeedKeyword objects.
    """
    if not html.strip():
        return []

    soup = BeautifulSoup(html, "html.parser")
    candidates: list[tuple[str, str]] = []

    # Title
    title_tag = soup.find("title")
    if title_tag and title_tag.string:
        candidates.append((title_tag.string.strip(), "title"))

    # Meta description
    meta_tag = soup.find("meta", attrs={"name": "description"})
    if meta_tag and meta_tag.get("content"):  # type: ignore[union-attr]
        content = str(meta_tag["content"])  # type: ignore[index]
        candidates.append((content.strip(), "meta_description"))

    # Headings h1-h3
    for level in ("h1", "h2", "h3"):
        for tag in soup.find_all(level):
            text = tag.get_text(strip=True)
            if text:
                candidates.append((text, level))

    # Breadcrumbs
    breadcrumb_nav = soup.find("nav", attrs={"aria-label": "breadcrumb"}) or soup.find(
        "ol", class_="breadcrumb"
    )
    if breadcrumb_nav:
        for li in breadcrumb_nav.find_all("li"):  # type: ignore[union-attr]
            text = li.get_text(strip=True)
            if text and text.lower() != "home":
                candidates.append((text, "breadcrumb"))

    # Deduplicate by lowercase term
    seen: set[str] = set()
    seeds: list[SeedKeyword] = []
    for term, element in candidates:
        lower = term.lower()
        if lower not in seen:
            seen.add(lower)
            seeds.append(
                SeedKeyword(term=term, source_url=source_url, source_element=element)
            )

    return seeds
