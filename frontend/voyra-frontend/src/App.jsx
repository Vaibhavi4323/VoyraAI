import { useState } from "react";

function App() {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState("");
  const [result, setResult] = useState("");
  const [budget, setBudget] = useState("");

  const handleSubmit = async () => {
    const response = await fetch("http://127.0.0.1:8000/plan-trip", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        city: destination,
        days: Number(days),
        budget: Number(budget),
      }),
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>VoyraAI 🌍</h1>

      <input
        placeholder="Enter Destination"
        onChange={(e) => setDestination(e.target.value)}
      />
      <br />
      <br />

      <input
        placeholder="Number of Days"
        onChange={(e) => setDays(e.target.value)}
      />
      <br />
      <br />

      <input
        placeholder="Budget"
        type="number"
        onChange={(e) => setBudget(e.target.value)}
      />
      <br />
      <br />

      <button onClick={handleSubmit}>Generate Plan</button>

      {result && (
        <div>
          <h2>Trip Plan for {result.city}</h2>

          {result.itinerary.map((day) => (
            <div key={day.day}>
              <h3>Day {day.day}</h3>
              <p>{day.places.join(", ")}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default App;
