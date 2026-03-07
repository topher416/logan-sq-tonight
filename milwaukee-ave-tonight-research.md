# Milwaukee Ave Tonight — Research & Architecture Doc

**Project:** Event aggregator for bars, venues, and spaces along Milwaukee Ave in Logan Square
**Core stretch:** California Ave → Kedzie Ave (expandable)
**Status:** Prototype built, switching to Claude Code for expanded build
**Date:** March 7, 2026

---

## Venue Registry

### Tier 1 — Core Block (California to Kedzie on Milwaukee)

| Venue | Address | Website | Events Source | Scrape Difficulty | Notes |
|-------|---------|---------|--------------|-------------------|-------|
| **Cafe Mustache** | 2313 N Milwaukee | cafemustache.com | Homepage (Webflow) | EASY | Coffee shop by day, venue by night. Chicago Reader's "Best Non-Traditional Music Venue." Programs something almost every night — live music, comedy, karaoke (Fri 10pm, Sat & Sun 8pm), literary events, DJ nights. Brunch on Sundays. Events listed directly on homepage in a weekly format. Booking: stachebooking@gmail.com |
| **Coles** | 2338 N Milwaukee | colesbarchicago.com | WordPress + Do312 | MEDIUM | Always free. Live bands Fri/Sat starting ~9:30-10pm. Wednesday comedy open mic (sign up 7:15, show 8pm) is a Chicago institution — launched by Cameron Esposito in 2009, currently hosted by Victoria Vincent and Lucia Whalen. Monday jam sessions. Has a vintage FILM photo booth. Capacity ~99. Booking: collaborative team via email. |
| **Slippery Slope** | 2357 N Milwaukee | (Do312 primary) | Do312 | EASY (API) | Dance/DJ bar, late night. Events aggregated on Do312. |
| **Emporium Arcade Bar** | 2363 N Milwaukee | emporiumarcadebar.com | Own site + Do312 | MEDIUM | Largest Chicago location — arcade games, pool, pinball, foosball, air hockey. Live DJs weekends, weekly trivia, game tournaments. 21+ only. Events listed on their site with dates/times. |
| **The Native** | 2416 N Milwaukee | thenativechicago.com | Own site | NEEDS LLM | Vegan-friendly neighborhood bar. Large outdoor patio. Events programming varies — check site and Instagram. |
| **The Whistler** | 2421 N Milwaukee | whistlerchicago.com/calendar | Squarespace calendar | EASY | Bar, gallery, record label, venue. Live music and DJs 7 nights/week. GQ's 25 Best Cocktail Bars. Downbeat top jazz venues. Beautifully structured Squarespace event calendar — the dream scraping target. Jazz series Tue/Wed ("Relax Attack"), DJs Thu-Sun, literary events monthly ("Test Literary Series"), launch parties. Always-changing cocktail menu. |
| **The Owl** | 2521 N Milwaukee | owlbarchicago.com | Own site + Instagram | NEEDS LLM | Logan Square's 4am bar. Happy hour specials, live events, jukebox. Events info is sparse on site — Instagram (@theowlbar) is likely the better source. Good for late-night after other venues close. |

### Tier 2 — Expanded Radius (within ~1 mile of core block)

| Venue | Address | Website | Events Source | Scrape Difficulty | Notes |
|-------|---------|---------|--------------|-------------------|-------|
| **The Harding Tavern** | 2732 N Milwaukee | thehardingtavern.com | Own site | NEEDS LLM | Named after the Harding Theater (1925-1963). 12 drafts, ~50 bottles/cans, craft cocktails. Monthly events with breweries. Kitchen open late. Events info mostly on-site/Instagram. |
| **Logan Theatre** | 2646 N Milwaukee | thelogantheatre.com | Own site | TBD | Historic movie theater — showtimes, special screenings, events. Likely has a structured showtime feed or partners with a movie data API. Worth investigating if they use a ticketing platform (Eventbrite, etc.) |
| **Lincoln Lodge** | (verify current location) | lincolnlodge.com | Own site | TBD | Comedy venue — one of Chicago's longest-running independent comedy shows. Regular weekly lineup. Check if they use Eventbrite or similar. |
| **Rosa's Lounge** | 3420 W Armitage | rosaslounge.com | Own site | TBD | Family-owned Chicago blues institution. Not on Milwaukee but close to the neighborhood. Regular live blues schedule — likely has a structured calendar. |
| **Concord Music Hall** | 2047 N Milwaukee | concordmusichall.com | Ticketing platform | EASY (API) | Major music venue — will be on Ticketmaster, AXS, or similar with structured event data. South of the core block but on Milwaukee. |
| **Logan Square Auditorium** | 2539 N Kedzie | logansquareauditorium.com | Own site + ticketing | MEDIUM | Historic venue, live music, events. Right at the square. |

---

## Data Collected So Far (Real Events, March 2026)

### The Whistler — March 6-28, 2026 (from whistlerchicago.com/calendar)

**Programming pattern:** Something every night. Jazz series Tue/Wed, DJs Thu-Sun, special events scattered.

- **Fri 3/6:** Rare Cuts by Jackersize
- **Sat 3/7:** Feelgood Saturday (DJ #Feelgood — R&B, Rap, Soul classics)
- **Sun 3/8:** Sunday Service (DJ Matriarch / DJ Cryberbully / J3rmgirl)
- **Tue 3/10:** Relax Attack Jazz Series: Sarah Clausen Trio
- **Wed 3/11:** Test Literary Series (monthly interactive reading) + Relax Attack Jazz: Katja Ji Trio
- **Thu 3/12:** Blesstonio presents: Fusion + Prosperity Room (RnB, Afrobeats, Baile Funk)
- **Fri 3/13:** Music That Will Change Your Life (DJs Esteban & Brian Trent)
- **Sat 3/14:** All Love
- **Sun 3/15:** Le Besoin
- **Tue 3/17:** Relax Attack Jazz: Laurenzi / Rumback
- **Wed 3/18:** Relax Attack Jazz: Greg Wahl Quintet ft. Julia Minkin
- **Thu 3/19:** Research & Development
- **Fri 3/20:** Buen Viaje (balearic to underground house)
- **Sat 3/21:** Sweet Spot w/ Tommaso
- **Sun 3/22:** Deep In the Bag: Kai Castro
- **Tue 3/24:** Relax Attack Jazz: Kehsin Xu
- **Wed 3/25:** Relax Attack Jazz: Tromblau ft.
- **Thu 3/26:** Prosperity Room
- **Fri 3/27:** DJ chico (groovy tunes & dance beats)
- **Sat 3/28:** Music We Love (DJs Pauly & Ashina — House, Funk, Disco, Afrobeat, Latin)

### Cafe Mustache — Late Feb / Early March 2026 (from cafemustache.com)

**Programming pattern:** Live music most nights, karaoke Fri/Sat/Sun, brunch Sun, eclectic booking (comedy, film, literary, DJ, experimental).

- **Mon 2/23:** King Love, B.Lake
- **Tue 2/24:** Oyeme, Sana All, Twila Ping (fundraiser for Midwest Immigration Bond Fund)
- **Wed 2/25:** Lake Town Film Series' Sci-Fi Night (short films)
- **Thu 2/26:** Genius Night (feat. Joe Anderson, Gwynn Fulcher, Arish Singh + more) hosted by Tom Harrison + Cryotrance (trance night: Alucard, care_online, Dabzard, Venosci B2B Zaxy)
- **Fri 2/27:** Jaff Graffner, Bret Koontz, Alga + Friday Karaoke
- **Sat 2/28:** Three to Tango (live music & dancing) + Saturday Karaoke
- **Sun 3/1:** Beats n' Brunch (250 Split, Monét) + Sunday Karaoke
- **Mon 3/2:** Hot Potato Hearts speed dating + Fieldmates album release show w/ Receiver
- **Tue 3/3:** Gutter Fart: Stand Up Comedy (Wet Beef Comedy presents)
- **Wed 3/4:** Open House — Service Industry Listening Night
- **Thu 3/5:** Kate Ji presents "Warm Music for a Freezing Chicago Night" + Wax On! Vinyl DJs
- **Fri 3/6:** Flash Flash, Rahim Salaam, Alchemist Conneections + Friday Karaoke
- **Sat 3/7:** Open Decks w/ Brendan + Saturday Karaoke
- **Sun 3/8:** Magic Brunch w/ Merlin Brando & Majik Æon + Sunday Karaoke

### Coles — March 5-9, 2026 (from Do312)

- **Wed 3/5:** Cameron Davies, Leili Grzybowski, Karl Kirkpatrick, The Devil Said Jump
- **Fri 3/6:** CDPROM, White Lucy, Anaiet Soul (10pm)
- **Sat 3/7:** Zastava, Hearthands, Mail., Cabwaylingo (10pm)
- **Sun 3/8:** King Dom Cummies, Girl Panic, Jane Plane (9pm)
- **Mon 3/9:** Free Video Game Music DJ Night with Equip & Mukqs

### Emporium Arcade Bar — Late Feb / Early March 2026

- **Fri 2/27:** Video Rampage w/ Eddie Rampage (9pm-1am)
- **Sat 2/28:** Dance Planet w/ Jillian X (9pm-2am)
- **Tue 3/3:** Girl Power! Women in History Trivia w/ Whaddyaknow (7pm-9pm)
- **Fri 3/6:** Escobae x Vince Lazarus (9pm-1am)

---

## Scraping Architecture

### Pipeline Overview

```
① FETCH     Python cron job hits each venue URL (daily or 2x daily)
② EXTRACT   Raw HTML → Claude API (Haiku) → structured JSON
③ NORMALIZE Dates, times, venue IDs standardized to common schema
④ STORE     Write to events.json (or SQLite for query flexibility)
⑤ SERVE     Static frontend reads JSON, renders daily/weekly calendar
```

### Event Schema

```json
{
  "id": "whistler-2026-03-07-feelgood",
  "venue_id": "whistler",
  "venue_name": "The Whistler",
  "title": "Feelgood Saturday",
  "description": "DJ #Feelgood delivers R&B, Rap, Soul classics and current bangers",
  "date": "2026-03-07",
  "time_start": "21:00",
  "time_end": "02:00",
  "price": "free",
  "tags": ["dj", "rnb", "soul", "dance"],
  "source_url": "https://whistlerchicago.com/events/feelgood-mar-2026",
  "scraped_at": "2026-03-07T08:00:00Z"
}
```

### Venue Config Schema

```json
{
  "id": "whistler",
  "name": "The Whistler",
  "display_name": "The Whistler",
  "address": "2421 N Milwaukee Ave",
  "lat": 41.9267,
  "lng": -87.6979,
  "url": "https://whistlerchicago.com",
  "events_url": "https://whistlerchicago.com/calendar",
  "scrape_strategy": "fetch_html_llm_extract",
  "platform": "squarespace",
  "color": "#E8C547",
  "tags": ["cocktails", "djs", "jazz", "gallery"],
  "instagram": "@thewhistlerchicago",
  "do312_slug": "the-whistler"
}
```

### Scraping Strategies (per venue type)

**Strategy 1: Structured HTML → LLM Extract**
Best for: The Whistler (Squarespace), Cafe Mustache (Webflow), Coles (WordPress)
- Fetch raw HTML from events page
- Send to Claude Haiku with extraction prompt
- Prompt returns structured JSON array of events
- Cost: ~$0.005 per venue per run

**Strategy 2: Do312 Aggregator**
Best for: Slippery Slope, Coles, Emporium, The Whistler (backup)
- Do312 (do312.com/venues/{slug}) aggregates many Logan Square venues
- Semi-structured HTML, consistent layout across venues
- Could also scrape do312.com for the whole neighborhood in one pass
- Also check: chicagoshowcalendar.com, Songkick, Bandsintown, Resident Advisor

**Strategy 3: Ticketing Platform APIs**
Best for: Concord Music Hall, Logan Square Auditorium, larger venues
- Eventbrite API, Ticketmaster Discovery API, AXS
- Structured data, reliable, but only covers ticketed events

**Strategy 4: Instagram Scraping / Manual**
Best for: The Owl, The Native, Harding Tavern
- These venues post events primarily on Instagram
- Options: Instagram Basic Display API (limited), third-party scrapers, or manual curation
- LLM could process Instagram post captions if images are fetched

**Strategy 5: Movie Showtime APIs**
Best for: Logan Theatre
- Gracenote/TMS, TMDB, or the theater's own feed
- Many indie theaters use Veezi, Vista, or similar POS with public feeds

### Estimated Costs

- **Claude Haiku API:** ~$0.005 per venue extraction → 8 venues = ~$0.04/day = ~$1.20/month
- **Hosting:** Vercel free tier (static site) or Cloudflare Pages
- **Domain:** ~$12/year if you want a custom one
- **Total:** Under $2/month to run

---

## Data Sources Summary

| Source | URL | Covers | Data Quality |
|--------|-----|--------|-------------|
| Venue websites (direct) | Various | Individual venue | Varies widely |
| Do312 | do312.com | Many Chicago venues | Good — consistent format |
| Chicago Show Calendar | chicagoshowcalendar.com | Music-focused | Good for bands |
| Songkick | songkick.com | Concert listings | Good but incomplete |
| Bandsintown | bandsintown.com | Concert listings | Good for touring acts |
| Resident Advisor | ra.co | DJ/electronic events | Excellent for dance music |
| 5 Magazine | 5mag.net | House music events | Niche but relevant (Whistler, etc.) |

---

## Frontend (Prototype Built)

Current prototype: `milwaukee-ave-tonight.jsx` — React component with:
- **Daily view:** Date strip picker, event cards sorted by time, venue color coding
- **Weekly view:** Compact 7-day scan with venue dots
- **Pipeline view:** Architecture explainer + venue status dashboard

### Next Steps for Frontend
- Add venue filter toggles
- Add event type filter (music, comedy, karaoke, trivia, DJ, etc.)
- Map view (venues are all within ~0.5 mi on Milwaukee)
- "Tonight" quick link that auto-selects current date
- Share/link to specific date
- Mobile-first responsive layout

---

## Expansion Candidates (Beyond Current Scope)

These are within the broader Logan Square / Milwaukee Ave corridor:

- **Revolution Brewing** (2323 N Milwaukee) — brewpub, occasional events
- **Webster's Wine Bar** (2601 N Milwaukee) — wine bar, occasional live music
- **Best Intentions** (2500 N Milwaukee) — dive bar
- **Welcome Back Lounge** — DJs, outdoor space
- **Comfort Station** (2579 N Milwaukee) — free concerts, film screenings, art
- **Longman & Eagle** (2657 N Kedzie) — whiskey bar, not really events
- **Stan Mansion** (2408 N Kedzie) — candlelight concerts, private events

---

## Notes for Claude Code Build

1. Start with The Whistler + Cafe Mustache — cleanest data, most events
2. Layer in Do312 scraping for Coles, Slippery Slope, Emporium
3. Logan Theatre showtimes — investigate their site platform and whether they use a showtime API
4. Lincoln Lodge — verify current location and website, check for Eventbrite integration
5. Rosa's Lounge — check rosaslounge.com for calendar structure
6. Consider building the scraper as a single Python script with a YAML venue config file
7. Cron schedule: twice daily (8am and 4pm) should be sufficient
8. Output: single `events.json` file that the frontend reads
9. Future: could add email digest ("Tonight on Milwaukee Ave") or SMS alerts
