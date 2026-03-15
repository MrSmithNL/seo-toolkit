"""LLM-based keyword clustering: prompt building and response parsing.

Pure functions for building the clustering prompt, parsing the LLM's
structured JSON response, and chunking keyword lists.
"""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field

from src.research_engine.models.result import Err, Ok, Result

# ---------------------------------------------------------------------------
# Response models (LLM output schema)
# ---------------------------------------------------------------------------


class LLMClusterOutput(BaseModel):
    """A single cluster from the LLM response."""

    name: str
    rationale: str
    pillar_keyword: str
    pillar_rationale: str
    coherence_score: int
    coherence_rationale: str
    keywords: list[str]


class ClusteringLLMResponse(BaseModel):
    """Structured response from the clustering LLM call."""

    clusters: list[LLMClusterOutput]
    unclustered: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

_PROMPT_TEMPLATE = """\
You are a keyword clustering assistant for SEO content strategy.

Given the following list of keywords, group them into semantic topic clusters.

Rules:
- Each cluster must contain between {min_size} and {max_size} keywords.
- Keywords with no clear semantic grouping go in the "unclustered" list.
- Select one "pillar_keyword" per cluster (highest volume, broadest scope).
- Assign a coherence_score from 1 to 10 for each cluster.
- Provide a short rationale for each cluster and pillar selection.

Keywords:
{keywords}

Return ONLY valid JSON with this exact structure:
{{
  "clusters": [
    {{
      "name": "Topic name",
      "rationale": "1-2 sentence explanation of why these keywords belong together.",
      "pillar_keyword": "the chosen pillar keyword",
      "pillar_rationale": "1 sentence why this is the pillar.",
      "coherence_score": 8,
      "coherence_rationale": "1 sentence explaining the score.",
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }}
  ],
  "unclustered": ["standalone keyword"]
}}
"""


def build_clustering_prompt(
    keywords: list[str],
    min_size: int = 3,
    max_size: int = 20,
) -> str:
    """Build the clustering prompt with keywords injected.

    Args:
        keywords: List of keyword terms to cluster.
        min_size: Minimum keywords per cluster.
        max_size: Maximum keywords per cluster.

    Returns:
        Complete prompt string ready for LLM.
    """
    keyword_list = "\n".join(f"- {kw}" for kw in keywords)
    return _PROMPT_TEMPLATE.format(
        keywords=keyword_list,
        min_size=min_size,
        max_size=max_size,
    )


# ---------------------------------------------------------------------------
# Response parsing
# ---------------------------------------------------------------------------

_MARKDOWN_FENCE_RE = re.compile(r"```(?:json)?\s*\n?(.*?)\n?\s*```", re.DOTALL)


def _strip_markdown_fences(raw: str) -> str:
    """Remove markdown code fences from LLM output."""
    match = _MARKDOWN_FENCE_RE.search(raw)
    if match:
        return match.group(1)
    return raw


def parse_clustering_response(  # noqa: C901
    raw_json: str,
    input_keywords: list[str],
) -> Result[ClusteringLLMResponse, str]:
    """Parse and validate the LLM clustering response.

    Validates:
    - Valid JSON structure
    - Every input keyword appears exactly once
    - No invented keywords
    - Coherence scores in range 1-10
    - Pillar keyword is in its cluster's keyword list
    - No duplicate keywords across clusters

    Args:
        raw_json: Raw JSON string from LLM.
        input_keywords: Original input keywords for completeness check.

    Returns:
        Ok(response) on success, Err(message) on validation failure.
    """
    cleaned = _strip_markdown_fences(raw_json.strip())

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return Err(f"Failed to parse JSON: {exc}")

    try:
        response = ClusteringLLMResponse.model_validate(data)
    except Exception as exc:  # noqa: BLE001
        return Err(f"Invalid response structure: {exc}")

    # Collect all output keywords
    all_output: list[str] = []
    for cluster in response.clusters:
        all_output.extend(cluster.keywords)
    all_output.extend(response.unclustered)

    # Check for duplicates
    seen: set[str] = set()
    for kw in all_output:
        kw_lower = kw.lower()
        if kw_lower in seen:
            return Err(f"Duplicate keyword in output: '{kw}'")
        seen.add(kw_lower)

    # Check completeness: every input keyword must appear
    input_lower = {kw.lower() for kw in input_keywords}
    output_lower = {kw.lower() for kw in all_output}

    missing = input_lower - output_lower
    if missing:
        return Err(f"Missing keywords from output: {sorted(missing)}")

    invented = output_lower - input_lower
    if invented:
        return Err(f"Invented keywords in output: {sorted(invented)}")

    # Validate each cluster
    for cluster in response.clusters:
        # Coherence score range
        if not (1 <= cluster.coherence_score <= 10):
            return Err(
                f"Coherence score {cluster.coherence_score} out of range "
                f"[1,10] for cluster '{cluster.name}'"
            )

        # Pillar must be in the cluster
        cluster_lower = {kw.lower() for kw in cluster.keywords}
        if cluster.pillar_keyword.lower() not in cluster_lower:
            return Err(
                f"Pillar keyword '{cluster.pillar_keyword}' not found "
                f"in cluster '{cluster.name}'"
            )

    return Ok(response)


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def chunk_keywords(
    keywords: list[str],
    max_per_chunk: int = 150,
) -> list[list[str]]:
    """Split keyword list into chunks for LLM context limits.

    Args:
        keywords: List of keyword terms.
        max_per_chunk: Maximum keywords per chunk.

    Returns:
        List of keyword chunks.
    """
    if not keywords:
        return []
    return [
        keywords[i : i + max_per_chunk] for i in range(0, len(keywords), max_per_chunk)
    ]
