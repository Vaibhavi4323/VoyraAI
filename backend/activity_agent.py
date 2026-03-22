# backend/activity_agent.py

from __future__ import annotations

import hashlib
import logging
import math
import os
import time
from dataclasses import asdict, dataclass, field
from functools import wraps
from typing import Optional

import googlemaps
from googlemaps.exceptions import ApiError, ApiException, HTTPError, Timeout
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────── Logging ────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("activity_agent")

# ─────────────────────────── Constants ──────────────────────────

CATEGORIES = {
    "attractions": "tourist_attraction",
    "museums": "museum",
    "parks": "park",
    "adventure": "tourist_attraction",
    "nightlife": "bar",
    "shopping": "shopping_mall",
}

_VALID_SORT = {"rating", "user_ratings_total", "price_level", "score"}

# ─────────────────────────── Exceptions ─────────────────────────

class ActivityAgentError(Exception): pass
class ValidationError(ActivityAgentError): pass
class APIError(ActivityAgentError): pass
class NoActivitiesFoundError(ActivityAgentError): pass

# ─────────────────────────── Data Model ─────────────────────────

@dataclass
class Activity:
    place_id: str
    name: str
    address: str
    latitude: float
    longitude: float
    rating: Optional[float]
    user_ratings_total: Optional[int]
    price_level: Optional[int]
    is_open: Optional[bool]
    types: list[str] = field(default_factory=list)

    website: Optional[str] = None
    phone: Optional[str] = None
    photo_reference: Optional[str] = None

    def score(self) -> float:
        """Smart ranking score"""
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
        if time.monotonic() > expiry:
            return None
        return data

    def set(self, params, value):
        self.store[self._key(params)] = (value, time.monotonic() + self.ttl)

# ─────────────────────────── Retry ──────────────────────────────

def with_retry(max_attempts=3):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            delay = 1
            for i in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except (Timeout, HTTPError, ApiException, ApiError) as e:
                    if i == max_attempts - 1:
                        raise APIError(e)
                    time.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator

# ─────────────────────────── Validation ─────────────────────────

def _validate(location, min_rating, max_results, radius, sort_by):
    if not location or len(location) < 2:
        raise ValidationError("Invalid location")
    if not (0 <= min_rating <= 5):
        raise ValidationError("Invalid rating")
    if not (1 <= max_results <= 60):
        raise ValidationError("Invalid max_results")
    if not (500 <= radius <= 50000):
        raise ValidationError("Invalid radius")
    if sort_by not in _VALID_SORT:
        raise ValidationError("Invalid sort_by")

# ─────────────────────────── Agent ──────────────────────────────

class ActivityAgent:

    def __init__(self):
        key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not key:
            raise EnvironmentError("Missing GOOGLE_PLACES_API_KEY")

        self.client = googlemaps.Client(key=key)
        self.cache = TTLCache()

    @with_retry()
    def _geocode(self, location):
        return self.client.geocode(location)[0]["geometry"]["location"]

    @with_retry()
    def _nearby(self, latlng, radius, type_):
        return self.client.places_nearby(
            location=latlng,
            radius=radius,
            type=type_
        )

    @with_retry()
    def _details(self, place_id):
        return self.client.place(place_id=place_id)["result"]

    def search(
        self,
        location: str,
        category: str = "attractions",
        min_rating: float = 0.0,
        max_results: int = 10,
        radius: int = 5000,
        sort_by: str = "score",
        include_details: bool = False,
    ):
        _validate(location, min_rating, max_results, radius, sort_by)

        if category in CATEGORIES:
            category = CATEGORIES[category]

        params = locals()

        cached = self.cache.get(params)
        if cached:
            return cached

        latlng = self._geocode(location)

        data = self._nearby(latlng, radius, category)

        results = data.get("results", [])

        # Pagination
        while "next_page_token" in data and len(results) < max_results:
            time.sleep(2)
            data = self.client.places_nearby(page_token=data["next_page_token"])
            results.extend(data.get("results", []))

        activities = []

        for place in results:
            rating = place.get("rating", 0)
            if rating < min_rating:
                continue

            geo = place["geometry"]["location"]

            act = Activity(
                place_id=place["place_id"],
                name=place.get("name"),
                address=place.get("vicinity"),
                latitude=geo["lat"],
                longitude=geo["lng"],
                rating=rating,
                user_ratings_total=place.get("user_ratings_total"),
                price_level=place.get("price_level"),
                is_open=place.get("opening_hours", {}).get("open_now"),
                types=place.get("types", []),
                photo_reference=(place.get("photos") or [{}])[0].get("photo_reference")
            )

            if include_details:
                details = self._details(act.place_id)
                act.website = details.get("website")
                act.phone = details.get("formatted_phone_number")

            activities.append(act)

            if len(activities) >= max_results:
                break

        if not activities:
            raise NoActivitiesFoundError("No activities found")

        # Sorting fix
        activities.sort(
            key=lambda a: (
                getattr(a, sort_by) is None,
                getattr(a, sort_by)() if callable(getattr(a, sort_by, None)) else getattr(a, sort_by)
            ),
            reverse=True
        )

        self.cache.set(params, activities)
        return activities


# ─────────────────────────── Helper ─────────────────────────────

_agent = None

def get_activities(location, **kwargs):
    global _agent
    if _agent is None:
        _agent = ActivityAgent()
    return [a.to_dict() for a in _agent.search(location, **kwargs)]