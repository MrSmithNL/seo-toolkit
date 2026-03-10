---
paths:
  - "scripts/**/*.py"
  - "tests/**/*.py"
---
# Python Code Quality Rules

- Run `ruff check` and `black --check` before committing
- All functions require type hints on parameters and return values (mypy strict)
- Tests require `--cov-fail-under=80` (enforced in pyproject.toml)
- Use Google-style docstrings on all public functions/classes
- Max 30 lines per function, max 400 lines per file
- No bare `except:` — always catch specific exceptions
- Mutation testing: mutmut configured in pyproject.toml, runs weekly in CI
- Pre-push hook runs pytest automatically — do not bypass with `--no-verify`
