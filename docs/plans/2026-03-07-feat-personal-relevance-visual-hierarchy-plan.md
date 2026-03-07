---
title: "feat: Personal relevance visual hierarchy"
type: feat
date: 2026-03-07
---

# Personal Relevance Visual Hierarchy

## Overview

Make Logan Square Tonight actually useful as a personal discovery tool by visually boosting events Topher and Cassie care about (comedy, trivia, live music, theater) and muting DJ sets. Expand the event type system, add recurring event detection, and prepare for venue expansion.

## Problem Statement

The event feed is dominated by DJ sets that will never be attended. Scanning the list feels like noise. The site needs a visual hierarchy that makes "your kind of thing" pop at a glance, without hiding anything.

## Proposed Solution

Three phased changes, each independently shippable:

### Phase 1: Visual Hierarchy (Quick Win)

**Hardcode preferences in the frontend. No settings UI needed — this is a site for two people.**

1. **Add preference constants** — new file `frontend/src/lib/preferences.ts`:
   ```ts
   export const BOOSTED_TYPES = ['comedy', 'trivia', 'music', 'theater', 'film', 'food-event', 'literary']
   export const MUTED_TYPES = ['dj']
   // Everything else (including 'other', 'karaoke') renders with default styling
   ```

2. **Add CSS classes** in `frontend/src/styles/global.css`:
   - `.event-card.boosted` — subtle accent left-border or enhanced venue-bar glow, full opacity
   - `.event-card.muted` — `opacity: 0.55`, remove `box-shadow` glow from venue bar
   - Default cards (type `other`, `karaoke`, etc.) keep current styling — no boost, no mute

3. **Apply classes** in `frontend/src/components/EventCard.tsx`:
   - Import `BOOSTED_TYPES` and `MUTED_TYPES`
   - Add conditional class to the `.event-card` element based on `event.type`

4. **Sort boosted events first within same time slot** in `frontend/src/components/EventList.tsx`:
   - Primary sort: `time_start` ascending (unchanged)
   - Secondary sort: boosted > default > muted

**Files changed:**
- `frontend/src/lib/preferences.ts` (new, ~5 lines)
- `frontend/src/styles/global.css` (~15 lines added)
- `frontend/src/components/EventCard.tsx` (~5 lines changed)
- `frontend/src/components/EventList.tsx` (~8 lines changed)

**Design notes:**
- Treat `other` as neutral — not muted, not boosted. This avoids hiding misclassified events.
- The `music` type is already distinct from `dj` in the enum. Boost all `music` since it means bands/jazz/singer-songwriter, not DJs.
- Muted cards stay fully readable — reduced opacity, not hidden. The venue color bar stays but loses its glow.

### Phase 2: Type Enrichment + Recurring Detection (Scraper)

**Expand the event type enum and add a recurring field so the scraper extracts richer data.**

1. **Add new event types** to `EventType` enum in `scraper/models.py:12`:
   - `theater` — plays, improv, staged performances (improv is close to comedy but distinct enough for theater venues)
   - `food_event` — pop-ups, tastings, supper clubs, food markets

2. **Add `recurring` field** to `Event` model in `scraper/models.py:31`:
   ```python
   recurring: str | None = None  # e.g. "every Tuesday", "weekly", "first Friday of the month"
   ```

3. **Update LLM tool schema** in `scraper/scrape.py:280-307`:
   - Add `theater` and `food_event` to the type enum
   - Add `recurring` as a nullable string field with description: "If the event happens on a regular schedule, describe it (e.g. 'every Tuesday', 'weekly'). Null if one-time or unknown."

4. **Update system prompt** in `scraper/scrape.py:48-59`:
   - Explicitly list all valid types with examples so Haiku classifies more accurately
   - Mention the recurring field

5. **Update frontend `Event` type** in `frontend/src/types.ts:1-16`:
   - Add `recurring?: string` field
   - Optionally tighten `type` from `string` to the union of valid values

6. **Render recurring badge** in `frontend/src/components/EventCard.tsx`:
   - If `event.recurring` is set, show a small badge/tag (e.g., "every Tuesday") below the event type label

**Files changed:**
- `scraper/models.py` (~5 lines)
- `scraper/scrape.py` (~15 lines)
- `frontend/src/types.ts` (~2 lines)
- `frontend/src/components/EventCard.tsx` (~5 lines)
- `frontend/src/styles/global.css` (~5 lines for recurring badge)

**Validation:** Run `python3 scraper/scrape.py --dry-run` after changes and check:
- How many events get the new types vs. `other`
- How many events get `recurring` tags
- Whether DJ vs. music classification holds up

### Phase 3: Venue Expansion (Research + Config)

**Add venues that host the events they care about. This requires research first.**

1. **Must-adds (Logan Square):**
   - Middle Brow (beer + food events — check if they have an events page)
   - Any venues with regular trivia nights
   - Revolution Brewing (events/comedy)

2. **Neighborhood expansion (Bucktown / Wicker Park):**
   - Comedy clubs and improv theaters
   - Venues with known trivia/game nights
   - Small theaters

3. **For each new venue:**
   - Add to `data/venues.yaml` with color, tags, scrape strategy
   - Add to `frontend/src/lib/venues.ts` (id, name, color)
   - Copy updated `venues.yaml` to `frontend/public/data/`
   - Test with `--dry-run`
   - Consider whether venue is Wix (use structured extractor) or needs LLM fallback

4. **Address naming/identity:** If expanding beyond Logan Square, the site name "Logan Square Tonight" may need updating — or keep it and just note it covers nearby neighborhoods. This is a product call, not a technical one.

**Scaling note:** At 15+ venues, consider a build-time script that reads `venues.yaml` and generates `venues.ts` to avoid manual sync.

## Acceptance Criteria

### Phase 1
- [ ] DJ events render with reduced opacity and no venue-bar glow
- [ ] Comedy, trivia, music, theater, film events render with enhanced visual presence
- [ ] Events with type `other` render with default (current) styling
- [ ] Within the same time slot, boosted events sort before muted ones
- [ ] No events are hidden or removed from the feed
- [ ] Mobile layout still looks good with muted/boosted styling

### Phase 2
- [ ] `theater` and `food_event` are valid event types in scraper and frontend
- [ ] Events with recurring schedules show a badge (e.g., "every Tuesday")
- [ ] `--dry-run` produces reasonable type classifications with expanded enum
- [ ] Carried-forward events with old types still render correctly

### Phase 3
- [ ] At least 3 new venues added (Middle Brow + 2 others)
- [ ] New venues produce events on `--dry-run`
- [ ] Frontend displays events from new venues with correct colors

## Dependencies & Risks

- **Classification accuracy:** The biggest risk. If Haiku misclassifies a jazz show as "dj", it gets muted — worse than no hierarchy at all. Mitigated by running `--dry-run` and validating before deploying, and by treating `other` as neutral rather than muted.
- **"other" bucket size:** If too many events fall into `other`, the visual hierarchy has limited impact. Phase 2's prompt improvements should reduce this.
- **Venue expansion scrapability:** New venues may have platforms that don't work well (client-side JS, 403 blocks like Do312). Research before committing.
- **Carry-forward compatibility:** Old events retain old types. Frontend must handle unknown types gracefully (treat as neutral).

## Implementation Order

Start with **Phase 1** — it's the highest-impact, lowest-effort change. Pure frontend, no scraper changes, immediately makes the feed more scannable. Then Phase 2 to improve data quality. Phase 3 is independent research that can happen anytime.

## References

- Brainstorm: `docs/brainstorms/2026-03-07-personal-relevance-brainstorm.md`
- Event type enum: `scraper/models.py:12-20`
- LLM tool schema: `scraper/scrape.py:280-307`
- Event card rendering: `frontend/src/components/EventCard.tsx:9-53`
- Event list sort logic: `frontend/src/components/EventList.tsx:14-47`
- CSS styles: `frontend/src/styles/global.css:118-198`
- Venue config: `data/venues.yaml`, `frontend/src/lib/venues.ts`
