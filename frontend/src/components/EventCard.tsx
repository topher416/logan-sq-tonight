import { getVenueColor } from "../lib/venues";
import { formatTime } from "../lib/tonight";
import { BOOSTED_TYPES, MUTED_TYPES } from "../lib/preferences";
import type { Event } from "../types";

interface EventCardProps {
  event: Event;
}

export function EventCard({ event }: EventCardProps) {
  const color = getVenueColor(event.venue_id);
  const time = formatTime(event.time_start);
  const isFree =
    event.price?.toLowerCase() === "free" ||
    event.price === "$0" ||
    event.price === "0";
  const relevance = BOOSTED_TYPES.includes(event.type)
    ? "boosted"
    : MUTED_TYPES.includes(event.type)
      ? "muted"
      : "";

  return (
    <a
      href={event.source_url}
      target="_blank"
      rel="noopener noreferrer"
      class={`event-card ${relevance}`}
    >
      <div
        class="venue-bar"
        style={{
          backgroundColor: color,
          boxShadow: relevance === "muted" ? "none" : `0 0 8px ${color}44`,
        }}
      />
      <div class="event-card-content">
        <div class="event-card-top">
          <span class="event-title">{event.title}</span>
          {time && <span class="event-time">{time}</span>}
        </div>
        <div class="event-meta">
          <span class="event-venue">{event.venue_name}</span>
          {event.price && (
            <span class={`price-badge ${isFree ? "free" : ""}`}>
              {isFree ? "free" : event.price}
            </span>
          )}
          {event.type !== "other" && (
            <span>{event.type}</span>
          )}
        </div>
        {event.description && (
          <p class="event-description">{event.description}</p>
        )}
      </div>
    </a>
  );
}
