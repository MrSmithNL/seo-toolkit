"""Tests for F-004 SERP rate limiter.

TDD: Tests for T-003 covering ATS-004, ATS-007, PI-009, INT-006.
"""

from __future__ import annotations

from datetime import UTC, datetime

from hypothesis import given, settings
from hypothesis import strategies as st

from src.research_engine.services.serp_rate_limiter import SerpRateLimiter

# ---------------------------------------------------------------------------
# ATS-004: Daily rate limit enforcement (51st request blocked)
# ---------------------------------------------------------------------------


class TestDailyRateLimit:
    """ATS-004: Daily limit enforcement."""

    def test_first_request_allowed(self) -> None:
        """First request is always allowed."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})
        can, remaining = limiter.can_request("dataforseo")
        assert can is True
        assert remaining == 50

    def test_request_at_limit_blocked(self) -> None:
        """51st request is blocked when limit is 50."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})
        for _ in range(50):
            limiter.record_request("dataforseo")
        can, remaining = limiter.can_request("dataforseo")
        assert can is False
        assert remaining == 0

    def test_error_message_on_limit(self) -> None:
        """Error message matches spec format."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})
        for _ in range(50):
            limiter.record_request("dataforseo")
        msg = limiter.limit_message("dataforseo")
        assert "SERP daily limit reached (50/50)" in msg
        assert "midnight UTC" in msg

    def test_50th_request_allowed(self) -> None:
        """Exactly the 50th request is allowed (limit is exclusive)."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})
        for _ in range(49):
            limiter.record_request("dataforseo")
        can, remaining = limiter.can_request("dataforseo")
        assert can is True
        assert remaining == 1


# ---------------------------------------------------------------------------
# ATS-007: Configurable daily limit via env var
# ---------------------------------------------------------------------------


class TestConfigurableLimit:
    """ATS-007: Configurable daily limit."""

    def test_custom_limit_25(self) -> None:
        """Custom limit of 25 blocks the 26th request."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 25})
        for _ in range(25):
            limiter.record_request("dataforseo")
        can, _ = limiter.can_request("dataforseo")
        assert can is False

    def test_different_limits_per_source(self) -> None:
        """DataForSEO and Google have independent limits."""
        limiter = SerpRateLimiter(
            daily_limits={"dataforseo": 50, "google_scrape": 30},
        )
        for _ in range(30):
            limiter.record_request("google_scrape")

        # Google exhausted
        can_google, _ = limiter.can_request("google_scrape")
        assert can_google is False

        # DataForSEO still available
        can_dfs, remaining = limiter.can_request("dataforseo")
        assert can_dfs is True
        assert remaining == 50

    def test_google_limit_30(self) -> None:
        """Google scraper limit defaults to 30."""
        limiter = SerpRateLimiter(daily_limits={"google_scrape": 30})
        for _ in range(30):
            limiter.record_request("google_scrape")
        can, _ = limiter.can_request("google_scrape")
        assert can is False
        msg = limiter.limit_message("google_scrape")
        assert "(30/30)" in msg


# ---------------------------------------------------------------------------
# PI-009: Daily limit respected — counter never exceeds limit
# ---------------------------------------------------------------------------


class TestDailyLimitProperty:
    """PI-009: Property-based test for daily limit invariant."""

    @given(
        limit=st.integers(min_value=1, max_value=100),
        requests=st.integers(min_value=0, max_value=200),
    )
    @settings(max_examples=50)
    def test_counter_never_exceeds_limit(self, limit: int, requests: int) -> None:
        """Property: counter never exceeds configured limit."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": limit})
        allowed = 0
        for _ in range(requests):
            can, _ = limiter.can_request("dataforseo")
            if can:
                limiter.record_request("dataforseo")
                allowed += 1
        assert allowed <= limit

    @given(limit=st.integers(min_value=1, max_value=100))
    @settings(max_examples=20)
    def test_exactly_limit_requests_allowed(self, limit: int) -> None:
        """Property: exactly <limit> requests are allowed, never more."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": limit})
        allowed = 0
        for _ in range(limit + 10):
            can, _ = limiter.can_request("dataforseo")
            if can:
                limiter.record_request("dataforseo")
                allowed += 1
        assert allowed == limit


# ---------------------------------------------------------------------------
# INT-006: Counter persistence across resets
# ---------------------------------------------------------------------------


class TestCounterState:
    """INT-006: Counter state management."""

    def test_get_daily_count(self) -> None:
        """Daily count is trackable."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})
        for _ in range(10):
            limiter.record_request("dataforseo")
        assert limiter.get_daily_count("dataforseo") == 10

    def test_reset_counter(self) -> None:
        """Counter can be reset (simulates midnight UTC)."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})
        for _ in range(30):
            limiter.record_request("dataforseo")
        limiter.reset("dataforseo")
        assert limiter.get_daily_count("dataforseo") == 0
        can, remaining = limiter.can_request("dataforseo")
        assert can is True
        assert remaining == 50

    def test_unknown_source_returns_zero(self) -> None:
        """Unknown source has zero count."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})
        assert limiter.get_daily_count("unknown") == 0

    def test_unknown_source_blocked(self) -> None:
        """Source without configured limit is blocked."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})
        can, _ = limiter.can_request("unknown")
        assert can is False


# ---------------------------------------------------------------------------
# Date-aware counter
# ---------------------------------------------------------------------------


class TestDateAwareCounter:
    """Counter auto-resets on new UTC day."""

    def test_new_day_resets_counter(self) -> None:
        """Counter resets when the UTC date changes."""
        limiter = SerpRateLimiter(daily_limits={"dataforseo": 50})

        # Record with today's date
        today = datetime(2026, 3, 15, 10, 0, 0, tzinfo=UTC)
        for _ in range(30):
            limiter.record_request("dataforseo", now=today)

        assert limiter.get_daily_count("dataforseo", now=today) == 30

        # Next day — counter should reset
        tomorrow = datetime(2026, 3, 16, 10, 0, 0, tzinfo=UTC)
        assert limiter.get_daily_count("dataforseo", now=tomorrow) == 0
        can, remaining = limiter.can_request("dataforseo", now=tomorrow)
        assert can is True
        assert remaining == 50
