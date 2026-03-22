import { useState } from "react";

function App() {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState("");
  const [budget, setBudget] = useState("budget");

  const [result, setResult] = useState(null);
  const [budgetData, setBudgetData] = useState(null);

  const handleSubmit = async () => {
    const response = await fetch("http://127.0.0.1:8000/plan-trip", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        destination: destination,
        days: Number(days),
        budget: budget,
        interests: [],
      }),
    });

    const data = await response.json();

    setResult(data);
    setBudgetData(data.budget_breakdown);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>VoyraAI 🌍</h1>

      {/* Destination */}
      <input
        placeholder="Enter Destination"
        onChange={(e) => setDestination(e.target.value)}
      />
      <br /><br />

      {/* Days */}
      <input
        type="number"
        placeholder="Number of Days"
        onChange={(e) => setDays(e.target.value)}
      />
      <br /><br />

      {/* Budget Dropdown */}
      <select onChange={(e) => setBudget(e.target.value)}>
        <option value="budget">Budget</option>
        <option value="mid-range">Mid Range</option>
        <option value="luxury">Luxury</option>
      </select>
      <br /><br />

      {/* Button */}
      <button onClick={handleSubmit}>Generate Plan</button>

      {/* Result */}
      {result && (
        <div style={{ marginTop: "20px" }}>
          <h2>Trip Plan for {result.destination}</h2>

          <p>{result.itinerary}</p>

          {budgetData && (
            <div>
              <h3>Budget Breakdown</h3>
              <p>Stay: ₹{budgetData.stay}</p>
              <p>Food: ₹{budgetData.food}</p>
              <p>Travel: ₹{budgetData.travel}</p>
              <p><strong>Total: ₹{budgetData.total}</strong></p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default App;