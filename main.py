import os
import traceback
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ai_engine import HybridEngine, AIPlanError
from search_engine import SearchError


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


app = FastAPI(
    title="VoyageAI Hybrid Travel Planner",
    version="7.0.0"
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(BASE_DIR / "static")
    ),
    name="static",
)


class TripRequest(BaseModel):

    origin: str = Field(
        min_length=2
    )

    destination: str = Field(
        min_length=2
    )

    start_date: str = Field(
        min_length=10
    )

    nights: int = Field(
        default=3,
        ge=1,
        le=20
    )

    adults_count: int = Field(
        default=2,
        ge=1,
        le=15
    )

    children_count: int = Field(
        default=0,
        ge=0,
        le=8
    )

    child_age: Optional[int] = Field(
        default=None,
        ge=1,
        le=17
    )

    rooms_count: int = Field(
        default=1,
        ge=1,
        le=8
    )

    transport_mode: str = "Bus"

    budget_type: str = "cheapest_best"

    budget_amount_try: Optional[float] = None

    hotel_min_rating: float = Field(
        default=8.0,
        ge=0,
        le=10
    )

    hotel_location: str = "city_center"

    amenities: List[str] = Field(
        default_factory=list
    )

    meal_board: str = "breakfast_only"

    special_notes: str = ""

    language: str = "tr"


@app.exception_handler(
    RequestValidationError
)
async def validation_handler(
    request: Request,
    exc: RequestValidationError
):

    error = exc.errors()[0]

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": (
                f"{error.get('loc')} — "
                f"{error.get('msg')}"
            ),
        },
    )


@app.get("/")
async def home():

    return FileResponse(
        BASE_DIR
        / "templates"
        / "index.html"
    )


@app.get("/api/health")
async def health():

    serp_key = os.getenv(
        "SERPAPI_KEY",
        ""
    ).strip()

    gemini_key = os.getenv(
        "GEMINI_API_KEY",
        ""
    ).strip()

    return {
        "success": True,

        "serpapi_configured": bool(
            serp_key
            and serp_key != "serpapi"
        ),

        "gemini_configured": bool(
            gemini_key
            and gemini_key != "gemini"
        ),

        "gemini_model": os.getenv(
            "GEMINI_MODEL",
            "gemini-3.6-flash"
        ),

        "mode":
            "hybrid-free-no-grounding",

        "gemini_grounding":
            False,
    }


@app.post("/api/plan-trip")
async def plan_trip(
    payload: TripRequest
):

    if (
        payload.origin.strip().casefold()
        ==
        payload.destination.strip().casefold()
    ):

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error":
                    (
                        "Departure and destination "
                        "must be different."
                    ),
            },
        )

    try:

        result = HybridEngine().plan(
            payload.model_dump()
        )

        return {
            "success": True,
            "data": result,
        }

    except (
        SearchError,
        AIPlanError
    ) as exc:

        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "error": str(exc),
            },
        )

    except Exception as exc:

        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(exc),
            },
        )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )