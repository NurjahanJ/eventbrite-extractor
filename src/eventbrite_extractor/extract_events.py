"""CLI script to extract and transform AI events from Eventbrite."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import sys
from pathlib import Path

from eventbrite_extractor.client import EventbriteClient
from eventbrite_extractor.config import NYC_PLACE_ID
from eventbrite_extractor.transform import transform_events

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def _save_json(data: list[dict], filepath: Path) -> None:
    """Write transformed event dicts to JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info("JSON saved to %s", filepath)


def _save_csv(data: list[dict], filepath: Path) -> None:
    """Write transformed event dicts to CSV."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if not data:
        filepath.write_text("", encoding="utf-8")
        return
    fieldnames = list(data[0].keys())
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            row = dict(row)
            if isinstance(row.get("tags"), list):
                row["tags"] = ", ".join(row["tags"])
            writer.writerow(row)
    logger.info("CSV saved to %s", filepath)


def main(argv: list[str] | None = None) -> None:
    """Run the extract + transform pipeline."""
    parser = argparse.ArgumentParser(
        description="Extract and transform AI events from Eventbrite.",
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

    # ── Extract ──────────────────────────────────────────────────
    logger.info(
        "Searching Eventbrite for '%s' events in %s (max %d pages)...",
        args.query,
        location_label,
        args.pages,
    )

    client = EventbriteClient()
    raw_events = client.search_events(
        keyword=args.query,
        place_id=place_id,
        online_only=args.online_only,
        max_pages=args.pages,
        page_size=args.page_size,
    )

    if not raw_events:
        logger.warning("No events found for query '%s'.", args.query)
        sys.exit(0)

    # ── Transform ────────────────────────────────────────────────
    events = transform_events(raw_events)

    if not events:
        logger.warning("No events remaining after transform.")
        sys.exit(0)

    # ── Export ────────────────────────────────────────────────────
    output_dir = Path(args.output_dir)
    if args.format in ("json", "both"):
        _save_json(events, output_dir / "events.json")

    if args.format in ("csv", "both"):
        _save_csv(events, output_dir / "events.csv")

    # ── Summary ──────────────────────────────────────────────────
    print(f"\n{'=' * 64}")
    print(f"  {len(events)} AI events in {location_label} (from Eventbrite)")
    print(f"{'=' * 64}\n")
    for i, event in enumerate(events, 1):
        print(f"  {i}. [{event['event_type']}] {event['title']}")
        print(f"     {event['display_date']}")
        print(f"     Location: {event['location']}")
        print(f"     Price: {event['display_price']}")
        print(f"     {event['url']}")
        print()


if __name__ == "__main__":
    main()
