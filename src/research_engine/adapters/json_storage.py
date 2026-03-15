"""JSON file storage adapter for keywords.

Stores keywords as JSON files on disk. Used for standalone CLI mode.
Implements the KeywordStoragePort protocol.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path

from src.research_engine.models.keyword import Keyword, KeywordGap

logger = logging.getLogger(__name__)


class JsonFileKeywordAdapter:
    """JSON file-based keyword storage.

    Stores keywords grouped by campaign_id in separate JSON files.

    Args:
        data_dir: Root directory for JSON files.
    """

    def __init__(self, data_dir: Path) -> None:  # noqa: D107
        self._data_dir = data_dir
        self._data_dir.mkdir(parents=True, exist_ok=True)

    def _keywords_path(self, campaign_id: str) -> Path:
        """Get the JSON file path for a campaign's keywords."""
        return self._data_dir / f"keywords_{campaign_id}.json"

    def _gaps_path(self, campaign_id: str) -> Path:
        """Get the JSON file path for a campaign's gaps."""
        return self._data_dir / f"gaps_{campaign_id}.json"

    def _load_keywords(self, campaign_id: str) -> dict[str, dict]:
        """Load keywords from JSON file, keyed by normalized_key."""
        path = self._keywords_path(campaign_id)
        if not path.exists():
            return {}
        data = json.loads(path.read_text())
        return {item["normalized_key"]: item for item in data}

    def _persist_keywords(self, campaign_id: str, store: dict[str, dict]) -> None:
        """Write keywords dict to JSON file."""
        path = self._keywords_path(campaign_id)
        path.write_text(json.dumps(list(store.values()), indent=2, default=str))

    def save(self, keywords: list[Keyword]) -> int:
        """Save keywords with upsert by campaign_id + normalized_key.

        Args:
            keywords: List of keywords to persist.

        Returns:
            Number of keywords saved/updated.
        """
        by_campaign: dict[str, list[Keyword]] = {}
        for kw in keywords:
            by_campaign.setdefault(kw.campaign_id, []).append(kw)

        total = 0
        for campaign_id, kws in by_campaign.items():
            store = self._load_keywords(campaign_id)
            for kw in kws:
                store[kw.normalized_key] = kw.model_dump(mode="json")
                total += 1
            self._persist_keywords(campaign_id, store)

        return total

    def get_by_campaign(
        self,
        campaign_id: str,
        locale: str | None = None,
        min_volume: int | None = None,
        max_difficulty: int | None = None,
    ) -> list[Keyword]:
        """Query keywords with optional filters.

        Args:
            campaign_id: Campaign to query.
            locale: Optional locale filter (not used in JSON mode).
            min_volume: Optional minimum volume filter.
            max_difficulty: Optional max difficulty filter.

        Returns:
            Filtered list of keywords.
        """
        store = self._load_keywords(campaign_id)
        results: list[Keyword] = []
        for data in store.values():
            kw = Keyword.model_validate(data)
            if min_volume is not None and (kw.difficulty or 0) < min_volume:
                continue
            if max_difficulty is not None and (kw.difficulty or 0) > max_difficulty:
                continue
            results.append(kw)
        return results

    def save_gaps(self, gaps: list[KeywordGap]) -> int:
        """Save keyword gap records.

        Args:
            gaps: List of gap records.

        Returns:
            Number of gaps saved.
        """
        by_campaign: dict[str, list[dict]] = {}
        for gap in gaps:
            by_campaign.setdefault(gap.campaign_id, []).append(
                gap.model_dump(mode="json")
            )

        total = 0
        for campaign_id, gap_dicts in by_campaign.items():
            path = self._gaps_path(campaign_id)
            existing: list[dict] = []
            if path.exists():
                existing = json.loads(path.read_text())
            existing.extend(gap_dicts)
            path.write_text(json.dumps(existing, indent=2, default=str))
            total += len(gap_dicts)

        return total

    def get_gaps(self, campaign_id: str) -> list[KeywordGap]:
        """Get all gap records for a campaign.

        Args:
            campaign_id: Campaign to query.

        Returns:
            List of gap records.
        """
        path = self._gaps_path(campaign_id)
        if not path.exists():
            return []
        data = json.loads(path.read_text())
        return [KeywordGap.model_validate(item) for item in data]

    def update_intent_fields(
        self,
        keyword_id: str,
        intent: str,
        intent_confidence: str,
        intent_rationale: str,
        recommended_format: str,
        format_signal: str | None,
        classified_at: datetime,
    ) -> bool:
        """Update intent classification fields on a keyword.

        Args:
            keyword_id: ID of the keyword to update.
            intent: Intent type string.
            intent_confidence: Confidence level string.
            intent_rationale: One-sentence rationale.
            recommended_format: Content format string.
            format_signal: Detected signal or None.
            classified_at: When classification was performed.

        Returns:
            True if keyword was found and updated.
        """
        for path in self._data_dir.glob("keywords_*.json"):
            data = json.loads(path.read_text())
            modified = False
            for item in data:
                if item.get("id") == keyword_id:
                    item["intent"] = intent
                    item["intent_confidence"] = intent_confidence
                    item["intent_rationale"] = intent_rationale
                    item["recommended_format"] = recommended_format
                    item["format_signal"] = format_signal
                    item["classified_at"] = classified_at.isoformat()
                    modified = True
                    break
            if modified:
                path.write_text(json.dumps(data, indent=2, default=str))
                return True
        return False
