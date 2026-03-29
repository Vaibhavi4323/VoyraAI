import { useState } from "react";
import TripInput from "./TripInput";
import TripResults from "./TripResults";

function App() {
  const [destination, setDestination] = useState("");
  const [days, setDays] = useState("");
  const [budget, setBudget] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    try {
      setLoading(true);
      setResult(null);

      const res = await fetch("http://127.0.0.1:8000/plan-trip", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          destination,
          days: Number(days),
          budget,
          interests: [],
        }),
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center px-4 pb-16">

      {/* Logo bar */}
      <div className="w-full max-w-6xl py-5 flex items-center gap-2">
        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"
            stroke="white" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="2" y1="12" x2="22" y2="12" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10
                     15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
          </svg>
        </div>
        <span className="text-base font-semibold text-gray-900">VoyraAI</span>
      </div>

      {/* Hero */}
      <div className="text-center max-w-2xl mt-10 flex flex-col items-center">
        <div className="flex items-center gap-1.5 bg-blue-100 text-blue-600
                        text-xs font-medium px-4 py-1.5 rounded-full mb-5">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          AI-Powered Travel Planning
        </div>

        <h1 className="text-5xl font-bold leading-tight text-gray-900">
          Plan your perfect trip<br />with AI
        </h1>

        <p className="text-gray-500 text-sm mt-4 max-w-md leading-relaxed">
          Tell us where you want to go, and our AI will create a personalized
          itinerary with flights, hotels, and activities tailored just for you.
        </p>
      </div>

      {/* Input card */}
      <div className="mt-10 w-full max-w-xl">
        <div className="bg-white border border-gray-200 rounded-2xl p-6">
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
        </div>
      </div>

      {/* Loading state */}
      {loading && (
        <div className="mt-6 flex items-center gap-2 text-sm text-gray-400">
          <svg className="animate-spin" width="14" height="14"
            viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 12a9 9 0 1 1-6.219-8.56" />
          </svg>
          Generating your trip plan...
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <div className="w-full max-w-4xl mt-12">
          <TripResults result={result} />
        </div>
      )}

    </div>
  );
}

export default App;