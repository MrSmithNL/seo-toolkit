"""PageDownloader for F-005 with SSRF protection.

Fetches competitor pages with URL validation, robots.txt compliance,
rate limiting, retry with exponential backoff, and MD5 hashing.

TypeScript equivalent: modules/content-engine/research/services/page-downloader.ts
"""

from __future__ import annotations

import hashlib
import ipaddress
import logging
import socket
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from src.research_engine.services.crawl_rate_limiter import CrawlRateLimiter
from src.research_engine.services.robots_txt_checker import RobotsTxtChecker

logger = logging.getLogger(__name__)

# Private IP ranges to block (SSRF protection)
_PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("::1/128"),
    ipaddress.ip_network("fc00::/7"),
    ipaddress.ip_network("fe80::/10"),
]

_ALLOWED_SCHEMES = {"http", "https"}
_MAX_REDIRECTS = 3
_MAX_RESPONSE_BYTES = 10 * 1024 * 1024  # 10MB


@dataclass
class DownloadResult:
    """Result of a page download attempt."""

    success: bool
    html: str = ""
    raw_html_hash: str = ""
    http_status_code: int | None = None
    error: str | None = None
    retries_attempted: int = 0
    is_robots_blocked: bool = False


@dataclass
class DownloadConfig:
    """Configuration for page downloading."""

    user_agent: str = "SEOToolkit/1.0 (Competitor Analysis)"
    max_retries: int = 3
    retry_delays: tuple[float, ...] = (30.0, 60.0, 120.0)
    connect_timeout: float = 10.0
    read_timeout: float = 30.0


class PageDownloader:
    """Downloads competitor pages with safety controls.

    Features:
    - SSRF protection (private IP blocking, scheme allowlist)
    - robots.txt compliance via RobotsTxtChecker
    - Rate limiting via CrawlRateLimiter
    - Retry with exponential backoff on 429/5xx
    - MD5 hashing of raw HTML for change detection
    """

    def __init__(
        self,
        robots_checker: RobotsTxtChecker,
        rate_limiter: CrawlRateLimiter,
        config: DownloadConfig | None = None,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        """Initialise downloader with dependencies.

        Args:
            robots_checker: For robots.txt compliance.
            rate_limiter: For crawl rate limiting.
            config: Download configuration.
            http_client: Optional httpx client (for testing).
        """
        self._robots = robots_checker
        self._rate_limiter = rate_limiter
        self._config = config or DownloadConfig()
        self._http_client = http_client

    def download(self, url: str) -> DownloadResult:
        """Download a competitor page with all safety controls.

        Pipeline: validate URL → check robots.txt → rate limit → fetch → hash.

        Args:
            url: The URL to download.

        Returns:
            DownloadResult with HTML content or error details.
        """
        # Step 1: URL validation (SSRF protection)
        validation_error = validate_url(url)
        if validation_error:
            return DownloadResult(
                success=False,
                error=validation_error,
                http_status_code=None,
            )

        # Step 2: robots.txt check
        robots_result = self._robots.check(url)
        if not robots_result.allowed:
            return DownloadResult(
                success=False,
                error=f"Blocked by robots.txt: {url}",
                is_robots_blocked=True,
            )

        # Apply crawl-delay from robots.txt if available
        parsed = urlparse(url)
        domain = parsed.netloc
        if robots_result.crawl_delay:
            delay_ms = int(robots_result.crawl_delay * 1000)
            self._rate_limiter.set_domain_delay(domain, delay_ms)

        # Step 3: Rate limit wait
        self._rate_limiter.acquire_sync(domain)

        # Step 4: Fetch with retry
        return self._fetch_with_retry(url)

    def _fetch_with_retry(self, url: str) -> DownloadResult:
        """Fetch URL with exponential backoff on retryable errors.

        Args:
            url: The URL to fetch.

        Returns:
            DownloadResult with content or error.
        """
        last_error = ""
        last_status = None

        for attempt in range(self._config.max_retries + 1):
            try:
                client = self._http_client or httpx.Client(
                    timeout=httpx.Timeout(
                        connect=self._config.connect_timeout,
                        read=self._config.read_timeout,
                        write=self._config.read_timeout,
                        pool=self._config.read_timeout,
                    ),
                    follow_redirects=True,
                    max_redirects=_MAX_REDIRECTS,
                )

                try:
                    response = client.get(
                        url,
                        headers={"User-Agent": self._config.user_agent},
                    )
                finally:
                    if self._http_client is None:
                        client.close()

                last_status = response.status_code

                if response.status_code == 200:  # noqa: PLR2004
                    html = response.text
                    raw_hash = hashlib.md5(html.encode()).hexdigest()  # noqa: S324
                    return DownloadResult(
                        success=True,
                        html=html,
                        raw_html_hash=raw_hash,
                        http_status_code=200,
                        retries_attempted=attempt,
                    )

                if (
                    response.status_code == 429 or response.status_code >= 500
                ):  # noqa: PLR2004
                    last_error = f"HTTP {response.status_code}"
                    if attempt < self._config.max_retries:
                        delay = self._config.retry_delays[
                            min(attempt, len(self._config.retry_delays) - 1)
                        ]
                        logger.info(
                            "Retryable error %d for %s, waiting %.1fs (attempt %d/%d)",
                            response.status_code,
                            url,
                            delay,
                            attempt + 1,
                            self._config.max_retries,
                        )
                        time.sleep(delay)
                        continue

                # Non-retryable error (4xx except 429)
                return DownloadResult(
                    success=False,
                    http_status_code=response.status_code,
                    error=f"HTTP {response.status_code}",
                    retries_attempted=attempt,
                )

            except (httpx.HTTPError, OSError) as exc:
                last_error = str(exc)
                if attempt < self._config.max_retries:
                    delay = self._config.retry_delays[
                        min(attempt, len(self._config.retry_delays) - 1)
                    ]
                    time.sleep(delay)
                    continue

        return DownloadResult(
            success=False,
            http_status_code=last_status,
            error=f"Max retries exceeded: {last_error}",
            retries_attempted=self._config.max_retries,
        )


def validate_url(url: str) -> str | None:
    """Validate URL for SSRF protection.

    Checks:
    - Scheme is http or https
    - Hostname doesn't resolve to private IP
    - URL is well-formed

    Args:
        url: URL to validate.

    Returns:
        Error message string if invalid, None if valid.
    """
    try:
        parsed = urlparse(url)
    except Exception:  # noqa: BLE001
        return f"Invalid URL: {url}"

    # Scheme check
    if parsed.scheme not in _ALLOWED_SCHEMES:
        return f"Disallowed scheme: {parsed.scheme}. Only http/https allowed."

    # Hostname required
    if not parsed.hostname:
        return f"No hostname in URL: {url}"

    # DNS resolution and private IP check
    try:
        addr_infos = socket.getaddrinfo(parsed.hostname, None)
        for _family, _type, _proto, _canonname, sockaddr in addr_infos:
            ip = ipaddress.ip_address(sockaddr[0])
            for network in _PRIVATE_NETWORKS:
                if ip in network:
                    return (
                        f"SSRF blocked: {parsed.hostname} resolves to private IP {ip}"
                    )
    except socket.gaierror:
        return f"DNS resolution failed for {parsed.hostname}"

    return None
