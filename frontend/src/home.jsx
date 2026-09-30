import PriorityBadge from "../components/PriorityBadge.jsx";

export default function Home() {
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
              Fire at the old warehouse on 5th Street, my dad isn't breathing. I'm <mark>NAME</mark>, call me on{" "}
              <mark>PHONE</mark>.
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
            <div className="tile">
              <h3>Privacy comes first</h3>
              <p>Phone numbers, emails and stated names are redacted before text reaches any cloud model. Each card lists what was removed.</p>
            </div>
            <div className="tile">
              <h3>Every card shows its reasoning</h3>
              <p>Open “Why this priority” to see exactly which rules fired. No black box between a report and a ranking.</p>
            </div>
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