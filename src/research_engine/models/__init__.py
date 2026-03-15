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

__all__ = [
    "ContentFormat",
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
]
