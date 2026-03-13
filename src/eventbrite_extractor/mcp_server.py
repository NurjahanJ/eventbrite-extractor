"""MCP server for Eventbrite event extraction.

Exposes tools and resources for AI assistants to query Eventbrite data.
"""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from eventbrite_extractor.client import EventbriteClient
from eventbrite_extractor.config import NYC_PLACE_ID
from eventbrite_extractor.transform import transform_events

# Initialize FastMCP server
mcp = FastMCP(
    "Eventbrite Extractor",
    dependencies=["requests", "python-dotenv"],
)


# ---------------------------------------------------------------------------
# Tools - Functions that AI assistants can call
# ---------------------------------------------------------------------------


@mcp.tool()
def search_events(
    keyword: str,
    location: str = "nyc",
    max_pages: int = 1,
    online_only: bool = False,
    free_first: bool = False,
) -> str:
    """Search for events on Eventbrite.

    Args:
        keyword: Search query (e.g., "AI", "machine learning", "python")
        location: Location filter - "nyc" for New York City, "worldwide" for no filter,
                  or a Who's On First place ID
        max_pages: Maximum number of pages to fetch (1-10)
        online_only: If True, only return online/virtual events
        free_first: If True, sort free events before paid events

    Returns:
        JSON string containing enriched event data with fields:
        - event_id, title, summary
        - start_date, start_time, timezone
        - venue_name, venue_address, is_online
        - organizer_name, url
        - is_free, price, currency
        - display_price, display_date, display_location, event_type
    """
    # Resolve location
    if location.lower() == "nyc":
        place_id = NYC_PLACE_ID
    elif location.lower() == "worldwide":
        place_id = None
    else:
        place_id = location

    # Limit max_pages to prevent abuse
    max_pages = min(max(1, max_pages), 10)

    # Extract events
    client = EventbriteClient()
    raw_events = client.search_events(
        keyword=keyword,
        place_id=place_id,
        online_only=online_only,
        max_pages=max_pages,
        page_size=20,
    )

    # Transform and enrich
    enriched = transform_events(raw_events, free_first=free_first)

    return json.dumps(enriched, indent=2, ensure_ascii=False)


@mcp.tool()
def get_event_by_id(event_id: str) -> str:
    """Fetch a specific event by its Eventbrite ID.

    Args:
        event_id: The Eventbrite event ID (e.g., "1234567890123")

    Returns:
        JSON string containing the event details
    """
    client = EventbriteClient()
    event = client.get_event_by_id(event_id)
    return json.dumps(event.to_dict(), indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Resources - Static or dynamic data that can be read
# ---------------------------------------------------------------------------


@mcp.resource("eventbrite://events/ai-nyc")
def get_ai_events_nyc() -> str:
    """Get the latest AI events in New York City.

    Returns:
        JSON string with up to 20 upcoming AI events in NYC
    """
    client = EventbriteClient()
    raw_events = client.search_events(
        keyword="AI",
        place_id=NYC_PLACE_ID,
        max_pages=1,
        page_size=20,
    )
    enriched = transform_events(raw_events)
    return json.dumps(enriched, indent=2, ensure_ascii=False)


@mcp.resource("eventbrite://events/{keyword}/{location}")
def get_events_by_keyword_location(keyword: str, location: str) -> str:
    """Get events for a specific keyword and location.

    Args:
        keyword: Search term (e.g., "python", "data-science")
        location: "nyc", "worldwide", or a place ID

    Returns:
        JSON string with matching events
    """
    # Resolve location
    if location.lower() == "nyc":
        place_id = NYC_PLACE_ID
    elif location.lower() == "worldwide":
        place_id = None
    else:
        place_id = location

    client = EventbriteClient()
    raw_events = client.search_events(
        keyword=keyword,
        place_id=place_id,
        max_pages=1,
        page_size=20,
    )
    enriched = transform_events(raw_events)
    return json.dumps(enriched, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Prompts - Templates for generating LLM prompts
# ---------------------------------------------------------------------------


@mcp.prompt()
def event_summary_prompt(keyword: str, location: str = "nyc") -> str:
    """Generate a prompt for summarizing events.

    Args:
        keyword: Event topic to search for
        location: Location filter (default: NYC)

    Returns:
        A prompt template for the LLM
    """
    return f"""Please search for {keyword} events in {location} and provide a \
concise summary including:

1. Total number of events found
2. Date range (earliest to latest event)
3. Price range (free vs paid, and typical costs)
4. Most common event types (workshops, conferences, meetups, etc.)
5. Top 3 most interesting events with brief descriptions

Use the search_events tool to fetch the data."""


@mcp.prompt()
def event_recommendation_prompt(
    interests: str,
    budget: str = "any",
    timeframe: str = "next month",
) -> str:
    """Generate a prompt for event recommendations.

    Args:
        interests: User's interests (e.g., "AI and machine learning")
        budget: Budget constraint ("free", "under $50", "any")
        timeframe: When they want to attend ("this week", "next month", etc.)

    Returns:
        A prompt template for personalized recommendations
    """
    return f"""I'm interested in {interests} and looking for events {timeframe}.
My budget is: {budget}.

Please:
1. Search for relevant events using the search_events tool
2. Filter based on my budget preference
3. Recommend the top 5 events that best match my interests
4. For each event, explain why it's a good fit
5. Include practical details (date, time, location, price, link)"""
