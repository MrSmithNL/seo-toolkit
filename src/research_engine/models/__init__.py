"""Research Engine domain models."""

from src.research_engine.models.contracts import KeywordRecord
from src.research_engine.models.intent import (
    ContentFormat,
    IntentClassification,
    IntentConfidence,
    IntentType,
)
from src.research_engine.models.keyword import (
    DifficultySource,
    GapStatus,
    Keyword,
    KeywordGap,
    KeywordIntent,
    KeywordMetric,
    KeywordSource,
)
from src.research_engine.models.result import Err, Ok, Result
from src.research_engine.models.serp import (
    ApiSource,
    ContentType,
    SerpFeatures,
    SerpResult,
    SerpSnapshot,
)

__all__ = [
    "ApiSource",
    "ContentFormat",
    "ContentType",
    "DifficultySource",
    "Err",
    "GapStatus",
    "IntentClassification",
    "IntentConfidence",
    "IntentType",
    "Keyword",
    "KeywordGap",
    "KeywordIntent",
    "KeywordMetric",
    "KeywordRecord",
    "KeywordSource",
    "Ok",
    "Result",
    "SerpFeatures",
    "SerpResult",
    "SerpSnapshot",
]
