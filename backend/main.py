from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
from planner_agent import generate_itinerary

app = FastAPI(
    title="VoyraAI - AI Travel Planner",
    description="Generate personalized travel itineraries powered by GPT-4",
    version="2.0.0"
)

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request & Response Models ---

class TripRequest(BaseModel):
    destination: str = Field(..., min_length=2, description="Travel destination")
    days: int = Field(..., gt=0, le=30, description="Number of days (1–30)")
    budget: Optional[str] = Field("budget", description="budget | mid-range | luxury")
    interests: Optional[list[str]] = Field(default_factory=list, description="List of interests")

    class Config:
        json_schema_extra = {
            "example": {
                "destination": "Bali, Indonesia",
                "days": 5,
                "budget": "budget",
                "interests": ["beaches", "temples", "food"]
            }
        }

class TripResponse(BaseModel):
    success: bool
    destination: str
    days: int
    budget: str
    interests: list[str]
    itinerary: Optional[str] = None
    tokens_used: Optional[int] = None
    model: Optional[str] = None
    error: Optional[str] = None


# --- Routes ---

@app.get("/")
def home():
    return {"message": "VoyraAI backend is running 🚀", "version": "2.0.0", "status": "healthy"}


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "VoyraAI"}


@app.post("/plan-trip", response_model=TripResponse)
def plan_trip(data: TripRequest = Body(...)):
    """
    Generate a personalized travel itinerary.
    
    - **destination**: Where you want to travel
    - **days**: How many days (1–30)
    - **budget**: budget / mid-range / luxury
    - **interests**: Your travel interests (food, hiking, history, etc.)
    """

    # Validate budget value
    valid_budgets = ["budget", "mid-range", "luxury"]
    if data.budget not in valid_budgets:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid budget. Choose from: {', '.join(valid_budgets)}"
        )

    result = generate_itinerary(
        destination=data.destination,
        days=data.days,
        budget=data.budget,
        interests=data.interests
    )

    if not result["success"]:
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "Failed to generate itinerary")
        )

    return TripResponse(**result)


@app.get("/sample-destinations")
def sample_destinations():
    """Returns sample destinations to help users get started."""
    return {
        "popular": [
            {"name": "Bali, Indonesia", "best_for": "beaches, culture, budget travel"},
            {"name": "Bangkok, Thailand", "best_for": "street food, temples, nightlife"},
            {"name": "Prague, Czech Republic", "best_for": "history, architecture, budget Europe"},
            {"name": "Lisbon, Portugal", "best_for": "food, coastal views, affordable Europe"},
            {"name": "Kyoto, Japan", "best_for": "temples, culture, nature"},
        ]
    }


# --- Run server ---
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)