import type { VenueConfig } from "../types";

/** Venue color map — loaded from venues.yaml at build time,
 *  but hardcoded here since we only have 3 venues and the YAML
 *  is in the scraper, not the frontend bundle. */
const VENUES: VenueConfig[] = [
  { id: "whistler", name: "The Whistler", color: "#E8C547" },
  { id: "cafe-mustache", name: "Cafe Mustache", color: "#C75B39" },
  { id: "coles", name: "Coles Bar", color: "#4A90D9" },
  { id: "native", name: "The Native", color: "#2ECC71" },
  { id: "owl", name: "The Owl", color: "#E67E22" },
  { id: "harding-tavern", name: "The Harding Tavern", color: "#1ABC9C" },
  { id: "logan-theatre", name: "Logan Theatre", color: "#E74C3C" },
];

const venueMap = new Map(VENUES.map((v) => [v.id, v]));

export function getVenueColor(venueId: string): string {
  return venueMap.get(venueId)?.color ?? "#888888";
}

export function getVenueName(venueId: string): string {
  return venueMap.get(venueId)?.name ?? venueId;
}

export function getAllVenues(): VenueConfig[] {
  return VENUES;
}
