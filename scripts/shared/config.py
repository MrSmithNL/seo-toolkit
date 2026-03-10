"""Configuration loader for SEO Toolkit site configs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_site_config(config_path: str | Path) -> dict[str, Any]:
    """Load a site configuration JSON file.

    Args:
        config_path: Path to the site config JSON file.

    Returns:
        Parsed configuration dictionary.

    Raises:
        FileNotFoundError: If the config file does not exist.
        json.JSONDecodeError: If the config file is not valid JSON.
    """
    path = Path(config_path)
    if not path.exists():
        msg = f"Config file not found: {path}"
        raise FileNotFoundError(msg)
    with path.open() as f:
        return json.load(f)  # type: ignore[no-any-return]


def get_configs_dir() -> Path:
    """Return the path to the configs directory.

    Returns:
        Absolute path to the configs/ directory.
    """
    return Path(__file__).resolve().parent.parent.parent / "configs"
