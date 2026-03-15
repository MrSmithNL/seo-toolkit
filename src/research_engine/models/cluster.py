"""Keyword cluster models for the Research Engine.

Pydantic v2 models for F-002 Topic Clustering. Each cluster groups
semantically related keywords with a pillar keyword and coherence score.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.research_engine.models.keyword import SUPPORTED_LOCALES


def _generate_tc_id() -> str:
    """Generate a prefixed topic cluster ID."""
    return f"tc_{uuid.uuid4().hex[:12]}"


def _now_utc() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(tz=UTC)


class KeywordCluster(BaseModel):
    """Topic cluster grouping semantically related keywords.

    Maps to the `keyword_cluster` table in the target Drizzle schema.
    """

    model_config = ConfigDict(use_enum_values=False)

    id: str = Field(default_factory=_generate_tc_id)
    tenant_id: Annotated[uuid.UUID, Field()]
    campaign_id: str
    locale: str
    name: str = Field(min_length=1)
    rationale: str
    pillar_keyword_id: str | None = None
    pillar_rationale: str | None = None
    keyword_count: int = 0
    coherence_score: Annotated[int | None, Field(ge=1, le=10)] = None
    coherence_rationale: str | None = None
    no_pillar_flag: str | None = None
    prompt_version: str = "clustering-v1"
    llm_tokens_used: int | None = None
    deleted_at: datetime | None = None
    created_at: datetime = Field(default_factory=_now_utc)
    updated_at: datetime = Field(default_factory=_now_utc)

    @field_validator("locale")
    @classmethod
    def validate_locale(cls, v: str) -> str:
        """Validate locale is in the supported set."""
        if v not in SUPPORTED_LOCALES:
            msg = f"Unsupported locale: {v}. Must be one of {sorted(SUPPORTED_LOCALES)}"
            raise ValueError(msg)
        return v
