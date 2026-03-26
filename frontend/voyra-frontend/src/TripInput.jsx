import { useState } from "react";

function TripInput({
  destination,
  setDestination,
  days,
  setDays,
  budget,
  setBudget,
  onGenerate,
  isLoading,
}) {
  return (
    <div style={{ maxWidth: "600px", margin: "0 auto" }}>
      <div style={{
        background: "#fff",
        padding: "20px",
        borderRadius: "16px",
        boxShadow: "0 10px 25px rgba(0,0,0,0.1)"
      }}>

        <h3>Plan Your Trip</h3>

        {/* Destination */}
        <input
          placeholder="Where do you want to go?"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
        />

        {/* Days */}
        <input
          type="number"
          placeholder="How many days?"
          value={days}
          onChange={(e) => setDays(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
        />

        {/* Budget */}
        <select
          value={budget}
          onChange={(e) => setBudget(e.target.value)}
          style={{ width: "100%", padding: "10px", marginBottom: "10px" }}
        >
          <option value="budget">Budget</option>
          <option value="mid-range">Mid-range</option>
          <option value="luxury">Luxury</option>
        </select>

        {/* Button */}
        <button
          onClick={onGenerate}
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "12px",
            background: "#3b82f6",
            color: "#fff",
            borderRadius: "10px",
            border: "none",
            cursor: "pointer"
          }}
        >
          {isLoading ? "Generating..." : "Generate Plan"}
        </button>

      </div>
    </div>
  );
}

export default TripInput;