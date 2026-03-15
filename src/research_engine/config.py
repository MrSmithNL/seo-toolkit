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
