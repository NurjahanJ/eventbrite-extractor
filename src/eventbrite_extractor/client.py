"""Eventbrite API client for extracting public event data."""

from __future__ import annotations

import logging
import time

import requests

from eventbrite_extractor.config import (
    BASE_URL,
    DEFAULT_PAGE_SIZE,
    NYC_PLACE_ID,
    REQUEST_TIMEOUT,
    get_api_key,
)
from eventbrite_extractor.models import Event

logger = logging.getLogger(__name__)

# Fields to expand in the destination/search response
_EXPAND_FIELDS = [
    "primary_venue",
    "image",
    "primary_organizer",
    "ticket_availability",
]


class EventbriteClient:
    """Client for the Eventbrite destination/search API.

    Handles authentication, event searching, continuation-based
    pagination, and rate limit retries.
    """

    def __init__(self, api_key: str | None = None):
        """Initialize the client.

        Args:
            api_key: Eventbrite private token. If not provided,
                     reads from the EVENTBRITE_API_KEY env var.
        """
        self._api_key = api_key or get_api_key()
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            }
        )

    def _post(self, endpoint: str, body: dict) -> dict:
        """Make a POST request to the Eventbrite API.

        Handles rate limiting with exponential backoff.

        Args:
            endpoint: API endpoint path.
            body: JSON request body.

        Returns:
            Parsed JSON response as a dict.

        Raises:
            requests.HTTPError: If the request fails after retries.
        """
        url = f"{BASE_URL}{endpoint}"
        max_retries = 3

        for attempt in range(max_retries):
            response = self._session.post(url, json=body, timeout=REQUEST_TIMEOUT)

            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 2**attempt))
                logger.warning("Rate limited. Retrying in %d seconds...", wait)
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response.json()

        # Final attempt
        response = self._session.post(url, json=body, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        """Make a GET request to the Eventbrite API.

        Args:
            endpoint: API endpoint path.
            params: Query parameters.

        Returns:
            Parsed JSON response as a dict.
        """
        url = f"{BASE_URL}{endpoint}"
        max_retries = 3

        for attempt in range(max_retries):
            response = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT)

            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", 2**attempt))
                logger.warning("Rate limited. Retrying in %d seconds...", wait)
                time.sleep(wait)
                continue

            response.raise_for_status()
            return response.json()

        response = self._session.get(url, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def search_events(
        self,
        keyword: str,
        place_id: str | None = NYC_PLACE_ID,
        online_only: bool = False,
        max_pages: int = 1,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> list[Event]:
        """Search for public events on Eventbrite.

        Uses the destination/search endpoint with POST and
        continuation-based pagination.

        Args:
            keyword: Search query (e.g. "AI", "machine learning").
            place_id: Who's On First place ID to filter by location.
                      Defaults to NYC ("85977539"). Pass None for
                      worldwide results.
            online_only: If True, only return online events.
            max_pages: Maximum number of pages to fetch.
            page_size: Number of results per page (max 50).

        Returns:
            A list of Event objects.
        """
        event_search: dict = {
            "q": keyword,
            "dates": ["current_future"],
            "page_size": min(page_size, 50),
        }

        if place_id:
            event_search["places"] = [place_id]

        if online_only:
            event_search["online_events_only"] = True

        body: dict = {
            "event_search": event_search,
            "expand.destination_event": _EXPAND_FIELDS,
        }

        all_events: list[Event] = []
        seen_ids: set[str] = set()

        for page_num in range(1, max_pages + 1):
            logger.info("Fetching page %d...", page_num)

            data = self._post("/destination/search/", body=body)
            events_data = data.get("events", {})
            raw_events = events_data.get("results", [])

            if not raw_events:
                logger.info("No more events found on page %d.", page_num)
                break

            for raw in raw_events:
                event = Event.from_api_response(raw)
                if event.event_id not in seen_ids:
                    seen_ids.add(event.event_id)
                    all_events.append(event)

            # Check for next page via continuation token
            pagination = events_data.get("pagination", {})
            continuation = pagination.get("continuation")

            if not continuation:
                logger.info("No more pages available.")
                break

            # Set continuation for next request
            event_search["continuation"] = continuation
            body["event_search"] = event_search

        logger.info("Extracted %d unique events.", len(all_events))
        return all_events

    def get_event_by_id(self, event_id: str) -> Event:
        """Fetch a single event by its Eventbrite ID.

        Args:
            event_id: The Eventbrite event ID.

        Returns:
            An Event object.

        Raises:
            requests.HTTPError: If the event is not found.
        """
        data = self._get(f"/events/{event_id}/")
        return Event.from_api_response(data)
