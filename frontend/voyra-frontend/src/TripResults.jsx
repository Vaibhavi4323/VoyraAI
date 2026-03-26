import ItineraryCard from "./ItineraryCard";

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

      {/* Flights */}
      {result.flights && result.flights.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h3>Flights</h3>
          {result.flights.map((f, i) => (
            <p key={i}>
              {f.airline} | ₹{f.price} | {f.departure_airport} →{" "}
              {f.arrival_airport}
            </p>
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