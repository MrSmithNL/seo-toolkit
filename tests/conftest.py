"""Shared test fixtures for the SEO Toolkit test suite."""

import json
from pathlib import Path

import pytest


@pytest.fixture
def sample_config() -> dict:
    """Return a minimal valid site configuration dictionary."""
    return {
        "name": "Test Site",
        "domain": "example.com",
        "primary_keywords": ["test keyword"],
        "competitors": [],
        "schedule": {
            "audit": "weekly",
            "rank_check": "daily",
        },
    }


@pytest.fixture
def config_file(sample_config: dict, tmp_path: Path) -> Path:
    """Write sample config to a temporary JSON file and return its path."""
    config_path = tmp_path / "test.config.json"
    config_path.write_text(json.dumps(sample_config))
    return config_path
