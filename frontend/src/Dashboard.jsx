import { useEffect, useState } from "react";
import { fetchCards } from "../api.js";
import DispatchCard from "../components/DispatchCard.jsx";
import UploadPanel from "../components/UploadPanel.jsx";

const FILTERS = ["All", "Category 1", "Category 2", "Category 3"];

export default function Dashboard() {
  const [cards, setCards] = useState([]);
  const [loadError, setLoadError] = useState("");
  const [filter, setFilter] = useState("All");

  async function refresh() {
    try {
      setCards(await fetchCards());
      setLoadError("");
    } catch {
      setLoadError("Can't reach the backend. Start it with: uvicorn app.main:app --reload --port 8000");
    }
  }

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 4000);
    return () => clearInterval(t);
  }, []);

  const visible = cards.filter((c) => filter === "All" || c.urgency.category.startsWith(filter));
  const count = (f) => (f === "All" ? cards.length : cards.filter((c) => c.urgency.category.startsWith(f)).length);

  return (
    <div className="wrap">
      <div className="page-head">
        <h1>Dispatch dashboard</h1>
        <p>Live cards from audio, SMS and photo reports. Updates every few seconds.</p>
      </div>

      <UploadPanel onNewCard={(card) => setCards((prev) => [card, ...prev])} />
      {loadError && <p className="error">{loadError}</p>}

      <div className="toolbar" role="group" aria-label="Filter by priority">
        {FILTERS.map((f) => (
          <button key={f} className={`filter ${filter === f ? "on" : ""}`} onClick={() => setFilter(f)}>
            {f} ({count(f)})
          </button>
        ))}
      </div>

      <section className="card-grid">
        {visible.length === 0 && <p className="empty">No incidents here yet. Submit an SMS above to create the first card.</p>}
        {visible.map((card) => (
          <DispatchCard key={card.id} card={card} />
        ))}
      </section>
    </div>
  );
}