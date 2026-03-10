"""Tests for the shared config module."""

import json
from pathlib import Path

import pytest

from scripts.shared.config import get_configs_dir, load_site_config


class TestLoadSiteConfig:
    """Tests for load_site_config."""

    def test_loads_valid_config(self, config_file: Path, sample_config: dict) -> None:
        """Test that a valid JSON config file loads correctly."""
        result = load_site_config(config_file)
        assert result == sample_config

    def test_returns_domain(self, config_file: Path) -> None:
        """Test that domain field is accessible from loaded config."""
        result = load_site_config(config_file)
        assert result["domain"] == "example.com"

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        """Test that FileNotFoundError is raised for missing config."""
        with pytest.raises(FileNotFoundError):
            load_site_config(tmp_path / "nonexistent.json")

    def test_raises_on_invalid_json(self, tmp_path: Path) -> None:
        """Test that JSONDecodeError is raised for invalid JSON."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json{{{")
        with pytest.raises(json.JSONDecodeError):
            load_site_config(bad_file)


class TestGetConfigsDir:
    """Tests for get_configs_dir."""

    def test_returns_path_object(self) -> None:
        """Test that get_configs_dir returns a Path."""
        result = get_configs_dir()
        assert isinstance(result, Path)

    def test_ends_with_configs(self) -> None:
        """Test that the returned path ends with 'configs'."""
        result = get_configs_dir()
        assert result.name == "configs"
