from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

# ✅ NEW: Use orchestrator instead of individual agents
from orchestrator import run_trip_pipeline

app = FastAPI(
    title="VoyraAI - AI Travel Planner",
    description="Generate personalized travel itineraries powered by Local LLM (Ollama)",
    version="3.0.0"
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
    error: Optional[str] = None
    budget_breakdown: Optional[dict] = None  


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
    """
    Generate a personalized travel itinerary using multi-agent pipeline.
    """

