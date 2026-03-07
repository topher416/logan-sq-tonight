import { useState, useEffect } from "preact/hooks";
import { Header } from "./Header";
import { DateStrip } from "./DateStrip";
import { EventList } from "./EventList";
import { PlacesDirectory } from "./PlacesDirectory";
import { Footer } from "./Footer";
import { getTonightDate, isValidDate } from "../lib/tonight";
import type { Event, Restaurant } from "../types";

type View = "events" | "places";

export function App() {
  const [events, setEvents] = useState<Event[]>([]);
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [selectedDate, setSelectedDate] = useState(getTonightDate());
  const [view, setView] = useState<View>("events");
  const [scrapedAt, setScrapedAt] = useState<string | null>(null);

  useEffect(() => {
    // Read date from URL hash
    const hash = window.location.hash.slice(1);
    if (hash && isValidDate(hash)) {
      setSelectedDate(hash);
    }
  }, []);

  useEffect(() => {
    fetch("/data/events.json")
      .then((r) => r.json())
      .then((data: Event[]) => {
        setEvents(data);
        if (data.length > 0) {
          setScrapedAt(data[0].scraped_at);
        }
      })
      .catch(() => setEvents([]));

    fetch("/data/restaurants.json")
      .then((r) => r.json())
      .then((data: Restaurant[]) => setRestaurants(data))
      .catch(() => setRestaurants([]));
  }, []);

  function handleDateChange(date: string) {
    setSelectedDate(date);
    window.location.hash = date;
  }

  return (
    <>
      <Header view={view} onViewChange={setView} />
      {view === "events" ? (
        <>
          <DateStrip selected={selectedDate} onChange={handleDateChange} />
          <EventList events={events} date={selectedDate} />
        </>
      ) : (
        <PlacesDirectory restaurants={restaurants} />
      )}
      <Footer scrapedAt={scrapedAt} />
    </>
  );
}
