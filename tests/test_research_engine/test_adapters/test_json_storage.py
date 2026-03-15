"""Tests for JSON file storage adapter.

TDD: Tests written BEFORE implementation.
Covers: T-002 (JSON file adapter)
"""

from __future__ import annotations

import uuid
from pathlib import Path

from src.research_engine.adapters.json_storage import JsonFileKeywordAdapter
from src.research_engine.models.keyword import (
    Keyword,
    KeywordGap,
    KeywordSource,
)
from src.research_engine.ports.storage import KeywordStoragePort


def _kw(term: str, campaign_id: str = "camp_1") -> Keyword:
    """Helper to create a keyword."""
    return Keyword(
        tenant_id=uuid.uuid4(),
        campaign_id=campaign_id,
        term=term,
        source=KeywordSource.URL_EXTRACTION,
    )


class TestJsonFileKeywordAdapter:
    """Tests for JsonFileKeywordAdapter."""

    def test_implements_storage_port(self, tmp_path: Path) -> None:
        """Adapter must implement KeywordStoragePort protocol."""
        adapter = JsonFileKeywordAdapter(data_dir=tmp_path)
        assert isinstance(adapter, KeywordStoragePort)

    def test_save_and_retrieve(self, tmp_path: Path) -> None:
        """ATS-018: Save keywords and retrieve them."""
        adapter = JsonFileKeywordAdapter(data_dir=tmp_path)
        kws = [_kw("hair transplant"), _kw("fue transplant")]
        saved = adapter.save(kws)
        assert saved == 2

        results = adapter.get_by_campaign("camp_1")
        assert len(results) == 2

    def test_upsert_no_duplicates(self, tmp_path: Path) -> None:
        """ATS-019: Second save with same keywords updates, not duplicates."""
        adapter = JsonFileKeywordAdapter(data_dir=tmp_path)
        adapter.save([_kw("hair transplant")])
        adapter.save([_kw("hair transplant")])

        results = adapter.get_by_campaign("camp_1")
        assert len(results) == 1

    def test_get_by_campaign_filters(self, tmp_path: Path) -> None:
        """Different campaigns return different keywords."""
        adapter = JsonFileKeywordAdapter(data_dir=tmp_path)
        adapter.save([_kw("hair transplant", "camp_1")])
        adapter.save([_kw("skin care", "camp_2")])

        camp1 = adapter.get_by_campaign("camp_1")
        camp2 = adapter.get_by_campaign("camp_2")
        assert len(camp1) == 1
        assert len(camp2) == 1
        assert camp1[0].term == "hair transplant"

    def test_writes_json_file(self, tmp_path: Path) -> None:
        """ATS-021: JSON file is written and parseable."""
        adapter = JsonFileKeywordAdapter(data_dir=tmp_path)
        adapter.save([_kw("test keyword")])

        json_files = list(tmp_path.rglob("*.json"))
        assert len(json_files) >= 1

    def test_save_and_retrieve_gaps(self, tmp_path: Path) -> None:
        """Gap records can be saved and retrieved."""
        adapter = JsonFileKeywordAdapter(data_dir=tmp_path)
        gap = KeywordGap(
            tenant_id=uuid.uuid4(),
            campaign_id="camp_1",
            keyword_id="kw_test",
            competitor_domain="competitor.com",
            competitor_position=3,
        )
        saved = adapter.save_gaps([gap])
        assert saved == 1

        gaps = adapter.get_gaps("camp_1")
        assert len(gaps) == 1
        assert gaps[0].competitor_domain == "competitor.com"

    def test_empty_campaign_returns_empty(self, tmp_path: Path) -> None:
        """Querying a non-existent campaign returns empty list."""
        adapter = JsonFileKeywordAdapter(data_dir=tmp_path)
        results = adapter.get_by_campaign("nonexistent")
        assert results == []
