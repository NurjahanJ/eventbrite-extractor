# Project Info

## Overview

This project is a Python package (Python 3.9+) that extracts public event data from Eventbrite. It implements a complete **Extract → Transform → Export** pipeline focused on collecting, enriching, and exporting structured event data.

## Project Goals

- Programmatically extract public event data from Eventbrite
- Organize raw event information into a structured, reusable format
- Enrich events with display-ready fields (formatted dates, prices, locations, event types)
- Export clean data to JSON and CSV for downstream use

## What is Eventbrite?

Eventbrite is an online event discovery and ticketing platform. It hosts structured data including:

- Event titles and descriptions
- Dates, times, and timezones
- Physical and online locations
- Organizer details
- Pricing and ticketing information
- Categories and tags

## Why Eventbrite?

- Publicly accessible event listings
- Events searchable by keyword, location, and date
- Consistent, structured data suitable for automated extraction
- Official developer documentation available

## Pipeline

```
Extract (client.py)  →  Transform (transform.py)  →  Export (export.py)
  Eventbrite API          Filter, sort, enrich        JSON / CSV files
```

### Extract

- Connects to Eventbrite's `destination/search` API
- Supports keyword and location-based search
- Handles pagination via continuation tokens
- Automatic deduplication across pages
- Rate limit handling with exponential backoff

### Transform

- Filters cancelled and past events
- Sorts by date or title
- Enriches each event with display-ready fields:
  - `display_price` — `"Free"`, `"$50 USD"`, `"Paid"`
  - `display_date` — `"Wed, Mar 4 at 10:00 AM"`
  - `display_location` — Venue name, `"Online"`, or `"Location TBD"`
  - `event_type` — Conference, Workshop, Meetup, Talk, etc.

### Export

- JSON and CSV output
- Automatic directory creation

## Data Fields

The `Event` dataclass contains 23 fields per event:

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | `str` | Eventbrite event ID |
| `title` | `str` | Event name |
| `summary` | `str` | Short description |
| `start_date` / `end_date` | `str` | Date in `YYYY-MM-DD` format |
| `start_time` / `end_time` | `str` | Time in `HH:MM` format |
| `timezone` | `str` | Event timezone (e.g. `America/New_York`) |
| `is_online` | `bool` | Whether the event is virtual |
| `venue_name` | `str` | Venue name |
| `venue_address` | `str` | City, region, country (e.g. `New York, NY, US`) |
| `organizer_name` / `organizer_id` | `str` | Event organizer details |
| `url` | `str` | Eventbrite event page link |
| `is_free` | `bool` | Whether the event is free |
| `price` | `str` | Minimum ticket price |
| `currency` | `str` | Price currency code (e.g. `USD`) |
| `category` | `str` | Event category from Eventbrite tags |
| `tags` | `list[str]` | Tag display names |
| `image_url` | `str` | Event banner image URL |
| `is_cancelled` | `bool` | Whether the event is cancelled |
| `published` | `str` | Publication timestamp |
| `source_platform` | `str` | Always `"eventbrite"` |

## Scope

### Included

- Keyword and location-based event search
- Continuation-based pagination
- Deduplication, filtering, sorting, and enrichment
- JSON and CSV export
- CLI for one-command extraction
- Docker support for portable, reproducible runs

### Not Included

- Newsletter formatting or email delivery
- Database storage
- Subscriber management or scheduling

## Data Source

- [Eventbrite Platform API](https://www.eventbrite.com/platform/api)
- [Authentication Docs](https://www.eventbrite.com/platform/docs/authentication)
- [Events Endpoint Docs](https://www.eventbrite.com/platform/docs/events)
- [Rate Limits](https://www.eventbrite.com/platform/docs/rate-limits)
- [API Terms of Use](https://www.eventbrite.com/help/en-us/articles/833731/eventbrite-api-terms-of-use)