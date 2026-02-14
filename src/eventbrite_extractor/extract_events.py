"""CLI script to extract AI events from Eventbrite."""

from __future__ import annotations

import argparse
import logging
import sys

from eventbrite_extractor.client import EventbriteClient
from eventbrite_extractor.config import NYC_PLACE_ID
from eventbrite_extractor.export import export_to_csv, export_to_json
from eventbrite_extractor.transform import transform_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    """Run the event extraction pipeline."""
    parser = argparse.ArgumentParser(
        description="Extract AI events from Eventbrite.",
    )
    parser.add_argument(
        "-q",
        "--query",
        default="AI",
        help="Search keyword (default: 'AI').",
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=3,
        help="Max pages to fetch (default: 3).",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=20,
        help="Results per page (default: 20, max: 50).",
    )
    parser.add_argument(
        "--place-id",
        default=NYC_PLACE_ID,
        help="Who's On First place ID for location filter "
        "(default: NYC '85977539'). Use 'none' for worldwide.",
    )
    parser.add_argument(
        "--online-only",
        action="store_true",
        help="Only include online events.",
    )
    parser.add_argument(
        "--sort-by",
        choices=["date", "title"],
        default="date",
        help="Sort events by 'date' or 'title' (default: date).",
    )
    parser.add_argument(
        "--free-first",
        action="store_true",
        help="Show free events before paid events.",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv", "both"],
        default="both",
        help="Output format (default: both).",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output",
        help="Output directory (default: 'output/').",
    )

    args = parser.parse_args(argv)

    place_id = None if args.place_id.lower() == "none" else args.place_id
    location_label = "NYC" if place_id == NYC_PLACE_ID else (place_id or "worldwide")

    logger.info(
        "Searching Eventbrite for '%s' events in %s (max %d pages)...",
        args.query,
        location_label,
        args.pages,
    )

    client = EventbriteClient()
    events = client.search_events(
        keyword=args.query,
        place_id=place_id,
        online_only=args.online_only,
        max_pages=args.pages,
        page_size=args.page_size,
    )

    if not events:
        logger.warning("No events found for query '%s'.", args.query)
        sys.exit(0)

    logger.info("Found %d raw events. Transforming...", len(events))

    # --- Transform ---
    enriched = transform_events(
        events,
        sort_by=args.sort_by,
        free_first=args.free_first,
    )

    if not enriched:
        logger.warning("No events remaining after filtering.")
        sys.exit(0)

    logger.info("%d events after transform. Exporting...", len(enriched))

    # --- Export ---
    output_dir = args.output_dir
    if args.format in ("json", "both"):
        path = export_to_json(events, f"{output_dir}/events.json")
        logger.info("JSON saved to %s", path)

    if args.format in ("csv", "both"):
        path = export_to_csv(events, f"{output_dir}/events.csv")
        logger.info("CSV saved to %s", path)

    # --- Print summary ---
    print(f"\n{'=' * 64}")
    print(f"  {len(enriched)} events in {location_label} (from {len(events)} raw)")
    print(f"{'=' * 64}\n")

    for i, ev in enumerate(enriched, 1):
        tag = ev["event_type"]
        print(f"  {i}. [{tag}] {ev['title']}")
        print(f"     {ev['display_date']}")
        print(f"     {ev['display_location']}")
        print(f"     {ev['display_price']}")
        print(f"     {ev['url']}")
        print()


if __name__ == "__main__":
    main()
