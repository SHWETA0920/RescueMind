import { useState } from "react";

function mask(text) {
  const rules = [
    [/[\w.+-]+@[\w-]+\.[\w.]+/g, "EMAIL"],
    [/\+?\d[\d\s().-]{7,}\d/g, "PHONE"],
    [/\b(?:my name is|i am|i'm|this is)\s+[A-Z][a-z]+(?:\s[A-Z][a-z]+)?/g, "NAME"],
  ];
  const found = [];
  let out = text;
  for (const [re, label] of rules) {
    out = out.replace(re, (m) => {
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

export default function HowItWorks() {
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