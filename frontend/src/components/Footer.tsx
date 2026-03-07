interface FooterProps {
  scrapedAt: string | null;
}

export function Footer({ scrapedAt }: FooterProps) {
  let label = "waiting for first scrape";
  if (scrapedAt) {
    const d = new Date(scrapedAt);
    const time = d.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      timeZone: "America/Chicago",
    }).toLowerCase();
    label = `checked today, ${time}`;
  }

  return <footer class="footer">{label}</footer>;
}
