from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import date
from typing import Optional

import requests
from dotenv import load_dotenv
load_dotenv(dotenv_path="backend/.env")

load_dotenv()

# ─────────────────────────── Logging ────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("flight_agent")

# ─────────────────────────── City → IATA Mapping ─────────────────

CITY_TO_AIRPORT = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "goa": "GOI",
    "bangalore": "BLR",
    "hyderabad": "HYD",
    "chennai": "MAA",
    "kolkata": "CCU"
}

# ─────────────────────────── Exceptions ─────────────────────────

class FlightAgentError(Exception): pass
class ValidationError(FlightAgentError): pass
class APIError(FlightAgentError): pass
class NoFlightsFoundError(FlightAgentError): pass

# ─────────────────────────── Helpers ────────────────────────────

def _normalize_location(loc: str) -> str:
    loc = loc.strip().lower()
    return CITY_TO_AIRPORT.get(loc, loc.upper())

# ─────────────────────────── Data Model ─────────────────────────

@dataclass
class Flight:
    airline: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    status: str

    def to_dict(self):
        return asdict(self)

# ─────────────────────────── Cache ──────────────────────────────

class TTLCache:
    def __init__(self, ttl=300):
        self.store = {}
        self.ttl = ttl

    def _key(self, params):
        return hashlib.sha256(
            repr(sorted(params.items())).encode()
        ).hexdigest()

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

# ─────────────────────────── Validation ─────────────────────────

def _validate(origin, destination, departure_date):
    if origin == destination:
        raise ValidationError("Origin and destination cannot be same")

    try:
        dep = date.fromisoformat(departure_date)
        if dep < date.today():
            raise ValidationError("Date must be future")
    except:
        raise ValidationError("Invalid date format")

# ─────────────────────────── Agent ──────────────────────────────

class FlightAgent:

    BASE_URL = "http://api.aviationstack.com/v1/flights"

    def __init__(self):
        self.api_key = os.getenv("AVIATIONSTACK_API_KEY")
        print("AVIATION KEY:", self.api_key)
        if not self.api_key:
            raise ValueError("AVIATIONSTACK_API_KEY not set")

        self.cache = TTLCache()

    def _call_api(self, params):
        try:
            response = requests.get(self.BASE_URL, params=params)

            # 🔍 DEBUG LOGS
            print("\n===== AVIATIONSTACK DEBUG =====")
            print("URL:", response.url)
            print("STATUS:", response.status_code)
            print("RESPONSE:", response.text[:500])
            print("================================\n")

            data = response.json()

            if "error" in data:
                raise APIError(data["error"])

            return data.get("data", [])

        except Exception as e:
            raise APIError(e)

    def search(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        max_results: int = 10,
    ):

        origin = _normalize_location(origin)
        destination = _normalize_location(destination)

        _validate(origin, destination, departure_date)

        # ❌ Removed flight_date (free plan issue)
        params = {
            "access_key": self.api_key
        }

        cached = self.cache.get(params)
        if cached:
            return cached

        data = self._call_api(params)

        if not data:
            raise NoFlightsFoundError("No flights returned from API")

        # ✅ Manual filtering (IMPORTANT)
        filtered = [
            f for f in data
            if f.get("departure", {}).get("iata") == origin
            and f.get("arrival", {}).get("iata") == destination
        ]

        if not filtered:
            raise NoFlightsFoundError("No matching flights found")

        flights = []

        for f in filtered[:max_results]:
            try:
                flight = Flight(
                    airline=f.get("airline", {}).get("name", "Unknown"),
                    flight_number=f.get("flight", {}).get("iata", "N/A"),
                    departure_airport=f.get("departure", {}).get("iata", "N/A"),
                    arrival_airport=f.get("arrival", {}).get("iata", "N/A"),
                    departure_time=f.get("departure", {}).get("scheduled", "N/A"),
                    arrival_time=f.get("arrival", {}).get("scheduled", "N/A"),
                    status=f.get("flight_status", "unknown")
                )
                flights.append(flight)

            except Exception as e:
                logger.warning(f"Skipping invalid flight data: {e}")
                continue

        if not flights:
            raise NoFlightsFoundError("No valid flights after parsing")

        self.cache.set(params, flights)

        return flights

# ─────────────────────────── Helper ─────────────────────────────

_agent = None

def get_flights(origin, destination, date, **kwargs):
    global _agent
    if _agent is None:
        _agent = FlightAgent()

    flights = _agent.search(origin, destination, date, **kwargs)

    return [f.to_dict() for f in flights]