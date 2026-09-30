import { useEffect, useState } from "react";
import { fetchCards } from "./api.js";
import DispatchCard from "./components/DispatchCard.jsx";
import UploadPanel from "./components/UploadPanel.jsx";

export default function App() {
  const [cards, setCards] = useState([]);
  const [loadError, setLoadError] = useState("");

  async function refresh() {
    try {
      const data = await fetchCards();
      setCards(data);
      setLoadError("");
    } catch (err) {
      setLoadError(err.message);
    }
  }

  useEffect(() => {
    refresh();
    const interval = setInterval(refresh, 4000);
    return () => clearInterval(interval);
  }, []);

  function handleNewCard(card) {
    setCards((prev) => [card, ...prev]);
  }

  return (
    <div className="app">
      <header>
        <h1>Incident triage dashboard</h1>
        <p className="subtitle">
          Live dispatch cards, auto-populated from audio, SMS, and photo reports.
        </p>
      </header>

      <UploadPanel onNewCard={handleNewCard} />

      {loadError && <p className="error">{loadError}</p>}

      <section className="card-grid">
        {cards.length === 0 && <p className="empty">No incidents yet.</p>}
        {cards.map((card) => (
          <DispatchCard key={card.id} card={card} />
        ))}
      </section>
    </div>
  );
}
