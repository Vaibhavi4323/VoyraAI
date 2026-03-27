import requests
import json


# ─────────────────────────── Ollama Call ───────────────────────────

def call_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 1600
                },
            },
            timeout=500,
        )

        result = response.json()["response"].strip()
        return result

    except Exception as e:
        print("Ollama Error:", e)
        return ""


# ─────────────────────────── FIXED PARSER ───────────────────────────

def parse_itinerary(text):
    days = []
    current_day = None
    current_section = None

    for line in text.split("\n"):
        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        # Detect DAY
        if "day" in lower:
            if current_day:
                days.append(current_day)

            current_day = {
                "day": len(days) + 1,
                "morning": "",
                "afternoon": "",
                "evening": "",
            }
            current_section = None

        elif "morning" in lower:
            current_section = "morning"

        elif "afternoon" in lower:
            current_section = "afternoon"

        elif "evening" in lower:
            current_section = "evening"

        elif current_section:
            clean_line = line.replace("•", "").strip()
            current_day[current_section] += clean_line + " "

    if current_day:
        days.append(current_day)

    return days


# ─────────────────────────── MAIN FUNCTION ───────────────────────────

def generate_itinerary(
    destination: str,
    days: int,
    budget: str = "budget",
    interests: list = None
) -> dict:

    interests_str = ", ".join(interests) if interests else "general sightseeing"

    try:
        # ✅ UPDATED STRICT PROMPT
        full_prompt = f"""
You are a STRICT travel itinerary generator.

Generate EXACTLY {days} days for {destination}.

STRICT RULES (DO NOT BREAK):
- Output EXACTLY {days} days (not more, not less)
- Each day MUST have:
  - Morning (at least 1 activity)
  - Afternoon (at least 1 activity)
  - Evening (at least 1 activity)
- NO section can be empty
- DO NOT skip any section
- DO NOT stop early

FORMAT:

=== DAY 1 ===
Morning:
• Activity - short description - approx cost ₹X

Afternoon:
• Activity - short description - approx cost ₹X

Evening:
• Activity - short description - approx cost ₹X

Continue until DAY {days}

IMPORTANT:
- Each activity on NEW LINE
- Always include cost
- Keep same detail level for ALL days
- DO NOT generate extra days
- Focus on: {interests_str}
"""

        itinerary_text = call_ollama(full_prompt)

        if not itinerary_text:
            return {
                "success": False,
                "error": "Empty response from model",
                "destination": destination,
                "days": days,
            }

        # ✅ Parse
        structured_itinerary = parse_itinerary(itinerary_text)

        # ✅ FIX 1: Limit extra days
        structured_itinerary = structured_itinerary[:days]

        # ✅ FIX 2: Fill missing sections
        for day_item in structured_itinerary:
            if not day_item["morning"]:
                day_item["morning"] = "Explore local attractions and nearby landmarks"
            if not day_item["afternoon"]:
                day_item["afternoon"] = "Visit popular spots and enjoy local experiences"
            if not day_item["evening"]:
                day_item["evening"] = "Relax with dinner and explore nightlife"

        # 🚨 Fallback if parsing fails
        if not structured_itinerary:
            structured_itinerary = [{
                "day": 1,
                "morning": itinerary_text[:200],
                "afternoon": "",
                "evening": ""
            }]

        return {
            "success": True,
            "destination": destination,
            "days": days,
            "budget": budget,
            "interests": interests or [],
            "itinerary": structured_itinerary,
            "raw_itinerary": itinerary_text,
            "model": "mistral"
        }

    except Exception as e:
        print("Planner Error:", e)
        return {
            "success": False,
            "error": str(e),
            "destination": destination,
            "days": days
        }


# ─────────────────────────── CLI TEST ───────────────────────────

def display_itinerary(result: dict):
    if not result["success"]:
        print("Error:", result.get("error"))
        return

    print("\n=== TRAVEL PLAN ===")

    for day in result["itinerary"]:
        print(f"\nDay {day['day']}")
        print("Morning:", day["morning"])
        print("Afternoon:", day["afternoon"])
        print("Evening:", day["evening"])


if __name__ == "__main__":
    result = generate_itinerary(
        destination="Udaipur",
        days=4,
        budget="mid-range",
        interests=["culture", "food"]
    )

    display_itinerary(result)