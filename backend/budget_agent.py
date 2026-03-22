def optimize_budget(itinerary, budget, days, costs=None, priorities=None):
    """
    Optimizes travel budget across stay, food, and travel categories.

    Args:
        itinerary  : Trip description or plan.
        budget     : Total available budget (must be > 0).
        days       : Number of days (must be >= 1).
        costs      : Optional dict with per-day costs.
                     Keys: 'stay_per_day', 'food_per_day', 'travel_per_day'
        priorities : Optional list defining spending priority order.
                     e.g., ['stay', 'food', 'travel']
                     Higher priority categories are cut last when over budget.

    Returns:
        dict with itinerary and budget_breakdown.
    """

    # ─── 1. Input Validation ───────────────────────────────────────────────

    if not isinstance(budget, (int, float)) or budget <= 0:
        raise ValueError(f"Budget must be a positive number. Got: {budget}")

    if not isinstance(days, int) or days < 1:
        raise ValueError(f"Days must be a positive integer. Got: {days}")

    if itinerary is None or (isinstance(itinerary, str) and not itinerary.strip()):
        raise ValueError("Itinerary cannot be empty or None.")

    # ─── 2. Default Costs ──────────────────────────────────────────────────

    default_costs = {
        "stay_per_day": 1500,
        "food_per_day": 800,
        "travel_per_day": 500,
    }

    # Override defaults if custom costs provided
    if costs is not None:
        if not isinstance(costs, dict):
            raise TypeError("costs must be a dictionary.")
        for key in costs:
            if key not in default_costs:
                raise KeyError(f"Unknown cost key '{key}'. Valid keys: {list(default_costs.keys())}")
            if not isinstance(costs[key], (int, float)) or costs[key] < 0:
                raise ValueError(f"Cost for '{key}' must be a non-negative number. Got: {costs[key]}")
        default_costs.update(costs)

    stay_per_day = default_costs["stay_per_day"]
    food_per_day = default_costs["food_per_day"]
    travel_per_day = default_costs["travel_per_day"]

    # ─── 3. Initial Cost Breakdown ─────────────────────────────────────────

    breakdown = {
        "stay": stay_per_day * days,
        "food": food_per_day * days,
        "travel": travel_per_day * days,
    }

    total_cost = sum(breakdown.values())

    # ─── 4. Priority Handling ──────────────────────────────────────────────

    default_priorities = ["stay", "food", "travel"]

    if priorities is not None:
        if not isinstance(priorities, list):
            raise TypeError("priorities must be a list.")
        if sorted(priorities) != sorted(default_priorities):
            raise ValueError(f"priorities must contain exactly: {default_priorities}. Got: {priorities}")
    else:
        priorities = default_priorities

    # ─── 5. Budget Optimization ────────────────────────────────────────────

    if total_cost > budget:
        excess = total_cost - budget

        # Cut from lowest priority first
        for category in reversed(priorities):
            if excess <= 0:
                break

            reducible = min(breakdown[category], excess)
            breakdown[category] -= reducible
            excess -= reducible

        total_cost = sum(breakdown.values())

    # ─── 6. Final Output ───────────────────────────────────────────────────

    return {
        "itinerary": itinerary,
        "budget_breakdown": {
            "stay": round(breakdown["stay"], 2),
            "food": round(breakdown["food"], 2),
            "travel": round(breakdown["travel"], 2),
            "total": round(total_cost, 2),
        }
    }


# ─── Example Usage (Optional Test Block) ─────────────────────────────────────

if __name__ == "__main__":
    result = optimize_budget(
        itinerary="Goa Trip - Beach & Sightseeing",
        budget=10000,
        days=5,
        costs={
            "stay_per_day": 1200,
            "food_per_day": 600,
            "travel_per_day": 400,
        },
        priorities=["stay", "food", "travel"]
    )

    print("Itinerary :", result["itinerary"])
    print("Breakdown :")
    for k, v in result["budget_breakdown"].items():
        print(f"  {k.capitalize():10} ₹{v}")