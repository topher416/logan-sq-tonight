import { useState } from "preact/hooks";
import { EventCard } from "./EventCard";
import { EmptyState } from "./EmptyState";
import { getVenueColor } from "../lib/venues";
import { BOOSTED_TYPES, MUTED_TYPES } from "../lib/preferences";
import type { Event } from "../types";

interface EventListProps {
  events: Event[];
  date: string;
}

const COLLAPSIBLE_VENUE = "logan-theatre";

export function EventList({ events, date }: EventListProps) {
  const [showShowtimes, setShowShowtimes] = useState(false);

  const relevanceRank = (e: Event) =>
    BOOSTED_TYPES.includes(e.type) ? 0 : MUTED_TYPES.includes(e.type) ? 2 : 1;

  const dayEvents = events
    .filter((e) => e.date === date)
    .sort((a, b) => {
      // Sort by time_start, nulls last; then boosted before muted within same time
      if (!a.time_start && !b.time_start) return relevanceRank(a) - relevanceRank(b);
      if (!a.time_start) return 1;
      if (!b.time_start) return -1;
      const timeCmp = a.time_start.localeCompare(b.time_start);
      if (timeCmp !== 0) return timeCmp;
      return relevanceRank(a) - relevanceRank(b);
    });

  if (dayEvents.length === 0) {
    return <EmptyState date={date} />;
  }

  const showtimes = dayEvents.filter((e) => e.venue_id === COLLAPSIBLE_VENUE);
  const otherEvents = dayEvents.filter((e) => e.venue_id !== COLLAPSIBLE_VENUE);

  return (
    <div class="event-list">
      {otherEvents.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
      {showtimes.length > 0 && (
        <ShowtimesGroup
          events={showtimes}
          expanded={showShowtimes}
          onToggle={() => setShowShowtimes(!showShowtimes)}
        />
      )}
    </div>
  );
}

function ShowtimesGroup({
  events,
  expanded,
  onToggle,
}: {
  events: Event[];
  expanded: boolean;
  onToggle: () => void;
}) {
  const color = getVenueColor(COLLAPSIBLE_VENUE);

  return (
    <div class="showtimes-group">
      <button class="showtimes-toggle" onClick={onToggle}>
        <div
          class="venue-bar"
          style={{
            backgroundColor: color,
            boxShadow: `0 0 8px ${color}44`,
          }}
        />
        <div class="showtimes-toggle-content">
          <span class="showtimes-toggle-title">
            Logan Theatre
          </span>
          <span class="showtimes-toggle-count">
            {events.length} showtime{events.length !== 1 ? "s" : ""}
          </span>
        </div>
        <span class={`showtimes-chevron ${expanded ? "open" : ""}`}>
          ›
        </span>
      </button>
      {expanded && (
        <div class="showtimes-list">
          {events.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      )}
    </div>
  );
}
