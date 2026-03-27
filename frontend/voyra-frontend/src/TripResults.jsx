import ItineraryCard from "./ItineraryCard";
import FlightCard from "./FlightCard"; // ✅ ADD THIS

function TripResults({ result }) {
  if (!result) return null;

  return (
    <div style={{ marginTop: "30px" }}>
      <h2>Trip Plan for {result.destination}</h2>

      {/* Itinerary Section */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
          gap: "16px",
          marginTop: "20px",
        }}
      >
        {Array.isArray(result.itinerary) &&
          result.itinerary.map((dayItem, index) => (
            <ItineraryCard
              key={index}
              day={dayItem.day}
              morning={dayItem.morning}
              afternoon={dayItem.afternoon}
              evening={dayItem.evening}
            />
          ))}
      </div>

      {/* ✅ FIXED Flights Section */}
      {result.flights && result.flights.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h3>Flights</h3>

          {result.flights.map((f, i) => (
            <FlightCard
              key={i}
              flight={{
                airline: f.airline || "Unknown Airline",
                from: f.departure_airport || "N/A",
                to: f.arrival_airport || "N/A",

                // ⚠️ aviationstack DOES NOT GIVE PRICE → fallback
                price: f.price ? `₹${f.price}` : "N/A",

                // fallback duration (not available in API)
                duration:
                  f.departure_time && f.arrival_time
                    ? `${f.departure_time} → ${f.arrival_time}`
                    : "Duration not available",
              }}
            />
          ))}
        </div>
      )}

      {/* Hotels */}
      {result.hotels && result.hotels.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h3>Hotels</h3>
          {result.hotels.map((h, i) => (
            <p key={i}>{h.name}</p>
          ))}
        </div>
      )}

      {/* Activities */}
      {result.activities && result.activities.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h3>Activities</h3>
          {result.activities.map((a, i) => (
            <p key={i}>{a.name}</p>
          ))}
        </div>
      )}
    </div>
  );
}

export default TripResults;