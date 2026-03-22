import requests

def enhance_itinerary(itinerary):
    prompt = f"""
    Improve the following travel itinerary.
    Make it more readable, structured, and attractive.

    Add:
    - Day headings
    - Bullet points
    - Emojis

    Itinerary:
    {itinerary}
    """

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        data = response.json()

        return {
            "success": True,
            "enhanced_itinerary": data["response"]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }