#!/usr/bin/env python3
"""Logan Square Tonight — event scraper.

Fetches venue websites, extracts events via Claude Haiku, writes events.json.
Usage:
    python scraper/scrape.py              # normal run
    python scraper/scrape.py --dry-run    # fetch + extract, don't write files
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import httpx
import structlog
import yaml

from models import Event, EventType, ScrapeResult, VenueConfig, VenueEvents

# Suppress httpx debug logging (leaks API key in headers)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
)
log = structlog.get_logger()

CHICAGO = ZoneInfo("America/Chicago")
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
VENUES_FILE = DATA_DIR / "venues.yaml"
EVENTS_FILE = DATA_DIR / "events.json"

USER_AGENT = "LoganSqTonight/1.0 (https://github.com/topher416/logan-sq-tonight)"

SYSTEM_PROMPT = f"""You extract structured event data from Chicago venue websites.
The current year is {date.today().year}.

RULES:
- Only extract events with clear evidence in the content. Never fabricate.
- If a field is not present, return null.
- Dates: ISO 8601 (YYYY-MM-DD). The current year is {date.today().year}. If dates lack a year, assume {date.today().year}.
- Times: 24-hour HH:MM format (e.g. 21:00 not 9pm).
- If no events found, return an empty events list.
- "Events" includes concerts, shows, open mics, trivia, DJ sets, karaoke, film screenings, movie showtimes, literary events, comedy shows.
- Ignore navigation, ads, footers, and non-event content.
- For the source_url field, return the URL of the specific event page if available, otherwise return null."""

# How many days back to keep (grace window for late-night events)
GRACE_DAYS = 1
# How far forward to accept events
MAX_FUTURE_DAYS = 60


def get_tonight_date() -> date:
    """Get tonight's date using 5am rollover."""
    now = datetime.now(CHICAGO)
    if now.hour < 5:
        return (now - timedelta(days=1)).date()
    return now.date()


def load_venues() -> list[VenueConfig]:
    """Load and validate venue configs from YAML."""
    raw = yaml.safe_load(VENUES_FILE.read_text())
    venues = [VenueConfig.model_validate(v) for v in raw]
    log.info("venues_loaded", count=len(venues))
    return venues


def sanitize_text(text: str | None) -> str | None:
    """Strip HTML tags from text fields."""
    if text is None:
        return None
    cleaned = re.sub(r"<[^>]+>", "", text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned if cleaned else None


def is_valid_date(event_date_str: str) -> bool:
    """Check if an event date is within our acceptable range."""
    try:
        event_date = date.fromisoformat(event_date_str)
    except (ValueError, TypeError):
        return False
    today = get_tonight_date()
    earliest = today - timedelta(days=GRACE_DAYS)
    latest = today + timedelta(days=MAX_FUTURE_DAYS)
    return earliest <= event_date <= latest


def make_event_id(venue_id: str, event: dict) -> str:
    """Generate a deterministic event ID."""
    title_slug = re.sub(r"[^a-z0-9]+", "-", (event.get("title") or "unknown").lower()).strip("-")
    return f"{venue_id}-{event['date']}-{title_slug}"


def dedup_key(venue_id: str, event: dict) -> str:
    """Dedup key: venue_id + date + time_start."""
    return f"{venue_id}|{event.get('date')}|{event.get('time_start', 'none')}"


def convert_html_to_markdown(html: str) -> str:
    """Convert HTML to markdown for token reduction."""
    try:
        from markdownify import markdownify as md
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")
        # Remove non-content elements
        for tag in soup.find_all(
            ["script", "style", "link", "meta", "noscript", "iframe", "svg", "nav", "footer", "header"]
        ):
            tag.decompose()
        # Find main content area if possible
        main = soup.find("main") or soup.find(id="content") or soup.find(class_="events") or soup
        return md(str(main), strip=["video", "audio"])
    except ImportError:
        # Fallback: basic HTML stripping
        text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text


def try_extract_jsonld(html: str) -> list[dict] | None:
    """Try to extract events from schema.org/Event JSON-LD."""
    try:
        import extruct

        data = extruct.extract(html, syntaxes=["json-ld", "microdata"])
        events = []

        # Check JSON-LD
        for item in data.get("json-ld", []):
            if isinstance(item, dict) and item.get("@type") == "Event":
                events.append(item)
            elif isinstance(item, dict) and isinstance(item.get("@graph"), list):
                for node in item["@graph"]:
                    if isinstance(node, dict) and node.get("@type") == "Event":
                        events.append(node)
            elif isinstance(item, dict) and item.get("@type") == "ItemList":
                for el in item.get("itemListElement", []):
                    if isinstance(el, dict) and el.get("@type") == "Event":
                        events.append(el)

        # Check microdata
        for item in data.get("microdata", []):
            if isinstance(item, dict) and "Event" in str(item.get("type", "")):
                events.append(item.get("properties", {}))

        if not events:
            return None

        # Convert to our format
        result = []
        for e in events:
            start = e.get("startDate", "")
            event_date = start[:10] if len(start) >= 10 else None
            time_start = None
            if "T" in start and len(start) >= 16:
                time_start = start[11:16]

            # Extract price from offers
            price = None
            offers = e.get("offers", {})
            if isinstance(offers, dict) and offers.get("price"):
                p = str(offers["price"])
                price = "free" if p == "0" else f"${p}"
            source = e.get("url") or (offers.get("url") if isinstance(offers, dict) else None)

            result.append(
                {
                    "title": e.get("name", "Unknown Event"),
                    "description": sanitize_text(e.get("description")),
                    "date": event_date,
                    "time_start": time_start,
                    "time_end": None,
                    "type": "other",
                    "price": price,
                    "tags": [],
                    "source_url": source,
                }
            )

        return result if result else None

    except ImportError:
        log.warning("extruct_not_installed")
        return None
    except Exception as exc:
        log.warning("jsonld_extraction_failed", error=str(exc))
        return None


async def fetch_html(client: httpx.AsyncClient, url: str, venue_id: str) -> str | None:
    """Fetch a venue page's HTML."""
    try:
        resp = await client.get(url, follow_redirects=True)
        resp.raise_for_status()
        log.info("fetched", venue_id=venue_id, status=resp.status_code, size=len(resp.text))
        return resp.text
    except httpx.HTTPError as exc:
        log.error("fetch_failed", venue_id=venue_id, error=str(exc))
        return None


async def extract_with_llm(markdown: str, venue_name: str) -> list[dict] | None:
    """Extract events using Claude Haiku via tool use for structured output."""
    try:
        import anthropic

        event_schema = {
            "type": "object",
            "properties": {
                "events": {
                    "type": "array",
                    "description": "List of events found on the venue page",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Event title"},
                            "description": {"type": ["string", "null"], "description": "Brief description"},
                            "date": {"type": ["string", "null"], "description": "ISO date YYYY-MM-DD"},
                            "time_start": {"type": ["string", "null"], "description": "Start time HH:MM 24hr"},
                            "time_end": {"type": ["string", "null"], "description": "End time HH:MM 24hr"},
                            "type": {
                                "type": "string",
                                "enum": ["music", "dj", "comedy", "karaoke", "trivia", "film", "literary", "other"],
                            },
                            "price": {"type": ["string", "null"], "description": "Price or 'free'"},
                            "tags": {"type": "array", "items": {"type": "string"}},
                            "source_url": {"type": ["string", "null"], "description": "URL to event details"},
                        },
                        "required": ["title", "date", "type"],
                    },
                }
            },
            "required": ["events"],
        }

        client = anthropic.Anthropic()
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=8192,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            tools=[
                {
                    "name": "extract_events",
                    "description": "Extract structured event data from venue page content",
                    "input_schema": event_schema,
                }
            ],
            tool_choice={"type": "tool", "name": "extract_events"},
            messages=[
                {
                    "role": "user",
                    "content": f"Venue: {venue_name}\n\n{markdown[:50000]}",
                }
            ],
        )

        if response.stop_reason == "max_tokens":
            log.warning("llm_truncated", venue=venue_name)
            return None

        # Extract the tool use result
        for block in response.content:
            if block.type == "tool_use" and block.name == "extract_events":
                return block.input.get("events", [])

        log.warning("no_tool_use_in_response", venue=venue_name)
        return None

    except ImportError:
        log.error("anthropic_not_installed")
        return None
    except Exception as exc:
        log.error("llm_extraction_failed", venue=venue_name, error=str(exc))
        return None


async def scrape_venue(
    client: httpx.AsyncClient,
    venue: VenueConfig,
    semaphore: asyncio.Semaphore,
) -> tuple[VenueConfig, ScrapeResult, list[dict]]:
    """Scrape a single venue and return validated events."""
    async with semaphore:
        log.info("scraping", venue_id=venue.id, strategy=venue.scrape_strategy)

        # Fetch HTML
        html = await fetch_html(client, venue.events_url, venue.id)
        if html is None:
            return venue, ScrapeResult.FETCH_FAILED, []

        # Try JSON-LD first
        jsonld_events = try_extract_jsonld(html)
        if jsonld_events:
            log.info("jsonld_found", venue_id=venue.id, count=len(jsonld_events))
            raw_events = jsonld_events
        elif venue.scrape_strategy in ("llm", "jsonld_with_llm_fallback"):
            # Convert to markdown and use LLM
            markdown = convert_html_to_markdown(html)
            log.info("llm_extracting", venue_id=venue.id, markdown_len=len(markdown))

            result = await extract_with_llm(markdown, venue.name)
            if result is None:
                return venue, ScrapeResult.EXTRACTION_FAILED, []

            raw_events = result
            log.info("llm_extracted", venue_id=venue.id, count=len(raw_events))
        else:
            log.warning("no_extraction_strategy", venue_id=venue.id)
            return venue, ScrapeResult.EXTRACTION_FAILED, []

        if not raw_events:
            return venue, ScrapeResult.NO_EVENTS, []

        # Validate and build final events
        now_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        valid_events = []
        for raw in raw_events:
            # Date validation
            if not raw.get("date") or not is_valid_date(raw["date"]):
                log.debug("invalid_date", venue_id=venue.id, date=raw.get("date"), title=raw.get("title"))
                continue

            # Sanitize text fields
            raw["title"] = sanitize_text(raw.get("title")) or "Unknown Event"
            raw["description"] = sanitize_text(raw.get("description"))

            # Source URL: default to venue events page if not provided
            source_url = raw.get("source_url") or venue.events_url
            # Make relative URLs absolute
            if source_url and source_url.startswith("/"):
                source_url = venue.url.rstrip("/") + source_url

            event = {
                "id": make_event_id(venue.id, raw),
                "venue_id": venue.id,
                "venue_name": venue.name,
                "title": raw["title"],
                "description": raw.get("description"),
                "date": raw["date"],
                "time_start": raw.get("time_start"),
                "time_end": raw.get("time_end"),
                "timezone": "America/Chicago",
                "type": raw.get("type", "other"),
                "price": raw.get("price"),
                "tags": raw.get("tags", []),
                "source_url": source_url,
                "scraped_at": now_utc,
            }
            valid_events.append(event)

        if valid_events:
            return venue, ScrapeResult.SUCCESS, valid_events
        else:
            return venue, ScrapeResult.NO_EVENTS, []


def load_previous_events() -> list[dict]:
    """Load previously scraped events for carry-forward on failure."""
    if EVENTS_FILE.exists():
        try:
            return json.loads(EVENTS_FILE.read_text())
        except (json.JSONDecodeError, Exception):
            return []
    return []


def purge_past_events(events: list[dict]) -> list[dict]:
    """Remove events with dates before yesterday (using 5am rollover)."""
    tonight = get_tonight_date()
    cutoff = tonight - timedelta(days=GRACE_DAYS)
    cutoff_str = cutoff.isoformat()
    return [e for e in events if e.get("date", "") >= cutoff_str]


def deduplicate(events: list[dict]) -> list[dict]:
    """Deduplicate by venue_id + date + time_start."""
    seen: set[str] = set()
    unique: list[dict] = []
    for event in events:
        key = dedup_key(event.get("venue_id", ""), event)
        if key not in seen:
            seen.add(key)
            unique.append(event)
    return unique


async def run(dry_run: bool = False) -> None:
    """Main scraper entrypoint."""
    venues = load_venues()
    previous_events = load_previous_events()
    semaphore = asyncio.Semaphore(5)

    async with httpx.AsyncClient(
        headers={"User-Agent": USER_AGENT},
        timeout=30.0,
        limits=httpx.Limits(max_connections=6, max_keepalive_connections=3),
    ) as client:
        tasks = [scrape_venue(client, v, semaphore) for v in venues]
        results = await asyncio.gather(*tasks)

    # Collect all new events
    all_events: list[dict] = []
    successful_venue_ids: set[str] = set()
    failed_venue_ids: set[str] = set()

    for venue, result, events in results:
        log.info(
            "venue_result",
            venue_id=venue.id,
            result=result.value,
            events_found=len(events),
        )
        if result == ScrapeResult.SUCCESS:
            all_events.extend(events)
            successful_venue_ids.add(venue.id)
        elif result in (ScrapeResult.NO_EVENTS,):
            successful_venue_ids.add(venue.id)
        else:
            failed_venue_ids.add(venue.id)

    # Carry forward events from failed venues (don't drop them)
    if failed_venue_ids and previous_events:
        carried = [e for e in previous_events if e.get("venue_id") in failed_venue_ids]
        if carried:
            log.info("carrying_forward", count=len(carried), venues=list(failed_venue_ids))
            all_events.extend(carried)

    # Purge past events and deduplicate
    all_events = purge_past_events(all_events)
    all_events = deduplicate(all_events)

    # Sort by date, then time_start
    all_events.sort(key=lambda e: (e.get("date", ""), e.get("time_start") or "99:99"))

    log.info(
        "scrape_complete",
        total_events=len(all_events),
        venues_succeeded=len(successful_venue_ids),
        venues_failed=len(failed_venue_ids),
    )

    if dry_run:
        log.info("dry_run", message="Not writing files")
        print(json.dumps(all_events, indent=2))
        return

    # Write events.json
    EVENTS_FILE.write_text(json.dumps(all_events, indent=2) + "\n")
    log.info("events_written", path=str(EVENTS_FILE), count=len(all_events))

    # Also copy to frontend public dir
    frontend_data = Path(__file__).resolve().parent.parent / "frontend" / "public" / "data"
    if frontend_data.exists():
        (frontend_data / "events.json").write_text(json.dumps(all_events, indent=2) + "\n")
        log.info("frontend_data_copied")


def main():
    parser = argparse.ArgumentParser(description="Logan Square Tonight scraper")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and extract but don't write files")
    args = parser.parse_args()
    asyncio.run(run(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
