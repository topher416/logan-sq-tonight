import { EventCard } from "./EventCard";
import { EmptyState } from "./EmptyState";
import type { Event } from "../types";

interface EventListProps {
  events: Event[];
  date: string;
}

export function EventList({ events, date }: EventListProps) {
  const dayEvents = events
    .filter((e) => e.date === date)
    .sort((a, b) => {
      // Sort by time_start, nulls last
      if (!a.time_start && !b.time_start) return 0;
      if (!a.time_start) return 1;
      if (!b.time_start) return -1;
      return a.time_start.localeCompare(b.time_start);
    });

  if (dayEvents.length === 0) {
    return <EmptyState date={date} />;
  }

  return (
    <div class="event-list">
      {dayEvents.map((event) => (
        <EventCard key={event.id} event={event} />
      ))}
    </div>
  );
}
