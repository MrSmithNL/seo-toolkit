"""CalendarRenderer — generates Markdown + JSON output files.

Per ADR-F007-002: dual output. Markdown for human review,
JSON for machine consumption. JSON is authoritative.

TypeScript equivalent:
  modules/content-engine/research/services/calendar-renderer.ts
"""

from __future__ import annotations

import json
import logging
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.research_engine.models.content_brief import ContentBrief

logger = logging.getLogger(__name__)


def _render_markdown_entry(index: int, brief: ContentBrief) -> str:
    """Render a single calendar entry as Markdown."""
    headings_list = "\n".join(f"  - {h}" for h in brief.recommended_headings)

    # Compute avg depth score
    avg_depth = 0.0
    if brief.competitor_depth_scores:
        avg_depth = sum(brief.competitor_depth_scores) / len(
            brief.competitor_depth_scores
        )

    kw = brief.target_keyword
    ct = brief.content_type.value
    vol = f"{brief.keyword_volume:,}"
    diff = brief.keyword_difficulty
    avg_wc = f"{brief.competitor_avg_word_count:,}"
    top_url = brief.top_competitor_url or "N/A"
    rec_wc = f"{brief.recommended_word_count:,}"
    pub = brief.suggested_publish_date

    lines = [
        f"## {index}. {kw} ({ct})",
        f"**Keyword:** {kw} | **Volume:** {vol}/mo" f" | **Difficulty:** {diff}/100",
        f"**Rationale:** {brief.opportunity_score_rationale}",
        f"**Competitors:** Avg {avg_wc} words,"
        f" depth {avg_depth:.1f}/5. Top: {top_url}",
        f"**Our recommendation:** {rec_wc} words," f" {ct}, publish {pub}",
        "**Headings:**",
        headings_list,
        "**Action:** [ ] Approve | [ ] Reject" " | [ ] Edit (add notes below)",
        "",
        "---",
        "",
    ]
    return "\n".join(lines)


def render_calendar_markdown(
    briefs: list[ContentBrief],
    calendar_date: str | None = None,
) -> str:
    """Render the full calendar as Markdown.

    Sections: "New Content" (own_gap + new_opportunity, sorted by score)
    then "Content to Update" (thin_content, sorted by score).
    """
    from src.research_engine.models.content_brief import GapType

    cal_date = calendar_date or date.today().isoformat()

    new_content = [
        b for b in briefs if b.gap_type in (GapType.OWN_GAP, GapType.NEW_OPPORTUNITY)
    ]
    thin_content = [b for b in briefs if b.gap_type == GapType.THIN_CONTENT]

    # Sort within sections by score descending
    new_content.sort(key=lambda b: b.opportunity_score, reverse=True)
    thin_content.sort(key=lambda b: b.opportunity_score, reverse=True)

    lines = [f"# Content Calendar — {cal_date}\n"]
    total = len(briefs)
    new_ct = len(new_content)
    thin_ct = len(thin_content)
    lines.append(
        f"**Total topics:** {total}"
        f" | **New content:** {new_ct}"
        f" | **Updates:** {thin_ct}\n"
    )

    if new_content:
        lines.append("# New Content\n")
        for i, brief in enumerate(new_content, 1):
            lines.append(_render_markdown_entry(i, brief))

    if thin_content:
        lines.append("# Content to Update\n")
        offset = len(new_content)
        for i, brief in enumerate(thin_content, offset + 1):
            lines.append(_render_markdown_entry(i, brief))

    if not new_content and not thin_content:
        lines.append("\n*No content topics generated.*\n")

    return "\n".join(lines)


def render_calendar_json(briefs: list[ContentBrief]) -> str:
    """Render briefs as JSON array.

    Validates each brief against the schema before serialisation.
    """
    return json.dumps(
        [brief.model_dump(mode="json") for brief in briefs],
        indent=2,
        default=str,
    )


def write_calendar_files(
    briefs: list[ContentBrief],
    output_dir: Path,
    calendar_date: str | None = None,
) -> tuple[Path, Path]:
    """Write calendar Markdown and JSON files.

    Args:
        briefs: Validated ContentBrief records.
        output_dir: Directory to write files.
        calendar_date: Optional date string (YYYY-MM-DD).

    Returns:
        Tuple of (markdown_path, json_path).
    """
    cal_date = calendar_date or date.today().isoformat()
    output_dir.mkdir(parents=True, exist_ok=True)

    md_path = output_dir / f"calendar-{cal_date}.md"
    json_path = output_dir / f"calendar-{cal_date}.json"

    md_content = render_calendar_markdown(briefs, cal_date)
    json_content = render_calendar_json(briefs)

    md_path.write_text(md_content, encoding="utf-8")
    json_path.write_text(json_content, encoding="utf-8")

    logger.info(
        "Calendar files written: md=%s json=%s briefs=%d",
        md_path,
        json_path,
        len(briefs),
    )

    return md_path, json_path
