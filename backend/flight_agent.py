# backend/flight_agent.py

from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from functools import wraps
from typing import Optional

from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────── Logging ────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("flight_agent")

# ─────────────────────────── Airline Mapping ─────────────────────

AIRLINE_MAP = {
    "AI": "Air India",
    "6E": "IndiGo",
    "SG": "SpiceJet",
    "UK": "Vistara",
    "G8": "Go First"
}

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

def _duration_to_minutes(duration: str) -> int:
    hours, minutes = 0, 0
    if "H" in duration:
        hours = int(duration.split("T")[1].split("H")[0])
    if "M" in duration:
        minutes = int(duration.split("H")[-1].replace("M", ""))
    return hours * 60 + minutes


def _normalize_location(loc: str) -> str:
    loc = loc.strip().lower()
    return CITY_TO_AIRPORT.get(loc, loc.upper())

# ─────────────────────────── Data Models ────────────────────────

@dataclass
class Segment:
    carrier_code: str
    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str
    aircraft: Optional[str] = None

    @property
    def departure_dt(self):
        return datetime.fromisoformat(self.departure_time)

    @property
    def arrival_dt(self):
        return datetime.fromisoformat(self.arrival_time)


@dataclass
class FlightOffer:
    offer_id: str
    airline: str
    departure_airport: str
    arrival_airport: str
    departure_time: str
    arrival_time: str
    duration: str
    stops: int
    total_price: float
    price_per_person: float
    currency: str
    cabin_class: str
    seats_available: Optional[int]
    segments: list[Segment] = field(default_factory=list)

    @property
    def is_direct(self):
        return self.stops == 0

    def to_dict(self):
        d = asdict(self)
        d["is_direct"] = self.is_direct
        return d

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

# ─────────────────────────── Retry ──────────────────────────────

def with_retry(max_attempts=3):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            delay = 1
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except ResponseError as e:
                    status = getattr(e.response, "status_code", None)

                    if status == 429:
                        logger.warning("Rate limit hit, retrying...")
                    elif status and 400 <= status < 500:
                        raise APIError(e)

                    if attempt == max_attempts - 1:
                        raise APIError(e)

                    time.sleep(delay)
                    delay *= 2
        return wrapper
    return decorator

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

    def __init__(self):
        self.client = Client(
            client_id=os.getenv("AMADEUS_API_KEY"),
            client_secret=os.getenv("AMADEUS_API_SECRET")
        )
        self.cache = TTLCache()

    @with_retry()
    def _call_api(self, params):
        return self.client.shopping.flight_offers_search.get(**params).data

    def search(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        adults: int = 1,
        max_results: int = 10,
        sort_by: str = "price",
        max_price: Optional[float] = None,
        non_stop_only: bool = False
    ):

        origin = _normalize_location(origin)
        destination = _normalize_location(destination)

        _validate(origin, destination, departure_date)

        params = dict(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=departure_date,
            adults=adults,
            max=max_results
        )

        cached = self.cache.get(params)
        if cached:
            return cached

        data = self._call_api(params)

        if not data:
            raise NoFlightsFoundError("No flights found")

        flights = []

        for offer in data:
            itinerary = offer["itineraries"][0]
            segs = itinerary["segments"]

            first, last = segs[0], segs[-1]

            airline_code = first["carrierCode"]

            price = float(offer["price"]["total"])

            flight = FlightOffer(
                offer_id=offer["id"],
                airline=AIRLINE_MAP.get(airline_code, airline_code),
                departure_airport=first["departure"]["iataCode"],
                arrival_airport=last["arrival"]["iataCode"],
                departure_time=first["departure"]["at"],
                arrival_time=last["arrival"]["at"],
                duration=itinerary["duration"],
                stops=len(segs) - 1,
                total_price=price,
                price_per_person=price / adults,
                currency=offer["price"]["currency"],
                cabin_class="ECONOMY",
                seats_available=offer.get("numberOfBookableSeats"),
                segments=[]
            )

            if non_stop_only and flight.stops > 0:
                continue

            if max_price and flight.total_price > max_price:
                continue

            flights.append(flight)

        if sort_by == "price":
            flights.sort(key=lambda x: x.total_price)
        elif sort_by == "duration":
            flights.sort(key=lambda x: _duration_to_minutes(x.duration))
        elif sort_by == "stops":
            flights.sort(key=lambda x: x.stops)

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