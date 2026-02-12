"""Tests for the transform pipeline."""

from __future__ import annotations

from datetime import date

from eventbrite_extractor.models import Event
from eventbrite_extractor.transform import (
    classify_event_type,
    clean_tags,
    deduplicate,
    filter_cancelled,
    filter_past_events,
    format_display_date,
    normalize_pricing,
    transform_events,
)


def _make_event(**overrides) -> Event:
    """Create a test event with sensible defaults."""
    defaults = {
        "event_id": "1",
        "title": "AI Workshop",
        "start_date": "2026-06-01",
        "start_time": "10:00",
        "end_date": "2026-06-01",
        "end_time": "12:00",
        "timezone": "America/New_York",
    }
    defaults.update(overrides)
    return Event(**defaults)


class TestFilterCancelled:
    def test_removes_cancelled(self):
        events = [_make_event(), _make_event(event_id="2", is_cancelled=True)]
        result = filter_cancelled(events)
        assert len(result) == 1
        assert result[0].event_id == "1"

    def test_keeps_all_if_none_cancelled(self):
        events = [_make_event(), _make_event(event_id="2")]
        assert len(filter_cancelled(events)) == 2


class TestFilterPastEvents:
    def test_removes_past_events(self):
        events = [
            _make_event(start_date="2020-01-01"),
            _make_event(event_id="2", start_date="2030-01-01"),
        ]
        result = filter_past_events(events, cutoff=date(2025, 1, 1))
        assert len(result) == 1
        assert result[0].event_id == "2"

    def test_keeps_events_on_cutoff_date(self):
        events = [_make_event(start_date="2026-03-01")]
        result = filter_past_events(events, cutoff=date(2026, 3, 1))
        assert len(result) == 1

    def test_keeps_events_without_date(self):
        events = [_make_event(start_date=None)]
        result = filter_past_events(events, cutoff=date(2026, 1, 1))
        assert len(result) == 1


class TestDeduplicate:
    def test_removes_duplicates(self):
        events = [_make_event(), _make_event(), _make_event(event_id="2")]
        result = deduplicate(events)
        assert len(result) == 2

    def test_preserves_order(self):
        events = [
            _make_event(event_id="a"),
            _make_event(event_id="b"),
            _make_event(event_id="a"),
        ]
        result = deduplicate(events)
        assert [e.event_id for e in result] == ["a", "b"]


class TestNormalizePricing:
    def test_zero_price_becomes_free(self):
        event = _make_event(is_free=False, price="0.00", currency="USD")
        normalize_pricing(event)
        assert event.is_free is True
        assert event.price is None
        assert event.currency is None

    def test_free_event_clears_price(self):
        event = _make_event(is_free=True, price="10.00", currency="USD")
        normalize_pricing(event)
        assert event.price is None

    def test_paid_event_gets_symbol(self):
        event = _make_event(is_free=False, price="25.00", currency="USD")
        normalize_pricing(event)
        assert event.price == "$25.00"

    def test_eur_symbol(self):
        event = _make_event(is_free=False, price="50.00", currency="EUR")
        normalize_pricing(event)
        assert event.price == "€50.00"

    def test_unknown_currency_uses_code(self):
        event = _make_event(is_free=False, price="100.00", currency="JPY")
        normalize_pricing(event)
        assert event.price == "JPY 100.00"


class TestFormatDisplayDate:
    def test_formats_date_and_time(self):
        event = _make_event(start_date="2026-03-01", start_time="14:00")
        result = format_display_date(event)
        assert result == "Sun, Mar 01, 2026 at 02:00 PM"

    def test_no_time_defaults_to_midnight(self):
        event = _make_event(start_date="2026-03-01", start_time=None)
        result = format_display_date(event)
        assert "12:00 AM" in result

    def test_no_date_returns_none(self):
        event = _make_event(start_date=None)
        assert format_display_date(event) is None


class TestCleanTags:
    def test_removes_duplicate_tags(self):
        event = _make_event(tags=["Science", "Tech", "science", "AI"])
        clean_tags(event)
        assert len(event.tags) == 3
        assert "Science" in event.tags
        assert "AI" in event.tags

    def test_preserves_original_casing(self):
        event = _make_event(tags=["Machine Learning", "machine learning"])
        clean_tags(event)
        assert event.tags == ["Machine Learning"]


class TestClassifyEventType:
    def test_conference(self):
        event = _make_event(title="AI Summit 2026", tags=["Conference"])
        assert classify_event_type(event) == "Conference"

    def test_workshop(self):
        event = _make_event(title="Hands-On AI Workshop")
        assert classify_event_type(event) == "Workshop"

    def test_meetup(self):
        event = _make_event(title="AI Networking Mixer", tags=["Meetup"])
        assert classify_event_type(event) == "Meetup"

    def test_seminar_from_tags(self):
        event = _make_event(title="AI Event", tags=["Seminar or Talk"])
        assert classify_event_type(event) == "Seminar"

    def test_hackathon(self):
        event = _make_event(title="AI Hackathon NYC")
        assert classify_event_type(event) == "Hackathon"

    def test_course(self):
        event = _make_event(title="AI Certification Course")
        assert classify_event_type(event) == "Course"

    def test_default_event(self):
        event = _make_event(title="Something About AI", tags=[])
        assert classify_event_type(event) == "Event"


class TestTransformPipeline:
    def test_full_pipeline(self):
        events = [
            _make_event(
                event_id="1",
                start_date="2026-06-01",
                is_cancelled=False,
                is_free=False,
                price="0.00",
                currency="USD",
                tags=["Science", "science", "AI"],
            ),
            _make_event(event_id="2", is_cancelled=True),
            _make_event(event_id="1"),  # duplicate
            _make_event(event_id="3", start_date="2020-01-01"),  # past
        ]
        result = transform_events(events, cutoff=date(2025, 1, 1))

        assert len(result) == 1
        assert result[0]["event_id"] == "1"
        assert result[0]["display_price"] == "Free"
        assert result[0]["event_type"] == "Workshop"
        assert "display_date" in result[0]
        assert "location" in result[0]

    def test_sorts_by_date(self):
        events = [
            _make_event(event_id="b", start_date="2026-09-01"),
            _make_event(event_id="a", start_date="2026-03-01"),
        ]
        result = transform_events(events, cutoff=date(2025, 1, 1))
        assert result[0]["event_id"] == "a"
        assert result[1]["event_id"] == "b"

    def test_enriched_fields_present(self):
        events = [_make_event(is_online=True, is_free=True)]
        result = transform_events(events, cutoff=date(2025, 1, 1))
        assert result[0]["location"] == "Online"
        assert result[0]["display_price"] == "Free"
        assert result[0]["event_type"] is not None
        assert result[0]["display_date"] is not None
