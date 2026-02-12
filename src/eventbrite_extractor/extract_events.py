"""CLI script to extract AI events from Eventbrite for the newsletter."""

from __future__ import annotations

import argparse
import logging
import sys

from eventbrite_extractor.client import EventbriteClient
from eventbrite_extractor.config import NYC_PLACE_ID
from eventbrite_extractor.export import export_to_csv, export_to_json

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main(argv: list[str] | None = None) -> None:
    """Run the event extraction pipeline."""
    parser = argparse.ArgumentParser(
        description="Extract AI events from Eventbrite for newsletter use.",
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

    logger.info("Found %d events. Exporting...", len(events))

    output_dir = args.output_dir
    if args.format in ("json", "both"):
        path = export_to_json(events, f"{output_dir}/events.json")
        logger.info("JSON saved to %s", path)

    if args.format in ("csv", "both"):
        path = export_to_csv(events, f"{output_dir}/events.csv")
        logger.info("CSV saved to %s", path)

    # Print a summary to stdout
    print(f"\n{'=' * 60}")
    print(f"  Extracted {len(events)} AI events from Eventbrite ({location_label})")
    print(f"{'=' * 60}\n")
    for i, event in enumerate(events, 1):
        status = "FREE" if event.is_free else (event.price or "Paid")
        location = "Online" if event.is_online else (event.venue_name or "TBD")
        print(f"  {i}. {event.title}")
        print(f"     Date: {event.start_date} at {event.start_time}")
        print(f"     Location: {location}")
        print(f"     Price: {status}")
        print(f"     URL: {event.url}")
        print()


if __name__ == "__main__":
    main()
