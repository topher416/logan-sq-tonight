import { getVenueColor } from "../lib/venues";
import { formatTime } from "../lib/tonight";
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

  return (
    <a
      href={event.source_url}
      target="_blank"
      rel="noopener noreferrer"
      class="event-card"
    >
      <div
        class="venue-bar"
        style={{
          backgroundColor: color,
          boxShadow: `0 0 8px ${color}44`,
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
