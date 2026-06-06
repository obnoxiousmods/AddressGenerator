# Contributing

## Setup

```bash
uv sync --extra dev
```

## Standard Checks

```bash
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```

## Guidelines

- Do not add secret-seed handling.
- Keep public-key-only boundaries explicit in code and docs.
- Prefer dependency injection for networked services.
- Add or update tests for any behavior change.
