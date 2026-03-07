---
title: "feat: Logan Square Tonight Event Aggregator"
type: feat
date: 2026-03-07
deepened: 2026-03-07
---

# Logan Square Tonight — Implementation Plan

A nightly event aggregator for a small friend group (~15 people) near the California Blue Line stop in Logan Square, Chicago. Scrapes venue websites daily and serves a mobile-first website with event listings and a curated restaurant directory.

## Enhancement Summary

**Deepened on:** 2026-03-07
**Research agents used:** 10 (Python reviewer, TypeScript reviewer, Architecture strategist, Security sentinel, Performance oracle, Simplicity reviewer, Claude Haiku extraction research, GitHub Actions research, Frontend design, Vercel/React best practices)

### Key Improvements
1. **Preact over React** — 90% less JS, same DX, ~1s faster time-to-interactive on mobile
2. **TypeScript over JSX** — type safety for JSON data shapes, catches bugs at build time
3. **Simplified scraper** — consolidated to 2 files (scrape.py + models.py) instead of 5 modules
4. **"Late-Night Zine Board" design** — warm dark mode, venue color bar glows, Fraunces + DM Sans typography
5. **Standard API over Batch API** — Batch has 24hr turnaround, incompatible with same-day scraping
6. **Prompt caching** — 90% cheaper on cached system prompt across venue calls
7. **Auto-merge with notification** instead of PR-based human-in-the-loop (avoids daily bottleneck)
8. **HTML → Markdown conversion** before sending to Haiku (70-90% token reduction)
9. **Complete GitHub Actions workflow** with DST handling, uv for fast installs, auto-issue on failure
10. **Security hardening** — suppress httpx logging, sanitize LLM output, pin dependencies with hashes

### Conflicts Resolved
- Simplicity reviewer argued for plain HTML + single file. Overruled: 90+ restaurant directory with category filtering, date navigation, and routing warrant a framework — but Preact keeps it lightweight.
- Performance reviewer said use system fonts. Design reviewer specified Fraunces + DM Sans. Resolution: use the custom fonts with `font-display: swap` and preload — the typography is central to the "neighborhood zine" feel.
- Python reviewer said `client.messages.parse()` doesn't exist. Haiku research confirmed it DOES exist with `output_format` param. Using it.
- Architecture reviewer flagged Batch API timing risk. Confirmed: Batch API can take up to 24hrs. Using standard Messages API with prompt caching instead (~$1.70/mo vs ~$0.85/mo — worth the reliability).

---

## Overview

Two core components, built in 3 phases:

1. **Scraper** — Python script on GitHub Actions cron, fetches venue HTML, extracts events via Claude Haiku, writes `events.json`
2. **Frontend** — Preact + TypeScript site on Vercel, reads `events.json`, shows daily/weekly calendar + 90-spot restaurant directory

**Future (deprioritized):** SMS push via Twilio — can layer in later if we want daily texts.

**Budget:** ~$1.70/month (Haiku API with prompt caching, hosting free)

## Design Decisions (from brainstorm + research + deepening)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Scheduling | GitHub Actions (public repo) | Free, secrets management built in, no infra |
| HTTP client | httpx (async) | HTTP/2, connection pooling, concurrent venue fetches |
| HTML pre-processing | markdownify for token reduction, extruct for JSON-LD | Markdown is 70-90% fewer tokens than HTML; extruct catches schema.org/Event without LLM |
| JS-rendered pages | Playwright (surgical, 2-3 venues max) | Only for Do312 and venues that require JS rendering |
| LLM extraction | Claude Haiku 4.5 via standard Messages API | Batch API is 50% cheaper but 24hr turnaround is incompatible; prompt caching saves 90% on system prompt |
| Structured outputs | `client.messages.parse()` with Pydantic `output_format` | Constrained decoding guarantees valid JSON schema |
| Do312 | Algolia search API (exposed key, treat as secret) | More reliable than Playwright scraping; store key in GH Actions secret |
| Frontend | Preact + TypeScript, deployed on Vercel | 90% less JS than React (~4KB vs ~50KB gzipped), same component model |
| Data store | events.json + restaurants.json in repo | No database needed for this scale; Vercel auto-deploys on push |
| "Tonight" rollover | 5am | The Owl is open until 5am Sat; tonight means "until you go to sleep" |
| Design aesthetic | "Late-Night Zine Board" — warm dark mode | Feels like a neighborhood bar bulletin board, not a tech product |
| Model version | Pin to specific snapshot (e.g. `claude-haiku-4-5-20251001`) | Prevents silent behavior changes on model updates |

## Architecture

```
GitHub Actions (public repo)
├── Scrape workflow (3:00pm CT daily, cron: '0 20 * * *')
│   ├── Setup: Python 3.12 + uv (1-3s dep install)
│   ├── Playwright install chromium --with-deps (only if needed)
│   ├── Fetch venue HTML (httpx async, 5-6 concurrent, per-domain limit 1)
│   ├── Convert HTML → Markdown via markdownify (70-90% token reduction)
│   ├── Check extruct for schema.org/Event JSON-LD first (skip LLM if found)
│   ├── Fallback: Claude Haiku structured extraction with prompt caching
│   ├── Validate: Pydantic model, date sanity (yesterday..+30d), sanitize HTML tags
│   ├── Deduplicate: venue_id + date + time_start (not title — too fragile)
│   ├── Purge past events (using 5am rollover)
│   ├── Write events.json → auto-commit via stefanzweifel/git-auto-commit-action
│   ├── Vercel auto-deploys frontend on push
│   └── On failure: auto-create GitHub issue with run link
│
└── (Future: SMS workflow via Twilio — deprioritized)

Vercel (free tier)
├── / → redirect to /{computed-tonight-date}
├── /{date} → daily event view (e.g., /2026-03-07)
├── /week → 7-day compact scan (lazy-loaded)
├── /places → restaurant/bar directory with category filters (lazy-loaded)
└── Footer: "checked today, 3:12pm" (casual voice)

Data files (in repo, served as static assets from frontend/public/data/)
├── events.json → scraped events, auto-updated by scraper
├── restaurants.json → curated directory, manually updated
└── venues.yaml → scraper config (URLs, strategies, colors)
```

### Research Insights: Architecture

- **Git-as-database is correct at this scale.** One write/day, ~50 events, read-only frontend. Eliminates all database infra. Version-controlled history is actually better for debugging extraction issues.
- **Auto-commit with `[skip ci]`** in the commit message prevents recursive workflow triggers.
- **No symlinks for data files.** Copy `data/*.json` to `frontend/public/data/` in a build step. Symlinks break in CI.
- **Add `--dry-run` flag** to the scraper for local development (fetches and extracts but doesn't write or commit).

## Event Schema (refined)

```json
{
  "id": "whistler-2026-03-07-feelgood",
  "venue_id": "whistler",
  "venue_name": "The Whistler",
  "title": "Feelgood Saturday",
  "description": "DJ #Feelgood delivers R&B, Rap, Soul classics",
  "date": "2026-03-07",
  "time_start": "21:00",
  "time_end": "02:00",
  "timezone": "America/Chicago",
  "type": "dj",
  "price": "free",
  "tags": ["rnb", "soul", "dance"],
  "source_url": "https://whistlerchicago.com/events/feelgood-mar-2026",
  "scraped_at": "2026-03-07T20:00:00Z"
}
```

- `type` enum: `music`, `dj`, `comedy`, `karaoke`, `trivia`, `film`, `literary`, `other`
- `timezone` always `America/Chicago`
- `source_url` is required — users tap to verify events are real
- All string fields sanitized (HTML tags stripped) before writing to JSON

### Research Insights: Deduplication

- **Use `venue_id + date + time_start` as the dedup key**, not title. Titles are fragile — Claude may return "Feelgood Saturday" one run and "FEELGOOD SATURDAY" the next. Same venue + same date + same start time = same event.
- For edge cases (two events at same venue, same time), log as potential duplicates for manual review.

## Venue Config Schema (venues.yaml)

```yaml
- id: whistler
  name: The Whistler
  address: 2421 N Milwaukee Ave
  lat: 41.9267
  lng: -87.6979
  url: https://whistlerchicago.com
  events_url: https://whistlerchicago.com/calendar
  scrape_strategy: fetch_html_llm_extract  # or jsonld, do312_algolia
  platform: squarespace
  color: "#E8C547"
  tags: [cocktails, djs, jazz, gallery]
  instagram: "@thewhistlerchicago"
  do312_slug: the-whistler
  last_successful_scrape: null  # updated by scraper
```

### Research Insights: Config Validation

- Validate venues.yaml through a Pydantic model at scraper startup. Fail fast if config is malformed.

```python
class VenueConfig(BaseModel):
    id: str
    name: str
    events_url: HttpUrl
    scrape_strategy: Literal["jsonld", "llm", "jsonld_with_llm_fallback", "do312_algolia"]
    color: str
    last_successful_scrape: datetime | None = None
```

## Restaurant Schema (restaurants.json)

```json
{
  "id": "gretel",
  "name": "Gretel",
  "address": "2833 W Armitage Ave",
  "category": "restaurant",
  "cuisine": "Gastropub",
  "vibe": "Smash burger on everything bun, whiskey, dark & cozy",
  "price_range": "$$",
  "hours": "Tue-Sun 5pm-12am",
  "days_closed": ["Monday"],
  "outdoor_seating": false,
  "reservations": false,
  "status": "want-to-try",
  "google_maps_url": "https://maps.google.com/...",
  "website": "https://gretelchicago.com"
}
```

- `category` enum: `restaurant`, `bar`, `wine-bar`, `brewery`, `coffee`, `dessert`, `venue`, `distillery`
- `status`: `go-to`, `want-to-try`, `open` (no opinion yet), `coming-soon`, `closed`

## LLM Extraction Pipeline (critical for trust)

### Extraction Flow

```python
# 1. Fetch HTML
raw_html = await fetch(venue.events_url)

# 2. Try extruct JSON-LD first (free, deterministic)
jsonld_events = extract_jsonld(raw_html)  # schema.org/Event
if jsonld_events:
    return validate(jsonld_events)

# 3. Convert to Markdown (70-90% token reduction)
markdown = markdownify(raw_html, strip=["img", "video", "svg", "nav", "footer"])

# 4. Claude Haiku structured extraction with prompt caching
response = client.messages.parse(
    model="claude-haiku-4-5-20251001",  # pinned version
    max_tokens=4096,
    system=[{
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"}  # cached across calls
    }],
    messages=[{"role": "user", "content": f"Venue: {venue.name}\n\n{markdown}"}],
    output_format=VenueEvents,
)

# 5. Validate + sanitize
return validate_and_sanitize(response.parsed_output)
```

### Validation Layer

1. **Pydantic model** — constrained decoding guarantees valid schema, but validate field contents
2. **Date sanity** — accept `yesterday` through `+30 days` (1-day grace window for late-night events)
3. **HTML sanitization** — strip all HTML tags from title, description: `re.sub(r'<[^>]+>', '', text)`
4. **Source URL domain check** — must match the venue's configured domain
5. **Diff check** — if >50% of events changed AND venue has 5+ events, log warning (suggests extraction error)
6. **Structured logging** — use `structlog` with JSON output for GitHub Actions logs

```python
import structlog
logger = structlog.get_logger()
logger.info("venue_scraped", venue_id="whistler", events_found=3, strategy="llm", cached=True)
```

### Research Insights: Preventing API Key Leaks

- **Suppress httpx debug logging:** `logging.getLogger("httpx").setLevel(logging.WARNING)` — httpx logs request headers by default, which include the API key
- **Set Anthropic API spending limit** via dashboard (e.g., $5/month hard cap)
- **Catch `anthropic.APIError` specifically**, log only `e.message`, never the full exception (which may contain the key)

### Research Insights: Error Handling

```python
from enum import Enum

class ScrapeResult(Enum):
    SUCCESS = "success"
    FETCH_FAILED = "fetch_failed"
    EXTRACTION_FAILED = "extraction_failed"
    VALIDATION_FAILED = "validation_failed"
    NO_EVENTS = "no_events"
```

- Log result per venue. If a venue fails 3 consecutive runs, flag in the auto-created GitHub issue.
- On fetch failure: carry forward previous events for that venue (don't drop them).
- On `max_tokens` truncation (`stop_reason != "end_turn"`): retry with truncated input.
- Use `Anthropic(max_retries=3, timeout=30.0)` for built-in retry on transient errors.

### Prompt Design

```python
SYSTEM_PROMPT = """You extract structured event data from Chicago venue websites.

RULES:
- Only extract events with clear evidence in the content. Never fabricate.
- If a field is not present, return null.
- Dates: ISO 8601 (YYYY-MM-DD). If only day-of-week given, return null.
- Times: 24-hour HH:MM format.
- If no events found, return an empty list.
- "Events" includes concerts, shows, open mics, trivia, DJ sets, karaoke, film screenings, literary events.
- Ignore navigation, ads, and non-event content."""
```

## File Structure (simplified)

```
logan-sq-tonight/
├── .github/
│   └── workflows/
│       └── scrape.yml              # GitHub Actions workflow
├── scraper/
│   ├── scrape.py                   # Single script: fetch, extract, validate, dedup, write
│   ├── models.py                   # Pydantic models (Event, VenueEvents, VenueConfig)
│   └── requirements.txt            # httpx, anthropic, extruct, markdownify, pydantic, pyyaml, structlog
├── data/
│   ├── venues.yaml                 # Venue scraper config
│   ├── events.json                 # Auto-generated by scraper (committed)
│   └── restaurants.json            # Manually curated directory
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── vercel.json                 # Security headers
│   ├── index.html                  # Preload data JSON, viewport meta
│   └── src/
│       ├── main.tsx                # Entry point
│       ├── types.ts                # Event, Restaurant interfaces
│       ├── lib/
│       │   ├── tonight.ts          # getTonightDate() — 5am rollover logic (pure, testable)
│       │   └── venues.ts           # venue color mapping
│       ├── routes.ts               # Route config with loaders
│       ├── components/
│       │   ├── AppLayout.tsx       # Shared header + footer + <Outlet />
│       │   ├── DateStrip.tsx       # Horizontal scroll, scroll-snap, "Tonight" chip
│       │   ├── EventCard.tsx       # Venue color bar + title + time + source <a> link
│       │   ├── EventList.tsx       # Today's events sorted by time
│       │   ├── VenueDot.tsx        # Shared venue color indicator
│       │   ├── WeekView.tsx        # Lazy-loaded 7-day scan
│       │   ├── PlacesDirectory.tsx # Lazy-loaded restaurant directory
│       │   ├── EmptyState.tsx      # "Quiet night" with inline place suggestions
│       │   └── Footer.tsx          # "checked today, 3:12pm"
│       └── styles/
│           └── global.css          # Dark mode, venue glows, Fraunces + DM Sans
├── docs/
│   ├── brainstorms/
│   └── plans/
├── milwaukee-ave-tonight-research.md
└── README.md
```

### Research Insights: Simplification

- **2 scraper files instead of 5.** `scrape.py` (~200 lines) handles fetch, extract, validate, dedup, and write. `models.py` holds Pydantic models. At 3-15 venues, separate fetcher/extractor/validator modules are premature abstraction.
- **Keep venues.yaml** (not a Python dict) — YAML is human-readable and editable by non-programmers. Worth the PyYAML dependency.

## Frontend Design: "Late-Night Zine Board"

### Color Palette

```css
:root {
  --bg-primary: #1a1714;        /* dark walnut, like a bar counter */
  --bg-surface: #242019;        /* slightly lifted surface */
  --bg-card: #2c2720;           /* card backgrounds */
  --text-primary: #e8e0d4;      /* cream, not white */
  --text-secondary: #9b9183;    /* muted warm gray */
  --text-tertiary: #6b6358;     /* de-emphasized */
  --accent: #d4845a;            /* warm terracotta — Logan Square brick */
  --accent-muted: #d4845a33;
  --free: #7ab87a;              /* sage green for "free" badges */
  --venue-glow: 0 0 8px var(--venue-color);  /* neon sign on wet pavement */
}
```

### Typography

```css
--font-display: 'Fraunces', serif;    /* quirky editorial serif — headers, empty states */
--font-body: 'DM Sans', sans-serif;   /* clean utilitarian — body text, times */
```

Load with `font-display: swap` and `<link rel="preload">` to avoid render blocking.

### Key Design Patterns

- **Venue color bars (not dots)** — 4px vertical bar running full card height, with soft glow. More scannable than circles.
- **No borders on cards** — subtle background color shifts and spacing. Borders feel corporate.
- **Casual voice everywhere** — "8pm" not "8:00 PM", "checked today, 3:12pm" not "Last Updated: March 7, 2026 3:12 PM"
- **Full card is the tap target** — `<a href={source_url}>` wrapping the whole card. No tiny buttons.
- **"Tonight" chip** in the date strip instead of day name for today's date.
- **Status badges** — go-to (terracotta fill), want-to-try (dashed border), coming-soon (ochre)
- **Vibe one-liner in italic** — "cash-only Polish diner" reads like a friend's whisper
- **Staggered card entrance animation** — subtle 40ms delay per card, caps at 6 cards
- **"Live now" glow pulse** on venue bar for events currently happening

### Mobile-First Constraints

- 44px minimum touch targets on all interactive elements
- `scroll-snap-type: x mandatory` on DateStrip — no JS scroll management
- `content-visibility: auto` on event/place cards for faster paint on long lists
- Max-width: 430px centered — single column always
- Sticky category tabs on /places with horizontal scroll

### Research Insights: Performance

- **Preact + Vite:** ~4KB gzipped JS vs ~50KB for React. Use `@preact/preset-vite`.
- **Lazy-load** WeekView and PlacesDirectory — only the tonight/date view loads on first visit.
- **Preload data JSON** in HTML head: `<link rel="preload" href="/data/events.json" as="fetch" crossorigin>`
- **React Router loaders** for data — data is ready before component renders, no flash of empty content.
- **`/` redirects to `/{computed-date}`** (e.g., `/2026-03-07`), not `/tonight` — every URL is a real date and shareable by default.
- **Date param validation** — invalid dates redirect to tonight.

### Security Headers (vercel.json)

```json
{
  "headers": [{
    "source": "/(.*)",
    "headers": [
      { "key": "X-Content-Type-Options", "value": "nosniff" },
      { "key": "X-Frame-Options", "value": "DENY" },
      { "key": "Referrer-Policy", "value": "strict-origin-when-cross-origin" }
    ]
  }]
}
```

## GitHub Actions Workflow

```yaml
name: Daily Event Scraper

on:
  schedule:
    - cron: '0 20 * * *'    # 3pm CDT / 2pm CST (accept 1hr DST drift)
  workflow_dispatch:          # manual trigger for testing

permissions:
  contents: write
  issues: write

jobs:
  scrape:
    runs-on: ubuntu-latest
    timeout-minutes: 10

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
          cache: 'pip'
          cache-dependency-path: 'scraper/requirements.txt'

      - name: Install dependencies
        run: |
          pip install uv
          uv pip install --system -r scraper/requirements.txt

      - name: Install Playwright Chromium (if needed)
        run: playwright install chromium --with-deps

      - name: Run scraper
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: python scraper/scrape.py

      - name: Copy data to frontend
        run: cp data/events.json frontend/public/data/events.json

      - name: Commit updated data
        uses: stefanzweifel/git-auto-commit-action@v5
        with:
          commit_message: "data: update events [skip ci]"
          file_pattern: 'data/events.json frontend/public/data/events.json'
          commit_user_name: 'github-actions[bot]'
          commit_user_email: 'github-actions[bot]@users.noreply.github.com'

      - name: Create issue on failure
        if: failure()
        uses: dacbd/create-issue-action@main
        with:
          token: ${{ github.token }}
          title: "Scraper failed on ${{ github.event.schedule || 'manual' }}"
          body: |
            The daily event scraper workflow failed.
            **Run:** ${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}
          labels: bug,automated
          assignees: topher416
```

### Research Insights: GitHub Actions

- **uv** (Rust pip replacement) installs deps in 1-3s vs 15-30s for pip.
- **`[skip ci]`** in commit message prevents recursive workflow triggers.
- **Only `git add` specific files** — never `git add .` (security hardening).
- **`workflow_dispatch`** enables manual triggering for debugging.
- **Auto-issue on failure** with link to the run — you'll get an email notification from GitHub too.
- **Total runtime: ~1-3 minutes.** Well within free tier limits (unlimited for public repos).

## Implementation Phases (consolidated)

### Phase 1: Scraper + Data (start here)

Build the scraper for 3 venues, populate restaurants.json, output all data.

**Venues:** The Whistler (Squarespace), Cafe Mustache (Webflow), Coles (Do312)

**Tasks:**

- [ ] `scraper/models.py` — Pydantic models: `Event`, `VenueEvents`, `VenueConfig`, `ScrapeResult` enum
- [ ] `data/venues.yaml` — config for 3 venues, validated through VenueConfig at startup
- [ ] `scraper/scrape.py`:
  - Load and validate venues.yaml
  - Async httpx fetch with User-Agent `LoganSqTonight/1.0 (your@email.com)`, 5-6 concurrent, per-domain limit 1
  - Try extruct JSON-LD first (check microdata and RDFa too, not just JSON-LD)
  - Fallback: markdownify HTML → Claude Haiku `client.messages.parse()` with prompt caching
  - Validate: Pydantic + date sanity (yesterday..+30d) + HTML sanitization
  - Dedup by venue_id + date + time_start
  - Purge events with date before today (5am rollover)
  - Carry forward previous events for failed venues (don't drop)
  - Write events.json
  - `--dry-run` flag for local dev
  - structlog JSON logging, suppress httpx debug level
- [ ] `scraper/requirements.txt` — pin exact versions, generate hashes with `pip-compile --generate-hashes`
- [ ] `data/restaurants.json` — convert brainstorm tables to JSON (all 90+ spots, all categories)
- [ ] `data/events.json` — initial empty `[]`
- [ ] Test locally against live venue pages, compare output to research doc's manually collected data

**Acceptance criteria:**
- [ ] `python scraper/scrape.py` produces valid events.json with real events from 3 venues
- [ ] Every event has a working source_url matching the venue domain
- [ ] No hallucinated events (verify manually against venue websites)
- [ ] Past events purged, duplicates removed
- [ ] restaurants.json has all 90+ spots with name, address, category, status at minimum
- [ ] `--dry-run` mode works without writing files

### Phase 2: Frontend + Deployment

Mobile-first Preact site + GitHub Actions automation.

**Tasks:**

- [ ] `frontend/` — scaffold with Vite + Preact + TypeScript (`@preact/preset-vite`)
- [ ] `src/types.ts` — Event, Restaurant, VenueConfig interfaces
- [ ] `src/lib/tonight.ts` — `getTonightDate()` pure function with 5am rollover, unit tested
- [ ] `src/lib/venues.ts` — venue color mapping from venues.yaml data
- [ ] `src/routes.ts` — React Router config:
  - `/` → loader redirects to `/{getTonightDate()}`
  - `/:date` → EventList with loader (validates date param, redirects invalid)
  - `/week` → lazy-loaded WeekView
  - `/places` → lazy-loaded PlacesDirectory
- [ ] `src/components/AppLayout.tsx` — shared header ("Logan Square Tonight" in Fraunces) + nav toggle + Footer + `<Outlet />`
- [ ] `src/components/DateStrip.tsx` — horizontal scroll with `scroll-snap-type: x mandatory`, "Tonight" chip for today, 7 days forward
- [ ] `src/components/EventCard.tsx` — full-card `<a href={source_url}>`, venue color bar with glow, time ("8pm"), price badge, "free" in sage green
- [ ] `src/components/EventList.tsx` — sorted by time_start, staggered entrance animation
- [ ] `src/components/PlacesDirectory.tsx` — category filter tabs (horizontal scroll, sticky), place cards with vibe italic one-liner, status badges, price dots
- [ ] `src/components/EmptyState.tsx` — "Quiet night in the neighborhood" (Fraunces italic) with inline top restaurant picks
- [ ] `src/components/Footer.tsx` — "checked today, 3:12pm", sticky with gradient fade
- [ ] `src/styles/global.css` — dark walnut palette, venue glow animations, Fraunces + DM Sans
- [ ] `frontend/vercel.json` — security headers
- [ ] `frontend/index.html` — viewport meta, font preloads, data JSON preloads
- [ ] Deploy frontend to Vercel, confirm auto-deploy on push
- [ ] `.github/workflows/scrape.yml` — full workflow (see above)
- [ ] Add `ANTHROPIC_API_KEY` to GitHub repo secrets
- [ ] Set Anthropic API spending limit ($5/month cap)

**Acceptance criteria:**
- [ ] Site loads on phone in <2s on LTE, shows tonight's events
- [ ] Tapping an event card opens the venue's source page
- [ ] Date picker navigates between days, URL updates to shareable date
- [ ] Restaurant directory shows all spots with category filtering
- [ ] "checked today" timestamp visible in footer
- [ ] Scraper runs daily via GitHub Actions and auto-deploys new data
- [ ] Scraper failures auto-create a GitHub issue
- [ ] Dark mode looks good — warm, not cold

### Phase 3: Expand Venues

Add remaining venues once the pipeline is proven reliable.

**Tasks:**

- [ ] Add Do312 venues via Algolia API: Slippery Slope, Emporium (+ Coles backup)
- [ ] Add direct-scrape venues: The Native, The Owl, Harding Tavern
- [ ] Add ticketing platform venues: Concord Music Hall, Logan Square Auditorium
- [ ] Add Logan Theatre (investigate showtime API/platform)
- [ ] Add Lincoln Lodge (check Eventbrite integration)
- [ ] Test each new venue's extraction quality before adding to venues.yaml
- [ ] Add scraper health status to frontend (which venues are healthy/failing)

**Acceptance criteria:**
- [ ] 10+ venues producing reliable event data
- [ ] Each venue's events verified against their actual website
- [ ] No increase in hallucinated/phantom events
- [ ] Scraper health visible on the site

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Haiku hallucinating events | Medium | High (trust killer) | Constrained decoding + date sanity + source_url domain check + manual verification for v1 |
| Venue changes site layout | Medium | Low (LLM handles it) | LLM extraction is layout-agnostic; extruct JSON-LD is structure-agnostic. Monitor via structlog. |
| GitHub Actions delay (>30 min) | Medium | Low | Accept it — data is still same-day fresh. Footer shows actual check time. |
| Venue blocks scraper | Low | Medium | Polite scraping (5-6 concurrent, per-domain 1, User-Agent with contact email), 1x daily |
| API key leaked in Actions logs | Low | Medium | Suppress httpx logging, catch APIError specifically, set spending limit |
| Cost overrun | Low | Low | Prompt caching (90% savings), spending limit, ~15 venues = ~$1.70/mo |

## Not Building (YAGNI)

- Map view (everyone knows where Milwaukee Ave is)
- User accounts or login
- Service worker / offline mode (consider for v2)
- SMS push via Twilio (deprioritized — can layer in later)
- Email digest
- Analytics beyond Vercel's free built-in
- Native app
- Public-facing product features (SEO, onboarding, etc.)
- Instagram scraping (too complex for v1; manual curation for Instagram-only venues)
- Batch API (24hr turnaround incompatible with same-day scraping)

## References

- Brainstorm doc: `docs/brainstorms/2026-03-07-logan-sq-tonight-brainstorm.md`
- Research doc: `milwaukee-ave-tonight-research.md`
- Claude structured outputs: https://docs.anthropic.com/en/docs/build-with-claude/structured-outputs
- Claude prompt caching: https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching
- Anthropic Python SDK: https://github.com/anthropics/anthropic-sdk-python
- extruct library: https://github.com/scrapinghub/extruct
- markdownify: https://github.com/matthewwithanm/python-markdownify
- GitHub Actions cron: https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions
- stefanzweifel/git-auto-commit-action: https://github.com/stefanzweifel/git-auto-commit-action
- Preact: https://preactjs.com/
- Fraunces font: https://fonts.google.com/specimen/Fraunces
- DM Sans font: https://fonts.google.com/specimen/DM+Sans
