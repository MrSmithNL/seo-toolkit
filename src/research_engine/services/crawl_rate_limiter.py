"""Domain-aware crawl rate limiter for F-005.

Per-domain token bucket with configurable delay (default 500ms).
Global concurrency limited to max in-flight requests.
Per ADR-F005-003.

TypeScript equivalent: modules/content-engine/research/services/crawl-rate-limiter.ts
"""

from __future__ import annotations

import asyncio
import logging
import time

logger = logging.getLogger(__name__)


class CrawlRateLimiter:
    """Per-domain rate limiter with global concurrency control.

    Each domain gets its own delay bucket. Global concurrency
    limits total in-flight requests across all domains.
    """

    def __init__(
        self,
        default_delay_ms: int = 500,
        max_concurrent: int = 2,
    ) -> None:
        """Initialise rate limiter.

        Args:
            default_delay_ms: Minimum delay between requests to same domain.
            max_concurrent: Maximum in-flight requests across all domains.
        """
        self._default_delay_ms = default_delay_ms
        self._max_concurrent = max_concurrent
        self._domain_last_request: dict[str, float] = {}
        self._domain_delays: dict[str, int] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self._lock = asyncio.Lock()

    def set_domain_delay(self, domain: str, delay_ms: int) -> None:
        """Set a custom delay for a domain (e.g., from robots.txt crawl-delay).

        Args:
            domain: The domain name.
            delay_ms: Delay in milliseconds.
        """
        self._domain_delays[domain] = delay_ms

    def get_delay_ms(self, domain: str) -> int:
        """Get the effective delay for a domain.

        Args:
            domain: The domain name.

        Returns:
            Delay in milliseconds.
        """
        return self._domain_delays.get(domain, self._default_delay_ms)

    async def acquire(self, domain: str) -> None:
        """Wait until it's safe to make a request to the domain.

        Blocks until:
        1. Global concurrency slot is available
        2. Per-domain delay has elapsed

        Args:
            domain: The domain to request.
        """
        await self._semaphore.acquire()

        async with self._lock:
            delay_ms = self.get_delay_ms(domain)
            last_request = self._domain_last_request.get(domain, 0.0)
            now = time.monotonic()
            elapsed_ms = (now - last_request) * 1000

            if elapsed_ms < delay_ms:
                wait_ms = delay_ms - elapsed_ms
                await asyncio.sleep(wait_ms / 1000)

            self._domain_last_request[domain] = time.monotonic()

    def release(self) -> None:
        """Release a global concurrency slot after request completes."""
        self._semaphore.release()

    def acquire_sync(self, domain: str) -> None:
        """Synchronous version of acquire for non-async contexts.

        Blocks the thread until it's safe to request.

        Args:
            domain: The domain to request.
        """
        delay_ms = self.get_delay_ms(domain)
        last_request = self._domain_last_request.get(domain, 0.0)
        now = time.monotonic()
        elapsed_ms = (now - last_request) * 1000

        if elapsed_ms < delay_ms:
            wait_s = (delay_ms - elapsed_ms) / 1000
            time.sleep(wait_s)

        self._domain_last_request[domain] = time.monotonic()

    def release_sync(self) -> None:
        """Synchronous release (no-op for sync usage — concurrency not tracked)."""

    @property
    def default_delay_ms(self) -> int:
        """Get the default delay in milliseconds."""
        return self._default_delay_ms

    @property
    def max_concurrent(self) -> int:
        """Get the max concurrent requests."""
        return self._max_concurrent
