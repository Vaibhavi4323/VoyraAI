function ItineraryCard({ day, morning, afternoon, evening }) {
  return (
    <div style={{
      border: "1px solid #eee",
      borderRadius: "16px",
      padding: "16px",
      marginBottom: "16px",
      boxShadow: "0 4px 10px rgba(0,0,0,0.05)"
    }}>
      <h3>Day {day}</h3>

      <p><strong>Morning:</strong> {morning}</p>
      <p><strong>Afternoon:</strong> {afternoon}</p>
      <p><strong>Evening:</strong> {evening}</p>
    </div>
  );
}

export default ItineraryCard;