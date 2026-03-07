import { formatDateLabel } from "../lib/tonight";

interface EmptyStateProps {
  date: string;
}

const SUGGESTIONS = [
  { name: "Lula Cafe", vibe: "neighborhood fine dining" },
  { name: "Cafe Mustache", vibe: "weird cozy bar with live music" },
  { name: "Wolfbait", vibe: "cocktails + gallery vibes" },
];

export function EmptyState({ date }: EmptyStateProps) {
  const label = formatDateLabel(date);

  return (
    <div class="empty-state">
      <h2>Quiet night in the neighborhood</h2>
      <p>
        Nothing scraped for {label} yet. Events usually show up by 3pm.
      </p>
      <div class="empty-suggestions">
        <p style={{ fontSize: "0.75rem", color: "var(--text-tertiary)", marginBottom: "4px" }}>
          meanwhile, might we suggest...
        </p>
        {SUGGESTIONS.map((s) => (
          <div key={s.name} class="empty-suggestion">
            <span class="name">{s.name}</span>
            <span class="vibe">{s.vibe}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
