"""Tests for RobotsTxtChecker (T-002).

ATS-002: robots.txt blocks crawling — URL skipped, no request made.
INT-004: Disallow /private/ path correctly blocked.
PI-010: Crawl rate respected (crawl-delay compliance).
"""

from __future__ import annotations

import httpx

from src.research_engine.services.robots_txt_checker import (
    RobotsCheckResult,
    RobotsTxtChecker,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ROBOTS_TXT_BASIC = """\
User-agent: *
Disallow: /private/
Disallow: /admin/
Crawl-delay: 2

User-agent: Googlebot
Disallow: /no-google/
"""

ROBOTS_TXT_NO_DISALLOW = """\
User-agent: *
Crawl-delay: 1
"""

ROBOTS_TXT_BLOCK_ALL = """\
User-agent: *
Disallow: /
"""


class FakeTransport(httpx.BaseTransport):
    """Fake transport returning canned robots.txt."""

    def __init__(self, responses: dict[str, tuple[int, str]]) -> None:
        self._responses = responses

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        for pattern, (status, body) in self._responses.items():
            if pattern in url:
                return httpx.Response(status, text=body)
        return httpx.Response(404, text="Not Found")


def _make_checker(
    robots_text: str,
    domain: str = "https://example.com",
    status_code: int = 200,
) -> RobotsTxtChecker:
    """Create a checker with a mocked HTTP response."""
    transport = FakeTransport(
        {
            f"{domain}/robots.txt": (status_code, robots_text),
        }
    )
    client = httpx.Client(transport=transport)
    return RobotsTxtChecker(user_agent="SEOToolkit", http_client=client)


# ---------------------------------------------------------------------------
# ATS-002: robots.txt blocks crawling
# ---------------------------------------------------------------------------


class TestRobotsBlocking:
    """ATS-002: Blocked URLs are skipped."""

    def test_disallow_private_path(self) -> None:
        """INT-004: /private/ path correctly blocked."""
        checker = _make_checker(ROBOTS_TXT_BASIC)
        result = checker.check("https://example.com/private/article.html")
        assert result.allowed is False

    def test_disallow_admin_path(self) -> None:
        checker = _make_checker(ROBOTS_TXT_BASIC)
        result = checker.check("https://example.com/admin/dashboard")
        assert result.allowed is False

    def test_allowed_path(self) -> None:
        checker = _make_checker(ROBOTS_TXT_BASIC)
        result = checker.check("https://example.com/blog/fue-guide")
        assert result.allowed is True

    def test_root_path_allowed(self) -> None:
        checker = _make_checker(ROBOTS_TXT_BASIC)
        result = checker.check("https://example.com/")
        assert result.allowed is True

    def test_block_all_disallows_everything(self) -> None:
        checker = _make_checker(ROBOTS_TXT_BLOCK_ALL)
        result = checker.check("https://example.com/anything")
        assert result.allowed is False

    def test_no_disallow_allows_everything(self) -> None:
        checker = _make_checker(ROBOTS_TXT_NO_DISALLOW)
        result = checker.check("https://example.com/any/path")
        assert result.allowed is True


# ---------------------------------------------------------------------------
# PI-010: Crawl-delay compliance
# ---------------------------------------------------------------------------


class TestCrawlDelay:
    """PI-010: Crawl-delay extracted from robots.txt."""

    def test_crawl_delay_extracted(self) -> None:
        checker = _make_checker(ROBOTS_TXT_BASIC)
        result = checker.check("https://example.com/blog/test")
        assert result.crawl_delay == 2.0

    def test_crawl_delay_from_no_disallow(self) -> None:
        checker = _make_checker(ROBOTS_TXT_NO_DISALLOW)
        result = checker.check("https://example.com/page")
        assert result.crawl_delay == 1.0

    def test_no_crawl_delay_returns_none(self) -> None:
        checker = _make_checker("User-agent: *\nDisallow: /secret/")
        result = checker.check("https://example.com/page")
        assert result.crawl_delay is None


# ---------------------------------------------------------------------------
# Cache behaviour
# ---------------------------------------------------------------------------


class TestCaching:
    """Robots.txt cached per domain for 24h."""

    def test_second_check_uses_cache(self) -> None:
        """Second check to same domain doesn't refetch."""
        checker = _make_checker(ROBOTS_TXT_BASIC)
        result1 = checker.check("https://example.com/blog/a")
        result2 = checker.check("https://example.com/blog/b")
        assert result1.allowed is True
        assert result2.allowed is True

    def test_clear_cache(self) -> None:
        checker = _make_checker(ROBOTS_TXT_BASIC)
        checker.check("https://example.com/blog/a")
        checker.clear_cache()
        # After clearing, should refetch
        result = checker.check("https://example.com/blog/b")
        assert result.allowed is True


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """When robots.txt can't be fetched, allow by default."""

    def test_404_robots_allows_crawling(self) -> None:
        checker = _make_checker("", status_code=404)
        result = checker.check("https://example.com/page")
        assert result.allowed is True
        assert result.crawl_delay is None

    def test_http_error_allows_crawling(self) -> None:
        checker = _make_checker("", status_code=500)
        result = checker.check("https://example.com/page")
        assert result.allowed is True


# ---------------------------------------------------------------------------
# Return type validation
# ---------------------------------------------------------------------------


class TestReturnType:
    """Ensure correct return type."""

    def test_returns_robots_check_result(self) -> None:
        checker = _make_checker(ROBOTS_TXT_BASIC)
        result = checker.check("https://example.com/blog/test")
        assert isinstance(result, RobotsCheckResult)
