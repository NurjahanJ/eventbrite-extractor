# Development Guide

## Running Tests

```bash
pytest tests/ -v
```

The test suite includes **62 tests** across 4 modules:

| Module | Tests | Coverage |
|--------|-------|----------|
| `test_models.py` | 9 | Event creation, API response parsing, serialization |
| `test_client.py` | 8 | Search, pagination, deduplication, location filtering |
| `test_export.py` | 8 | JSON and CSV file output, empty lists, directory creation |
| `test_transform.py` | 37 | Filtering, sorting, price/date formatting, classification, full pipeline |

## Linting and Formatting

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and formatting.

```bash
ruff check .        # Lint
ruff check . --fix  # Lint with auto-fix
ruff format .       # Format code
ruff format --check # Check formatting without changes
```

### Ruff Configuration

Configured in `pyproject.toml` with the following rule sets:

- **E/W** — pycodestyle errors and warnings
- **F** — pyflakes
- **I** — isort (import sorting)
- **N** — pep8-naming
- **UP** — pyupgrade
- **B** — flake8-bugbear
- **SIM** — flake8-simplify

## Project Architecture

```
src/eventbrite_extractor/
├── config.py           # Loads .env, defines constants (API URL, NYC place ID)
├── models.py           # Event dataclass with from_api_response() factory
├── client.py           # EventbriteClient — POST to destination/search API
├── transform.py        # Filter, sort, enrich, classify events
├── export.py           # export_to_json() and export_to_csv()
├── extract_events.py   # CLI entry point (Extract → Transform → Export)
└── __init__.py         # Public API exports
```

### Pipeline

```
Extract (client.py)  →  Transform (transform.py)  →  Export (export.py)
  Eventbrite API          Filter, sort, enrich        JSON / CSV files
```

### Key Design Decisions

- **destination/search API** — The old `/events/search/` endpoint is deprecated. This package uses the current `POST /destination/search/` endpoint.
- **Continuation-based pagination** — The API uses opaque continuation tokens instead of page numbers.
- **Place IDs** — Location filtering uses Who's On First place IDs (e.g. `85977539` for NYC).
- **Rate limit handling** — Automatic retry with exponential backoff on HTTP 429 responses.
- **Deduplication** — Events are deduplicated by ID across pages.
- **Keyword-based classification** — Events are classified into types (Conference, Workshop, Meetup, etc.) by scanning title, summary, and tags for known keywords.
- **Cross-platform date formatting** — Avoids platform-specific strftime flags (`%-d` vs `%#d`).
