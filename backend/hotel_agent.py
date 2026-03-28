# backend/hotel_agent.py

import requests
import os
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Optional

load_dotenv()

API_KEY = os.getenv("OPENTRIPMAP_API_KEY")

BASE_URL = "https://api.opentripmap.com/0.1/en/places/radius"

# ─────────────────────────── Exceptions ─────────────────────────

class HotelAgentError(Exception): pass
class APIError(HotelAgentError): pass
class NoHotelsFoundError(HotelAgentError): pass

# ─────────────────────────── Data Model ─────────────────────────

@dataclass
class Hotel:
    name: str
    address: str
    rating: Optional[float]
    total_reviews: Optional[int]
    latitude: float
    longitude: float

    def to_dict(self):
        return asdict(self)

# ─────────────────────────── Cache ──────────────────────────────

class TTLCache:
    def __init__(self, ttl=300):
        self.store = {}
        self.ttl = ttl

    def _key(self, params):
        return hashlib.sha256(str(sorted(params.items())).encode()).hexdigest()

    def get(self, params):
        key = self._key(params)
        val = self.store.get(key)
        if not val:
            return None
        data, expiry = val
        if time.time() > expiry:
            del self.store[key]
            return None
        return data

    def set(self, params, value):
        self.store[self._key(params)] = (value, time.time() + self.ttl)

# ─────────────────────────── Agent ──────────────────────────────

class HotelAgent:

    BASE_URL = "https://api.opentripmap.com/0.1/en/places/radius"
    BASE_URL = "https://api.opentripmap.com/0.1/en/places/radius"

    def __init__(self):
        self.api_key = os.getenv("OPENTRIPMAP_API_KEY")

        if not self.api_key:
            raise ValueError("OPENTRIPMAP_API_KEY not set")
            raise ValueError("OPENTRIPMAP_API_KEY not set")

        self.cache = TTLCache()

    # ✅ NEW: Get city coordinates first
    def _get_coordinates(self, city):
        url = "https://api.opentripmap.com/0.1/en/places/geoname"
        params = {
            "name": city,
            "apikey": self.api_key
        }

        res = requests.get(url, params=params).json()

        if "lat" not in res or "lon" not in res:
            raise APIError("Could not fetch city coordinates")

        return res["lat"], res["lon"]

    def _call_api(self, params):
        try:
            response = requests.get(self.BASE_URL, params=params)
            data = response.json()

            # OpenTripMap returns "features"
            return data.get("features", [])

        except Exception as e:
            raise APIError(e)

    def search(
        self,
        city: str,
        max_results: int = 10,
        min_rating: Optional[float] = None
    ):

        params = {
            "city": city
        }

        geo_res = requests.get(geo_url, params=geo_params).json()

        lat = geo_res.get("lat")
        lon = geo_res.get("lon")

        if not lat or not lon:
            return []

        # ✅ FIX: Get coordinates
        lat, lon = self._get_coordinates(city)

        # ✅ FIX: Correct params for radius API
        api_params = {
            "radius": 5000,
            "lon": lon,
            "lat": lat,
            "kinds": "interesting places",  # hotel category
            "limit": limit,
            "apikey": self.api_key
        }

        data = self._call_api(api_params)

        if not data:
            raise NoHotelsFoundError(f"No hotels found in {city}")

        hotels = []

        for place in data:
            try:
                props = place.get("properties", {})
                geometry = place.get("geometry", {}).get("coordinates", [0, 0])

                rating = props.get("rate")

                if min_rating and (rating is None or rating < min_rating):
                    continue

                h = Hotel(
                    name=props.get("name"),
                    address=props.get("address", {}).get("road", city),
                    rating=rating,
                    total_reviews=None,
                    latitude=geometry[1],
                    longitude=geometry[0]
                )

                hotels.append(h)

                if len(hotels) >= max_results:
                    break

            except Exception:
                continue

        self.cache.set(params, hotels)

        return hotels

# ─────────────────────────── Helper ─────────────────────────────

_agent = None

def get_hotels(city, **kwargs):
    global _agent
    if _agent is None:
        _agent = HotelAgent()

    hotels = _agent.search(city, **kwargs)

    # ✅ Normalize for frontend (UNCHANGED)
    formatted_hotels = []

    for h in hotels:
        formatted_hotels.append({
            "name": h.name,
            "location": h.address,
            "rating": h.rating,
            "price": "N/A",
            "image": "https://via.placeholder.com/300"
        })

    if not formatted_hotels:
        formatted_hotels = [
            {
                "name": f"Hotel in {city}",
                "location": city,
                "rating": 4.0,
                "price": "₹2000",
                "image": "https://via.placeholder.com/300"
            }
        ]

    return formatted_hotels
