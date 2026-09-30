export default function PriorityBadge({ category }) {
  const styles = {
    "Category 1 - Immediate": { bg: "#4a1b0c", fg: "#fac775", label: "Category 1 - Immediate" },
    "Category 2 - Urgent": { bg: "#633806", fg: "#fac775", label: "Category 2 - Urgent" },
    "Category 3 - Non-Urgent": { bg: "#173404", fg: "#c0dd97", label: "Category 3 - Non-Urgent" },
  };
  const style = styles[category] || { bg: "#2c2c2a", fg: "#d3d1c7", label: category };

  return (
    <span
      style={{
        background: style.bg,
        color: style.fg,
        padding: "4px 10px",
        borderRadius: "999px",
        fontSize: "12px",
        fontWeight: 500,
        whiteSpace: "nowrap",
      }}
    >
      {style.label}
    </span>
  );
}
