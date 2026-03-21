import { useState } from "react";

function App() {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState("");
  const [result, setResult] = useState("");

  const handleSubmit = async () => {
    const response = await fetch("http://127.0.0.1:8000/plan-trip", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ destination, days }),
    });

    const data = await response.json();
    setResult(data.itinerary);
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>VoyraAI 🌍</h1>

      <input
        placeholder="Enter Destination"
        onChange={(e) => setDestination(e.target.value)}
      />
      <br /><br />

      <input
        placeholder="Number of Days"
        onChange={(e) => setDays(e.target.value)}
      />
      <br /><br />

      <button onClick={handleSubmit}>Generate Plan</button>

      <h2>{result}</h2>
    </div>
  );
}

export default App;