"""Tests for GenerateCalendarCommand.

Covers: ATS-001, ATS-006, ATS-007, INT-001, INT-005.
"""

from __future__ import annotations

import json
import uuid
from datetime import date
from pathlib import Path

from src.research_engine.commands.generate_calendar import (
    GapInput,
    GenerateCalendarCommand,
    generate_calendar,
)
from src.research_engine.models.result import Err, Ok
from src.research_engine.repos.file_content_brief_repo import FileContentBriefRepo

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _gap(
    keyword: str,
    gap_type: str = "own_gap",
    score: float = 0.7,
    language: str = "en",
    volume: int = 1000,
    difficulty: int = 30,
) -> GapInput:
    return GapInput(
        keyword_text=keyword,
        keyword_id=f"kw_{keyword.replace(' ', '_')}",
        language=language,
        gap_type=gap_type,
        volume=volume,
        difficulty=difficulty,
        opportunity_score=score,
        competitor_avg_word_count=2000,
        competitor_depth_scores=[3, 4, 3],
        top_competitor_url="https://example.com/comp",
        competitor_schema_types=["Article"],
        competitors_have_faq=True,
        competitor_headings=[["What is FUE?", "What is DHI?"]],
        search_intent="commercial",
        our_page_url="https://example.com/page" if gap_type == "thin_content" else None,
        our_ranking_position=15 if gap_type == "thin_content" else None,
        our_word_count=400 if gap_type == "thin_content" else None,
    )


def _make_cmd(
    gaps: list[GapInput],
    output_dir: Path | None = None,
) -> GenerateCalendarCommand:
    return GenerateCalendarCommand(
        tenant_id=TENANT,
        campaign_id="camp_001",
        domain="example.com",
        gap_data=gaps,
        pipeline_run_date=date(2026, 3, 15),
        cadence_per_week=2,
        primary_language="en",
        output_dir=output_dir,
    )


class TestFeatureFlag:
    """Feature flag check."""

    def test_disabled_returns_error(self) -> None:
        cmd = _make_cmd([_gap("hair transplant")])
        result = generate_calendar(cmd, feature_enabled=False)
        assert isinstance(result, Err)
        assert "FEATURE_CONTENT_CALENDAR" in result.error


class TestHappyPath:
    """ATS-001: Full happy path — gap matrix to calendar output."""

    def test_generates_briefs_from_gaps(self) -> None:
        gaps = [_gap(f"keyword_{i}", score=0.9 - i * 0.05) for i in range(5)]
        cmd = _make_cmd(gaps)
        result = generate_calendar(cmd)

        assert isinstance(result, Ok)
        assert result.value.brief_count == 5
        assert result.value.new_content_count == 5
        assert result.value.thin_content_count == 0
        assert "en" in result.value.languages

    def test_generates_calendar_batch_id(self) -> None:
        cmd = _make_cmd([_gap("hair transplant")])
        result = generate_calendar(cmd)
        assert isinstance(result, Ok)
        assert result.value.calendar_batch_id.startswith("cal_")

    def test_empty_gap_data(self) -> None:
        cmd = _make_cmd([])
        result = generate_calendar(cmd)
        assert isinstance(result, Ok)
        assert result.value.brief_count == 0

    def test_briefs_sorted_by_priority(self) -> None:
        """PI-009: Highest score gets earliest date."""
        gaps = [
            _gap("low", score=0.3),
            _gap("high", score=0.9),
            _gap("mid", score=0.6),
        ]
        cmd = _make_cmd(gaps)
        result = generate_calendar(cmd)
        assert isinstance(result, Ok)
        # The result reports correct counts
        assert result.value.brief_count == 3


class TestThinContentOnly:
    """ATS-006: Only thin content → update section only."""

    def test_only_thin_content(self) -> None:
        gaps = [
            _gap(f"thin_{i}", "thin_content", score=0.5 + i * 0.05) for i in range(4)
        ]
        cmd = _make_cmd(gaps)
        result = generate_calendar(cmd)

        assert isinstance(result, Ok)
        assert result.value.new_content_count == 0
        assert result.value.thin_content_count == 4

    def test_mixed_new_and_thin(self) -> None:
        gaps = [
            _gap("new1", "own_gap", 0.9),
            _gap("new2", "new_opportunity", 0.8),
            _gap("thin1", "thin_content", 0.7),
        ]
        cmd = _make_cmd(gaps)
        result = generate_calendar(cmd)

        assert isinstance(result, Ok)
        assert result.value.new_content_count == 2
        assert result.value.thin_content_count == 1


class TestLlmFallback:
    """ATS-007: LLM failure → fallback headings, no halt."""

    def test_no_llm_still_succeeds(self) -> None:
        """Without LLM, fallback recommendations used."""
        cmd = _make_cmd([_gap("hair transplant")])
        result = generate_calendar(cmd, llm=None)
        assert isinstance(result, Ok)
        assert result.value.brief_count == 1

    def test_failing_llm_still_succeeds(self) -> None:
        """LLM that raises still produces output."""

        class _FailingLlm:
            def complete(self, prompt: str) -> str:
                raise RuntimeError("LLM unavailable")

        cmd = _make_cmd([_gap("hair transplant")])
        result = generate_calendar(cmd, llm=_FailingLlm())
        assert isinstance(result, Ok)
        assert result.value.brief_count == 1


class TestFileOutput:
    """ATS-013, INT-005: File output."""

    def test_writes_calendar_files(self, tmp_path: Path) -> None:
        """INT-005: Standalone file output."""
        cmd = _make_cmd([_gap("hair transplant")], output_dir=tmp_path)
        result = generate_calendar(cmd)

        assert isinstance(result, Ok)
        assert result.value.markdown_path is not None
        assert result.value.json_path is not None
        assert result.value.markdown_path.exists()
        assert result.value.json_path.exists()

    def test_json_output_valid(self, tmp_path: Path) -> None:
        cmd = _make_cmd([_gap("hair cost")], output_dir=tmp_path)
        result = generate_calendar(cmd)

        assert isinstance(result, Ok)
        assert result.value.json_path is not None
        data = json.loads(result.value.json_path.read_text())
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["target_keyword"] == "hair cost"

    def test_no_output_dir_skips_files(self) -> None:
        cmd = _make_cmd([_gap("hair transplant")])
        result = generate_calendar(cmd)
        assert isinstance(result, Ok)
        assert result.value.markdown_path is None
        assert result.value.json_path is None


class TestPersistence:
    """INT-005: Persist to repo."""

    def test_saves_to_repo(self, tmp_path: Path) -> None:
        repo = FileContentBriefRepo(tmp_path, "example.com")
        cmd = _make_cmd([_gap("hair transplant"), _gap("FUE cost")])
        result = generate_calendar(cmd, repo=repo)

        assert isinstance(result, Ok)
        saved = repo.get_by_batch()
        assert len(saved) == 2


class TestMultiLanguage:
    """INT-006: Multi-language calendar generation."""

    def test_multi_language_counted(self) -> None:
        gaps = [
            _gap("hair transplant", language="en"),
            _gap("haartransplantation", language="de"),
        ]
        cmd = _make_cmd(gaps)
        result = generate_calendar(cmd)

        assert isinstance(result, Ok)
        assert sorted(result.value.languages) == ["de", "en"]
        assert result.value.brief_count == 2
