from planner_agent import generate_itinerary
from budget_agent import optimize_budget
from enhancer_agent import enhance_itinerary


def run_trip_pipeline(destination, days, budget, interests):
    try:
        # 🔹 Step 1: Planner
        plan = generate_itinerary(destination, days, budget, interests)

        if not plan["success"]:
            return {"success": False, "error": "Planner failed"}

        # 🔹 Step 2: Budget
        budget_map = {
            "budget": 5000,
            "mid-range": 15000,
            "luxury": 40000
        }

        optimized = optimize_budget(
            itinerary=plan["itinerary"],
            budget=budget_map.get(budget, 10000),
            days=days
        )

        # 🔹 Step 3: Enhancer
        enhanced = enhance_itinerary(plan["itinerary"])

        if not enhanced["success"]:
            enhanced_text = plan["itinerary"]  # fallback
        else:
            enhanced_text = enhanced["enhanced_itinerary"]

        # 🔹 Final Response
        return {
            "success": True,
            "destination": destination,
            "days": days,
            "budget": budget,
            "interests": interests,
            "itinerary": enhanced_text,
            "budget_breakdown": optimized["budget_breakdown"]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }