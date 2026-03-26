# backend/activity_agent.py

from __future__ import annotations

import hashlib
import logging
import math
import os
import time
from dataclasses import asdict, dataclass, field
from typing import Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────── Logging ────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("activity_agent")

# ─────────────────────────── Constants ──────────────────────────

CATEGORIES = {
    "attractions": "tourist attractions",
    "museums": "museums",
    "parks": "parks",
    "adventure": "adventure activities",
    "nightlife": "nightlife clubs",
    "shopping": "shopping malls",
}

_VALID_SORT = {"rating", "user_ratings_total", "score"}

# ─────────────────────────── Exceptions ─────────────────────────

class ActivityAgentError(Exception): pass
class ValidationError(ActivityAgentError): pass
class APIError(ActivityAgentError): pass
class NoActivitiesFoundError(ActivityAgentError): pass

# ─────────────────────────── Data Model ─────────────────────────

@dataclass
class Activity:
    name: str
    address: str
    latitude: float
    longitude: float
    rating: Optional[float]
    user_ratings_total: Optional[int]
    types: list[str] = field(default_factory=list)
    photo_reference: Optional[str] = None

    def score(self) -> float:
        rating = self.rating or 0
        reviews = self.user_ratings_total or 0
        return rating * math.log(reviews + 1)

    def to_dict(self):
        d = asdict(self)
        d["score"] = self.score()
        return d

# ─────────────────────────── Cache ──────────────────────────────

class TTLCache:
    def __init__(self, ttl=300):
        self.store = {}
        self.ttl = ttl

    def _key(self, params):
        return hashlib.sha256(repr(sorted(params.items())).encode()).hexdigest()

    def get(self, params):
        val = self.store.get(self._key(params))
        if not val:
            return None
        data, expiry = val
        if time.time() > expiry:
            return None
        return data

    def set(self, params, value):
        self.store[self._key(params)] = (value, time.time() + self.ttl)

# ─────────────────────────── Validation ─────────────────────────

def _validate(location, min_rating, max_results, sort_by):
    if not location or len(location) < 2:
        raise ValidationError("Invalid location")
    if not (0 <= min_rating <= 5):
        raise ValidationError("Invalid rating")
    if not (1 <= max_results <= 20):
        raise ValidationError("Invalid max_results")
    if sort_by not in _VALID_SORT:
        raise ValidationError("Invalid sort_by")

# ─────────────────────────── Agent ──────────────────────────────

class ActivityAgent:

    BASE_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            raise EnvironmentError("Missing GOOGLE_PLACES_API_KEY")

        self.cache = TTLCache()

    def _call_api(self, params):
        try:
            response = requests.get(self.BASE_URL, params=params)
            data = response.json()

            if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                raise APIError(data)

            return data

        except Exception as e:
            raise APIError(e)

    def search(
        self,
        location: str,
        category: str = "attractions",
        min_rating: float = 0.0,
        max_results: int = 10,
        sort_by: str = "score",
    ):
        _validate(location, min_rating, max_results, sort_by)

        query_type = CATEGORIES.get(category, category)
        query = f"{query_type} in {location}"

        params = {
            "query": query,
            "key": self.api_key
        }

        cached = self.cache.get(params)
        if cached:
            return cached

        data = self._call_api(params)
        results = data.get("results", [])

        activities = []

        for place in results:
            rating = place.get("rating", 0)
            if rating < min_rating:
                continue

            geo = place["geometry"]["location"]

            act = Activity(
                name=place.get("name"),
                address=place.get("formatted_address"),
                latitude=geo["lat"],
                longitude=geo["lng"],
                rating=rating,
                user_ratings_total=place.get("user_ratings_total"),
                types=place.get("types", []),
                photo_reference=(place.get("photos") or [{}])[0].get("photo_reference")
            )

            activities.append(act)

            if len(activities) >= max_results:
                break

        if not activities:
            raise NoActivitiesFoundError("No activities found")

        # Sorting
        if sort_by == "rating":
            activities.sort(key=lambda x: x.rating or 0, reverse=True)
        elif sort_by == "user_ratings_total":
            activities.sort(key=lambda x: x.user_ratings_total or 0, reverse=True)
        else:
            activities.sort(key=lambda x: x.score(), reverse=True)

        self.cache.set(params, activities)
        return activities

# ─────────────────────────── Helper ─────────────────────────────

_agent = None

def get_activities(location, **kwargs):
    global _agent
    if _agent is None:
        _agent = ActivityAgent()

    return [a.to_dict() for a in _agent.search(location, **kwargs)]