# CLI Usage

The package includes a command-line script for extracting events in a single command.

## Basic Usage

```bash
python -m eventbrite_extractor.extract_events
```

By default this searches for **AI events in New York City** and exports results to both JSON and CSV in the `output/` directory.

## Options

| Flag | Default | Description |
|------|---------|-------------|
| `-q`, `--query` | `AI` | Search keyword |
| `--pages` | `3` | Maximum number of pages to fetch |
| `--page-size` | `20` | Results per page (max 50) |
| `--place-id` | `85977539` (NYC) | Who's On First place ID for location filtering. Use `none` for worldwide. |
| `--online-only` | `False` | Only include online events |
| `--sort-by` | `date` | Sort events by `date` or `title` |
| `--free-first` | `False` | Show free events before paid events |
| `--format` | `both` | Output format: `json`, `csv`, or `both` |
| `-o`, `--output-dir` | `output/` | Output directory |

## Examples

### Extract AI events in NYC (default)

```bash
python -m eventbrite_extractor.extract_events
```

### Search for machine learning events, 5 pages, JSON only

```bash
python -m eventbrite_extractor.extract_events -q "machine learning" --pages 5 --format json
```

### Online-only AI events (worldwide)

```bash
python -m eventbrite_extractor.extract_events --online-only --place-id none
```

### Free events first, sorted by date

```bash
python -m eventbrite_extractor.extract_events --free-first
```

### Export to a custom directory

```bash
python -m eventbrite_extractor.extract_events -o data/ai_events
```

## Pipeline

The CLI runs a full **Extract → Transform → Export** pipeline:

1. **Extract** — Fetches raw events from the Eventbrite API
2. **Transform** — Filters cancelled/past events, sorts, and enriches each event with:
   - **`display_price`** — `"Free"`, `"$50 USD"`, `"Paid"`
   - **`display_date`** — `"Wed, Mar 4 at 10:00 AM"`
   - **`display_location`** — Venue name, `"Online"`, or `"Location TBD"`
   - **`event_type`** — Conference, Workshop, Meetup, Webinar, Hackathon, Talk, Course, or Event
3. **Export** — Saves event data to JSON and/or CSV

## Output

The script produces:

- **`output/events.json`** — Full event data in JSON format
- **`output/events.csv`** — Tabular event data in CSV format

The terminal summary shows enriched data with event types, formatted dates, and clean pricing.
