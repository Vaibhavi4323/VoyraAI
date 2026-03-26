import { useState } from "react";
import TripInput from "./TripInput";
import ItineraryCard from "./ItineraryCard"; // kept (not breaking anything)
import LoadingState from "./LoadingState";
import TripResults from "./TripResults";

function App() {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState("");
  const [budget, setBudget] = useState("budget");

  const [result, setResult] = useState(null);
  const [budgetData, setBudgetData] = useState(null);

  // Loading state
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);

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

      console.log(data);

      setResult(data);
      setBudgetData(data.budget_breakdown);
    } catch (error) {
      console.error("Error:", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: "20px" }}>
      <h1>VoyraAI 🌍</h1>

      {/* Input Component */}
      <TripInput
        destination={destination}
        setDestination={setDestination}
        days={days}
        setDays={setDays}
        budget={budget}
        setBudget={setBudget}
        onGenerate={handleSubmit}
        isLoading={loading}
      />

      {/* Loading */}
      {loading && <LoadingState />}

      {/* ✅ FIX: Pass full result object */}
      {!loading && result && (
        <TripResults result={result} />
      )}
    </div>
  );
}

export default App;