"""Intent classification enums and contract types for F-003.

Defines IntentType, IntentConfidence, ContentFormat enums and
the IntentClassification Pydantic model. These are the single
source of truth for intent data structures.

TypeScript equivalent: contracts/intent-type.ts, contracts/content-format.ts
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class IntentType(StrEnum):
    """Search intent classification (4-type taxonomy).

    Industry-standard taxonomy matching all major SEO tools.
    """

    INFORMATIONAL = "informational"
    COMMERCIAL = "commercial"
    TRANSACTIONAL = "transactional"
    NAVIGATIONAL = "navigational"


class IntentConfidence(StrEnum):
    """Confidence level for intent classification."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ContentFormat(StrEnum):
    """Recommended content format for a keyword.

    Fixed enum for R1 — extensible in R2+ via config.
    """

    HOW_TO_GUIDE = "how-to-guide"
    DEFINITION_EXPLAINER = "definition-explainer"
    COMPARISON_ARTICLE = "comparison-article"
    LISTICLE = "listicle"
    FAQ_PAGE = "faq-page"
    PRODUCT_LANDING_PAGE = "product-landing-page"
    CATEGORY_PAGE = "category-page"
    LOCATION_PAGE = "location-page"
    BRAND_NAVIGATIONAL_PAGE = "brand-navigational-page"


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class IntentClassification(BaseModel):
    """A single keyword's intent classification result.

    Produced by the LLM classification pipeline (F-003).
    """

    keyword: str = Field(min_length=1)
    intent: IntentType
    confidence: IntentConfidence
    rationale: str = Field(min_length=1)
    recommended_format: ContentFormat
    format_signal: str | None = None

    @field_validator("rationale", mode="before")
    @classmethod
    def strip_rationale(cls, v: str) -> str:
        """Strip whitespace; reject blank rationales."""
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                msg = "Rationale must not be empty or whitespace-only"
                raise ValueError(msg)
            return stripped
        return v
