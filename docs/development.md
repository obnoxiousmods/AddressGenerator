# Development

## Tooling

- `uv` for dependency management and execution
- `ruff` for linting and formatting
- `ty` for static type checking
- `pytest` with coverage enforcement for tests

## Common Commands

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format .
uv run ty check
uv run pytest
uv lock
```

## Repository Layout

```text
src/address_generator/
tests/
docs/
examples/
.github/
```
