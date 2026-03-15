"""Research Engine configuration via environment variables.

Uses Pydantic BaseSettings to load config from .env files and
environment variables. API keys use SecretStr to prevent leaking.
"""

from __future__ import annotations

from typing import Literal

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ResearchConfig(BaseSettings):
    """Configuration for the Research Engine module.

    Loads from environment variables and .env file.
    API keys are wrapped in SecretStr to prevent accidental exposure
    in logs, repr, or error messages.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Environment
    environment: str = "production"

    # Feature flags
    feature_keyword_research: bool = False
    feature_topic_clustering: bool = False
    feature_intent_classification: bool = False

    # Intent classification (F-003)
    intent_chunk_size: int = 50
    intent_max_retries: int = 1

    # Storage
    storage_mode: Literal["sqlite", "json"] = "json"

    # API keys (SecretStr prevents leaking in logs/repr)
    keywords_everywhere_api_key: SecretStr | None = None
    dataforseo_login: str | None = None
    dataforseo_password: SecretStr | None = None

    # Crawling limits
    max_crawl_pages: int = 50

    # Autocomplete rate limiting
    autocomplete_daily_limit: int = 100
    autocomplete_delay_seconds: float = 2.0

    # SERP analysis (F-004)
    feature_serp_analysis: bool = False
    serp_daily_limit: int = 50
    serp_daily_limit_google: int = 30
    serp_cache_days: int = 7
    serp_google_delay_seconds: float = 5.0

    # Competitor analysis (F-005)
    feature_competitor_analysis: bool = False
    crawl_min_delay_ms: int = 500
    crawl_max_concurrent: int = 2
    crawl_max_retries: int = 3
    crawl_user_agent: str = "SEOToolkit/1.0 (Competitor Analysis)"
    quality_llm_model: str = "claude-haiku"
    quality_batch_size: int = 5
    quality_max_input_chars: int = 8000
    quality_max_tokens_per_page: int = 2000
