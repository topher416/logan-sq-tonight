"""Pydantic models for Logan Square Tonight scraper."""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class EventType(str, Enum):
    MUSIC = "music"
    DJ = "dj"
    COMEDY = "comedy"
    KARAOKE = "karaoke"
    TRIVIA = "trivia"
    FILM = "film"
    LITERARY = "literary"
    OTHER = "other"


class ScrapeResult(str, Enum):
    SUCCESS = "success"
    FETCH_FAILED = "fetch_failed"
    EXTRACTION_FAILED = "extraction_failed"
    VALIDATION_FAILED = "validation_failed"
    NO_EVENTS = "no_events"


class Event(BaseModel):
    """A single event at a venue."""

    title: str = Field(description="Event title")
    description: str | None = Field(default=None, description="Brief event description")
    date: str = Field(description="ISO 8601 date, e.g. 2026-03-07")
    time_start: str | None = Field(default=None, description="Start time in HH:MM 24hr format")
    time_end: str | None = Field(default=None, description="End time in HH:MM 24hr format")
    type: EventType = Field(default=EventType.OTHER, description="Event category")
    price: str | None = Field(default=None, description="Ticket price or 'free'")
    tags: list[str] = Field(default_factory=list, description="Freeform tags")
    source_url: str | None = Field(default=None, description="Link to event details page")


class VenueEvents(BaseModel):
    """Events extracted from a single venue page."""

    venue_name: str
    events: list[Event]


class VenueConfig(BaseModel):
    """Configuration for a single venue to scrape."""

    id: str
    name: str
    address: str
    url: str
    events_url: str
    scrape_strategy: Literal["jsonld", "llm", "jsonld_with_llm_fallback", "do312_algolia"]
    platform: str | None = None
    color: str = "#888888"
    tags: list[str] = Field(default_factory=list)
    instagram: str | None = None
    do312_slug: str | None = None
    last_successful_scrape: str | None = None
