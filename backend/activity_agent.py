# backend/activity_agent.py

from __future__ import annotations

import logging
import math
import os
import time
from dataclasses import dataclass, asdict, field
from typing import Optional, List

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────── Logging ────────────────────────────

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("activity_agent")

# ─────────────────────────── Constants ──────────────────────────

OPENTRIP_BASE = "https://api.opentripmap.com/0.1/en/places"

# ─────────────────────────── Data Model ─────────────────────────

@dataclass
class Activity:
    name: str
    duration: str
    price: str
    category: str

    def to_dict(self):
        return asdict(self)

# ─────────────────────────── Agent ──────────────────────────────

class ActivityAgent:

    def __init__(self):
        self.api_key = os.getenv("OPENTRIPMAP_API_KEY")

    # 🔹 STEP 1: Get coordinates
    def _get_coordinates(self, location: str):
        url = f"{OPENTRIP_BASE}/geoname"
        params = {
            "name": location,
            "apikey": self.api_key
        }

        res = requests.get(url, params=params).json()
        return res.get("lat"), res.get("lon")

    # 🔹 STEP 2: Get places
    def _get_places(self, lat, lon):
        url = f"{OPENTRIP_BASE}/radius"

        params = {
            "radius": 5000,
            "lon": lon,
            "lat": lat,
            "limit": 10,
            "apikey": self.api_key
        }

        res = requests.get(url, params=params).json()
        return res.get("features", [])

    # 🔹 STEP 3: Convert to our format
    def _format_activities(self, places):
        activities = []

        for p in places:
            props = p.get("properties", {})

            activity = Activity(
                name=props.get("name") or "Local Activity",
                duration="2-3 hrs",
                price="₹500-₹1500",
                category=self._map_category(props.get("kinds", ""))
            )

            activities.append(activity.to_dict())

        return activities

    # 🔹 STEP 4: Category Mapping
    def _map_category(self, kinds: str):
        kinds = kinds.lower()

        if "museum" in kinds:
            return "culture"
        elif "park" in kinds:
            return "relaxation"
        elif "sport" in kinds or "adventure" in kinds:
            return "adventure"
        elif "restaurant" in kinds or "food" in kinds:
            return "food"
        else:
            return "general"

    # 🔥 STEP 5: FALLBACK SYSTEM
    def _fallback(self, location: str):
        logger.warning("Using fallback activities")

        return [
            {
                "name": f"City Walk in {location}",
                "duration": "2 hrs",
                "price": "Free",
                "category": "relaxation"
            },
            {
                "name": f"Local Food Tour in {location}",
                "duration": "3 hrs",
                "price": "₹800",
                "category": "food"
            },
            {
                "name": f"Explore Museums in {location}",
                "duration": "2-4 hrs",
                "price": "₹300",
                "category": "culture"
            }
        ]

    # 🚀 MAIN FUNCTION
    def get_activities(self, location: str):
        try:
            if not self.api_key:
                raise Exception("Missing API key")

            lat, lon = self._get_coordinates(location)

            if not lat or not lon:
                raise Exception("Invalid coordinates")

            places = self._get_places(lat, lon)

            if not places:
                raise Exception("No places found")

            return self._format_activities(places)

        except Exception as e:
            logger.error(f"Activity API failed: {e}")
            return self._fallback(location)

# ─────────────────────────── Helper ─────────────────────────────

_agent = None

def get_activities(location):
    global _agent

    if _agent is None:
        _agent = ActivityAgent()

    return _agent.get_activities(location)