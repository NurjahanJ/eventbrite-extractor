"""Eventbrite Data Extraction Package for Newsletter ETL Pipeline."""

__version__ = "0.1.0"

from eventbrite_extractor.client import EventbriteClient
from eventbrite_extractor.export import export_to_csv, export_to_json
from eventbrite_extractor.models import Event
from eventbrite_extractor.render import render_newsletter, render_newsletter_to_file
from eventbrite_extractor.transform import transform_events

__all__ = [
    "EventbriteClient",
    "Event",
    "export_to_json",
    "export_to_csv",
    "transform_events",
    "render_newsletter",
    "render_newsletter_to_file",
]
