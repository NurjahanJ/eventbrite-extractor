# Transform Pipeline

The transform module processes raw extracted events into clean, enriched records ready for newsletter use.

## Pipeline Steps

The `transform_events()` function runs these steps in order:

1. **Filter cancelled** — Removes events marked as cancelled
2. **Filter past events** — Removes events with a start date before today
3. **Deduplicate** — Removes duplicate events by event ID
4. **Normalize pricing** — Cleans up pricing fields:
   - `$0.00` events are marked as "Free"
   - Free events have price/currency cleared
   - Paid events get a currency symbol prefix (e.g. `$25.00`, `€50.00`)
5. **Clean tags** — Removes duplicate tags (case-insensitive)
6. **Classify event type** — Categorizes each event as one of:
   - Conference, Workshop, Meetup, Webinar, Seminar, Hackathon, Course, or Event (default)
7. **Format display date** — Creates human-readable dates (e.g. `Thu, Feb 27, 2026 at 12:00 PM`)
8. **Sort by date** — Earliest events first

## Enriched Fields

The transform adds these fields to each event dict:

| Field | Example | Description |
|-------|---------|-------------|
| `event_type` | `"Workshop"` | Classified event type |
| `display_date` | `"Thu, Feb 27, 2026 at 12:00 PM"` | Human-readable date |
| `display_price` | `"Free"` or `"$25.00"` | Formatted price string |
| `location` | `"Google NYC - Pier 57"` or `"Online"` | Venue name or "Online"/"TBD" |

## Usage

### In the CLI

The transform runs automatically when you use the CLI:

```bash
python -m eventbrite_extractor.extract_events
```

### In Python

```python
from eventbrite_extractor import EventbriteClient, transform_events

client = EventbriteClient()
raw_events = client.search_events(keyword="AI", max_pages=3)

# Transform returns a list of enriched dicts
newsletter_events = transform_events(raw_events)

for event in newsletter_events:
    print(f"[{event['event_type']}] {event['title']}")
    print(f"  {event['display_date']}")
    print(f"  {event['display_price']} — {event['location']}")
```

### Individual Functions

You can also use the transform functions individually:

```python
from eventbrite_extractor.transform import (
    filter_cancelled,
    filter_past_events,
    deduplicate,
    normalize_pricing,
    clean_tags,
    classify_event_type,
    format_display_date,
)
```
