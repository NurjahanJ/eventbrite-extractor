# Eventbrite Event Data Extraction

A Python package that extracts, transforms, and exports public event data from Eventbrite — focused on **AI events in New York City**.

**Python 3.9+** · **62 tests** · **Linted with Ruff**

## Features

- Search events by keyword and location (default: AI events in NYC)
- Continuation-based pagination with automatic deduplication
- Rate limit handling with exponential backoff
- Transform pipeline: filter, sort, classify, and enrich events
- Export to JSON and CSV
- CLI for one-command extraction
- Docker support for reproducible, portable runs

## Quick Start

```bash
git clone https://github.com/NurjahanJ/eventbrite-extractor.git
cd eventbrite-extractor
python -m venv .venv
.venv\Scripts\activate              # Windows
pip install -r requirements.txt
pip install -e ".[dev]"
cp .env.example .env                # Add your Eventbrite Private token
python -m eventbrite_extractor.extract_events
```

## Pipeline

```
Extract (client.py)  →  Transform (transform.py)  →  Export (export.py)
  Eventbrite API          Filter, sort, enrich        JSON / CSV files
```

1. **Extract** — Fetches raw events from Eventbrite's `destination/search` API
2. **Transform** — Filters cancelled/past events, sorts, and enriches with display-ready fields
3. **Export** — Saves structured data to JSON and/or CSV

## Sample Output

Running the default extraction produces a terminal summary like this:

```
================================================================
  56 events in NYC (from 56 raw)
================================================================

  1. [Talk] AI Search and News
     Wed, Feb 19 at 12:00 PM
     Lecture Hall, Columbia Journalism School
     Free
     https://www.eventbrite.com/e/ai-search-and-news-tickets-1981061406997

  2. [Meetup] AI x Wellness x Tech Mixer: Tools, Habits & Human Connection
     Wed, Feb 19 at 6:00 PM
     The Lobby Bar & Garden
     $17.85 USD
     https://www.eventbrite.com/e/...
```

Output files are saved to `output/events.json` and `output/events.csv`.

## Project Structure

```
├── src/eventbrite_extractor/          # Package source code
│   ├── __init__.py                    #   Public API exports
│   ├── config.py                      #   Environment config and constants
│   ├── models.py                      #   Event dataclass (23 fields)
│   ├── client.py                      #   Eventbrite API client
│   ├── transform.py                   #   Filter, sort, enrich, classify
│   ├── export.py                      #   JSON and CSV export
│   └── extract_events.py             #   CLI entry point
├── tests/                             # 62 tests across 4 modules
│   ├── test_models.py                 #   Event creation and parsing
│   ├── test_client.py                 #   API search, pagination, dedup
│   ├── test_export.py                 #   JSON/CSV file output
│   └── test_transform.py             #   Filter, sort, format, classify
├── Docs/                              # Documentation
│   ├── Project_Info.md                #   Project overview and scope
│   ├── Setup.md                       #   Installation and API key setup
│   ├── CLI_Usage.md                   #   CLI options and examples
│   ├── API_Reference.md              #   Python API reference
│   └── Development.md                #   Testing, linting, architecture
├── output/                            # Sample extracted data (JSON, CSV)
├── Dockerfile                         # Multi-stage Docker build
├── .dockerignore                      # Docker build exclusions
├── .env.example                       # Environment variable template
├── pyproject.toml                     # Build config and Ruff settings
└── requirements.txt                   # Python dependencies
```

## Documentation

- **[Setup Guide](Docs/Setup.md)** — Installation, virtual environment, API key configuration
- **[CLI Usage](Docs/CLI_Usage.md)** — Command-line options, examples, and output formats
- **[API Reference](Docs/API_Reference.md)** — Python API, Event fields, and export functions
- **[Development](Docs/Development.md)** — Testing, linting, project architecture
- **[Project Info](Docs/Project_Info.md)** — Project goals, scope, and data source details

## Docker

Run the extractor without installing Python or dependencies:

```bash
# Build the image
docker build -t eventbrite-extractor .

# Run extraction (pass your API key via .env file)
docker run --env-file .env -v "$(pwd)/output:/app/output" eventbrite-extractor

# Run with custom arguments
docker run --env-file .env -v "$(pwd)/output:/app/output" eventbrite-extractor \
  python -m eventbrite_extractor.extract_events -q "machine learning" --pages 5

# Run tests inside the container
docker build --target test -t eventbrite-extractor-test .
docker run eventbrite-extractor-test
```

The `-v` flag mounts your local `output/` directory so extracted files persist after the container exits.

See the [Setup Guide](Docs/Setup.md) for more details.

## License

This project is for educational purposes.
