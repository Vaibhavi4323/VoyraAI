import requests
import json

# Ollama call
def call_ollama(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "mistral",
                "prompt": prompt,
                "stream": False
            },
            timeout=60
        )

        result = response.json()["response"].strip()

        return result  # keep as text (same as OpenAI behavior)

    except Exception as e:
        return f"Error: {str(e)}"


def generate_itinerary(destination: str, days: int, budget: str = "budget", interests: list = None) -> dict:

    interests_str = ", ".join(interests) if interests else "general sightseeing"

    system_prompt = """You are an expert travel planner specializing in student and budget travel. 
    You provide detailed, practical, and realistic travel itineraries.
    Always include specific place names, estimated costs, and practical tips.
    Format your response in clear sections."""

    user_prompt = f"""
    Plan a {days}-day trip to {destination} for a student traveler.

    Trip Details:
    - Duration: {days} days
    - Budget Level: {budget}
    - Interests: {interests_str}

    Please provide:

    1. TRIP OVERVIEW
       - Best time to visit
       - Estimated total budget range
       - Getting there (transport options)

    2. DAY-BY-DAY ITINERARY
       For each day include:
       - Morning / Afternoon / Evening activities
       - Specific places to visit with brief descriptions
       - Estimated time at each place

    3. TOP MUST-VISIT PLACES (with entry fees if any)

    4. FOOD GUIDE
       - Must-try local dishes
       - Recommended budget-friendly restaurants/street food spots
       - Estimated meal costs

    5. ACCOMMODATION OPTIONS
       - Budget hostels/guesthouses
       - Estimated cost per night

    6. PRACTICAL TRAVEL TIPS
       - Local transport options & costs
       - Safety tips
       - Cultural etiquette
       - Packing essentials

    7. ESTIMATED BUDGET BREAKDOWN
       - Accommodation, food, transport, activities (per day)

    Make it practical, fun, and student-friendly!
    """

    try:
        #  Merge prompts (important for Ollama)
        full_prompt = system_prompt + "\n\n" + user_prompt

        # Replace OpenAI call
        itinerary_text = call_ollama(full_prompt) or "No itinerary generated."

        return {
            "success": True,
            "destination": destination,
            "days": days,
            "budget": budget,
            "interests": interests or [],
            "itinerary": itinerary_text,
            "tokens_used": None,   # ❌ not available in Ollama
            "model": "mistral"     # ✅ manually set
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "destination": destination,
            "days": days
        }


def display_itinerary(result: dict) -> None:
    if not result["success"]:
        print(f"Error generating itinerary: {result['error']}")
        return

    print("\n" + "="*60)
    print(f" TRAVEL ITINERARY: {result['destination'].upper()}")
    print(f" Duration: {result['days']} days | 💰 Budget: {result['budget'].title()}")

    if result["interests"]:
        print(f" Interests: {', '.join(result['interests'])}")

    print("="*60)
    print(result["itinerary"])
    print("="*60)
    print(f" Tokens used: {result['tokens_used']} | Model: {result['model']}")
    print("="*60 + "\n")


def interactive_planner():
    print("\n Welcome to AI Travel Planner!")
    print("-" * 40)

    destination = input("Enter your destination: ").strip()
    if not destination:
        print(" Destination cannot be empty.")
        return

    try:
        days = int(input("Number of days: ").strip())
        if days <= 0:
            raise ValueError
    except ValueError:
        print(" Please enter a valid number of days.")
        return

    print("Budget options: budget / mid-range / luxury")
    budget = input("Budget level (default: budget): ").strip().lower() or "budget"
    if budget not in ["budget", "mid-range", "luxury"]:
        budget = "budget"

    interests_input = input("Your interests (e.g. food, history, hiking): ").strip()
    interests = [i.strip() for i in interests_input.split(",")] if interests_input else []

    print("\n⏳ Generating your personalized itinerary...\n")
    result = generate_itinerary(destination, days, budget, interests)
    display_itinerary(result)


if __name__ == "__main__":
    result = generate_itinerary(
        destination="Bali, Indonesia",
        days=5,
        budget="budget",
        interests=["beaches", "temples", "food", "surfing"]
    )
    display_itinerary(result)