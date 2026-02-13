"""Newsletter rendering module using Jinja2 templates."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

# Path to the templates directory
_TEMPLATES_DIR = Path(__file__).parent / "templates"

# Preferred display order for event types
_TYPE_ORDER = [
    "Conference",
    "Workshop",
    "Hackathon",
    "Course",
    "Talk",
    "Webinar",
    "Meetup",
    "Event",
]


def _group_events(
    enriched_events: list[dict],
) -> list[dict]:
    """Group enriched event dicts by event_type.

    Returns a list of dicts with 'type' and 'events' keys,
    ordered by _TYPE_ORDER.
    """
    buckets: dict[str, list[dict]] = defaultdict(list)
    for event in enriched_events:
        event_type = event.get("event_type", "Event")
        buckets[event_type].append(event)

    groups: list[dict] = []
    for event_type in _TYPE_ORDER:
        if event_type in buckets:
            groups.append({"type": event_type, "events": buckets.pop(event_type)})

    # Any remaining types not in _TYPE_ORDER
    for event_type, events in sorted(buckets.items()):
        groups.append({"type": event_type, "events": events})

    return groups


def render_newsletter(
    enriched_events: list[dict],
    title: str = "AI Events in NYC",
    subtitle: str | None = None,
    intro_text: str | None = None,
    template_name: str = "newsletter.html",
) -> str:
    """Render enriched events into an HTML newsletter.

    Args:
        enriched_events: List of enriched event dicts from
                         transform_events().
        title: Newsletter title.
        subtitle: Subtitle shown below the title.
        intro_text: Introductory paragraph text.
        template_name: Jinja2 template filename.

    Returns:
        Rendered HTML string.
    """
    today = date.today()

    if subtitle is None:
        subtitle = today.strftime("%B %Y")

    if intro_text is None:
        intro_text = (
            f"Here are {len(enriched_events)} upcoming AI events "
            f"we found for you this week. Happy networking!"
        )

    event_groups = _group_events(enriched_events)

    env = Environment(
        loader=FileSystemLoader(str(_TEMPLATES_DIR)),
        autoescape=True,
    )
    template = env.get_template(template_name)

    html = template.render(
        title=title,
        subtitle=subtitle,
        intro_text=intro_text,
        event_groups=event_groups,
        total_events=len(enriched_events),
        generated_date=today.strftime("%B %d, %Y"),
    )

    logger.info(
        "Rendered newsletter with %d events in %d groups.",
        len(enriched_events),
        len(event_groups),
    )
    return html


def render_newsletter_to_file(
    enriched_events: list[dict],
    filepath: str | Path,
    **kwargs,
) -> Path:
    """Render and save the newsletter to an HTML file.

    Args:
        enriched_events: List of enriched event dicts.
        filepath: Output file path.
        **kwargs: Passed to render_newsletter().

    Returns:
        Path to the written file.
    """
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    html = render_newsletter(enriched_events, **kwargs)
    filepath.write_text(html, encoding="utf-8")

    logger.info("Newsletter saved to %s", filepath)
    return filepath
