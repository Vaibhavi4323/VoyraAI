function ActivityCard({ activity }) {
  const getCategoryColor = (category) => {
    switch ((category || "").toLowerCase()) {
      case "adventure":
        return { bg: "#d1fae5", text: "#065f46" };
      case "culture":
        return { bg: "#dbeafe", text: "#1e3a8a" };
      case "food":
        return { bg: "#ffedd5", text: "#9a3412" };
      case "relaxation":
        return { bg: "#f3e8ff", text: "#6b21a8" };
      default:
        return { bg: "#f3f4f6", text: "#374151" };
    }
  };

  const colors = getCategoryColor(activity.category);

  return (
    <div
      style={{
        border: "1px solid #eee",
        borderRadius: "16px",
        padding: "14px",
        boxShadow: "0 4px 10px rgba(0,0,0,0.05)",
        background: "#fff",
        transition: "all 0.3s ease",
      }}
    >
      {/* Top Section */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          marginBottom: "10px",
          gap: "8px",
        }}
      >
        <h3 style={{ margin: 0, fontSize: "16px" }}>
          🎯 {activity.name || "Activity"}
        </h3>

        <span
          style={{
            fontSize: "12px",
            padding: "4px 8px",
            borderRadius: "12px",
            background: colors.bg,
            color: colors.text,
            fontWeight: "500",
            whiteSpace: "nowrap",
          }}
        >
          {activity.category || "general"}
        </span>
      </div>

      {/* Bottom Section */}
      <div
        style={{
          display: "flex",
          gap: "16px",
          fontSize: "13px",
          color: "#555",
        }}
      >
        <div>🕒 {activity.duration || "Flexible"}</div>
        <div>💰 {activity.price || "Free"}</div>
      </div>
    </div>
  );
}

export default ActivityCard;