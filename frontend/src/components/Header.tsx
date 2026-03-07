type View = "events" | "places";

interface HeaderProps {
  view: View;
  onViewChange: (view: View) => void;
}

export function Header({ view, onViewChange }: HeaderProps) {
  return (
    <header class="header">
      <h1>Logan Sq Tonight</h1>
      <nav>
        <a
          href="#"
          class={view === "events" ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            onViewChange("events");
          }}
        >
          events
        </a>
        <a
          href="#"
          class={view === "places" ? "active" : ""}
          onClick={(e) => {
            e.preventDefault();
            onViewChange("places");
          }}
        >
          places
        </a>
      </nav>
    </header>
  );
}
