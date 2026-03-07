import { getDateRange, formatDateLabel } from "../lib/tonight";

interface DateStripProps {
  selected: string;
  onChange: (date: string) => void;
}

export function DateStrip({ selected, onChange }: DateStripProps) {
  const dates = getDateRange(10);

  return (
    <div class="date-strip">
      {dates.map((date) => (
        <button
          key={date}
          class={`date-chip ${date === selected ? "active" : ""}`}
          onClick={() => onChange(date)}
        >
          {formatDateLabel(date)}
        </button>
      ))}
    </div>
  );
}
