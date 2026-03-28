function FlightCard({ flight }) {
  return (
    <div
      style={{
        borderRadius: "16px",
        border: "1px solid #e5e7eb",
        padding: "16px",
        marginBottom: "12px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
        transition: "all 0.3s ease",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        background: "#fff"
      }}
    >
      {/* Left Section */}
      <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
        <div
          style={{
            padding: "10px",
            borderRadius: "12px",
            background: "#e0edff"
          }}
        >
          ✈️
        </div>

        <div>
          <p style={{ fontWeight: "600", margin: 0 }}>
            {flight.airline}
          </p>
          <p style={{ fontSize: "12px", color: "#6b7280", margin: 0 }}>
            {flight.duration || "Duration not available"}
          </p>
        </div>
      </div>

      {/* Middle Section */}
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        <span style={{ fontWeight: "500" }}>
          {flight.from || "N/A"}
        </span>
        <span>➡️</span>
        <span style={{ fontWeight: "500" }}>
          {flight.to || "N/A"}
        </span>
      </div>

      {/* Right Section */}
      <div style={{ textAlign: "right" }}>
        <p
          style={{
            fontSize: "18px",
            fontWeight: "700",
            color: "#2563eb",
            margin: 0
          }}
        >
          {flight.price || "N/A"}
        </p>
        <p style={{ fontSize: "12px", color: "#6b7280", margin: 0 }}>
          per person
        </p>
      </div>
    </div>
  );
}

export default FlightCard;