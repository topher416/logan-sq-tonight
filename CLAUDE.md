# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Logan Square Tonight is a neighborhood event aggregator for Logan Square, Chicago. It scrapes venue websites daily, extracts events using Claude Haiku, and serves a mobile-first website showing what's happening tonight.

**GitHub:** topher416/logan-sq-tonight (personal account — use `Topher Rasmussen <topher416@gmail.com>` for git)
**Live site:** https://frontend-kohl-tau-44.vercel.app

## Commands

### Scraper (Python)
```bash
# From project root — scraper imports assume cwd is project root
ANTHROPIC_API_KEY="..." python3 scraper/scrape.py           # run scraper, write events.json
ANTHROPIC_API_KEY="..." python3 scraper/scrape.py --dry-run  # fetch + extract, print JSON, don't write

# Install deps (use venv)
pip install -r scraper/requirements.txt
```

### Frontend (Preact + Vite)
```bash
cd frontend
npm install
npm run dev      # dev server at localhost:5173
npm run build    # tsc + vite build → frontend/dist/
npm run preview  # preview production build
```

### Deploy
```bash
cd frontend && vercel --yes --prod   # deploy to Vercel
```

## Architecture

Two independent systems connected by `data/events.json`:

### Scraper (`scraper/`)
Python async script that runs daily via GitHub Actions (3pm CDT). Extraction pipeline per venue:

1. **Wix extractor** — for `platform: wix` venues, parses structured event JSON embedded in page source (UTC→Chicago time conversion). Accurate dates/times without LLM.
2. **JSON-LD / extruct** — checks for schema.org/Event data, including `ItemList.itemListElement` nesting.
3. **LLM fallback** — converts HTML→markdown via markdownify (strips nav/footer/header but keeps img for alt text), sends to Claude Haiku via tool-use pattern (`tools` + `tool_choice`, NOT `client.messages.parse()` which doesn't exist).

Key behaviors:
- **5am rollover**: `get_tonight_date()` treats hours before 5am as the previous day (late-night bars)
- **Carry-forward**: if a venue fetch fails, previous events for that venue are preserved
- **Dedup**: by `venue_id + date + time_start` (not title — too fragile)
- **Date validation**: accepts yesterday through +60 days, filters the rest
- **Relative URL fix**: source_url starting with `/` gets venue base URL prepended
- System prompt includes current year (Haiku was defaulting to 2024 without it)

`models.py` has Pydantic models. `data/venues.yaml` configures venues with id, URLs, scrape_strategy, platform, and color.

### Frontend (`frontend/`)
Preact + TypeScript + Vite. No router library — uses hash-based date navigation and view state.

- `App.tsx` fetches `/data/events.json` and `/data/restaurants.json` on mount
- `EventList.tsx` filters events by selected date, groups Logan Theatre showtimes into a collapsible section
- `PlacesDirectory.tsx` shows 100+ restaurants with category filter tabs
- `lib/tonight.ts` has the same 5am rollover logic as the scraper
- `lib/venues.ts` hardcodes venue colors (must be updated when adding venues to `venues.yaml`)
- Design: "Late-Night Zine Board" — dark walnut palette (#1a1714), venue color bar glows, Fraunces + DM Sans

### Data Flow
```
venues.yaml → scraper → data/events.json → frontend/public/data/events.json → site
                                         ↑ (also copied by scraper automatically)
GitHub Actions daily cron → auto-commit → Vercel auto-deploy
```

## Adding a New Venue

1. Add entry to `data/venues.yaml` (id, name, address, url, events_url, scrape_strategy, platform, color)
2. Add venue to `frontend/src/lib/venues.ts` VENUES array (id, name, color must match)
3. Copy updated venues.yaml to `frontend/public/data/venues.yaml`
4. Test: `python3 scraper/scrape.py --dry-run` and verify events extract correctly
5. Set `platform: wix` for Wix sites to use the structured extractor instead of LLM

## Known Limitations

- **Lincoln Lodge**: Wix site where events load via client-side JS — needs Playwright/headless browser
- **The Native, Harding Tavern**: Bar pages without structured event listings — produce 0 events
- **Cafe Mustache**: Site shows old events; only current-week events pass date validation
- **Coles Bar**: Large page (645KB HTML, 54KB markdown) — intermittent fetch timeouts
- **Do312**: Blocks scraping with 403 (Slippery Slope removed for this reason)
- Anthropic SDK: `client.messages.parse()` does NOT exist — use tool-use pattern with `tools` + `tool_choice`
