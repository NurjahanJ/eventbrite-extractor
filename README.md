# Eventbrite Data Extraction Package

A Python package that extracts public AI event data from Eventbrite (focused on **New York City**) as part of an ETL pipeline for newsletter content generation.

## Overview

This project implements a full **Extract → Transform → Render** pipeline. It pulls upcoming event data from Eventbrite, cleans and enriches it, and generates a ready-to-send HTML newsletter.

## Features

- Search events by keyword (default: "AI") and location (default: NYC)
- Continuation-based pagination and automatic deduplication
- Rate limit handling with exponential backoff
- Transform: filter, sort, classify, and format events for display
- Render: HTML newsletter grouped by event type (Conference, Workshop, Meetup, etc.)
- JSON and CSV export
- CLI script for one-command extraction + newsletter generation

## Quick Start

```bash
git clone https://github.com/NurjahanJ/newsletter.git
cd newsletter
python -m venv .venv
.venv\Scripts\activate              # Windows
pip install -r requirements.txt
pip install -e ".[dev]"
cp .env.example .env                # Add your Eventbrite Private token
python -m eventbrite_extractor.extract_events --newsletter
```

## Project Structure

```
newsletter/
├── Docs/                              # Documentation
│   ├── Basic_ Info.md                 # Project overview and goals
│   ├── Setup.md                       # Installation and API key setup
│   ├── CLI_Usage.md                   # CLI options and examples
│   ├── API_Reference.md              # Python API and Event fields
│   └── Development.md                # Testing, linting, architecture
├── src/eventbrite_extractor/          # Package source code
├── tests/                             # Test suite (79 tests)
├── output/                            # Extracted data + newsletter HTML
├── .env.example                       # Environment variable template
├── pyproject.toml                     # Build config and Ruff settings
└── requirements.txt                   # Python dependencies
```

## Documentation

- **[Setup Guide](Docs/Setup.md)** — Installation, virtual environment, API key configuration
- **[CLI Usage](Docs/CLI_Usage.md)** — Command-line options, examples, and output formats
- **[API Reference](Docs/API_Reference.md)** — Python API, Event fields, and export functions
- **[Development](Docs/Development.md)** — Testing, linting, project architecture
- **[Project Info](Docs/Basic_%20Info.md)** — Project goals, scope, and data source details

## License

This project is for educational purposes.
