import ItineraryCard from "./ItineraryCard";
import FlightCard from "./FlightCard";
import HotelCard from "./HotelCard";
import ActivityCard from "./ActivityCard"; // ✅ ADDED

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
            <FlightCard
              key={i}
              flight={{
                airline: f.airline || "Unknown Airline",
                from: f.departure_airport || "N/A",
                to: f.arrival_airport || "N/A",
                price: f.price ? `₹${f.price}` : "N/A",
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

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
              gap: "16px",
              marginTop: "10px",
            }}
          >
            {result.hotels.map((h, i) => (
              <HotelCard
                key={i}
                hotel={{
                  name: h.name || "Hotel",
                  location: h.location || "Location not available",
                  rating: h.rating || 0,
                  price: h.price ? `₹${h.price}` : "Price not available",
                  image:
                    h.image ||
                    "https://images.unsplash.com/photo-1566073771259-6a8506099945",
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Activities ✅ UPDATED */}
      {result.activities && result.activities.length > 0 && (
        <div style={{ marginTop: "30px" }}>
          <h3>Activities</h3>

          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))",
              gap: "16px",
              marginTop: "10px",
            }}
          >
            {result.activities.map((a, i) => (
              <ActivityCard
                key={i}
                activity={{
                  name: a.name || "Activity",
                  duration: a.duration || "2-3 hrs",
                  price: a.price || "Free",
                  category: a.category || "general",
                }}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default TripResults;