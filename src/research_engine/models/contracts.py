"""Downstream contract types for inter-feature communication.

KeywordRecord is the flat contract consumed by F-002 (Clustering),
F-003 (Intent Classification), and F-007 (Content Calendar).

This contract is frozen — changes require updating both Python and
target TypeScript versions.
"""

from __future__ import annotations

import uuid
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from src.research_engine.models.keyword import (
    SUPPORTED_LOCALES,
    DifficultySource,
    GapStatus,
    KeywordIntent,
    KeywordSource,
)


class KeywordRecord(BaseModel):
    """Flat contract combining Keyword + primary metric data.

    This is the output contract from F-001 consumed by downstream features.
    """

    id: str
    tenant_id: uuid.UUID
    campaign_id: str
    term: str
    locale: str
    volume: int | None = None
    cpc: float | None = None
    difficulty: Annotated[int | None, Field(ge=0, le=100)] = None
    difficulty_source: DifficultySource | None = None
    intent: KeywordIntent | None = None
    gap_status: GapStatus = GapStatus.NEW_OPPORTUNITY
    source: KeywordSource

    @field_validator("locale")
    @classmethod
    def validate_locale(cls, v: str) -> str:
        """Validate locale is in the supported set."""
        if v not in SUPPORTED_LOCALES:
            msg = f"Unsupported locale: {v}"
            raise ValueError(msg)
        return v
