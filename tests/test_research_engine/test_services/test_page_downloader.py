"""Tests for PageDownloader (T-005).

ATS-003: HTTP 404 → crawl_failed, pipeline continues.
ATS-006: 429 → exponential backoff (3 retries), then crawl_failed.
PI-007: raw_html_hash always non-empty MD5 string.
"""

from __future__ import annotations

import httpx

from src.research_engine.services.crawl_rate_limiter import CrawlRateLimiter
from src.research_engine.services.page_downloader import (
    DownloadConfig,
    PageDownloader,
    validate_url,
)
from src.research_engine.services.robots_txt_checker import RobotsTxtChecker

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeTransport(httpx.BaseTransport):
    """Fake transport for testing downloads."""

    def __init__(self, responses: dict[str, tuple[int, str]]) -> None:
        self._responses = responses
        self.request_count = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        self.request_count += 1
        url = str(request.url)
        for pattern, (status, body) in self._responses.items():
            if pattern in url:
                return httpx.Response(status, text=body)
        return httpx.Response(404, text="Not Found")


def _make_downloader(
    page_responses: dict[str, tuple[int, str]] | None = None,
    robots_text: str = "User-agent: *\nAllow: /",
) -> tuple[PageDownloader, _FakeTransport]:
    """Create a downloader with mocked HTTP responses."""
    all_responses = {
        "robots.txt": (200, robots_text),
    }
    if page_responses:
        all_responses.update(page_responses)

    transport = _FakeTransport(all_responses)
    client = httpx.Client(transport=transport)

    robots_checker = RobotsTxtChecker(user_agent="SEOToolkit", http_client=client)
    rate_limiter = CrawlRateLimiter(default_delay_ms=0)  # No delay in tests
    config = DownloadConfig(
        max_retries=2,
        retry_delays=(0.01, 0.01, 0.01),  # Fast retries in tests
    )

    downloader = PageDownloader(
        robots_checker=robots_checker,
        rate_limiter=rate_limiter,
        config=config,
        http_client=client,
    )
    return downloader, transport


# ---------------------------------------------------------------------------
# ATS-003: HTTP 404 → crawl_failed
# ---------------------------------------------------------------------------


class TestHttp404:
    """ATS-003: 404 returns crawl_failed, pipeline continues."""

    def test_404_returns_failed(self) -> None:
        downloader, _ = _make_downloader(
            {
                "example.com/missing": (404, "Not Found"),
            }
        )
        result = downloader.download("https://example.com/missing")
        assert result.success is False
        assert result.http_status_code == 404

    def test_404_does_not_retry(self) -> None:
        downloader, transport = _make_downloader(
            {
                "example.com/gone": (404, "Gone"),
            }
        )
        downloader.download("https://example.com/gone")
        # 1 robots.txt + 1 page fetch = 2 requests (no retries for 404)
        assert transport.request_count == 2


# ---------------------------------------------------------------------------
# ATS-006: 429 → retry → crawl_failed
# ---------------------------------------------------------------------------


class TestRateLimitRetry:
    """ATS-006: 429 triggers exponential backoff."""

    def test_429_retries_and_fails(self) -> None:
        downloader, transport = _make_downloader(
            {
                "example.com/page": (429, "Too Many Requests"),
            }
        )
        result = downloader.download("https://example.com/page")
        assert result.success is False
        assert result.http_status_code == 429
        assert result.retries_attempted == 2  # max_retries=2

    def test_500_retries(self) -> None:
        downloader, transport = _make_downloader(
            {
                "example.com/error": (500, "Server Error"),
            }
        )
        result = downloader.download("https://example.com/error")
        assert result.success is False
        assert result.retries_attempted == 2


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestHappyPath:
    """Successful download and hash computation."""

    def test_successful_download(self) -> None:
        downloader, _ = _make_downloader(
            {
                "example.com/page": (200, "<html><body>Hello</body></html>"),
            }
        )
        result = downloader.download("https://example.com/page")
        assert result.success is True
        assert result.http_status_code == 200
        assert "<html>" in result.html

    def test_pi_007_hash_is_md5(self) -> None:
        """PI-007: raw_html_hash is a valid MD5 string."""
        downloader, _ = _make_downloader(
            {
                "example.com/page": (200, "<html><body>Test</body></html>"),
            }
        )
        result = downloader.download("https://example.com/page")
        assert result.success is True
        assert len(result.raw_html_hash) == 32
        assert all(c in "0123456789abcdef" for c in result.raw_html_hash)


# ---------------------------------------------------------------------------
# robots.txt blocking
# ---------------------------------------------------------------------------


class TestRobotsBlocking:
    """ATS-002: robots.txt blocks crawling."""

    def test_robots_blocked_returns_failed(self) -> None:
        downloader, _ = _make_downloader(
            page_responses={"example.com/private": (200, "Secret")},
            robots_text="User-agent: *\nDisallow: /private/",
        )
        result = downloader.download("https://example.com/private/page")
        assert result.success is False
        assert result.is_robots_blocked is True


# ---------------------------------------------------------------------------
# SSRF protection
# ---------------------------------------------------------------------------


class TestSsrfProtection:
    """SSRF validation via validate_url()."""

    def test_private_ip_blocked(self) -> None:
        error = validate_url("http://127.0.0.1/page")
        assert error is not None
        assert "SSRF" in error or "private" in error.lower()

    def test_file_scheme_blocked(self) -> None:
        error = validate_url("file:///etc/passwd")
        assert error is not None
        assert "scheme" in error.lower()

    def test_ftp_scheme_blocked(self) -> None:
        error = validate_url("ftp://example.com/file")
        assert error is not None
        assert "scheme" in error.lower()

    def test_valid_https_url_passes(self) -> None:
        # This will attempt DNS resolution, which may fail for non-existent domains
        # but the scheme/structure check should pass
        error = validate_url("https://example.com/page")
        # example.com resolves to a public IP, should pass
        assert error is None

    def test_no_hostname_blocked(self) -> None:
        error = validate_url("https://")
        assert error is not None

    def test_private_10_range_blocked(self) -> None:
        error = validate_url("http://10.0.0.1/page")
        assert error is not None
        assert "SSRF" in error or "private" in error.lower()
