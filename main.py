import os
import traceback
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict

from ai_engine import TravelAIEngine, TravelAIError

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="VoyageAI Live Travel Searcher", version="4.0.0")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


class TripRequestPayload(BaseModel):
    model_config = ConfigDict(extra="ignore")

    origin: str = Field(min_length=2)
    destination: str = Field(min_length=2)
    start_date: str = Field(min_length=10)
    nights: int = Field(default=3, ge=1, le=30)
    adults_count: int = Field(default=2, ge=1, le=15)
    children_count: int = Field(default=0, ge=0, le=8)
    child_age: Optional[int] = Field(default=None, ge=0, le=17)
    rooms_count: int = Field(default=1, ge=1, le=8)
    transport_mode: str = "Bus"
    budget_type: str = "cheapest_best"
    budget_amount_try: Optional[float] = Field(default=None, gt=0)
    hotel_min_rating: float = Field(default=8.0, ge=0, le=10)
    hotel_location: str = "city_center"
    amenities: List[str] = Field(default_factory=list)
    meal_board: str = "breakfast_only"
    special_notes: str = ""
    language: str = "tr"



@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first = exc.errors()[0]
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": f"Invalid input: {first.get('loc')} — {first.get('msg')}",
        },
    )


@app.get("/")
async def serve_index():
    return FileResponse(BASE_DIR / "templates" / "index.html")


@app.get("/api/health")
async def health():
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return {
        "success": True,
        "gemini_key_configured": bool(key),
        "gemini_key_prefix": key[:3] if key else None,
        "model": os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
    }

@app.post("/api/plan-trip")
async def plan_trip(payload: TripRequestPayload):
    if payload.origin.strip().casefold() == payload.destination.strip().casefold():
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Departure and destination cities must be different."},
        )

    if payload.children_count > 0 and payload.child_age is None:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": "Child age is required when at least one child is traveling."},
        )

    try:
        engine = TravelAIEngine()
        plan = engine.generate_plan(payload.model_dump())
        return JSONResponse(content={"success": True, "data": plan})
    except TravelAIError as exc:
        status = 401 if "API key" in str(exc) or "401" in str(exc) else 502
        return JSONResponse(status_code=status, content={"success": False, "error": str(exc)})
    except Exception as exc:
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"success": False, "error": str(exc)})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
