# backend/hotel_agent.py

from __future__ import annotations

import hashlib
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import date
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
logger = logging.getLogger("hotel_agent")

# ─────────────────────────── City → IATA Mapping ─────────────────

CITY_TO_CODE = {
    "delhi": "DEL",
    "mumbai": "BOM",
    "goa": "GOI",
    "bangalore": "BLR",
    "hyderabad": "HYD",
    "chennai": "MAA",
    "kolkata": "CCU"
}

def _normalize_location(loc: str) -> str:
    loc = loc.strip().lower()
    return CITY_TO_CODE.get(loc, loc.upper())

# ─────────────────────────── Exceptions ─────────────────────────

class HotelAgentError(Exception): pass
class ValidationError(HotelAgentError): pass
class APIError(HotelAgentError): pass
class NoHotelsFoundError(HotelAgentError): pass

# ─────────────────────────── Helpers ────────────────────────────

def _validate(city_code: str, check_in: str, check_out: str):
    if len(city_code) != 3:
        raise ValidationError("Invalid city IATA code")

    try:
        ci = date.fromisoformat(check_in)
        co = date.fromisoformat(check_out)
        if ci >= co:
            raise ValidationError("Check-out must be after check-in")
    except:
        raise ValidationError("Invalid date format (YYYY-MM-DD required)")

# ─────────────────────────── Data Model ─────────────────────────

@dataclass
class HotelOffer:
    hotel_id: str
    hotel_name: str
    city_code: str
    price_total: float
    currency: str
    check_in: str
    check_out: str
    room_type: Optional[str]
    bed_type: Optional[str]

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

# ─────────────────────────── Agent ──────────────────────────────

class HotelAgent:

    def __init__(self):
        self.client = Client(
            client_id=os.getenv("AMADEUS_API_KEY"),
            client_secret=os.getenv("AMADEUS_API_SECRET")
        )
        self.cache = TTLCache()

    @with_retry()
    def _call_api(self, params):
        return self.client.shopping.hotel_offers.get(**params).data

    def search(
        self,
        city: str,
        check_in: str,
        check_out: str,
        adults: int = 1,
        max_results: int = 10,
        max_price: Optional[float] = None,
        sort_by: str = "price"
    ):
        city_code = _normalize_location(city)

        _validate(city_code, check_in, check_out)

        params = dict(
            cityCode=city_code,
            checkInDate=check_in,
            checkOutDate=check_out,
            adults=adults
        )

        cached = self.cache.get(params)
        if cached:
            return cached

        data = self._call_api(params)

        if not data:
            raise NoHotelsFoundError(f"No hotels found in {city}")

        hotels = []

        for hotel in data:
            try:
                offer = hotel["offers"][0]

                price = float(offer["price"]["total"])

                if max_price and price > max_price:
                    continue

                h = HotelOffer(
                    hotel_id=hotel["hotel"]["hotelId"],
                    hotel_name=hotel["hotel"]["name"],
                    city_code=city_code,
                    price_total=price,
                    currency=offer["price"]["currency"],
                    check_in=check_in,
                    check_out=check_out,
                    room_type=offer.get("room", {}).get("typeEstimated"),
                    bed_type=offer.get("room", {}).get("bedType")
                )

                hotels.append(h)

                if len(hotels) >= max_results:
                    break

            except Exception:
                continue

        if sort_by == "price":
            hotels.sort(key=lambda x: x.price_total)

        self.cache.set(params, hotels)

        return hotels

# ─────────────────────────── Helper ─────────────────────────────

_agent = None

def get_hotels(city, check_in, check_out, **kwargs):
    global _agent
    if _agent is None:
        _agent = HotelAgent()

    hotels = _agent.search(city, check_in, check_out, **kwargs)

    return [h.to_dict() for h in hotels]