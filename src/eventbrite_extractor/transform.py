"""Transform pipeline: filter, enrich, and categorize extracted events."""

from __future__ import annotations

import logging
from datetime import date, datetime

from eventbrite_extractor.models import Event

logger = logging.getLogger(__name__)

# Event type keywords mapped from Eventbrite tags and titles
_EVENT_TYPE_KEYWORDS: dict[str, list[str]] = {
    "Conference": ["conference", "summit", "symposium", "forum"],
    "Workshop": ["workshop", "hands-on", "bootcamp", "training", "masterclass"],
    "Meetup": ["meetup", "meet-up", "networking", "mixer", "happy hour"],
    "Webinar": ["webinar", "online session", "virtual talk"],
    "Seminar": ["seminar", "talk", "lecture", "panel", "fireside chat"],
    "Hackathon": ["hackathon", "hack day", "buildathon"],
    "Course": ["course", "class", "certification", "program"],
}


# ── Filtering ────────────────────────────────────────────────────────


def filter_cancelled(events: list[Event]) -> list[Event]:
    """Remove cancelled events."""
    result = [e for e in events if not e.is_cancelled]
    removed = len(events) - len(result)
    if removed:
        logger.info("Removed %d cancelled event(s).", removed)
    return result


def filter_past_events(events: list[Event], cutoff: date | None = None) -> list[Event]:
    """Remove events whose start_date is before the cutoff.

    Args:
        events: List of events.
        cutoff: Date to compare against. Defaults to today.

    Returns:
        Events on or after the cutoff date.
    """
    cutoff = cutoff or date.today()
    result: list[Event] = []
    for event in events:
        if not event.start_date:
            result.append(event)
            continue
        try:
            event_date = date.fromisoformat(event.start_date)
            if event_date >= cutoff:
                result.append(event)
        except ValueError:
            result.append(event)

    removed = len(events) - len(result)
    if removed:
        logger.info("Removed %d past event(s).", removed)
    return result


def deduplicate(events: list[Event]) -> list[Event]:
    """Remove duplicate events by event_id."""
    seen: set[str] = set()
    result: list[Event] = []
    for event in events:
        if event.event_id not in seen:
            seen.add(event.event_id)
            result.append(event)
    removed = len(events) - len(result)
    if removed:
        logger.info("Removed %d duplicate event(s).", removed)
    return result


# ── Enrichment ───────────────────────────────────────────────────────


def normalize_pricing(event: Event) -> Event:
    """Normalize pricing fields.

    - If price is "0.00" or "0", mark as free.
    - If is_free is True, clear price/currency.
    - Format price as a display string (e.g. "$25.00").
    """
    if event.price in ("0.00", "0", "0.0"):
        event.is_free = True
        event.price = None
        event.currency = None
    elif event.is_free:
        event.price = None
        event.currency = None

    if event.price and event.currency:
        currency_symbols = {"USD": "$", "EUR": "€", "GBP": "£", "CAD": "CA$"}
        symbol = currency_symbols.get(event.currency, f"{event.currency} ")
        if not event.price.startswith(symbol):
            event.price = f"{symbol}{event.price}"

    return event


def format_display_date(event: Event) -> str | None:
    """Create a human-readable date string from an event.

    Examples:
        "Thu, Feb 27, 2026 at 12:00 PM"
        "Thu, Feb 27, 2026 (Online)"

    Returns:
        Formatted date string, or None if no date available.
    """
    if not event.start_date:
        return None

    try:
        dt_str = f"{event.start_date} {event.start_time or '00:00'}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        formatted = dt.strftime("%a, %b %d, %Y at %I:%M %p")
        return formatted
    except ValueError:
        return event.start_date


def clean_tags(event: Event) -> Event:
    """Remove duplicate tags and normalize casing."""
    seen: set[str] = set()
    cleaned: list[str] = []
    for tag in event.tags:
        tag_lower = tag.lower()
        if tag_lower not in seen:
            seen.add(tag_lower)
            cleaned.append(tag)
    event.tags = cleaned
    return event


# ── Categorization ───────────────────────────────────────────────────


def classify_event_type(event: Event) -> str:
    """Determine the event type from tags and title.

    Returns:
        A string like "Conference", "Workshop", "Meetup", etc.
        Defaults to "Event" if no match is found.
    """
    searchable = " ".join(event.tags + [event.title]).lower()

    for event_type, keywords in _EVENT_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword in searchable:
                return event_type

    return "Event"


# ── Full Pipeline ────────────────────────────────────────────────────


def transform_events(events: list[Event], cutoff: date | None = None) -> list[dict]:
    """Run the full transform pipeline on a list of events.

    Steps:
        1. Remove cancelled events
        2. Remove past events
        3. Deduplicate
        4. Normalize pricing
        5. Clean tags
        6. Classify event type
        7. Format display date
        8. Sort by start date

    Args:
        events: Raw list of Event objects from the extractor.
        cutoff: Date cutoff for filtering past events.

    Returns:
        A list of enriched event dicts ready for newsletter use.
    """
    logger.info("Transforming %d raw events...", len(events))

    # Filter
    events = filter_cancelled(events)
    events = filter_past_events(events, cutoff=cutoff)
    events = deduplicate(events)

    # Enrich, categorize, and build output
    results: list[dict] = []
    for event in events:
        normalize_pricing(event)
        clean_tags(event)

        enriched = event.to_dict()
        enriched["event_type"] = classify_event_type(event)
        enriched["display_date"] = format_display_date(event)
        enriched["display_price"] = (
            "Free" if event.is_free else (event.price or "See event page")
        )
        enriched["location"] = (
            "Online" if event.is_online else (event.venue_name or "TBD")
        )

        results.append(enriched)

    # Sort by start_date (earliest first), events without dates go last
    results.sort(key=lambda e: e.get("start_date") or "9999-99-99")

    logger.info("Transform complete: %d events ready for newsletter.", len(results))
    return results
