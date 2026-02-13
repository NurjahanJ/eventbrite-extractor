# API Reference

## Python API

The package exposes four public components:

```python
from eventbrite_extractor import EventbriteClient, Event, export_to_json, export_to_csv
```

---

## EventbriteClient

### `EventbriteClient(api_key=None)`

Creates a new API client. If `api_key` is not provided, it reads from the `EVENTBRITE_API_KEY` environment variable.

```python
client = EventbriteClient()
```

### `client.search_events(keyword, place_id=NYC_PLACE_ID, online_only=False, max_pages=1, page_size=20)`

Search for public events on Eventbrite.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `keyword` | `str` | *(required)* | Search query (e.g. `"AI"`) |
| `place_id` | `str \| None` | `"85977539"` (NYC) | Who's On First place ID. `None` for worldwide. |
| `online_only` | `bool` | `False` | Only return online events |
| `max_pages` | `int` | `1` | Maximum pages to fetch |
| `page_size` | `int` | `20` | Results per page (max 50) |

**Returns:** `list[Event]`

```python
events = client.search_events(keyword="AI", max_pages=3)
```

### `client.get_event_by_id(event_id)`

Fetch a single event by its Eventbrite ID.

**Returns:** `Event`

```python
event = client.get_event_by_id("1980413631483")
```

---

## Event

A dataclass representing a single Eventbrite event.

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | `str` | Eventbrite event ID |
| `title` | `str` | Event name |
| `summary` | `str \| None` | Short description |
| `start_date` | `str \| None` | Start date (`YYYY-MM-DD`) |
| `start_time` | `str \| None` | Start time (`HH:MM`) |
| `end_date` | `str \| None` | End date |
| `end_time` | `str \| None` | End time |
| `timezone` | `str \| None` | Event timezone |
| `is_online` | `bool` | Whether the event is online |
| `venue_name` | `str \| None` | Venue name |
| `venue_address` | `str \| None` | Venue city, region, country |
| `organizer_name` | `str \| None` | Organizer name |
| `organizer_id` | `str \| None` | Organizer ID |
| `url` | `str \| None` | Eventbrite event page URL |
| `is_free` | `bool` | Whether the event is free |
| `price` | `str \| None` | Minimum ticket price |
| `currency` | `str \| None` | Price currency code |
| `category` | `str \| None` | Event category |
| `tags` | `list[str]` | Tag display names |
| `image_url` | `str \| None` | Event image URL |
| `is_cancelled` | `bool` | Whether the event is cancelled |
| `published` | `str \| None` | Publication timestamp |
| `source_platform` | `str` | Always `"eventbrite"` |

### Methods

- **`Event.from_api_response(data)`** — Create an Event from a raw API response dict
- **`event.to_dict()`** — Convert to a plain dictionary

---

## Export Functions

### `export_to_json(events, filepath, indent=2)`

Export events to a JSON file. Creates parent directories if needed.

**Returns:** `Path` to the written file.

```python
export_to_json(events, "output/events.json")
```

### `export_to_csv(events, filepath)`

Export events to a CSV file. List fields (tags) are joined as comma-separated strings.

**Returns:** `Path` to the written file.

```python
export_to_csv(events, "output/events.csv")
```

---

## Transform

### `transform_events(events, remove_cancelled=True, remove_past=True, sort_by="date", free_first=False, reference_date=None)`

Run the full transform pipeline: filter, sort, and enrich events.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `events` | `list[Event]` | *(required)* | Raw Event objects |
| `remove_cancelled` | `bool` | `True` | Drop cancelled events |
| `remove_past` | `bool` | `True` | Drop events before today |
| `sort_by` | `str` | `"date"` | `"date"` or `"title"` |
| `free_first` | `bool` | `False` | Free events appear first |
| `reference_date` | `date \| None` | `None` (today) | Date for past-event filtering |

**Returns:** `list[dict]` — Enriched event dicts with extra fields:

| Extra Field | Example |
|-------------|---------|
| `display_price` | `"Free"`, `"$50 USD"` |
| `display_date` | `"Wed, Mar 4 at 10:00 AM"` |
| `display_location` | `"Google NYC - Pier 57"`, `"Online"` |
| `event_type` | `"Workshop"`, `"Conference"`, `"Meetup"`, `"Talk"`, etc. |

### Helper Functions

These are also available individually:

- **`filter_events(events, ...)`** — Remove cancelled / past events
- **`sort_events(events, by, free_first)`** — Sort by date or title
- **`format_price(event)`** — `"Free"`, `"$50 USD"`, `"Paid"`
- **`format_date_display(event)`** — `"Wed, Mar 4 at 10:00 AM"`
- **`format_location(event)`** — `"Online"`, venue name, or `"Location TBD"`
- **`classify_event(event)`** — Conference, Workshop, Meetup, Webinar, Hackathon, Talk, Course, or Event

---

## Render

### `render_newsletter(enriched_events, title, subtitle, intro_text, template_name)`

Render enriched events into an HTML newsletter string.

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enriched_events` | `list[dict]` | *(required)* | Enriched dicts from `transform_events()` |
| `title` | `str` | `"AI Events in NYC"` | Newsletter title |
| `subtitle` | `str \| None` | Current month/year | Subtitle below the title |
| `intro_text` | `str \| None` | Auto-generated | Introductory paragraph |
| `template_name` | `str` | `"newsletter.html"` | Jinja2 template filename |

**Returns:** `str` — Rendered HTML.

### `render_newsletter_to_file(enriched_events, filepath, **kwargs)`

Render and save the newsletter to an HTML file. Creates parent directories if needed.

**Returns:** `Path` to the written file.

```python
from eventbrite_extractor.render import render_newsletter_to_file

render_newsletter_to_file(enriched, "output/newsletter.html", title="AI Events")
```

The newsletter template:
- Groups events by type (Conferences, Workshops, Talks, Meetups, etc.)
- Shows formatted date, location, price, and summary for each event
- Uses email-safe inline CSS with a modern purple gradient header
- Includes "View Event" buttons linking to Eventbrite

---

## Full Example

```python
from eventbrite_extractor import (
    EventbriteClient,
    transform_events,
    render_newsletter_to_file,
    export_to_json,
    export_to_csv,
)

client = EventbriteClient()

# Extract
events = client.search_events(keyword="AI", max_pages=3)

# Transform
enriched = transform_events(events, free_first=True)

# Export raw data
export_to_json(events, "output/events.json")
export_to_csv(events, "output/events.csv")

# Render newsletter
render_newsletter_to_file(enriched, "output/newsletter.html")

# Use enriched data
for ev in enriched:
    print(f"[{ev['event_type']}] {ev['title']}")
    print(f"  {ev['display_date']} · {ev['display_location']} · {ev['display_price']}")
```
