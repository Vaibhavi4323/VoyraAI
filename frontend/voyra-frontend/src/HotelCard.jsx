function HotelCard({ hotel }) {
  return (
    <div
      style={{
        border: "1px solid #eee",
        borderRadius: "16px",
        overflow: "hidden",
        boxShadow: "0 4px 10px rgba(0,0,0,0.05)",
        transition: "transform 0.2s ease",
        background: "#fff",
      }}
    >
      {/* Image */}
      <div
        style={{
          height: "150px",
          backgroundImage: `url(${hotel.image || "https://via.placeholder.com/300"})`,
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      />

      {/* Content */}
      <div style={{ padding: "12px" }}>
        <h3 style={{ margin: "0 0 5px 0" }}>
          {hotel.name || "Hotel Name"}
        </h3>

        <p style={{ margin: "0", fontSize: "14px", color: "#555" }}>
          📍 {hotel.location || "Location not available"}
        </p>

        <p style={{ margin: "5px 0", fontSize: "14px" }}>
          ⭐ {hotel.rating ? hotel.rating : "N/A"}
        </p>

        <p style={{ margin: "5px 0", fontWeight: "bold" }}>
          {hotel.price ? `₹${hotel.price}` : "Price not available"}
        </p>

        <p style={{ fontSize: "12px", color: "#777" }}>
          per night
        </p>
      </div>
    </div>
  );
}

export default HotelCard;