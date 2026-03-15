"""Tests for CrawlRateLimiter (T-003).

ATS-007: Requests spaced >= 500ms, max 2/sec per domain.
PI-010: Crawl rate respected for any request sequence.
"""

from __future__ import annotations

import time

from src.research_engine.services.crawl_rate_limiter import CrawlRateLimiter

# ---------------------------------------------------------------------------
# ATS-007: Crawl rate compliance (sync tests)
# ---------------------------------------------------------------------------


class TestSyncRateLimiting:
    """ATS-007: Requests spaced correctly with sync API."""

    def test_default_delay_is_500ms(self) -> None:
        limiter = CrawlRateLimiter(default_delay_ms=500)
        assert limiter.default_delay_ms == 500

    def test_max_concurrent_default(self) -> None:
        limiter = CrawlRateLimiter(max_concurrent=2)
        assert limiter.max_concurrent == 2

    def test_first_request_no_delay(self) -> None:
        """First request to a domain should not wait."""
        limiter = CrawlRateLimiter(default_delay_ms=500)
        start = time.monotonic()
        limiter.acquire_sync("example.com")
        elapsed = time.monotonic() - start
        # First request should be near-instant
        assert elapsed < 0.1

    def test_second_request_waits_minimum_delay(self) -> None:
        """Second request to same domain waits at least delay_ms."""
        limiter = CrawlRateLimiter(default_delay_ms=100)  # 100ms for fast test
        limiter.acquire_sync("example.com")
        start = time.monotonic()
        limiter.acquire_sync("example.com")
        elapsed_ms = (time.monotonic() - start) * 1000
        # Should wait at least 100ms (with some tolerance)
        assert elapsed_ms >= 80  # 80ms tolerance for timing jitter

    def test_different_domains_no_delay(self) -> None:
        """Requests to different domains don't block each other."""
        limiter = CrawlRateLimiter(default_delay_ms=500)
        limiter.acquire_sync("domain-a.com")
        start = time.monotonic()
        limiter.acquire_sync("domain-b.com")
        elapsed = time.monotonic() - start
        # Different domain should be near-instant
        assert elapsed < 0.1


# ---------------------------------------------------------------------------
# Custom domain delay (from robots.txt crawl-delay)
# ---------------------------------------------------------------------------


class TestCustomDomainDelay:
    """Per-domain custom delay via set_domain_delay."""

    def test_set_custom_delay(self) -> None:
        limiter = CrawlRateLimiter(default_delay_ms=500)
        limiter.set_domain_delay("slow-site.com", 2000)
        assert limiter.get_delay_ms("slow-site.com") == 2000

    def test_default_used_when_no_custom(self) -> None:
        limiter = CrawlRateLimiter(default_delay_ms=500)
        assert limiter.get_delay_ms("unknown.com") == 500

    def test_custom_delay_enforced(self) -> None:
        limiter = CrawlRateLimiter(default_delay_ms=50)
        limiter.set_domain_delay("slow.com", 150)
        limiter.acquire_sync("slow.com")
        start = time.monotonic()
        limiter.acquire_sync("slow.com")
        elapsed_ms = (time.monotonic() - start) * 1000
        assert elapsed_ms >= 120  # 150ms with tolerance


# ---------------------------------------------------------------------------
# Concurrency control
# ---------------------------------------------------------------------------


class TestConcurrencyControl:
    """Max concurrent requests property."""

    def test_max_concurrent_configurable(self) -> None:
        limiter = CrawlRateLimiter(default_delay_ms=500, max_concurrent=3)
        assert limiter.max_concurrent == 3

    def test_sync_release_is_noop(self) -> None:
        """Sync release doesn't raise."""
        limiter = CrawlRateLimiter()
        limiter.release_sync()  # Should not raise


# ---------------------------------------------------------------------------
# PI-010: Property invariants
# ---------------------------------------------------------------------------


class TestPropertyInvariants:
    """PI-010: Crawl rate always respected."""

    def test_rapid_requests_always_spaced(self) -> None:
        """Multiple rapid requests are always properly spaced."""
        limiter = CrawlRateLimiter(default_delay_ms=50)
        times: list[float] = []
        for _ in range(5):
            limiter.acquire_sync("test.com")
            times.append(time.monotonic())

        # Check each pair is spaced by at least ~50ms
        for i in range(1, len(times)):
            delta_ms = (times[i] - times[i - 1]) * 1000
            assert delta_ms >= 30  # 50ms target with tolerance
