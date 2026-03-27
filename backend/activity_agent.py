# backend/activity_agent.py

import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENTRIPMAP_API_KEY")

BASE_URL = "https://api.opentripmap.com/0.1/en/places/radius"

def get_activities(city, radius=5000, limit=10):
    try:
        # Step 1: Convert city → coordinates
        geo_url = "https://api.opentripmap.com/0.1/en/places/geoname"
        geo_params = {
            "name": city,
            "apikey": API_KEY
        }

        geo_res = requests.get(geo_url, params=geo_params).json()

        lat = geo_res.get("lat")
        lon = geo_res.get("lon")

        if not lat or not lon:
            return []

        # Step 2: Get activities
        params = {
            "radius": radius,
            "lon": lon,
            "lat": lat,
            "limit": limit,
            "apikey": API_KEY
        }

        res = requests.get(BASE_URL, params=params).json()

        places = []

        for p in res.get("features", []):
            prop = p["properties"]

            places.append({
                "name": prop.get("name"),
                "kind": prop.get("kinds"),
                "rating": prop.get("rate"),
                "lat": p["geometry"]["coordinates"][1],
                "lon": p["geometry"]["coordinates"][0]
            })

        return places

    except Exception as e:
        print("Activity Agent Error:", e)
        return []