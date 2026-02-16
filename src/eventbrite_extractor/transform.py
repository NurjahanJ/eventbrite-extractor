"""Transform module for cleaning, filtering, and enriching event data."""

from __future__ import annotations

import logging
from datetime import date, datetime

from eventbrite_extractor.models import Event

logger = logging.getLogger(__name__)

# Keywords used to classify events into categories
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Conference": [
        "conference",
        "summit",
        "symposium",
        "forum",
        "congress",
    ],
    "Workshop": [
        "workshop",
        "hands-on",
        "hands on",
        "bootcamp",
        "boot camp",
        "training",
        "masterclass",
        "master class",
        "crash course",
    ],
    "Meetup": [
        "meetup",
        "meet-up",
        "meet up",
        "networking",
        "mixer",
        "social",
        "happy hour",
        "after dark",
    ],
    "Webinar": [
        "webinar",
        "online session",
        "virtual event",
        "livestream",
        "live stream",
    ],
    "Hackathon": [
        "hackathon",
        "hack-a-thon",
        "buildathon",
        "code jam",
    ],
    "Talk": [
        "talk",
        "lecture",
        "keynote",
        "speaker",
        "panel",
        "fireside chat",
        "presentation",
    ],
    "Course": [
        "course",
        "class",
        "certification",
        "fundamentals",
        "foundations",
        "intro to",
        "introduction to",
        "basics",
    ],
}


def filter_events(
    events: list[Event],
    remove_cancelled: bool = True,
    remove_past: bool = True,
    reference_date: date | None = None,
) -> list[Event]:
    """Remove cancelled and past events.

    Args:
        events: List of events to filter.
        remove_cancelled: Drop events where is_cancelled is True.
        remove_past: Drop events whose start_date is before today.
        reference_date: Date to compare against (default: today).

    Returns:
        Filtered list of events.
    """
    today = reference_date or date.today()
    original_count = len(events)
    result: list[Event] = []

    for event in events:
        if remove_cancelled and event.is_cancelled:
            logger.debug("Filtered out cancelled event: %s", event.title)
            continue

        if remove_past and event.start_date:
            try:
                event_date = datetime.strptime(event.start_date, "%Y-%m-%d").date()
                if event_date < today:
                    logger.debug(
                        "Filtered out past event: %s (%s)",
                        event.title,
                        event.start_date,
                    )
                    continue
            except ValueError:
                pass  # Keep events with unparseable dates

        result.append(event)

    removed = original_count - len(result)
    if removed:
        logger.info("Filtered out %d events (%d remaining).", removed, len(result))
    return result


def sort_events(
    events: list[Event],
    by: str = "date",
    free_first: bool = False,
) -> list[Event]:
    """Sort events by the specified criteria.

    Args:
        events: List of events to sort.
        by: Sort key — "date" (earliest first) or "title" (alphabetical).
        free_first: If True, free events appear before paid events.

    Returns:
        Sorted list of events.
    """

    def _sort_key(event: Event) -> tuple:
        free_rank = 0 if (free_first and event.is_free) else 1

        if by == "title":
            return (free_rank, event.title.lower())

        # Default: sort by date, then time
        return (
            free_rank,
            event.start_date or "9999-99-99",
            event.start_time or "99:99",
        )

    return sorted(events, key=_sort_key)


def format_price(event: Event) -> str:
    """Return a human-readable price string for an event.

    Examples: "Free", "$50.00 USD", "Paid"
    """
    if event.is_free:
        return "Free"

    if event.price is not None:
        # Strip trailing zeros for clean display (50.00 -> $50, 5.04 -> $5.04)
        try:
            amount = float(event.price)
            if amount == 0:
                return "Free"
            formatted = f"{amount:.2f}".rstrip("0").rstrip(".")
            currency = event.currency or "USD"
            return f"${formatted} {currency}"
        except ValueError:
            return event.price

    return "Paid"


def format_date_display(event: Event) -> str:
    """Return a human-readable date string for an event.

    Examples: "Tue, Mar 4 at 10:00 AM", "Online · Sat, Feb 15"
    """
    parts: list[str] = []

    if event.start_date:
        try:
            dt = datetime.strptime(event.start_date, "%Y-%m-%d")
            # e.g. "Wed, Mar 4"
            day = dt.day  # int, no zero-padding
            parts.append(f"{dt.strftime('%a, %b')} {day}")
        except ValueError:
            parts.append(event.start_date)

    if event.start_time:
        try:
            t = datetime.strptime(event.start_time, "%H:%M")
            hour = t.hour % 12 or 12
            minute = t.strftime("%M")
            ampm = "AM" if t.hour < 12 else "PM"
            parts.append(f"at {hour}:{minute} {ampm}")
        except ValueError:
            parts.append(f"at {event.start_time}")

    return " ".join(parts) if parts else "Date TBD"


def format_location(event: Event) -> str:
    """Return a concise location string for an event."""
    if event.is_online:
        return "Online"
    if event.venue_name:
        return event.venue_name
    return "Location TBD"


def classify_event(event: Event) -> str:
    """Classify an event into a category based on its title and tags.

    Returns one of: Conference, Workshop, Meetup, Webinar, Hackathon,
    Talk, Course, or "Event" as a fallback.
    """
    searchable = event.title.lower()
    if event.summary:
        searchable += " " + event.summary.lower()
    for tag in event.tags:
        searchable += " " + tag.lower()

    for category, keywords in _CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in searchable:
                return category

    return "Event"


def transform_events(
    events: list[Event],
    remove_cancelled: bool = True,
    remove_past: bool = True,
    sort_by: str = "date",
    free_first: bool = False,
    reference_date: date | None = None,
) -> list[dict]:
    """Run the full transform pipeline on a list of events.

    Steps:
        1. Filter out cancelled and past events
        2. Sort by date (or title), optionally free-first
        3. Enrich each event with formatted display fields and category

    Args:
        events: Raw Event objects from the extractor.
        remove_cancelled: Drop cancelled events.
        remove_past: Drop events before today.
        sort_by: Sort key — "date" or "title".
        free_first: Put free events first.
        reference_date: Date to compare against for past-event filtering.

    Returns:
        List of enriched event dicts with display-ready fields.
    """
    # Step 1: Filter
    filtered = filter_events(
        events,
        remove_cancelled=remove_cancelled,
        remove_past=remove_past,
        reference_date=reference_date,
    )

    # Step 2: Sort
    sorted_events = sort_events(filtered, by=sort_by, free_first=free_first)

    # Step 3: Enrich
    enriched: list[dict] = []
    for event in sorted_events:
        data = event.to_dict()
        data["display_price"] = format_price(event)
        data["display_date"] = format_date_display(event)
        data["display_location"] = format_location(event)
        data["event_type"] = classify_event(event)
        enriched.append(data)

    logger.info(
        "Transform complete: %d events → %d enriched records.",
        len(events),
        len(enriched),
    )
    return enriched
