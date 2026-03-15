"""Google Autocomplete adapter for keyword suggestions.

Queries Google's autocomplete endpoint to expand seed keywords.
Rate-limited: 2s between requests, 100 requests/day.
"""

from __future__ import annotations

import logging
import time

import httpx
from defusedxml import ElementTree

from src.research_engine.ports.data_source import KeywordVolumeResult

logger = logging.getLogger(__name__)

AUTOCOMPLETE_URL = "http://suggestqueries.google.com/complete/search"


class GoogleAutocompleteAdapter:
    """Google Autocomplete keyword suggestion adapter.

    Implements KeywordDataSource protocol with 'suggestions' capability.

    Args:
        daily_limit: Maximum requests per day.
        delay_seconds: Minimum seconds between requests.
    """

    def __init__(  # noqa: D107
        self,
        daily_limit: int = 100,
        delay_seconds: float = 2.0,
    ) -> None:
        self._daily_limit = daily_limit
        self._delay_seconds = delay_seconds
        self._calls_today = 0
        self._last_call_time: float = 0.0

    @property
    def capabilities(self) -> set[str]:
        """Return supported capabilities."""
        return {"suggestions"}

    @property
    def calls_today(self) -> int:
        """Return number of calls made today."""
        return self._calls_today

    def get_keyword_volume(
        self,
        keywords: list[str],
        locale: str,
        country: str,
    ) -> list[KeywordVolumeResult]:
        """Not supported — raises NotImplementedError."""
        msg = "GoogleAutocompleteAdapter does not support volume lookups"
        raise NotImplementedError(msg)

    def get_keyword_suggestions(
        self,
        seed: str,
        locale: str,
    ) -> list[str]:
        """Fetch autocomplete suggestions for a seed keyword.

        Args:
            seed: Seed keyword to expand.
            locale: Language locale (e.g. 'en', 'de').

        Returns:
            List of suggestion strings. Empty on error or rate limit.
        """
        if self._calls_today >= self._daily_limit:
            logger.warning("Daily autocomplete limit reached (%d)", self._daily_limit)
            return []

        # Rate limiting
        now = time.monotonic()
        elapsed = now - self._last_call_time
        if elapsed < self._delay_seconds and self._last_call_time > 0:
            time.sleep(self._delay_seconds - elapsed)

        try:
            client = httpx.Client()
            response = client.get(
                AUTOCOMPLETE_URL,
                params={"output": "toolbar", "q": seed, "hl": locale},
                timeout=10.0,
            )
            self._last_call_time = time.monotonic()
            self._calls_today += 1

            if response.status_code != 200:  # noqa: PLR2004
                logger.warning("Autocomplete returned status %d", response.status_code)
                return []

            return self._parse_xml(response.text)

        except httpx.HTTPError as exc:
            logger.warning("Autocomplete HTTP error: %s", exc)
            return []
        finally:
            client.close()

    def _parse_xml(self, xml_text: str) -> list[str]:
        """Parse autocomplete XML response.

        Args:
            xml_text: Raw XML response body.

        Returns:
            List of suggestion strings.
        """
        try:
            root = ElementTree.fromstring(xml_text)
        except ElementTree.ParseError:
            logger.warning("Failed to parse autocomplete XML")
            return []

        suggestions: list[str] = []
        for suggestion in root.iter("suggestion"):
            data = suggestion.get("data")
            if data:
                suggestions.append(data)

        return suggestions
