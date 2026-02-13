"""Tests for the newsletter rendering module."""

from __future__ import annotations

from pathlib import Path

from eventbrite_extractor.render import (
    _group_events,
    render_newsletter,
    render_newsletter_to_file,
)


def _sample_events() -> list[dict]:
    """Create sample enriched event dicts for testing."""
    return [
        {
            "event_id": "1",
            "title": "AI Summit NYC",
            "summary": "A big AI conference.",
            "url": "https://example.com/1",
            "display_date": "Wed, Mar 4 at 10:00 AM",
            "display_location": "Javits Center",
            "display_price": "Free",
            "event_type": "Conference",
        },
        {
            "event_id": "2",
            "title": "Hands-On ML Workshop",
            "summary": "Build ML models.",
            "url": "https://example.com/2",
            "display_date": "Fri, Mar 6 at 2:00 PM",
            "display_location": "Google NYC",
            "display_price": "$50 USD",
            "event_type": "Workshop",
        },
        {
            "event_id": "3",
            "title": "AI Networking Mixer",
            "summary": None,
            "url": "https://example.com/3",
            "display_date": "Sat, Mar 7 at 6:00 PM",
            "display_location": "Online",
            "display_price": "Free",
            "event_type": "Meetup",
        },
        {
            "event_id": "4",
            "title": "Deep Learning Talk",
            "summary": "Expert panel.",
            "url": "https://example.com/4",
            "display_date": "Mon, Mar 9 at 7:00 PM",
            "display_location": "Columbia University",
            "display_price": "Free",
            "event_type": "Talk",
        },
    ]


class TestGroupEvents:
    """Tests for _group_events."""

    def test_groups_by_type(self):
        groups = _group_events(_sample_events())
        types = [g["type"] for g in groups]
        assert "Conference" in types
        assert "Workshop" in types
        assert "Meetup" in types
        assert "Talk" in types

    def test_group_order(self):
        """Groups should follow the preferred display order."""
        groups = _group_events(_sample_events())
        types = [g["type"] for g in groups]
        assert types.index("Conference") < types.index("Workshop")
        assert types.index("Workshop") < types.index("Talk")
        assert types.index("Talk") < types.index("Meetup")

    def test_events_in_correct_group(self):
        groups = _group_events(_sample_events())
        conf_group = next(g for g in groups if g["type"] == "Conference")
        assert len(conf_group["events"]) == 1
        assert conf_group["events"][0]["title"] == "AI Summit NYC"

    def test_empty_input(self):
        assert _group_events([]) == []


class TestRenderNewsletter:
    """Tests for render_newsletter."""

    def test_returns_html_string(self):
        html = render_newsletter(_sample_events())
        assert isinstance(html, str)
        assert html.startswith("<!DOCTYPE html>")

    def test_contains_title(self):
        html = render_newsletter(_sample_events(), title="Test Newsletter")
        assert "Test Newsletter" in html

    def test_contains_event_titles(self):
        html = render_newsletter(_sample_events())
        assert "AI Summit NYC" in html
        assert "Hands-On ML Workshop" in html
        assert "AI Networking Mixer" in html
        assert "Deep Learning Talk" in html

    def test_contains_display_fields(self):
        html = render_newsletter(_sample_events())
        assert "Wed, Mar 4 at 10:00 AM" in html
        assert "Javits Center" in html
        assert "$50 USD" in html

    def test_contains_event_urls(self):
        html = render_newsletter(_sample_events())
        assert "https://example.com/1" in html
        assert "https://example.com/2" in html

    def test_contains_group_headers(self):
        html = render_newsletter(_sample_events())
        assert "Conferences" in html or "Conference" in html
        assert "Workshops" in html or "Workshop" in html

    def test_custom_subtitle(self):
        html = render_newsletter(_sample_events(), subtitle="March 2026")
        assert "March 2026" in html

    def test_custom_intro(self):
        html = render_newsletter(
            _sample_events(), intro_text="Welcome to the newsletter!"
        )
        assert "Welcome to the newsletter!" in html

    def test_empty_events(self):
        html = render_newsletter([])
        assert "<!DOCTYPE html>" in html
        assert "0 upcoming AI events" in html


class TestRenderNewsletterToFile:
    """Tests for render_newsletter_to_file."""

    def test_creates_file(self, tmp_path: Path):
        out = tmp_path / "newsletter.html"
        result = render_newsletter_to_file(_sample_events(), out)
        assert result == out
        assert out.exists()

    def test_file_contains_html(self, tmp_path: Path):
        out = tmp_path / "newsletter.html"
        render_newsletter_to_file(_sample_events(), out)
        content = out.read_text(encoding="utf-8")
        assert "<!DOCTYPE html>" in content
        assert "AI Summit NYC" in content

    def test_creates_parent_dirs(self, tmp_path: Path):
        out = tmp_path / "sub" / "dir" / "newsletter.html"
        render_newsletter_to_file(_sample_events(), out)
        assert out.exists()

    def test_passes_kwargs(self, tmp_path: Path):
        out = tmp_path / "newsletter.html"
        render_newsletter_to_file(
            _sample_events(),
            out,
            title="Custom Title",
        )
        content = out.read_text(encoding="utf-8")
        assert "Custom Title" in content
