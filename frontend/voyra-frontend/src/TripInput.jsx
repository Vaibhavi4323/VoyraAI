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
    <div className="flex flex-col gap-4">

      {/* Destination */}
      <div>
        <label className="block text-sm font-medium text-gray-800 mb-1.5">
          Destination
        </label>
        <div className="relative">
          <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
            width="15" height="15" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
            <circle cx="12" cy="10" r="3" />
          </svg>
          <input
            type="text"
            placeholder="Where do you want to go?"
            value={destination}
            onChange={(e) => setDestination(e.target.value)}
            className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-200
                       bg-gray-50 text-sm text-gray-800 placeholder-gray-400
                       focus:outline-none focus:ring-2 focus:ring-blue-300"
          />
        </div>
      </div>

      {/* Days + Budget row */}
      <div className="grid grid-cols-2 gap-3">

        {/* Number of days */}
        <div>
          <label className="block text-sm font-medium text-gray-800 mb-1.5">
            Number of Days
          </label>
          <div className="relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" />
              <line x1="16" y1="2" x2="16" y2="6" />
              <line x1="8" y1="2" x2="8" y2="6" />
              <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
            <input
              type="number"
              placeholder="How many days?"
              value={days}
              onChange={(e) => setDays(e.target.value)}
              min={1}
              className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-200
                         bg-gray-50 text-sm text-gray-800 placeholder-gray-400
                         focus:outline-none focus:ring-2 focus:ring-blue-300"
            />
          </div>
        </div>

        {/* Budget */}
        <div>
          <label className="block text-sm font-medium text-gray-800 mb-1.5">
            Budget
          </label>
          <div className="relative">
            <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              width="14" height="14" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="1" x2="12" y2="23" />
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" />
            </svg>
            <select
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              className="w-full pl-9 pr-8 py-2.5 rounded-xl border border-gray-200
                         bg-gray-50 text-sm appearance-none cursor-pointer
                         text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-300"
            >
              <option value="" disabled>Select budget</option>
              <option value="budget">Budget</option>
              <option value="mid-range">Mid-range</option>
              <option value="luxury">Luxury</option>
            </select>
            <svg className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none"
              width="12" height="12" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2">
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </div>
        </div>

      </div>

      {/* Generate button */}
      <button
        onClick={onGenerate}
        disabled={isLoading || !destination || !days || !budget}
        className="w-full py-3 rounded-xl bg-blue-300 text-blue-900 text-sm font-medium
                   hover:bg-blue-400 active:scale-[0.99] transition disabled:opacity-50
                   disabled:cursor-not-allowed"
      >
        {isLoading ? "Generating..." : "Generate Plan"}
      </button>

    </div>
  );
}

export default TripInput;