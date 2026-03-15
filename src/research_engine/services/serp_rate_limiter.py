"""SERP rate limiter with per-source daily counters.

Token bucket pattern with daily reset at midnight UTC.
In-memory implementation for R1; Redis adapter for platform mode (R2+).

TypeScript equivalent: modules/content-engine/research/services/serp-rate-limiter.ts
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime

logger = logging.getLogger(__name__)


class SerpRateLimiter:
    """Per-source daily request rate limiter.

    Enforces configurable daily maximums per SERP data source.
    Counters auto-reset when the UTC date changes.

    Args:
        daily_limits: Map of source name to daily request limit.
            Example: {"dataforseo": 50, "google_scrape": 30}
    """

    def __init__(self, daily_limits: dict[str, int]) -> None:
        """Initialise with per-source daily limits."""
        self._limits = daily_limits
        self._counters: dict[str, int] = {}
        self._counter_dates: dict[str, str] = {}

    def can_request(
        self,
        source: str,
        *,
        now: datetime | None = None,
    ) -> tuple[bool, int]:
        """Check if a request is allowed for the given source.

        Args:
            source: SERP data source name (e.g., 'dataforseo').
            now: Override current time (for testing).

        Returns:
            Tuple of (allowed: bool, remaining: int).
        """
        if source not in self._limits:
            return False, 0

        self._auto_reset_if_new_day(source, now)
        limit = self._limits[source]
        count = self._counters.get(source, 0)
        remaining = max(0, limit - count)
        return remaining > 0, remaining

    def record_request(
        self,
        source: str,
        *,
        now: datetime | None = None,
    ) -> None:
        """Record a request for the given source.

        Increments the daily counter. Should only be called after
        can_request() returns True.

        Args:
            source: SERP data source name.
            now: Override current time (for testing).
        """
        ts = now or datetime.now(tz=UTC)
        self._auto_reset_if_new_day(source, ts)
        date_key = ts.strftime("%Y-%m-%d")
        self._counters[source] = self._counters.get(source, 0) + 1
        self._counter_dates[source] = date_key
        logger.debug(
            "SERP request recorded: source=%s count=%d/%d",
            source,
            self._counters[source],
            self._limits.get(source, 0),
        )

    def get_daily_count(
        self,
        source: str,
        *,
        now: datetime | None = None,
    ) -> int:
        """Get the current daily request count for a source.

        Args:
            source: SERP data source name.
            now: Override current time (for testing).

        Returns:
            Number of requests made today.
        """
        self._auto_reset_if_new_day(source, now)
        return self._counters.get(source, 0)

    def reset(self, source: str) -> None:
        """Manually reset the counter for a source.

        Args:
            source: SERP data source name.
        """
        self._counters[source] = 0
        self._counter_dates.pop(source, None)

    def limit_message(self, source: str) -> str:
        """Generate the standard rate limit error message.

        Args:
            source: SERP data source name.

        Returns:
            Human-readable rate limit message.
        """
        limit = self._limits.get(source, 0)
        count = self._counters.get(source, 0)
        return (
            f"SERP daily limit reached ({count}/{limit}). "
            f"Next requests available after midnight UTC."
        )

    def _auto_reset_if_new_day(
        self,
        source: str,
        now: datetime | None = None,
    ) -> None:
        """Reset counter if the UTC date has changed since last request."""
        ts = now or datetime.now(tz=UTC)
        today = ts.strftime("%Y-%m-%d")
        stored_date = self._counter_dates.get(source)
        if stored_date is not None and stored_date != today:
            self._counters[source] = 0
            self._counter_dates[source] = today
