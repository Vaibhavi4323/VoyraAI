from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uvicorn

from orchestrator import run_trip_pipeline

app = FastAPI(
    title="VoyraAI - AI Travel Planner",
    description="Generate personalized travel itineraries powered by Local LLM (Ollama)",
    version="3.0.0"
)

# ✅ CORS (correct)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request Model ---
class TripRequest(BaseModel):
    destination: str = Field(..., min_length=2)
    days: int = Field(..., gt=0, le=30)
    budget: Optional[str] = "budget"
    interests: Optional[list[str]] = []

# --- Response Model ---
class TripResponse(BaseModel):
    success: bool
    destination: str
    days: int
    budget: str
    interests: list[str]

    itinerary: Optional[Any] = None

    error: Optional[str] = None
    budget_breakdown: Optional[dict] = None

    # ✅ Existing
    flights: Optional[list] = None
    hotels: Optional[list] = None

    # 🔥 NEW: activities
    activities: Optional[list] = None


# --- Routes ---

@app.get("/")
def home():
    return {
        "message": "VoyraAI backend is running 🚀",
        "version": "3.0.0",
        "status": "healthy"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "VoyraAI"}

@app.post("/plan-trip", response_model=TripResponse)
def plan_trip(data: TripRequest = Body(...)):
    try:
        result = run_trip_pipeline(
            destination=data.destination,
            days=data.days,
            budget=data.budget,
            interests=data.interests
        )

        # ✅ Handle pipeline failure
        if not result.get("success"):
            return {
                "success": False,
                "destination": data.destination,
                "days": data.days,
                "budget": data.budget,
                "interests": data.interests,
                "itinerary": None,
                "budget_breakdown": None,
                "flights": [],
                "hotels": [],
                "activities": [],  # ✅ ADDED
                "error": result.get("error", "Pipeline failed")
            }

        return {
            "success": True,
            "destination": data.destination,
            "days": data.days,
            "budget": data.budget,
            "interests": data.interests,
            "itinerary": result.get("itinerary"),
            "budget_breakdown": result.get("budget_breakdown"),

            # ✅ Existing
            "flights": result.get("flights", []),
            "hotels": result.get("hotels", []),

            # 🔥 NEW
            "activities": result.get("activities", [])
        }

    except Exception as e:
        print("ERROR:", str(e))

        return {
            "success": False,
            "destination": data.destination,
            "days": data.days,
            "budget": data.budget,
            "interests": data.interests,
            "itinerary": None,
            "budget_breakdown": None,
            "flights": [],
            "hotels": [],
            "activities": [],  # ✅ ADDED
            "error": str(e)
        }