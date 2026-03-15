"""Tests for ApprovalWorkflow.

Covers: ATS-015, ATS-016, ATS-017, ATS-018, PI-010, PI-014.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

from src.research_engine.models.content_brief import (
    SCHEMA_VERSION,
    BriefStatus,
    ContentBrief,
    ContentType,
    GapType,
    SearchIntent,
)
from src.research_engine.models.result import Err, Ok
from src.research_engine.services.approval_workflow import (
    approve_brief,
    export_approved_briefs,
    load_briefs_from_json,
    reject_brief,
)

TENANT = uuid.UUID("12345678-1234-1234-1234-123456789abc")


def _make_brief(
    status: BriefStatus = BriefStatus.PENDING_REVIEW,
    score: float = 0.7,
    keyword: str = "hair transplant",
) -> ContentBrief:
    extra = {}
    if status in (BriefStatus.APPROVED, BriefStatus.REJECTED):
        extra = {
            "reviewed_by": "malcolm",
            "reviewed_at": datetime.now(tz=UTC),
        }
    return ContentBrief(
        tenant_id=TENANT,
        target_keyword=keyword,
        target_language="en",
        target_country="DE",
        search_intent=SearchIntent.COMMERCIAL,
        content_type=ContentType.BLOG_POST,
        keyword_volume=1000,
        keyword_difficulty=30,
        opportunity_score=score,
        opportunity_score_rationale=f"Score: {score}",
        gap_type=GapType.OWN_GAP,
        competitor_avg_word_count=2000,
        recommended_word_count=2200,
        suggested_publish_date="2026-03-16",
        status=status,
        **extra,
    )


class TestApproveBrief:
    """ATS-015, ATS-017, PI-014: Approve a brief."""

    def test_approve_pending_brief(self) -> None:
        """ATS-015: Approval sets audit fields."""
        brief = _make_brief()
        result = approve_brief(brief, reviewed_by="malcolm")
        assert isinstance(result, Ok)
        approved = result.value
        assert approved.status == BriefStatus.APPROVED
        assert approved.reviewed_by == "malcolm"
        assert approved.reviewed_at is not None

    def test_approve_with_word_count_override(self) -> None:
        """ATS-017: Word count override preserved alongside original."""
        brief = _make_brief()
        result = approve_brief(
            brief,
            reviewed_by="malcolm",
            overridden_word_count=2400,
        )
        assert isinstance(result, Ok)
        approved = result.value
        assert approved.overridden_word_count == 2400
        assert approved.recommended_word_count == 2200  # original preserved

    def test_approve_with_publish_date_override(self) -> None:
        brief = _make_brief()
        result = approve_brief(
            brief,
            reviewed_by="malcolm",
            overridden_publish_date="2026-04-01",
        )
        assert isinstance(result, Ok)
        assert result.value.overridden_publish_date == "2026-04-01"
        assert result.value.suggested_publish_date == "2026-03-16"

    def test_approve_with_notes(self) -> None:
        brief = _make_brief()
        result = approve_brief(brief, reviewed_by="malcolm", review_notes="Looks good")
        assert isinstance(result, Ok)
        assert result.value.review_notes == "Looks good"

    def test_approve_already_approved_fails(self) -> None:
        """State machine: approved → approved not allowed."""
        brief = _make_brief(BriefStatus.APPROVED)
        result = approve_brief(brief, reviewed_by="malcolm")
        assert isinstance(result, Err)
        assert "Invalid status transition" in result.error

    def test_approve_rejected_fails(self) -> None:
        """State machine: rejected → approved not allowed."""
        brief = _make_brief(BriefStatus.REJECTED)
        result = approve_brief(brief, reviewed_by="malcolm")
        assert isinstance(result, Err)


class TestRejectBrief:
    """ATS-016: Reject a brief."""

    def test_reject_pending_brief(self) -> None:
        brief = _make_brief()
        result = reject_brief(brief, reviewed_by="malcolm", review_notes="Not relevant")
        assert isinstance(result, Ok)
        assert result.value.status == BriefStatus.REJECTED
        assert result.value.reviewed_by == "malcolm"
        assert result.value.review_notes == "Not relevant"

    def test_reject_already_approved_fails(self) -> None:
        """State machine: approved → rejected not allowed."""
        brief = _make_brief(BriefStatus.APPROVED)
        result = reject_brief(brief, reviewed_by="malcolm")
        assert isinstance(result, Err)


class TestExportApprovedBriefs:
    """ATS-015, ATS-016, ATS-024, PI-010: Export approved briefs."""

    def test_export_only_approved(self, tmp_path: Path) -> None:
        """PI-010: Rejected briefs excluded from export."""
        approved = _make_brief(BriefStatus.APPROVED, keyword="approved kw")
        rejected = _make_brief(BriefStatus.REJECTED, keyword="rejected kw")
        pending = _make_brief(BriefStatus.PENDING_REVIEW, keyword="pending kw")

        output = tmp_path / "approved.json"
        result = export_approved_briefs(
            [approved, rejected, pending],
            campaign_id="camp_001",
            output_path=output,
        )

        assert isinstance(result, Ok)
        data = json.loads(output.read_text())
        assert data["schema_version"] == SCHEMA_VERSION
        assert len(data["briefs"]) == 1
        assert data["briefs"][0]["target_keyword"] == "approved kw"

    def test_export_validates_each_brief(self, tmp_path: Path) -> None:
        """ATS-024: Every record validated before writing."""
        brief = _make_brief(BriefStatus.APPROVED)
        output = tmp_path / "approved.json"
        result = export_approved_briefs(
            [brief],
            campaign_id="camp_001",
            output_path=output,
        )
        assert isinstance(result, Ok)
        assert output.exists()

    def test_export_empty_approved(self, tmp_path: Path) -> None:
        """No approved briefs → file still created with empty array."""
        output = tmp_path / "approved.json"
        result = export_approved_briefs(
            [_make_brief(BriefStatus.PENDING_REVIEW)],
            campaign_id="camp_001",
            output_path=output,
        )
        assert isinstance(result, Ok)
        data = json.loads(output.read_text())
        assert len(data["briefs"]) == 0

    def test_export_creates_parent_dir(self, tmp_path: Path) -> None:
        output = tmp_path / "deep" / "nested" / "approved.json"
        brief = _make_brief(BriefStatus.APPROVED)
        result = export_approved_briefs(
            [brief],
            campaign_id="camp_001",
            output_path=output,
        )
        assert isinstance(result, Ok)
        assert output.exists()


class TestLoadBriefsFromJson:
    """ATS-018: Invalid JSON edit caught by validation."""

    def test_load_valid_json(self, tmp_path: Path) -> None:
        brief = _make_brief()
        json_path = tmp_path / "briefs.json"
        json_path.write_text(
            json.dumps([brief.model_dump(mode="json")], default=str),
            encoding="utf-8",
        )
        result = load_briefs_from_json(json_path)
        assert isinstance(result, Ok)
        assert len(result.value) == 1
        assert result.value[0].target_keyword == "hair transplant"

    def test_load_invalid_json_syntax(self, tmp_path: Path) -> None:
        json_path = tmp_path / "bad.json"
        json_path.write_text("{not valid json", encoding="utf-8")
        result = load_briefs_from_json(json_path)
        assert isinstance(result, Err)
        assert "Failed to read JSON" in result.error

    def test_load_missing_required_field(self, tmp_path: Path) -> None:
        """ATS-018: Missing target_keyword caught."""
        brief_data = _make_brief().model_dump(mode="json")
        del brief_data["target_keyword"]
        json_path = tmp_path / "bad_brief.json"
        json_path.write_text(
            json.dumps([brief_data], default=str),
            encoding="utf-8",
        )
        result = load_briefs_from_json(json_path)
        assert isinstance(result, Err)
        assert "Invalid ContentBrief at index 0" in result.error

    def test_load_not_array(self, tmp_path: Path) -> None:
        json_path = tmp_path / "not_array.json"
        json_path.write_text('{"key": "value"}', encoding="utf-8")
        result = load_briefs_from_json(json_path)
        assert isinstance(result, Err)
        assert "JSON array" in result.error

    def test_load_nonexistent_file(self, tmp_path: Path) -> None:
        result = load_briefs_from_json(tmp_path / "missing.json")
        assert isinstance(result, Err)
