"""DataForSEO SERP API adapter.

Implements SerpDataSource protocol for the DataForSEO REST API.
Includes retry with exponential backoff (3x: 2s, 4s, 8s).
Credentials read from constructor args (injected from env vars by caller).

TypeScript equivalent: modules/content-engine/research/adapters/dataforseo-adapter.ts
"""

from __future__ import annotations

import base64
import logging
import time
from typing import Any

import httpx

from src.research_engine.models.serp import SerpFeatures
from src.research_engine.ports.serp_data_source import (
    RawSerpResponse,
    RawSerpResult,
)

logger = logging.getLogger(__name__)

_API_URL = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"

# Mapping from DataForSEO item_types to our canonical feature names
_FEATURE_MAP: dict[str, str] = {
    "ai_overview": "ai_overview",
    "featured_snippet": "featured_snippet",
    "people_also_ask": "people_also_ask",
    "knowledge_graph": "knowledge_panel",
    "images": "image_pack",
    "video": "video_carousel",
    "local_pack": "local_pack",
    "shopping": "shopping_results",
}


class DataForSeoAdapter:
    """DataForSEO SERP API adapter.

    Fetches top-10 organic results with SERP feature detection.
    Retries with configurable exponential backoff on failure.
    """

    def __init__(
        self,
        login: str,
        password: str,
        *,
        max_retries: int = 3,
        retry_delays: tuple[float, ...] = (2.0, 4.0, 8.0),
    ) -> None:
        """Initialise with credentials and retry config.

        Args:
            login: DataForSEO API login.
            password: DataForSEO API password.
            max_retries: Maximum number of retry attempts.
            retry_delays: Delay in seconds between retries.
        """
        self._login = login
        self._password = password
        self._max_retries = max_retries
        self._retry_delays = retry_delays

    def fetch_serp(
        self,
        keyword: str,
        language: str,
        country: str,
    ) -> RawSerpResponse:
        """Fetch SERP data from DataForSEO API.

        Args:
            keyword: Search query.
            language: BCP 47 language code (e.g., 'de').
            country: ISO 3166-1 country code (e.g., 'DE').

        Returns:
            Normalized SERP response.

        Raises:
            ConnectionError: After all retries exhausted.
        """
        payload = [
            {
                "keyword": keyword,
                "location_code": _country_to_location(country),
                "language_code": language,
                "depth": 10,
            }
        ]

        data = self._post_with_retry(payload)
        return self._parse_response(data)

    def _post_with_retry(self, payload: list[dict]) -> dict:
        """Post to API with exponential backoff retry.

        Args:
            payload: API request payload.

        Returns:
            Parsed JSON response.

        Raises:
            ConnectionError: After all retries exhausted.
        """
        last_error: Exception | None = None
        for attempt in range(1 + self._max_retries):
            try:
                data = self._post_api(payload)
                # Check for API-level error codes
                status = data.get("status_code", 0)
                if status >= 40000:
                    task = data.get("tasks", [{}])[0]
                    msg = task.get("status_message", "Unknown error")
                    if attempt < self._max_retries:
                        delay = self._retry_delays[
                            min(attempt, len(self._retry_delays) - 1)
                        ]
                        logger.warning(
                            "DataForSEO error (attempt %d/%d): %s. Retrying in %.1fs",
                            attempt + 1,
                            self._max_retries + 1,
                            msg,
                            delay,
                        )
                        time.sleep(delay)
                        continue
                    msg = f"DataForSEO API error after {attempt + 1} attempts: {msg}"
                    raise ConnectionError(msg)
                return data
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < self._max_retries:
                    delay = self._retry_delays[
                        min(attempt, len(self._retry_delays) - 1)
                    ]
                    logger.warning(
                        "DataForSEO request failed (attempt %d/%d): %s."
                        " Retrying in %.1fs",
                        attempt + 1,
                        self._max_retries + 1,
                        exc,
                        delay,
                    )
                    time.sleep(delay)
                    continue
                raise

        msg = f"DataForSEO API failed after {self._max_retries + 1} attempts"
        raise ConnectionError(msg) from last_error

    def _post_api(self, payload: list[dict]) -> dict[str, Any]:
        """Make the actual HTTP POST to DataForSEO API.

        Separated for easy mocking in tests.

        Args:
            payload: API request payload.

        Returns:
            Parsed JSON response dict.
        """
        auth_str = base64.b64encode(
            f"{self._login}:{self._password}".encode(),
        ).decode()
        with httpx.Client(timeout=10.0) as client:
            resp = client.post(
                _API_URL,
                json=payload,
                headers={
                    "Authorization": f"Basic {auth_str}",
                    "Content-Type": "application/json",
                },
            )
            resp.raise_for_status()
            result: dict[str, Any] = resp.json()
            return result

    def _parse_response(self, data: dict) -> RawSerpResponse:  # noqa: C901
        """Parse DataForSEO response into RawSerpResponse.

        Args:
            data: Raw API JSON response.

        Returns:
            Normalized SERP response.
        """
        tasks = data.get("tasks", [])
        if not tasks or not tasks[0].get("result"):
            return RawSerpResponse(
                organic_results=[],
                no_organic_results=True,
                api_source="dataforseo",
            )

        result = tasks[0]["result"][0]
        items = result.get("items", [])
        item_types = result.get("item_types", [])

        organic_results = _extract_organic(items)
        features = _build_features(item_types, items)

        return RawSerpResponse(
            organic_results=organic_results,
            features=features,
            no_organic_results=len(organic_results) == 0,
            api_source="dataforseo",
        )


def _extract_organic(items: list[dict]) -> list[RawSerpResult]:
    """Extract organic results from DataForSEO items."""
    results = []
    for item in items:
        if item.get("type") != "organic":
            continue
        results.append(
            RawSerpResult(
                position=item.get("rank_group", 0),
                url=item.get("url", ""),
                domain=item.get("domain", ""),
                title=item.get("title"),
                meta_description=item.get("description"),
                estimated_word_count=None,
                content_type=None,
            ),
        )
    return results


def _build_features(
    item_types: list[str],
    items: list[dict],
) -> SerpFeatures:
    """Build canonical SerpFeatures from DataForSEO data."""
    flags: dict[str, Any] = {}
    for item_type in item_types:
        canonical = _FEATURE_MAP.get(item_type)
        if canonical:
            flags[canonical] = True

    # Extract PAA questions
    paa: list[str] = []
    for item in items:
        if item.get("type") == "people_also_ask":
            for sub in item.get("items", [])[:5]:
                title = sub.get("title", "")
                if title:
                    paa.append(title)
    if paa:
        flags["paa_questions"] = paa

    return SerpFeatures(
        **{
            k: flags.get(k, False)
            for k in (
                "ai_overview",
                "featured_snippet",
                "people_also_ask",
                "knowledge_panel",
                "image_pack",
                "video_carousel",
                "local_pack",
                "shopping_results",
            )
        }
        | (
            {"paa_questions": flags["paa_questions"]}
            if "paa_questions" in flags
            else {}
        )
    )


def _country_to_location(country: str) -> int:
    """Map ISO 3166-1 country code to DataForSEO location code.

    Args:
        country: ISO 3166-1 alpha-2 country code.

    Returns:
        DataForSEO location code.
    """
    mapping = {
        "DE": 2276,
        "US": 2840,
        "GB": 2826,
        "FR": 2250,
        "NL": 2528,
        "ES": 2724,
        "IT": 2380,
        "PT": 2620,
        "PL": 2616,
        "TR": 2792,
    }
    return mapping.get(country, 2840)
