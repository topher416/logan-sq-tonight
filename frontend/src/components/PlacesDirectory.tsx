import { useState, useMemo } from "preact/hooks";
import type { Restaurant } from "../types";

interface PlacesDirectoryProps {
  restaurants: Restaurant[];
}

const ALL = "all";

export function PlacesDirectory({ restaurants }: PlacesDirectoryProps) {
  const [category, setCategory] = useState(ALL);

  const categories = useMemo(() => {
    const cats = new Set(restaurants.map((r) => r.category));
    return [ALL, ...Array.from(cats).sort()];
  }, [restaurants]);

  const filtered = useMemo(() => {
    const list =
      category === ALL
        ? restaurants
        : restaurants.filter((r) => r.category === category);
    // Sort: go-to first, then open, then want-to-try, then coming-soon, then closed
    const order: Record<string, number> = {
      "go-to": 0,
      open: 1,
      "want-to-try": 2,
      "coming-soon": 3,
      closed: 4,
    };
    return list
      .filter((r) => r.status !== "closed")
      .sort((a, b) => (order[a.status] ?? 5) - (order[b.status] ?? 5));
  }, [restaurants, category]);

  return (
    <>
      <div class="places-header">
        <h2>Places</h2>
      </div>
      <div class="category-tabs">
        {categories.map((cat) => (
          <button
            key={cat}
            class={`category-tab ${cat === category ? "active" : ""}`}
            onClick={() => setCategory(cat)}
          >
            {cat}
          </button>
        ))}
      </div>
      <div class="places-list">
        {filtered.map((place) => (
          <PlaceCard key={place.name} place={place} />
        ))}
        {filtered.length === 0 && (
          <p style={{ padding: "40px 0", textAlign: "center", color: "var(--text-tertiary)", fontSize: "0.875rem" }}>
            No spots in this category
          </p>
        )}
      </div>
    </>
  );
}

function PlaceCard({ place }: { place: Restaurant }) {
  const statusClass = place.status.replace(/\s+/g, "-");
  const showBadge = place.status !== "open";
  const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(place.name + ", " + place.address + ", Chicago, IL")}`;

  return (
    <a href={mapsUrl} target="_blank" rel="noopener noreferrer" class="place-card">
      <div class="place-card-top">
        <span class="place-name">{place.name}</span>
        <span class="place-price">{place.price}</span>
      </div>
      {place.vibe && <span class="place-vibe">{place.vibe}</span>}
      <div class="place-meta">
        <span>{place.category}</span>
        {place.subcategory && <span>{place.subcategory}</span>}
        {showBadge && (
          <span class={`status-badge ${statusClass}`}>{place.status}</span>
        )}
      </div>
    </a>
  );
}
