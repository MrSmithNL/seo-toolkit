"""Research Engine module factory.

Wires adapters based on configuration (real adapters for production,
mock adapters for test mode).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.research_engine.config import ResearchConfig


@dataclass
class ResearchModule:
    """Container for all Research Engine dependencies.

    Holds references to config and adapters. Created via
    create_research_module() factory.
    """

    config: ResearchConfig


def create_research_module(
    config: ResearchConfig | None = None,
) -> ResearchModule:
    """Create a wired ResearchModule from configuration.

    Args:
        config: Optional config override. If None, loads from env.

    Returns:
        A configured ResearchModule with adapters wired.
    """
    if config is None:
        config = ResearchConfig()

    return ResearchModule(config=config)
