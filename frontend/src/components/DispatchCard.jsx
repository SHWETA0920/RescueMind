import PriorityBadge from "./PriorityBadge.jsx";

const SOURCE_LABELS = { audio_call: "Audio call", sms: "SMS", photo: "Photo" };

export default function DispatchCard({ card }) {
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
          <ul>{urgency.triggered_rules.map((rule) => <li key={rule}>{rule.replaceAll("_", " ")}</li>)}</ul>
        </details>

        {card.pii_redactions.length > 0 && (
          <p className="redaction-note">Redacted before processing: {card.pii_redactions.join(", ").replaceAll("_", " ")}</p>
        )}
      </div>
    </div>
  );
}