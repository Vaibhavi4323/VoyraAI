# backend/orchestrator.py

from datetime import datetime, timedelta
from typing import Optional

from planner_agent import generate_itinerary

# ✅ ENABLE ONLY FLIGHT AGENT
from flight_agent import get_flights

# from budget_agent import optimize_budget
# from enhancer_agent import enhance_itinerary

# from hotel_agent import get_hotels
# from activity_agent import get_activities


# ─────────────────────────── Helpers ───────────────────────────

CITY_TO_IATA = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "goa": "GOI",
    "bangalore": "BLR",
    "hyderabad": "HYD",
    "chennai": "MAA",
    "kolkata": "CCU",
}


def get_iata(city: str) -> Optional[str]:
    return CITY_TO_IATA.get(city.lower())


def get_future_date(days_ahead: int = 7) -> str:
    return (datetime.now() + timedelta(days=days_ahead)).strftime("%Y-%m-%d")


def filter_flights_by_budget(flights, budget_per_person):
    return [f for f in flights if f.get("price") is None or f.get("price", 0) <= budget_per_person]


def filter_hotels_by_budget(hotels, budget_per_day):
    filtered = []
    for h in hotels:
        price_level = h.get("price_level")
        if price_level is None or price_level <= 3:
            filtered.append(h)
    return filtered


# ─────────────────────────── Main Pipeline ─────────────────────

def run_trip_pipeline(
    destination: str,
    days: int,
    budget: str,
    interests,
    origin: str = "Delhi"
):
    try:
        # ───────────────── Budget Mapping ─────────────────
        budget_map = {
            "budget": 5000,
            "mid-range": 15000,
            "luxury": 40000
        }

        total_budget = budget_map.get(budget.lower(), 10000)

        if not destination or days <= 0:
            return {"success": False, "error": "Invalid input"}

        # ───────────────── IATA Codes ─────────────────
        origin_code = get_iata(origin)
        dest_code = get_iata(destination)

        flights = []

        # ───────────────── Step 1: Planner ─────────────────
        plan = generate_itinerary(destination, days, budget, interests)

        if not plan.get("success"):
            return {"success": False, "error": "Planner failed"}

        itinerary_text = plan["itinerary"]

<<<<<<< day3-frontend
        # ───────────────── Step 2: Flights (ONLY FIXED PART) ─────────────────
        if origin_code and dest_code:
=======
        # ───────────────── Step 2: Flights ─────────────────
        if False: #origin_code and dest_code :
>>>>>>> main
            try:
                flights_raw = get_flights(
                    origin=origin_code,
                    destination=dest_code,
                    date=get_future_date(10),
                    max_results=5
                )

                flights = filter_flights_by_budget(
                    flights_raw,
                    budget_per_person=total_budget * 0.4
                )

                print("FLIGHTS:", flights)  # ✅ DEBUG

            except Exception as e:
                print("Flight Agent Error:", e)
                flights = []

        # ───────────────── Step 3: Hotels ─────────────────
<<<<<<< day3-frontend
        # try:
        #     hotels_raw = get_hotels(
        #         location=destination,
        #         max_results=10
        #     )
=======
        try:
            raise Exception("Skipping hotels (no API key)")
            check_in = get_future_date(7)
            check_out = get_future_date(7 + days)

            hotels_raw = get_hotels(
                city=destination,
                check_in=check_in,
                check_out=check_out,
                max_results=10
            )
>>>>>>> main

        #     hotels = filter_hotels_by_budget(
        #         hotels_raw,
        #         budget_per_day=total_budget / max(days, 1)
        #     )

        # except Exception as e:
        #     print("Hotel Agent Error:", e)
        #     hotels = []

        # ───────────────── Step 4: Activities ─────────────────
        # try:
        #     activities = get_activities(
        #         location=destination,
        #         max_results=10,
        #         min_rating=3.5
        #     )
        # except Exception as e:
        #     print("Activity Agent Error:", e)
        #     activities = []

        # ───────────────── Step 5: Budget Optimization ─────────────────
        # try:
        #     optimized = optimize_budget(
        #         itinerary=itinerary_text,
        #         budget=total_budget,
        #         days=days
        #     )
        #     budget_breakdown = optimized.get("budget_breakdown")
        # except Exception:
        #     budget_breakdown = None

        # ───────────────── Step 6: Enhance Itinerary ─────────────────
        # try:
        #     enhanced = enhance_itinerary(itinerary_text)
        #     final_itinerary = (
        #         enhanced.get("enhanced_itinerary")
        #         if enhanced.get("success")
        #         else itinerary_text
        #     )
        # except Exception:
        #     final_itinerary = itinerary_text

        final_itinerary = itinerary_text

        # ───────────────── Final Response ─────────────────
        return {
            "success": True,
            "destination": destination,
            "origin": origin,
            "days": days,
            "budget": budget,
            "interests": interests,

            "itinerary": final_itinerary,
            "budget_breakdown": None,

            # ✅ ONLY CHANGE THAT MATTERS
            "flights": flights,
            "hotels": [],
            "activities": []
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }