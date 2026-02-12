"""Tests for the Eventbrite API client."""

from unittest.mock import MagicMock, patch

import pytest

from eventbrite_extractor.client import EventbriteClient

# Sample event matching the real destination/search response format
SAMPLE_EVENT = {
    "id": "111",
    "name": "AI Workshop",
    "summary": "A workshop about AI.",
    "start_date": "2026-04-01",
    "start_time": "10:00",
    "end_date": "2026-04-01",
    "end_time": "12:00",
    "timezone": "UTC",
    "is_online_event": False,
    "primary_venue": {
        "name": "Test Venue",
        "address": {"city": "Boston", "region": "MA", "country": "US"},
    },
    "primary_organizer": {"name": "Test Org", "id": "org1"},
    "url": "https://www.eventbrite.com/e/111",
    "ticket_availability": {
        "is_free": True,
        "has_available_tickets": True,
        "is_sold_out": False,
    },
    "tags": [
        {
            "prefix": "EventbriteCategory",
            "display_name": "Science & Technology",
        },
    ],
    "image": {"url": "https://img.example.com/logo.png"},
    "published": "2026-01-10T08:00:00Z",
}

SAMPLE_SEARCH_RESPONSE = {
    "events": {
        "results": [SAMPLE_EVENT],
        "pagination": {
            "object_count": 1,
            "page_size": 20,
        },
    },
}


class TestEventbriteClient:
    """Tests for the EventbriteClient."""

    def _make_client(self):
        """Create a client with a fake API key."""
        return EventbriteClient(api_key="fake_token")

    def test_search_events_returns_events(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_SEARCH_RESPONSE
        mock_response.raise_for_status = MagicMock()

        client = self._make_client()
        client._session = MagicMock()
        client._session.post.return_value = mock_response

        events = client.search_events(keyword="AI")
        assert len(events) == 1
        assert events[0].event_id == "111"
        assert events[0].title == "AI Workshop"
        assert events[0].venue_name == "Test Venue"
        assert events[0].venue_address == "Boston, MA, US"

    def test_search_events_deduplicates(self):
        """Duplicate events in results should be deduplicated."""
        response = {
            "events": {
                "results": [SAMPLE_EVENT, SAMPLE_EVENT],
                "pagination": {
                    "object_count": 2,
                    "page_size": 20,
                },
            },
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = response
        mock_response.raise_for_status = MagicMock()

        client = self._make_client()
        client._session = MagicMock()
        client._session.post.return_value = mock_response

        events = client.search_events(keyword="AI")
        assert len(events) == 1

    def test_search_events_empty_response(self):
        empty_response = {
            "events": {
                "results": [],
                "pagination": {
                    "object_count": 0,
                    "page_size": 20,
                },
            },
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = empty_response
        mock_response.raise_for_status = MagicMock()

        client = self._make_client()
        client._session = MagicMock()
        client._session.post.return_value = mock_response

        events = client.search_events(keyword="nonexistent")
        assert len(events) == 0

    def test_search_events_pagination(self):
        """Test that continuation-based pagination works."""
        page1 = {
            "events": {
                "results": [SAMPLE_EVENT],
                "pagination": {
                    "object_count": 2,
                    "page_size": 1,
                    "continuation": "eyJwYWdlIjoyfQ",
                },
            },
        }
        event2 = {**SAMPLE_EVENT, "id": "222", "name": "AI Talk"}
        page2 = {
            "events": {
                "results": [event2],
                "pagination": {
                    "object_count": 2,
                    "page_size": 1,
                },
            },
        }

        mock_resp1 = MagicMock()
        mock_resp1.status_code = 200
        mock_resp1.json.return_value = page1
        mock_resp1.raise_for_status = MagicMock()

        mock_resp2 = MagicMock()
        mock_resp2.status_code = 200
        mock_resp2.json.return_value = page2
        mock_resp2.raise_for_status = MagicMock()

        client = self._make_client()
        client._session = MagicMock()
        client._session.post.side_effect = [mock_resp1, mock_resp2]

        events = client.search_events(keyword="AI", max_pages=2)
        assert len(events) == 2
        assert events[0].event_id == "111"
        assert events[1].event_id == "222"

    def test_get_event_by_id(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_EVENT
        mock_response.raise_for_status = MagicMock()

        client = self._make_client()
        client._session = MagicMock()
        client._session.get.return_value = mock_response

        event = client.get_event_by_id("111")
        assert event.event_id == "111"
        assert event.title == "AI Workshop"

    def test_search_events_includes_place_id(self):
        """Default search should include NYC place ID."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_SEARCH_RESPONSE
        mock_response.raise_for_status = MagicMock()

        client = self._make_client()
        client._session = MagicMock()
        client._session.post.return_value = mock_response

        client.search_events(keyword="AI")

        call_args = client._session.post.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert "places" in body["event_search"]
        assert body["event_search"]["places"] == ["85977539"]

    def test_search_events_no_place_id(self):
        """Passing place_id=None should omit places from search."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = SAMPLE_SEARCH_RESPONSE
        mock_response.raise_for_status = MagicMock()

        client = self._make_client()
        client._session = MagicMock()
        client._session.post.return_value = mock_response

        client.search_events(keyword="AI", place_id=None)

        call_args = client._session.post.call_args
        body = call_args.kwargs.get("json") or call_args[1].get("json")
        assert "places" not in body["event_search"]

    def test_client_requires_api_key(self):
        with (
            patch.dict("os.environ", {}, clear=True),
            patch(
                "eventbrite_extractor.config.os.getenv",
                return_value=None,
            ),
            pytest.raises(ValueError, match="EVENTBRITE_API_KEY"),
        ):
            EventbriteClient()
