from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "VoyraAI backend is running 🚀"}

@app.post("/plan-trip")
def plan_trip(data: dict):
    destination = data.get("destination")
    days = data.get("days")

    return {
        "itinerary": f"Sample itinerary for {days} days in {destination}"
    }