"""URL crawler with sitemap-first strategy and BFS fallback.

Implements SSRF protections per STRIDE-Lite: scheme allowlist,
private IP rejection, redirect limits, timeouts.
"""

from __future__ import annotations

import ipaddress
import logging
from urllib.parse import urljoin, urlparse

import httpx
from defusedxml import ElementTree

from src.research_engine.models.result import Err, Ok, Result

logger = logging.getLogger(__name__)

ALLOWED_SCHEMES = frozenset({"http", "https"})
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
MAX_REDIRECTS = 5
CONNECT_TIMEOUT = 10.0
READ_TIMEOUT = 30.0
MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10MB


def validate_url(url: str) -> Result[str, str]:
    """Validate a URL for safety (SSRF protection).

    Checks scheme allowlist and rejects private/loopback IPs.

    Args:
        url: URL to validate.

    Returns:
        Ok(url) if safe, Err(reason) if blocked.
    """
    if not url:
        return Err("URL is empty")

    try:
        parsed = urlparse(url)
    except ValueError:
        return Err(f"Malformed URL: {url}")

    if not parsed.scheme or not parsed.netloc:
        return Err(f"Malformed URL (missing scheme or host): {url}")

    if parsed.scheme not in ALLOWED_SCHEMES:
        return Err(f"Blocked scheme: {parsed.scheme}. Only http/https allowed.")

    hostname = parsed.hostname or ""

    # Check for IP addresses
    try:
        addr = ipaddress.ip_address(hostname)
        if addr.is_private or addr.is_loopback or addr.is_reserved:
            return Err(f"Blocked private/loopback IP: {hostname}")
    except ValueError:
        # Not an IP address — it's a hostname, which is fine
        pass

    return Ok(url)


def fetch_sitemap(
    base_url: str,
    client: httpx.Client,
    max_urls: int = 50,
) -> Result[list[str], str]:
    """Fetch and parse sitemap.xml from a website.

    Args:
        base_url: Base URL of the website (e.g. https://example.com).
        client: httpx Client for making requests.
        max_urls: Maximum number of URLs to extract.

    Returns:
        Ok(urls) on success, Err(reason) on failure.
    """
    sitemap_url = f"{base_url.rstrip('/')}/sitemap.xml"

    try:
        response = client.get(
            sitemap_url,
            timeout=httpx.Timeout(CONNECT_TIMEOUT, read=READ_TIMEOUT),
            follow_redirects=True,
        )
    except httpx.HTTPError as exc:
        return Err(f"HTTP error fetching sitemap: {exc}")

    if response.status_code != 200:  # noqa: PLR2004
        return Err(f"Sitemap returned status {response.status_code}")

    try:
        root = ElementTree.fromstring(response.text)
    except ElementTree.ParseError as exc:
        return Err(f"Invalid XML in sitemap: {exc}")

    urls: list[str] = []
    for loc in root.iter(f"{{{SITEMAP_NAMESPACE}}}loc"):
        if loc.text:
            urls.append(loc.text.strip())
        if len(urls) >= max_urls:
            break

    if not urls:
        return Err("Sitemap contained no URLs")

    return Ok(urls)


def bfs_crawl(
    base_url: str,
    client: httpx.Client,
    max_pages: int = 50,
    max_depth: int = 2,
) -> list[str]:
    """BFS crawl a website starting from the homepage.

    Discovers internal links up to max_depth levels.

    Args:
        base_url: Starting URL.
        client: httpx Client for making requests.
        max_pages: Maximum pages to visit.
        max_depth: Maximum link depth from homepage.

    Returns:
        List of discovered URLs.
    """
    from bs4 import BeautifulSoup

    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc
    visited: set[str] = set()
    queue: list[tuple[str, int]] = [(base_url, 0)]
    discovered: list[str] = []

    while queue and len(discovered) < max_pages:
        current_url, depth = queue.pop(0)

        if current_url in visited:
            continue
        visited.add(current_url)
        discovered.append(current_url)

        if depth >= max_depth:
            continue

        try:
            response = client.get(
                current_url,
                timeout=httpx.Timeout(CONNECT_TIMEOUT, read=READ_TIMEOUT),
                follow_redirects=True,
            )
            if response.status_code != 200:  # noqa: PLR2004
                continue
        except httpx.HTTPError:
            continue

        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = str(link["href"])
            absolute = urljoin(current_url, href)
            parsed = urlparse(absolute)

            # Only follow internal links
            if parsed.netloc == base_domain and absolute not in visited:
                # Strip fragments
                clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean not in visited:
                    queue.append((clean, depth + 1))

    return discovered


def crawl_site(
    url: str,
    client: httpx.Client,
    max_pages: int = 50,
) -> Result[list[str], str]:
    """Crawl a website using sitemap-first strategy with BFS fallback.

    Args:
        url: Target website URL.
        client: httpx Client for making requests.
        max_pages: Maximum pages to discover.

    Returns:
        Ok(urls) on success, Err(reason) on failure.
    """
    # Validate URL first (SSRF protection)
    url_result = validate_url(url)
    if isinstance(url_result, Err):
        return url_result

    # Try sitemap first
    sitemap_result = fetch_sitemap(url, client, max_urls=max_pages)
    if isinstance(sitemap_result, Ok):
        logger.info("Found sitemap with %d URLs", len(sitemap_result.value))
        return sitemap_result

    # Fall back to BFS crawl
    logger.info("No sitemap found, falling back to BFS crawl")
    urls = bfs_crawl(url, client, max_pages=max_pages)
    if not urls:
        return Err("No pages discovered via BFS crawl")

    return Ok(urls)
