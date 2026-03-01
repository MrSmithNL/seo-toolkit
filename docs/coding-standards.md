# SEO Toolkit — Coding Standards

Last updated: 2026-03-01

---

## Overview

This is a Python project. These standards apply to all code in the `scripts/` directory and any future Python modules. The goal is enterprise-quality code that any developer (human or AI) can understand and modify 12 months from now.

---

## Python Version

- **Minimum:** Python 3.11
- **Why:** f-string improvements, `tomllib` built-in, exception groups, `TaskGroup` for async

---

## Formatting & Linting

| Tool | Purpose | Config |
|------|---------|--------|
| **black** | Code formatter — consistent style, no debates | Default settings (line length 88) |
| **ruff** | Linter — catches bugs, enforces style, replaces flake8/isort/pylint | `pyproject.toml` configuration |
| **mypy** | Type checker (future) — enforces type hints | Strict mode when added |

### Running Locally

```bash
# Format all Python files
black scripts/

# Lint all Python files
ruff check scripts/

# Lint and auto-fix what can be fixed
ruff check scripts/ --fix
```

### Ruff Configuration

Add to `pyproject.toml`:

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort (import sorting)
    "N",    # pep8-naming
    "D",    # pydocstyle (docstrings)
    "UP",   # pyupgrade
    "B",    # flake8-bugbear
    "S",    # flake8-bandit (security)
    "C4",   # flake8-comprehensions
    "RET",  # flake8-return
    "SIM",  # flake8-simplify
]

[tool.ruff.lint.pydocstyle]
convention = "google"
```

---

## Type Hints

**Required on all public functions.** Type hints make the code self-documenting and catch bugs before runtime.

```python
# Good — type hints on parameters and return value
def get_keyword_volume(keyword: str, location_code: int = 2826) -> dict[str, int]:
    """Fetch search volume for a keyword from DataForSEO."""
    ...

# Bad — no type hints
def get_keyword_volume(keyword, location_code=2826):
    ...
```

For complex types, use `typing` imports:

```python
from typing import Optional

def find_competitors(
    domain: str,
    max_results: int = 10,
    include_subdomains: bool = False,
) -> list[dict[str, str | int]]:
    ...
```

---

## Docstrings

**Required on all public functions and classes.** Use Google-style docstrings.

```python
def run_audit(config_path: str, dry_run: bool = False) -> dict:
    """Run a technical SEO audit for a client website.

    Crawls the site, checks for technical issues (broken links, missing meta tags,
    slow pages, schema errors), and produces a structured report.

    Args:
        config_path: Path to the client config JSON file.
        dry_run: If True, show what would be checked without making API calls.

    Returns:
        A dictionary containing audit results with keys:
        - score: Overall audit score (0-100)
        - critical: List of critical issues
        - warnings: List of warning-level issues
        - passed: List of checks that passed

    Raises:
        FileNotFoundError: If config file does not exist.
        ValueError: If config file is missing required fields.
    """
    ...
```

---

## Module Structure

Each agent gets its own folder under `scripts/`. The structure within each agent folder should follow this pattern:

```
scripts/
├── audit/
│   ├── __init__.py
│   ├── run_audit.py          # Entry point — CLI interface
│   ├── crawler.py             # Site crawling logic
│   ├── checks.py              # Individual audit checks
│   └── report.py              # Report generation
├── keywords/
│   ├── __init__.py
│   ├── run_keywords.py        # Entry point
│   ├── research.py            # Keyword research logic
│   ├── gaps.py                # Competitor gap analysis
│   └── report.py              # Report generation
├── shared/                    # Shared utilities across all agents
│   ├── __init__.py
│   ├── config.py              # Client config loader + validation
│   ├── api_client.py          # DataForSEO, SE Ranking API wrappers
│   ├── cache.py               # Response caching to avoid redundant API calls
│   ├── report_base.py         # Base report template rendering
│   └── logging.py             # Consistent logging setup
└── ...
```

### Rules

1. **One folder per agent.** Never mix agent logic across folders.
2. **Shared code goes in `scripts/shared/`.** API clients, config loading, caching, logging — anything used by 2+ agents.
3. **Each agent has a `run_*.py` entry point.** This is what gets called from the CLI or scheduler.
4. **No circular imports.** Agents import from `shared/`. Agents never import from other agents.

---

## Client Configs

- All client configs live in `configs/`
- Format: JSON
- Schema validated by `scripts/shared/config.py` using `jsonschema`
- Template: `configs/example.config.json`

---

## Testing

| Tool | Purpose |
|------|---------|
| **pytest** | Test runner |
| **pytest-cov** | Coverage reporting |

### Test Structure

```
tests/
├── conftest.py                # Shared fixtures (mock configs, API responses)
├── test_audit/
│   ├── test_crawler.py
│   ├── test_checks.py
│   └── test_report.py
├── test_keywords/
│   ├── test_research.py
│   └── test_gaps.py
├── test_shared/
│   ├── test_config.py
│   ├── test_api_client.py
│   └── test_cache.py
└── fixtures/
    ├── sample_config.json     # Test config files
    └── mock_responses/        # Saved API responses for testing
        ├── dataforseo_keywords.json
        └── se_ranking_audit.json
```

### Rules

1. **Tests live in `tests/`, mirroring `scripts/` structure.**
2. **Every public function gets at least one test.**
3. **Mock external API calls.** Tests must not make real API requests.
4. **Use fixtures for test data.** Keep `tests/fixtures/` with sample configs and saved API responses.
5. **Run tests before every commit:**
   ```bash
   pytest tests/ -v --cov=scripts/
   ```

---

## Error Handling

```python
# Good — specific exception with context
try:
    response = dataforseo_client.get_keywords(keyword)
except requests.HTTPError as e:
    logger.error(f"DataForSEO API error for keyword '{keyword}': {e.response.status_code}")
    raise

# Bad — bare except
try:
    response = dataforseo_client.get_keywords(keyword)
except:
    pass
```

### Rules

1. **Never use bare `except:`.** Always catch specific exceptions.
2. **Log errors with context** — include what was being attempted, what input caused the failure.
3. **Fail loudly for critical errors** (missing config, API auth failure). Do not silently continue.
4. **Retry transient errors** (rate limits, timeouts) with exponential backoff.
5. **Use the shared logger** from `scripts/shared/logging.py` — never use `print()` for operational output.

---

## Environment Variables

```python
# Good — load from .env with fallback and validation
from dotenv import load_dotenv
import os

load_dotenv()

DATAFORSEO_LOGIN = os.environ.get("DATAFORSEO_LOGIN")
if not DATAFORSEO_LOGIN:
    raise EnvironmentError("DATAFORSEO_LOGIN not set. Add it to .env file.")
```

### Rules

1. **All credentials from environment variables.** Never hardcoded.
2. **Validate at startup.** Fail immediately if a required variable is missing.
3. **Use `python-dotenv`** to load `.env` files.

---

## Naming Conventions

| Item | Convention | Example |
|------|-----------|---------|
| Files | snake_case | `run_audit.py`, `api_client.py` |
| Functions | snake_case | `get_keyword_volume()`, `run_audit()` |
| Classes | PascalCase | `AuditReport`, `DataForSEOClient` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_LOCATION_CODE` |
| Config keys | snake_case | `primary_keywords`, `se_ranking_project_id` |

---

## Git Practices

1. **Commit messages:** Short, imperative mood. "Add audit crawler" not "Added audit crawler functionality."
2. **Branch names:** `feature/audit-agent`, `fix/keyword-api-timeout`, `docs/update-metrics`
3. **Never commit:** `.env`, `cache/`, `reports/`, `__pycache__/`, `.venv/`

---

## Dependencies

- All dependencies listed in `requirements.txt` with minimum version pins
- No unpinned dependencies (avoid `requests` without version — use `requests>=2.31.0`)
- Review dependencies before adding — prefer standard library where possible
- Document why each dependency is needed (comments in `requirements.txt`)

---

## Change Log

| Date | Change |
|------|--------|
| 2026-03-01 | Coding standards document created. Python standards, formatting, type hints, docstrings, testing, error handling, naming conventions documented. |
