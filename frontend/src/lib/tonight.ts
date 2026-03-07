/** Get "tonight's" date string (YYYY-MM-DD) using 5am rollover.
 *  Before 5am counts as the previous day — The Owl is open till 5am. */
export function getTonightDate(): string {
  const now = new Date();
  // Convert to Chicago time
  const chicago = new Date(
    now.toLocaleString("en-US", { timeZone: "America/Chicago" })
  );
  if (chicago.getHours() < 5) {
    chicago.setDate(chicago.getDate() - 1);
  }
  return formatDate(chicago);
}

/** Format a Date to YYYY-MM-DD */
export function formatDate(d: Date): string {
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}-${m}-${day}`;
}

/** Get the next N dates starting from tonight */
export function getDateRange(days: number): string[] {
  const tonight = getTonightDate();
  const start = new Date(tonight + "T12:00:00");
  const dates: string[] = [];
  for (let i = 0; i < days; i++) {
    const d = new Date(start);
    d.setDate(d.getDate() + i);
    dates.push(formatDate(d));
  }
  return dates;
}

/** Format a date string for display: "Tonight", "Tomorrow", "Wed Mar 12" */
export function formatDateLabel(dateStr: string): string {
  const tonight = getTonightDate();
  if (dateStr === tonight) return "Tonight";

  const tDate = new Date(tonight + "T12:00:00");
  const tomorrow = new Date(tDate);
  tomorrow.setDate(tomorrow.getDate() + 1);
  if (dateStr === formatDate(tomorrow)) return "Tomorrow";

  const d = new Date(dateStr + "T12:00:00");
  return d.toLocaleDateString("en-US", {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

/** Format 24hr time to casual: "21:00" → "9pm", "20:30" → "8:30pm" */
export function formatTime(time: string | null): string | null {
  if (!time) return null;
  const [h, m] = time.split(":").map(Number);
  const period = h >= 12 ? "pm" : "am";
  const hour = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return m === 0 ? `${hour}${period}` : `${hour}:${String(m).padStart(2, "0")}${period}`;
}

/** Check if a date string is valid */
export function isValidDate(dateStr: string): boolean {
  return /^\d{4}-\d{2}-\d{2}$/.test(dateStr) && !isNaN(Date.parse(dateStr));
}
