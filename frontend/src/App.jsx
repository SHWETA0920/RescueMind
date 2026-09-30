import { useEffect, useState } from "react";
import { fetchCards } from "./api.js";
import UploadPanel from "./components/UploadPanel.jsx";

/* ---------- shared bits ---------- */
const CLS = { "Category 1 - Immediate": "p1", "Category 2 - Urgent": "p2", "Category 3 - Non-Urgent": "p3" };
const SOURCE_LABELS = { audio_call: "Audio call", sms: "SMS", photo: "Photo" };

function PriorityBadge({ category }) {
  return <span className={`pill ${CLS[category] || ""}`}>{category}</span>;
}

function DispatchCard({ card }) {
  const { entities, urgency } = card;
  const tone = urgency.category.startsWith("Category 1") ? "c1" : urgency.category.startsWith("Category 2") ? "c2" : "c3";
  return (
    <div className={`card ${tone}`}>
      <div className="card-header">
        <span className="source-tag">{SOURCE_LABELS[card.source] || card.source}</span>
        <PriorityBadge category={urgency.category} />
      </div>
      <div className="card-body">
        <div className="field"><span className="field-label">Location</span><span>{entities.location || "Unknown"}</span></div>
        <div className="field"><span className="field-label">Type</span><span>{entities.incident_type}</span></div>
        <div className="field">
          <span className="field-label">Injuries</span>
          <span>{entities.injuries_reported ? `Reported (${entities.injury_severity})` : "None reported"}</span>
        </div>
        <div className="flags">
          {entities.unconscious_or_not_breathing && <span className="flag">Unconscious / not breathing</span>}
          {entities.fire_present && <span className="flag">Fire</span>}
          {entities.hazmat_or_explosion_risk && <span className="flag">Hazmat / explosion risk</span>}
          {entities.weapon_involved && <span className="flag">Weapon involved</span>}
        </div>
        <p className="summary">{entities.raw_summary}</p>
        <details>
          <summary>Why this priority</summary>
          <ul>{urgency.triggered_rules.map((r) => <li key={r}>{r.replaceAll("_", " ")}</li>)}</ul>
        </details>
        {card.pii_redactions.length > 0 && (
          <p className="redaction-note">Redacted before processing: {card.pii_redactions.join(", ").replaceAll("_", " ")}</p>
        )}
      </div>
    </div>
  );
}

/* ---------- Home ---------- */
function Home() {
  return (
    <>
      <section className="hero">
        <div className="wrap">
          <div>
            <h1>Every call, text and photo, sorted by urgency in seconds.</h1>
            <p className="lead">
              Incident Triage Copilot turns raw emergency reports into structured dispatch cards. Personal details
              are masked before any AI sees them, and a fixed rule table, not a chatbot, decides who gets help first.
            </p>
            <div className="cta">
              <a className="btn" href="#/dashboard">Open the dashboard</a>
              <a className="btn ghost" href="#/how-it-works">See how it works</a>
            </div>
            <div className="chips">
              {["Audio calls", "SMS", "Scene photos", "Runs offline in mock mode"].map((c) => (
                <span className="chip" key={c}>{c}</span>
              ))}
            </div>
          </div>
          <div className="demo" aria-label="Example of a report becoming a dispatch card">
            <small>Incoming SMS</small>
            <div className="msg">
              Fire at the old warehouse on 5th Street, my dad isn't breathing. I'm <mark>NAME</mark>, call me on <mark>PHONE</mark>.
            </div>
            <div className="arrow">Personal details masked, then fields extracted</div>
            <div className="card c1" style={{ marginTop: 8 }}>
              <div className="card-header">
                <span className="source-tag">SMS</span>
                <PriorityBadge category="Category 1 - Immediate" />
              </div>
              <div className="card-body">
                <div className="field"><span className="field-label">Location</span><span>Old warehouse, 5th Street</span></div>
                <div className="flags"><span className="flag">Fire</span><span className="flag">Unconscious / not breathing</span></div>
                <details open><summary>Why this priority</summary><ul><li>not breathing</li><li>fire present</li></ul></details>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="block">
        <div className="wrap">
          <h2>Built so a dispatcher can trust the order</h2>
          <p className="sub">Three decisions shape everything else in the system.</p>
          <div className="split">
            <div className="tile wide dark">
              <div>
                <h3>The urgency decision is never left to a language model</h3>
                <p>The AI only fills in fixed fields such as location, injury severity and hazards. A plain rule table then assigns Category 1, 2 or 3, so results are predictable, testable and easy to explain.</p>
              </div>
              <div className="code">{`unconscious_or_not_breathing  -> Category 1\nfire_present                  -> Category 1\ninjuries_reported (moderate)  -> Category 2\nno hazards, no injuries       -> Category 3`}</div>
            </div>
            <div className="tile"><h3>Privacy comes first</h3><p>Phone numbers, emails and stated names are redacted before text reaches any cloud model. Each card lists what was removed.</p></div>
            <div className="tile"><h3>Every card shows its reasoning</h3><p>Open “Why this priority” to see exactly which rules fired. No black box between a report and a ranking.</p></div>
          </div>
        </div>
      </section>

      <section className="block" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <h2>From report to dispatch card</h2>
          <p className="sub">One pipeline handles all three input types.</p>
          <div className="steps">
            <div className="step"><b>Receive</b><span>Audio, SMS or scene photo arrives.</span></div>
            <div className="step"><b>Transcribe and describe</b><span>Whisper turns speech into text; vision captions photos.</span></div>
            <div className="step"><b>Mask</b><span>Personal details are redacted.</span></div>
            <div className="step"><b>Extract</b><span>An LLM fills structured incident fields.</span></div>
            <div className="step"><b>Classify</b><span>Rules assign the category.</span></div>
          </div>
        </div>
      </section>

      <section className="block" style={{ paddingTop: 0 }}>
        <div className="wrap">
          <div className="band">
            <div>
              <h2>Try it in under a minute</h2>
              <p>Mock mode needs no API keys and no internet. Type a message and watch a card appear.</p>
            </div>
            <a className="btn" href="#/dashboard">Open the dashboard</a>
          </div>
        </div>
      </section>
    </>
  );
}

/* ---------- Dashboard ---------- */
const FILTERS = ["All", "Category 1", "Category 2", "Category 3"];

function Dashboard() {
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

  const count = (f) => (f === "All" ? cards.length : cards.filter((c) => c.urgency.category.startsWith(f)).length);
  const visible = cards.filter((c) => filter === "All" || c.urgency.category.startsWith(filter));

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
        {visible.map((card) => <DispatchCard key={card.id} card={card} />)}
      </section>
    </div>
  );
}

/* ---------- How it works ---------- */
function mask(text) {
  const rules = [
    [/[\w.+-]+@[\w-]+\.[\w.]+/g, "EMAIL"],
    [/\+?\d[\d\s().-]{7,}\d/g, "PHONE"],
    [/\b(?:my name is|i am|i'm|this is)\s+[A-Z][a-z]+(?:\s[A-Z][a-z]+)?/g, "NAME"],
  ];
  const found = [];
  let out = text;
  for (const [re, label] of rules) {
    out = out.replace(re, () => {
      found.push(label);
      return `\u0000${label}\u0001`;
    });
  }
  return { out, found };
}

const RULES = [
  ["Not breathing or unconscious", "Category 1", "p1", "Always wins over any lower signal"],
  ["Fire, hazmat or explosion risk", "Category 1", "p1", "Immediate danger to life"],
  ["Weapon involved", "Category 1", "p1", "Immediate danger to life"],
  ["Injuries reported, moderate or minor", "Category 2", "p2", "Needs a response soon"],
  ["No injuries and no hazard flags", "Category 3", "p3", "Can wait for available units"],
];

function HowItWorks() {
  const [text, setText] = useState("Hi, my name is Priya Sen. Smoke in the stairwell, call me on +91 98765 43210 or priya@example.com");
  const { out, found } = mask(text);
  const parts = out.split(/(\u0000[A-Z]+\u0001)/);

  return (
    <div className="wrap">
      <div className="page-head">
        <h1>How it works</h1>
        <p>Each stage does one job, and only the extraction step ever talks to an AI model.</p>
      </div>

      <section className="block" style={{ paddingTop: 32 }}>
        <div className="steps">
          <div className="step"><b>Speech and vision</b><span>faster-whisper transcribes calls. Groq vision describes photos. SMS passes straight through.</span></div>
          <div className="step"><b>PII masking</b><span>Regex redaction runs before anything leaves your server.</span></div>
          <div className="step"><b>Extraction</b><span>The LLM returns a fixed schema: location, injury severity, hazard flags.</span></div>
          <div className="step"><b>Rule classifier</b><span>A deterministic table maps those fields to a category.</span></div>
        </div>
      </section>

      <section className="block" style={{ paddingTop: 0 }}>
        <h2>Try the privacy filter</h2>
        <p className="sub">This runs in your browser as a preview. Edit the text and see what would be redacted.</p>
        <div className="lab">
          <div>
            <label htmlFor="pii">Original message</label>
            <textarea id="pii" rows={5} value={text} onChange={(e) => setText(e.target.value)} />
          </div>
          <div>
            <label>What the AI would see</label>
            <div className="out" aria-live="polite">
              {parts.map((p, i) => (p.startsWith("\u0000") ? <mark key={i}>{p.slice(1, -1)}</mark> : p))}
            </div>
            <p className="sub" style={{ margin: "8px 0 0", fontSize: 14 }}>
              {found.length ? `Redacted: ${[...new Set(found)].join(", ")}` : "Nothing to redact."}
            </p>
          </div>
        </div>
      </section>

      <section className="block" style={{ paddingTop: 0, paddingBottom: 72 }}>
        <h2>The urgency rules</h2>
        <p className="sub">Illustrative table. Keep it in sync with <code>services/classifier.py</code>.</p>
        <div className="tbl">
          <table>
            <thead><tr><th>When the report shows</th><th>Category</th><th>Meaning</th></tr></thead>
            <tbody>
              {RULES.map(([r, c, k, m]) => (
                <tr key={r}><td>{r}</td><td><span className={`pill ${k}`}>{c}</span></td><td>{m}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}

/* ---------- Safety and roadmap ---------- */
const GUARDS = [
  ["🔒", "Mask before you send", "Phone numbers, emails and stated names are redacted before text reaches any cloud LLM."],
  ["⚖️", "Rules decide, models describe", "The classifier is a plain rule table. The same input always gives the same category."],
  ["🔎", "Explain every ranking", "Cards list the rules that fired, so a dispatcher can check the reasoning at a glance."],
  ["🧪", "Test the sorting logic", "Unit tests cover every category boundary and confirm Category 1 always beats Category 2 signals."],
];

const ROAD = [
  ["Live streaming audio", "Replace batch upload with a websocket that feeds rolling chunks to faster-whisper and shows partial transcripts."],
  ["Stronger name detection", "Swap the regex name matcher for an NER model such as Microsoft Presidio."],
  ["Persistent storage", "Move the in-memory store to Postgres or Redis. Routers only call add_card and list_cards, so nothing else changes."],
  ["Labeled evaluation set", "Assert that sample calls and photos land in the expected category. This is the best proof the sorting is safe."],
];

function Safety() {
  return (
    <div className="wrap">
      <div className="page-head">
        <h1>Safety and roadmap</h1>
        <p>Emergency software has to be predictable. Here is how this one stays that way, and where it goes next.</p>
      </div>

      <section className="block" style={{ paddingTop: 32 }}>
        <div className="list">
          {GUARDS.map(([i, t, d]) => (
            <div className="tile" key={t}>
              <div className="ico" aria-hidden="true">{i}</div>
              <div><h3>{t}</h3><p>{d}</p></div>
            </div>
          ))}
        </div>
      </section>

      <section className="block" style={{ paddingTop: 0 }}>
        <h2>Two ways to run it</h2>
        <p className="sub">Switch modes with one line in <code>.env</code>.</p>
        <div className="split">
          <div className="tile"><h3>Mock mode (default)</h3><p>No API keys, no internet, no models. Every step returns realistic sample data, so you can demo and test instantly.</p></div>
          <div className="tile"><h3>Live mode</h3><p>Set MOCK_MODE=false and add a Groq API key for real Whisper transcription and real LLM extraction and vision.</p></div>
        </div>
      </section>

      <section className="block" style={{ paddingTop: 0, paddingBottom: 72 }}>
        <h2>What comes next</h2>
        <p className="sub">Planned improvements, in rough order of impact.</p>
        <div className="road">
          {ROAD.map(([t, d]) => (<div key={t}><b>{t}</b><p>{d}</p></div>))}
        </div>
      </section>
    </div>
  );
}

/* ---------- App shell ---------- */
const ROUTES = {
  "/": { label: "Home", el: <Home /> },
  "/dashboard": { label: "Dashboard", el: <Dashboard /> },
  "/how-it-works": { label: "How it works", el: <HowItWorks /> },
  "/safety": { label: "Safety and roadmap", el: <Safety /> },
};

const currentPath = () => window.location.hash.replace(/^#/, "") || "/";

export default function App() {
  const [path, setPath] = useState(currentPath());

  useEffect(() => {
    const onChange = () => {
      setPath(currentPath());
      window.scrollTo(0, 0);
    };
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);

  const route = ROUTES[path] || ROUTES["/"];

  return (
    <>
      <nav className="nav">
        <div className="wrap">
          <a className="logo" href="#/"><i aria-hidden="true">+</i>Triage Copilot</a>
          <div className="links">
            {Object.entries(ROUTES).map(([p, r]) => (
              <a key={p} href={`#${p}`} className={p === path ? "on" : ""} aria-current={p === path ? "page" : undefined}>
                {r.label}
              </a>
            ))}
          </div>
        </div>
      </nav>
      <main>{route.el}</main>
      <footer>
        <div className="wrap">
          <span>Incident Triage Copilot</span>
          <span>Masked before the model. Ranked by rules.</span>
        </div>
      </footer>
    </>
  );
}