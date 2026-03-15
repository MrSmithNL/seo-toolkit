"""Keywords Everywhere API adapter for volume and trend data.

Batch POST endpoint accepting up to 100 keywords per call.
Implements retry with exponential backoff on 429/5xx errors.
"""

from __future__ import annotations

import logging
import time

import httpx
from pydantic import SecretStr

from src.research_engine.ports.data_source import KeywordVolumeResult

logger = logging.getLogger(__name__)

API_URL = "https://api.keywordseverywhere.com/v1/get_keyword_data"
BATCH_SIZE = 100
MAX_RETRIES = 3


class KeywordsEverywhereAdapter:
    """Keywords Everywhere API adapter.

    Implements KeywordDataSource protocol with 'volume', 'suggestions',
    'trends' capabilities.

    Args:
        api_key: API key (SecretStr to prevent leaking).
        base_retry_delay: Base delay for exponential backoff (seconds).
    """

    def __init__(  # noqa: D107
        self,
        api_key: SecretStr,
        base_retry_delay: float = 1.0,
    ) -> None:
        self._api_key = api_key
        self._base_retry_delay = base_retry_delay

    @property
    def capabilities(self) -> set[str]:
        """Return supported capabilities."""
        return {"volume", "suggestions", "trends"}

    def _compute_batches(self, keywords: list[str]) -> list[list[str]]:
        """Split keywords into batches of BATCH_SIZE.

        Args:
            keywords: Full list of keywords.

        Returns:
            List of keyword batches.
        """
        return [
            keywords[i : i + BATCH_SIZE] for i in range(0, len(keywords), BATCH_SIZE)
        ]

    def get_keyword_volume(
        self,
        keywords: list[str],
        locale: str,
        country: str,
    ) -> list[KeywordVolumeResult]:
        """Fetch volume, CPC, and trends for keywords.

        Splits into batches of 100 and retries on transient errors.

        Args:
            keywords: List of keyword terms.
            locale: Language locale (e.g. 'en', 'de').
            country: Country code (e.g. 'US', 'DE').

        Returns:
            List of volume results. Empty on persistent failure.
        """
        batches = self._compute_batches(keywords)
        all_results: list[KeywordVolumeResult] = []

        for batch in batches:
            batch_results = self._fetch_batch(batch, country)
            all_results.extend(batch_results)

        return all_results

    def _fetch_batch(
        self,
        keywords: list[str],
        country: str,
    ) -> list[KeywordVolumeResult]:
        """Fetch a single batch of keywords with retry.

        Args:
            keywords: Batch of keyword terms (max 100).
            country: Country code.

        Returns:
            List of volume results for this batch.
        """
        for attempt in range(MAX_RETRIES + 1):
            try:
                client = httpx.Client()
                response = client.post(
                    API_URL,
                    headers={
                        "Authorization": f"Bearer {self._api_key.get_secret_value()}",
                    },
                    data={
                        "dataSource": "gkp",
                        "country": country,
                        "kw[]": keywords,
                    },
                    timeout=30.0,
                )
                client.close()

                if response.status_code == 200:  # noqa: PLR2004
                    return self._parse_response(response.json())

                if (  # noqa: SIM102
                    response.status_code in (429, 500, 502, 503, 504)
                    and attempt < MAX_RETRIES
                ):
                    delay = self._base_retry_delay * (2**attempt)
                    logger.warning(
                        "KE API returned %d, retrying in %.1fs (attempt %d/%d)",
                        response.status_code,
                        delay,
                        attempt + 1,
                        MAX_RETRIES,
                    )
                    time.sleep(delay)
                    continue

                logger.error(
                    "KE API returned %d after %d attempts",
                    response.status_code,
                    attempt + 1,
                )
                return []

            except httpx.HTTPError as exc:
                if attempt < MAX_RETRIES:
                    delay = self._base_retry_delay * (2**attempt)
                    logger.warning("KE API error: %s, retrying in %.1fs", exc, delay)
                    time.sleep(delay)
                    continue
                logger.error("KE API error after %d attempts: %s", MAX_RETRIES, exc)
                return []

        return []

    def _parse_response(self, data: dict) -> list[KeywordVolumeResult]:
        """Parse Keywords Everywhere API response.

        Args:
            data: Parsed JSON response.

        Returns:
            List of KeywordVolumeResult objects.
        """
        results: list[KeywordVolumeResult] = []
        for item in data.get("data", []):
            results.append(
                KeywordVolumeResult(
                    keyword=item["keyword"],
                    volume=item.get("vol"),
                    cpc=item.get("cpc"),
                    trend=item.get("trend"),
                )
            )
        return results

    def get_keyword_suggestions(
        self,
        seed: str,
        locale: str,
    ) -> list[str]:
        """Not the primary use — delegates to volume endpoint."""
        msg = "Use get_keyword_volume for Keywords Everywhere"
        raise NotImplementedError(msg)

    def __repr__(self) -> str:
        """Safe repr that hides the API key."""
        return "KeywordsEverywhereAdapter(api_key=***)"
