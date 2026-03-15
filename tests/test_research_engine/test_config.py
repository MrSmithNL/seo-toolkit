"""Tests for research engine config and module bootstrap.

TDD: These tests are written BEFORE the implementation.
Covers: T-010 (Config Validation & Module Bootstrap)
"""

from __future__ import annotations

import pytest
from pydantic import SecretStr, ValidationError

from src.research_engine.config import ResearchConfig
from src.research_engine.module import ResearchModule, create_research_module


class TestResearchConfig:
    """Tests for the ResearchConfig settings model."""

    def test_creates_valid_config_with_defaults(self) -> None:
        """Config with no env vars uses sensible defaults."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.environment == "test"
        assert config.feature_keyword_research is False
        assert config.storage_mode == "json"
        assert config.max_crawl_pages == 50

    def test_feature_flag_defaults_false(self) -> None:
        """FEATURE_KEYWORD_RESEARCH defaults to False."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.feature_keyword_research is False

    def test_api_key_is_secret_str(self) -> None:
        """API keys must be SecretStr to prevent leaking in logs."""
        config = ResearchConfig(
            environment="test",
            keywords_everywhere_api_key="sk-test-key-123",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert isinstance(config.keywords_everywhere_api_key, SecretStr)

    def test_secret_str_not_in_repr(self) -> None:
        """SecretStr must not leak in repr or str."""
        config = ResearchConfig(
            environment="test",
            keywords_everywhere_api_key="sk-test-key-123",
            _env_file=None,  # type: ignore[call-arg]
        )
        config_repr = repr(config)
        assert "sk-test-key-123" not in config_repr

    def test_secret_str_not_in_str(self) -> None:
        """SecretStr must not leak in string conversion."""
        config = ResearchConfig(
            environment="test",
            keywords_everywhere_api_key="sk-test-key-123",
            _env_file=None,  # type: ignore[call-arg]
        )
        config_str = str(config)
        assert "sk-test-key-123" not in config_str

    def test_test_mode_allows_missing_api_keys(self) -> None:
        """In test mode, missing API keys are OK."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.keywords_everywhere_api_key is None
        assert config.dataforseo_login is None

    def test_storage_mode_accepts_sqlite(self) -> None:
        """Storage mode 'sqlite' is valid."""
        config = ResearchConfig(
            environment="test",
            storage_mode="sqlite",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.storage_mode == "sqlite"

    def test_storage_mode_accepts_json(self) -> None:
        """Storage mode 'json' is valid."""
        config = ResearchConfig(
            environment="test",
            storage_mode="json",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.storage_mode == "json"

    def test_storage_mode_rejects_invalid(self) -> None:
        """Invalid storage mode must be rejected."""
        with pytest.raises(ValidationError):
            ResearchConfig(
                environment="test",
                storage_mode="redis",  # type: ignore[arg-type]
                _env_file=None,  # type: ignore[call-arg]
            )

    def test_autocomplete_config_defaults(self) -> None:
        """Autocomplete settings have sensible defaults."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.autocomplete_daily_limit == 100
        assert config.autocomplete_delay_seconds == 2.0

    def test_max_crawl_pages_default(self) -> None:
        """Max crawl pages defaults to 50."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.max_crawl_pages == 50

    def test_intent_classification_flag_defaults_false(self) -> None:
        """FEATURE_INTENT_CLASSIFICATION defaults to False."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.feature_intent_classification is False

    def test_intent_classification_flag_can_enable(self) -> None:
        """Intent classification can be enabled via config."""
        config = ResearchConfig(
            environment="test",
            feature_intent_classification=True,
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.feature_intent_classification is True

    def test_intent_chunk_size_default(self) -> None:
        """Intent chunk size defaults to 50."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.intent_chunk_size == 50

    def test_intent_max_retries_default(self) -> None:
        """Intent max retries defaults to 1."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        assert config.intent_max_retries == 1


class TestCreateResearchModule:
    """Tests for the module factory function."""

    def test_creates_module_in_test_mode(self) -> None:
        """Factory creates a valid module in test mode."""
        config = ResearchConfig(
            environment="test",
            feature_keyword_research=True,
            _env_file=None,  # type: ignore[call-arg]
        )
        module = create_research_module(config)
        assert isinstance(module, ResearchModule)
        assert module.config is config

    def test_module_has_config_reference(self) -> None:
        """Module holds a reference to its config."""
        config = ResearchConfig(
            environment="test",
            _env_file=None,  # type: ignore[call-arg]
        )
        module = create_research_module(config)
        assert module.config.environment == "test"
        assert module.config.storage_mode == "json"
