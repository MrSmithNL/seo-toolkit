"""Tests for URL crawler with sitemap parsing and BFS fallback.

TDD: Tests written BEFORE implementation.
Covers: T-004 (URL Crawler portion)
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from src.research_engine.domain.crawler import (
    crawl_site,
    fetch_sitemap,
    validate_url,
)
from src.research_engine.models.result import Err, Ok

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_fixture(name: str) -> str:
    """Load a fixture file as string."""
    return (FIXTURES_DIR / name).read_text()


# ===========================================================================
# validate_url() tests
# ===========================================================================


class TestValidateUrl:
    """Tests for URL validation with SSRF protection."""

    def test_accepts_https(self) -> None:
        """HTTPS URLs are accepted."""
        result = validate_url("https://example.com")
        assert isinstance(result, Ok)
        assert result.value == "https://example.com"

    def test_accepts_http(self) -> None:
        """HTTP URLs are accepted."""
        result = validate_url("http://example.com")
        assert isinstance(result, Ok)

    def test_rejects_file_scheme(self) -> None:
        """file:// URLs must be rejected (SSRF)."""
        result = validate_url("file:///etc/passwd")
        assert isinstance(result, Err)
        assert "scheme" in result.error.lower()

    def test_rejects_ftp_scheme(self) -> None:
        """ftp:// URLs must be rejected."""
        result = validate_url("ftp://example.com")
        assert isinstance(result, Err)

    def test_rejects_private_ip_127(self) -> None:
        """127.x.x.x (loopback) must be rejected."""
        result = validate_url("http://127.0.0.1")
        assert isinstance(result, Err)
        assert "private" in result.error.lower() or "blocked" in result.error.lower()

    def test_rejects_private_ip_10(self) -> None:
        """10.x.x.x (private) must be rejected."""
        result = validate_url("http://10.0.0.1")
        assert isinstance(result, Err)

    def test_rejects_private_ip_172(self) -> None:
        """172.16.x.x (private) must be rejected."""
        result = validate_url("http://172.16.0.1")
        assert isinstance(result, Err)

    def test_rejects_private_ip_192(self) -> None:
        """192.168.x.x (private) must be rejected."""
        result = validate_url("http://192.168.1.1")
        assert isinstance(result, Err)

    def test_rejects_empty_url(self) -> None:
        """Empty URL must be rejected."""
        result = validate_url("")
        assert isinstance(result, Err)

    def test_rejects_malformed_url(self) -> None:
        """Malformed URL must be rejected."""
        result = validate_url("not-a-url")
        assert isinstance(result, Err)


# ===========================================================================
# fetch_sitemap() tests
# ===========================================================================


class TestFetchSitemap:
    """Tests for sitemap fetching and parsing."""

    def test_parses_valid_sitemap(self, httpx_mock: pytest.fixture) -> None:
        """Valid sitemap.xml returns list of URLs."""
        sitemap_xml = _load_fixture("sitemap.xml")
        httpx_mock.add_response(  # type: ignore[attr-defined]
            url="https://example.com/sitemap.xml",
            text=sitemap_xml,
        )
        client = httpx.Client()
        result = fetch_sitemap("https://example.com", client)
        assert isinstance(result, Ok)
        assert len(result.value) == 10
        assert "https://example.com/" in result.value

    def test_returns_err_on_404(self, httpx_mock: pytest.fixture) -> None:
        """404 response returns Err (no sitemap found)."""
        httpx_mock.add_response(  # type: ignore[attr-defined]
            url="https://example.com/sitemap.xml",
            status_code=404,
        )
        client = httpx.Client()
        result = fetch_sitemap("https://example.com", client)
        assert isinstance(result, Err)

    def test_returns_err_on_invalid_xml(self, httpx_mock: pytest.fixture) -> None:
        """Invalid XML returns Err."""
        httpx_mock.add_response(  # type: ignore[attr-defined]
            url="https://example.com/sitemap.xml",
            text="<not valid xml",
        )
        client = httpx.Client()
        result = fetch_sitemap("https://example.com", client)
        assert isinstance(result, Err)


# ===========================================================================
# crawl_site() tests
# ===========================================================================


class TestCrawlSite:
    """Tests for the combined crawl strategy (sitemap-first, BFS fallback)."""

    def test_uses_sitemap_when_available(self, httpx_mock: pytest.fixture) -> None:
        """When sitemap exists, uses it instead of BFS."""
        sitemap_xml = _load_fixture("sitemap.xml")
        httpx_mock.add_response(  # type: ignore[attr-defined]
            url="https://example.com/sitemap.xml",
            text=sitemap_xml,
        )
        client = httpx.Client()
        result = crawl_site("https://example.com", client)
        assert isinstance(result, Ok)
        assert len(result.value) == 10

    def test_falls_back_to_bfs_on_no_sitemap(self, httpx_mock: pytest.fixture) -> None:
        """When sitemap is 404, falls back to BFS crawl."""
        httpx_mock.add_response(  # type: ignore[attr-defined]
            url="https://example.com/sitemap.xml",
            status_code=404,
        )
        homepage_html = """
        <html><body>
            <a href="/page1">Page 1</a>
            <a href="/page2">Page 2</a>
        </body></html>
        """
        httpx_mock.add_response(  # type: ignore[attr-defined]
            url="https://example.com",
            text=homepage_html,
        )
        httpx_mock.add_response(  # type: ignore[attr-defined]
            url="https://example.com/page1",
            text="<html><body><h1>Page 1</h1></body></html>",
        )
        httpx_mock.add_response(  # type: ignore[attr-defined]
            url="https://example.com/page2",
            text="<html><body><h1>Page 2</h1></body></html>",
        )
        client = httpx.Client()
        result = crawl_site("https://example.com", client)
        assert isinstance(result, Ok)
        assert len(result.value) >= 1  # at least homepage

    def test_rejects_invalid_url(self) -> None:
        """Invalid URL returns Err without making HTTP calls."""
        client = httpx.Client()
        result = crawl_site("file:///etc/passwd", client)
        assert isinstance(result, Err)
