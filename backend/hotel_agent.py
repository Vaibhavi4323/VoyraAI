# backend/hotel_agent.py

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import asdict, dataclass
from functools import wraps
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────── Logging ────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("hotel_agent")

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

    BASE_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")

        if not self.api_key:
            raise ValueError("GOOGLE_PLACES_API_KEY not set")

        self.cache = TTLCache()

    def _call_api(self, params):
        try:
            response = requests.get(self.BASE_URL, params=params)
            data = response.json()

            if data.get("status") != "OK":
                raise APIError(data)

            return data.get("results", [])

        except Exception as e:
            raise APIError(e)

    def search(
        self,
        city: str,
        max_results: int = 10,
        min_rating: Optional[float] = None
    ):

        query = f"hotels in {city}"

        params = {
            "query": query,
            "key": self.api_key
        }

        cached = self.cache.get(params)
        if cached:
            return cached

        data = self._call_api(params)

        if not data:
            raise NoHotelsFoundError(f"No hotels found in {city}")

        hotels = []

        for place in data:
            try:
                rating = place.get("rating")

                if min_rating and (rating is None or rating < min_rating):
                    continue

                h = Hotel(
                    name=place.get("name"),
                    address=place.get("formatted_address"),
                    rating=rating,
                    total_reviews=place.get("user_ratings_total"),
                    latitude=place["geometry"]["location"]["lat"],
                    longitude=place["geometry"]["location"]["lng"]
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

    return [h.to_dict() for h in hotels]


'''
print("API KEY:", os.getenv("GOOGLE_PLACES_API_KEY"))
'''