export interface Event {
  id: string;
  venue_id: string;
  venue_name: string;
  title: string;
  description: string | null;
  date: string;
  time_start: string | null;
  time_end: string | null;
  timezone: string;
  type: string;
  price: string | null;
  tags: string[];
  source_url: string;
  scraped_at: string;
}

export interface Restaurant {
  name: string;
  address: string;
  category: string;
  subcategory: string | null;
  vibe: string;
  price_range: string;
  status: string;
  note: string | null;
  website: string | null;
  instagram: string | null;
}

export interface VenueConfig {
  id: string;
  name: string;
  color: string;
}
