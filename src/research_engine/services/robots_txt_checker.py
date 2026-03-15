"""RobotsTxtChecker for F-005 competitor crawling.

Fetches and parses robots.txt per domain, checks if a URL path
is crawlable, and extracts crawl-delay. Caches per domain for 24h.

TypeScript equivalent: modules/content-engine/research/services/robots-txt-checker.ts
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

logger = logging.getLogger(__name__)

_CACHE_TTL_SECONDS = 86400  # 24 hours


@dataclass(frozen=True)
class RobotsCheckResult:
    """Result of a robots.txt check."""

    allowed: bool
    crawl_delay: float | None = None


@dataclass
class _CachedRobots:
    """Cached robots.txt data for a domain."""

    disallowed_paths: list[str]
    crawl_delay: float | None
    fetched_at: float


class RobotsTxtChecker:
    """Fetches and caches robots.txt, checks URL crawlability.

    Per-domain cache with 24h TTL (in-memory Map, cleared on restart).
    """

    def __init__(
        self,
        user_agent: str = "SEOToolkit",
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Initialise with User-Agent string.

        Args:
            user_agent: User-Agent to match in robots.txt rules.
            http_client: Optional httpx client for testing.
        """
        self._user_agent = user_agent.lower()
        self._cache: dict[str, _CachedRobots] = {}
        self._http_client = http_client

    def check(self, url: str) -> RobotsCheckResult:
        """Check if a URL is allowed by robots.txt.

        Args:
            url: Full URL to check.

        Returns:
            RobotsCheckResult with allowed status and crawl-delay.
        """
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        path = parsed.path or "/"

        robots = self._get_robots(domain)
        if robots is None:
            # Could not fetch robots.txt — allow by default
            return RobotsCheckResult(allowed=True, crawl_delay=None)

        for disallowed in robots.disallowed_paths:
            if path.startswith(disallowed):
                logger.info(
                    "URL blocked by robots.txt: %s (rule: Disallow %s)",
                    url,
                    disallowed,
                )
                return RobotsCheckResult(
                    allowed=False,
                    crawl_delay=robots.crawl_delay,
                )

        return RobotsCheckResult(
            allowed=True,
            crawl_delay=robots.crawl_delay,
        )

    def _get_robots(self, domain: str) -> _CachedRobots | None:
        """Get robots.txt data for a domain, using cache if available."""
        now = time.monotonic()

        # Check cache
        cached = self._cache.get(domain)
        if cached and (now - cached.fetched_at) < _CACHE_TTL_SECONDS:
            return cached

        # Fetch robots.txt
        robots_url = f"{domain}/robots.txt"
        try:
            client = self._http_client or httpx.Client(timeout=10.0)
            try:
                response = client.get(robots_url)
                if response.status_code != 200:  # noqa: PLR2004
                    # No robots.txt or error — allow everything
                    return None
                text = response.text
            finally:
                if self._http_client is None:
                    client.close()
        except (httpx.HTTPError, OSError):
            logger.warning("Failed to fetch robots.txt for %s", domain)
            return None

        # Parse
        parsed = self._parse_robots_txt(text)
        parsed.fetched_at = now
        self._cache[domain] = parsed
        return parsed

    def _parse_robots_txt(self, text: str) -> _CachedRobots:  # noqa: C901
        """Parse robots.txt content.

        Simple parser that handles User-agent matching (wildcard and
        specific), Disallow directives, and Crawl-delay.

        Args:
            text: Raw robots.txt content.

        Returns:
            Parsed robots data.
        """
        import contextlib

        disallowed: list[str] = []
        crawl_delay: float | None = None
        in_matching_block = False
        in_specific_block = False

        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or ":" not in line:
                continue

            key, _, value = line.partition(":")
            key = key.strip().lower()
            value = value.strip()

            if key == "user-agent":
                agent = value.lower()
                if agent == "*":
                    in_matching_block = True
                    in_specific_block = False
                elif self._user_agent in agent or agent in self._user_agent:
                    in_matching_block = True
                    in_specific_block = True
                elif in_matching_block and not in_specific_block:
                    in_matching_block = False
            elif key == "disallow" and in_matching_block and value:
                disallowed.append(value)
            elif key == "crawl-delay" and in_matching_block:
                with contextlib.suppress(ValueError):
                    crawl_delay = float(value)

        return _CachedRobots(
            disallowed_paths=disallowed,
            crawl_delay=crawl_delay,
            fetched_at=0.0,
        )

    def clear_cache(self) -> None:
        """Clear the robots.txt cache."""
        self._cache.clear()
