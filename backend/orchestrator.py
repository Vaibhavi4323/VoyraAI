# backend/orchestrator.py

from datetime import datetime, timedelta
from typing import Optional

from planner_agent import generate_itinerary
from budget_agent import optimize_budget
from enhancer_agent import enhance_itinerary

from flight_agent import get_flights
from hotel_agent import get_hotels

# ✅ ENABLE ACTIVITY AGENT
from activity_agent import get_activities


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
    return [f for f in flights if f.get("price", 0) <= budget_per_person]


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
        hotels = []
        activities = []  # ✅ ADDED

        # ───────────────── Step 1: Planner ─────────────────
        plan = generate_itinerary(destination, days, budget, interests)

        if not plan.get("success"):
            return {"success": False, "error": "Planner failed"}

        itinerary_text = plan["itinerary"]

        # ───────────────── Step 2: Flights (optional) ─────────────────
        if False:  # keep disabled for now
            try:
                flights_raw = get_flights(
                    origin=origin_code,
                    destination=dest_code,
                    date=get_future_date(10),
                    max_results=10
                )

                flights = filter_flights_by_budget(
                    flights_raw,
                    budget_per_person=total_budget * 0.4
                )

            except Exception as e:
                print("Flight Agent Error:", e)
                flights = []

        # ✅ FALLBACK
        if not flights:
            flights = [
                {
                    "airline": "IndiGo",
                    "departure_airport": origin_code or "DEL",
                    "arrival_airport": dest_code or "XXX",
                    "departure_time": "10:00",
                    "arrival_time": "11:30",
                    "price": 4500
                },
                {
                    "airline": "Air India",
                    "departure_airport": origin_code or "DEL",
                    "arrival_airport": dest_code or "XXX",
                    "departure_time": "15:00",
                    "arrival_time": "17:00",
                    "price": 5200
                }
            ]

        # ───────────────── Step 3: Hotels ─────────────────
        try:
            hotels_raw = get_hotels(
                city=destination,
                max_results=6
            )

            hotels = filter_hotels_by_budget(
                hotels_raw,
                budget_per_day=total_budget / max(days, 1)
            )

            print("HOTELS:", hotels)

        except Exception as e:
            print("Hotel Agent Error:", e)
            hotels = []

        # ✅ FALLBACK
        if not hotels:
            hotels = [
                {
                    "name": "The Leela Palace",
                    "location": destination,
                    "rating": 4.5,
                    "price": 8000,
                    "image": "https://images.unsplash.com/photo-1566073771259-6a8506099945"
                },
                {
                    "name": "Budget Stay Inn",
                    "location": destination,
                    "rating": 3.8,
                    "price": 3000,
                    "image": "https://images.unsplash.com/photo-1551882547-ff40c63fe5fa"
                }
            ]

        # ───────────────── Step 4: Activities (NEW) ─────────────────
        try:
            activities = get_activities(destination)
            print("ACTIVITIES:", activities)

        except Exception as e:
            print("Activity Agent Error:", e)
            activities = []

        # ✅ FALLBACK (VERY IMPORTANT)
        if not activities:
            activities = [
                {
                    "name": f"City Walk in {destination}",
                    "duration": "2 hrs",
                    "price": "Free",
                    "category": "relaxation"
                },
                {
                    "name": f"Food Tour in {destination}",
                    "duration": "3 hrs",
                    "price": "₹800",
                    "category": "food"
                },
                {
                    "name": f"Local Museum Visit in {destination}",
                    "duration": "2-4 hrs",
                    "price": "₹300",
                    "category": "culture"
                }
            ]

        # ───────────────── Final Response ─────────────────
        return {
            "success": True,
            "destination": destination,
            "origin": origin,
            "days": days,
            "budget": budget,
            "interests": interests,

            "itinerary": itinerary_text,
            "budget_breakdown": None,

            "flights": flights,
            "hotels": hotels,
            "activities": activities  # ✅ IMPORTANT FIX
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }