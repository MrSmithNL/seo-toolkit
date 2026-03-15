"""Tests for LLM prompt building and response parsing.

TDD: Tests written BEFORE implementation.
Covers: F-002 T-003 (LLM Prompt + Response Parser)
"""

from __future__ import annotations

import json
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from src.research_engine.domain.clustering import (
    build_clustering_prompt,
    chunk_keywords,
    parse_clustering_response,
)
from src.research_engine.models.result import Err, Ok

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def _load_fixture() -> str:
    """Load the golden LLM response fixture."""
    return (FIXTURES_DIR / "clustering_llm_response.json").read_text()


def _all_keywords() -> list[str]:
    """All keywords from the fixture response."""
    return [
        "hair transplant",
        "fue transplant",
        "fut transplant",
        "hair transplant cost",
        "hair loss treatment",
        "minoxidil results",
        "hair growth serum",
        "best barber near me",
    ]


class TestBuildClusteringPrompt:
    """Tests for prompt building."""

    def test_keywords_appear_in_prompt(self) -> None:
        """All keywords are injected into the prompt."""
        keywords = ["hair transplant", "fue surgery"]
        prompt = build_clustering_prompt(keywords, min_size=3, max_size=20)
        assert "hair transplant" in prompt
        assert "fue surgery" in prompt

    def test_min_max_sizes_in_prompt(self) -> None:
        """Min and max cluster sizes appear in the prompt."""
        prompt = build_clustering_prompt(["test"], min_size=5, max_size=15)
        assert "5" in prompt
        assert "15" in prompt

    def test_empty_keywords_produces_prompt(self) -> None:
        """Empty keyword list still produces a valid prompt."""
        prompt = build_clustering_prompt([], min_size=3, max_size=20)
        assert len(prompt) > 0


class TestParseClusteringResponse:
    """Tests for response parsing and validation."""

    def test_valid_fixture_parses_ok(self) -> None:
        """Golden fixture parses successfully."""
        raw = _load_fixture()
        result = parse_clustering_response(raw, _all_keywords())
        assert isinstance(result, Ok)
        assert len(result.value.clusters) == 2
        assert len(result.value.unclustered) == 1

    def test_cluster_has_required_fields(self) -> None:
        """Parsed clusters have name, rationale, keywords, pillar."""
        raw = _load_fixture()
        result = parse_clustering_response(raw, _all_keywords())
        assert isinstance(result, Ok)
        cluster = result.value.clusters[0]
        assert cluster.name == "Hair Transplant Procedures"
        assert len(cluster.keywords) == 4
        assert cluster.pillar_keyword == "hair transplant"
        assert cluster.coherence_score == 9

    def test_missing_keyword_returns_err(self) -> None:
        """If a keyword from input is missing from output, return Err."""
        raw = _load_fixture()
        # Add an extra keyword that the response doesn't include
        keywords = [*_all_keywords(), "missing keyword"]
        result = parse_clustering_response(raw, keywords)
        assert isinstance(result, Err)
        assert "missing" in result.error.lower()

    def test_invented_keyword_returns_err(self) -> None:
        """If output contains a keyword not in input, return Err."""
        raw = _load_fixture()
        # Remove a keyword from the input so it appears "invented"
        keywords = _all_keywords()[1:]  # Remove "hair transplant"
        result = parse_clustering_response(raw, keywords)
        assert isinstance(result, Err)

    def test_invalid_json_returns_err(self) -> None:
        """Malformed JSON returns Err."""
        result = parse_clustering_response("not json", ["test"])
        assert isinstance(result, Err)
        assert "json" in result.error.lower() or "parse" in result.error.lower()

    def test_json_with_markdown_fences(self) -> None:
        """JSON wrapped in markdown code fences is handled."""
        raw = f"```json\n{_load_fixture()}\n```"
        result = parse_clustering_response(raw, _all_keywords())
        assert isinstance(result, Ok)

    def test_coherence_out_of_range_returns_err(self) -> None:
        """Coherence score outside 1-10 returns Err."""
        data = json.loads(_load_fixture())
        data["clusters"][0]["coherence_score"] = 15
        result = parse_clustering_response(json.dumps(data), _all_keywords())
        assert isinstance(result, Err)
        assert "coherence" in result.error.lower()

    def test_pillar_not_in_cluster_returns_err(self) -> None:
        """Pillar keyword not in the cluster's keyword list returns Err."""
        data = json.loads(_load_fixture())
        data["clusters"][0]["pillar_keyword"] = "nonexistent keyword"
        result = parse_clustering_response(json.dumps(data), _all_keywords())
        assert isinstance(result, Err)
        assert "pillar" in result.error.lower()

    def test_duplicate_keyword_across_clusters_returns_err(self) -> None:
        """Same keyword in two clusters returns Err."""
        data = json.loads(_load_fixture())
        # Add a keyword from cluster 0 into cluster 1
        data["clusters"][1]["keywords"].append("hair transplant")
        result = parse_clustering_response(json.dumps(data), _all_keywords())
        assert isinstance(result, Err)
        assert "duplicate" in result.error.lower()


class TestChunkKeywords:
    """Tests for keyword chunking."""

    def test_small_list_single_chunk(self) -> None:
        """List under max stays as single chunk."""
        chunks = chunk_keywords(["a", "b", "c"], max_per_chunk=150)
        assert len(chunks) == 1
        assert chunks[0] == ["a", "b", "c"]

    def test_exact_boundary(self) -> None:
        """List exactly at max stays as single chunk."""
        kws = [f"kw_{i}" for i in range(150)]
        chunks = chunk_keywords(kws, max_per_chunk=150)
        assert len(chunks) == 1

    def test_over_boundary_splits(self) -> None:
        """List over max splits into multiple chunks."""
        kws = [f"kw_{i}" for i in range(300)]
        chunks = chunk_keywords(kws, max_per_chunk=150)
        assert len(chunks) == 2
        assert len(chunks[0]) == 150
        assert len(chunks[1]) == 150

    def test_empty_list(self) -> None:
        """Empty list returns empty chunks."""
        chunks = chunk_keywords([], max_per_chunk=150)
        assert chunks == []

    @given(n=st.integers(min_value=1, max_value=500))
    def test_all_keywords_preserved(self, n: int) -> None:
        """Chunking preserves all keywords."""
        kws = [f"kw_{i}" for i in range(n)]
        chunks = chunk_keywords(kws, max_per_chunk=150)
        flattened = [kw for chunk in chunks for kw in chunk]
        assert flattened == kws
