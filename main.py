import os
import traceback
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from ai_engine import (
    SerpApiSearchEngine,
    SearchEngineError
)

from ranking import (
    rank_hotels,
    rank_local_places,
    rank_transport,
    pick_distinct_days
)


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    BASE_DIR / ".env"
)


app = FastAPI(
    title="VoyageAI - SerpApi Travel Searcher",
    version="6.0.0"
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            BASE_DIR / "static"
        )
    ),
    name="static"
)


class TripRequest(BaseModel):

    origin: str = Field(
        min_length=2
    )

    destination: str = Field(
        min_length=2
    )

    start_date: str

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
        ge=0,
        le=17
    )

    rooms_count: int = Field(
        default=1,
        ge=1,
        le=8
    )

    transport_mode: str = "Bus"

    budget_type: str = (
        "cheapest_best"
    )

    budget_amount_try: Optional[
        float
    ] = None

    hotel_min_rating: float = Field(
        default=8.0,
        ge=0,
        le=10
    )

    hotel_location: str = (
        "city_center"
    )

    amenities: List[str] = Field(
        default_factory=list
    )

    meal_board: str = (
        "breakfast_only"
    )

    special_notes: str = ""

    language: str = "tr"


@app.exception_handler(
    RequestValidationError
)
async def validation_error(
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
            )
        }
    )


@app.get("/")
async def index():

    return FileResponse(
        BASE_DIR
        / "templates"
        / "index.html"
    )


@app.get("/api/health")
async def health():

    key = os.getenv(
        "SERPAPI_KEY",
        ""
    ).strip()

    return {
        "success": True,
        "serpapi_key_configured":
            bool(
                key
                and key != "serpapi"
            ),
        "serpapi_key_prefix":
            key[:5]
            if key
            else None,
        "search_provider":
            "SerpApi",
        "gemini_required":
            False,
        "free_plan":
            "250 searches/month, 50/hour"
    }


@app.post("/api/plan-trip")
async def plan_trip(
    payload: TripRequest
):

    if (
        payload.origin.casefold()
        ==
        payload.destination.casefold()
    ):

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error":
                    "Departure and destination "
                    "must be different."
            }
        )

    try:

        check_in = date.fromisoformat(
            payload.start_date
        )

    except ValueError:

        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error":
                    "Invalid start date."
            }
        )

    check_out = (
        check_in
        + timedelta(
            days=payload.nights
        )
    )

    engine = (
        SerpApiSearchEngine()
    )

    # =========================================================
    # 1. HOTELS
    # =========================================================

    children_ages = []

    if (
        payload.children_count > 0
        and payload.child_age is not None
    ):

        children_ages = [
            payload.child_age
            for _ in range(
                payload.children_count
            )
        ]

    try:

        raw_hotels = (
            engine.search_hotels(
                destination=
                    payload.destination,

                check_in=
                    check_in.isoformat(),

                check_out=
                    check_out.isoformat(),

                adults=
                    payload.adults_count,

                children=
                    payload.children_count,

                children_ages=
                    children_ages,

                rooms=
                    payload.rooms_count,

                min_rating=
                    payload.hotel_min_rating,

                location_preference=
                    payload.hotel_location,

                amenities=
                    payload.amenities
            )
        )

        ranked_hotels = (
            rank_hotels(
                raw_hotels,
                payload.hotel_min_rating,
                payload.amenities
            )
        )

    except SearchEngineError as exc:

        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "error": str(exc)
            }
        )

    # =========================================================
    # 2. RESTAURANTS
    # =========================================================

    try:

        raw_restaurants = (
            engine.search_restaurants(
                payload.destination,
                payload.special_notes
            )
        )

        ranked_restaurants = (
            rank_local_places(
                raw_restaurants
            )
        )

    except SearchEngineError as exc:

        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "error": str(exc)
            }
        )

    # =========================================================
    # 3. ATTRACTIONS
    # =========================================================

    try:

        raw_places = (
            engine.search_attractions(
                payload.destination
            )
        )

        ranked_places = (
            rank_local_places(
                raw_places
            )
        )

    except SearchEngineError as exc:

        return JSONResponse(
            status_code=502,
            content={
                "success": False,
                "error": str(exc)
            }
        )

    # =========================================================
    # 4. TRANSPORT
    # =========================================================

    if payload.transport_mode in {
        "Own Car",
        "Own EV"
    }:

        transport_ranked = []

    else:

        try:

            raw_transport = (
                engine.search_transport(
                    payload.origin,
                    payload.destination,
                    payload.start_date,
                    payload.transport_mode
                )
            )

            transport_ranked = (
                rank_transport(
                    raw_transport
                )
            )

        except SearchEngineError as exc:

            return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "error": str(exc)
                }
            )

    # =========================================================
    # HOTEL
    # =========================================================

    if ranked_hotels:

        selected_hotel = (
            ranked_hotels[0]
        )

    else:

        selected_hotel = None

    # =========================================================
    # TRANSPORT
    # =========================================================

    selected_transport = (
        transport_ranked[0]
        if transport_ranked
        else None
    )

    # =========================================================
    # DAILY DISTINCT PLACES
    # =========================================================

    day_pairs = (
        pick_distinct_days(
            ranked_places,
            ranked_restaurants,
            payload.nights
        )
    )

    daily_schedule = []

    for day_number, (
        places,
        restaurants
    ) in enumerate(
        day_pairs,
        start=1
    ):

        calendar_date = (
            check_in
            + timedelta(
                days=day_number - 1
            )
        ).isoformat()

        activities = []

        for index, place in enumerate(
            places
        ):

            activities.append({
                "time_slot":
                    (
                        "10:00"
                        if index == 0
                        else "15:00"
                    ),

                "place_name":
                    place.get(
                        "name",
                        ""
                    ),

                "category":
                    place.get(
                        "type",
                        ""
                    ),

                "address":
                    place.get(
                        "address",
                        ""
                    ),

                "rating":
                    place.get(
                        "rating"
                    ),

                "reviews":
                    place.get(
                        "reviews"
                    ),

                "map_url":
                    place.get(
                        "place_link"
                    )
                    or (
                        "https://www.google.com/maps/search/?api=1&query="
                        + str(
                            place.get(
                                "name",
                                ""
                            )
                        ).replace(
                            " ",
                            "+"
                        )
                        + "+"
                        + payload.destination.replace(
                            " ",
                            "+"
                        )
                    ),

                "source_url":
                    place.get(
                        "place_link"
                    ),

                "verified":
                    True
            })

        restaurant_data = []

        for restaurant in restaurants:

            restaurant_data.append({
                "meal_type":
                    "Lunch",

                "restaurant_name":
                    restaurant.get(
                        "name",
                        ""
                    ),

                "cuisine":
                    restaurant.get(
                        "type",
                        ""
                    ),

                "rating":
                    restaurant.get(
                        "rating"
                    ),

                "reviews":
                    restaurant.get(
                        "reviews"
                    ),

                "price":
                    restaurant.get(
                        "price"
                    ),

                "address":
                    restaurant.get(
                        "address",
                        ""
                    ),

                "map_url":
                    restaurant.get(
                        "place_link"
                    ),

                "source_url":
                    restaurant.get(
                        "place_link"
                    ),

                "verified":
                    True
            })

        daily_schedule.append({
            "day_number":
                day_number,

            "calendar_date":
                calendar_date,

            "day_title":
                f"Day {day_number} in "
                f"{payload.destination}",

            "breakfast_banner":
                (
                    "Breakfast at the hotel "
                    "according to the selected "
                    "meal plan."
                ),

            "lunch_banner":
                (
                    "Recommended restaurant "
                    "selected from ranked "
                    "live local results."
                ),

            "dinner_banner":
                (
                    "Dinner according to "
                    "the selected meal plan."
                ),

            "activities":
                activities,

            "restaurants":
                restaurant_data
        })

    # =========================================================
    # HOTEL RESPONSE
    # =========================================================

    if selected_hotel:

        hotel_response = {

            "name":
                selected_hotel[
                    "name"
                ],

            "stars":
                selected_hotel.get(
                    "stars"
                ),

            "rating":
                selected_hotel.get(
                    "rating"
                ),

            "reviews":
                selected_hotel.get(
                    "reviews"
                ),

            "price_per_room_per_night":
                selected_hotel.get(
                    "price_per_night_try"
                ),

            "total_hotel_cost":
                selected_hotel.get(
                    "total_price_try"
                ),

            "amenities":
                selected_hotel.get(
                    "amenities",
                    []
                ),

            "address":
                selected_hotel.get(
                    "address"
                ),

            "link":
                selected_hotel.get(
                    "link"
                ),

            "source":
                "Google Hotels via SerpApi",

            "ranking_score":
                selected_hotel.get(
                    "ranking_score"
                ),

            "verified":
                True
        }

    else:

        hotel_response = {
            "verified": False,
            "name": "",
            "warning":
                (
                    "No hotel matched the "
                    "selected criteria."
                )
        }

    # =========================================================
    # TRANSPORT RESPONSE
    # =========================================================

    if selected_transport:

        transport_response = {

            "mode":
                payload.transport_mode,

            "company":
                selected_transport.get(
                    "company"
                ),

            "title":
                selected_transport.get(
                    "title"
                ),

            "snippet":
                selected_transport.get(
                    "snippet"
                ),

            "price_try":
                selected_transport.get(
                    "price_try"
                ),

            "link":
                selected_transport.get(
                    "link"
                ),

            "ranking_score":
                selected_transport.get(
                    "ranking_score"
                ),

            "verified":
                True,

            "warning":
                (
                    ""
                    if selected_transport.get(
                        "price_try"
                    ) is not None
                    else
                    "The operator was found, "
                    "but a verified current "
                    "ticket price was not found."
                )
        }

    else:

        transport_response = {

            "mode":
                payload.transport_mode,

            "verified":
                False,

            "company":
                "",

            "price_try":
                None,

            "warning":
                (
                    "No reliable transport "
                    "company result was found "
                    "for this route."
                )
        }

    # =========================================================
    # WARNINGS
    # =========================================================

    warnings = []

    if not ranked_hotels:

        warnings.append(
            "No hotel matched the selected "
            "rating and amenity criteria."
        )

    elif selected_hotel.get(
        "total_price_try"
    ) is None:

        warnings.append(
            "The selected hotel has no "
            "verified total price from "
            "the current hotel result."
        )

    if not transport_ranked and payload.transport_mode not in {
        "Own Car",
        "Own EV"
    }:

        warnings.append(
            "Transport company information "
            "could not be reliably verified."
        )

    if len(
        ranked_places
    ) < payload.nights * 2:

        warnings.append(
            "There were not enough distinct "
            "ranked attractions for every day."
        )

    if len(
        ranked_restaurants
    ) < payload.nights:

        warnings.append(
            "There were not enough distinct "
            "ranked restaurants for every day."
        )

    # =========================================================
    # TOTAL
    # =========================================================

    hotel_total = (
        selected_hotel.get(
            "total_price_try"
        )
        if selected_hotel
        else None
    )

    transport_total = (
        selected_transport.get(
            "price_try"
        )
        if selected_transport
        else None
    )

    grand_total = None

    if (
        hotel_total is not None
        or transport_total is not None
    ):

        grand_total = sum(
            x
            for x in [
                hotel_total,
                transport_total
            ]
            if x is not None
        )

    # =========================================================
    # SOURCES
    # =========================================================

    sources = []

    if selected_hotel:

        if selected_hotel.get(
            "link"
        ):
            sources.append({
                "title":
                    selected_hotel[
                        "name"
                    ],

                "url":
                    selected_hotel[
                        "link"
                    ]
            })

    for place in ranked_places[:10]:

        if place.get(
            "place_link"
        ):

            sources.append({
                "title":
                    place.get(
                        "name",
                        "Place"
                    ),

                "url":
                    place[
                        "place_link"
                    ]
            })

    for restaurant in ranked_restaurants[:10]:

        if restaurant.get(
            "place_link"
        ):

            sources.append({
                "title":
                    restaurant.get(
                        "name",
                        "Restaurant"
                    ),

                "url":
                    restaurant[
                        "place_link"
                    ]
            })

    if selected_transport and selected_transport.get(
        "link"
    ):

        sources.append({
            "title":
                selected_transport.get(
                    "company",
                    "Transport"
                ),

            "url":
                selected_transport[
                    "link"
                ]
        })

    response = {

        "destination_city":
            payload.destination,

        "origin_city":
            payload.origin,

        "adults_count":
            payload.adults_count,

        "children_count":
            payload.children_count,

        "rooms_count":
            payload.rooms_count,

        "total_travelers":
            (
                payload.adults_count
                + payload.children_count
            ),

        "meal_board":
            payload.meal_board,

        "start_date":
            payload.start_date,

        "end_date":
            check_out.isoformat(),

        "grand_total_trip_cost_try":
            grand_total,

        "hotel":
            hotel_response,

        "transportation":
            transport_response,

        "daily_schedule":
            daily_schedule,

        "departure_day_buffer":
            {
                "departure_mode":
                    payload.transport_mode,

                "checkout_time":
                    "12:00",

                "return_departure_time":
                    "",

                "arrival_at_home_time":
                    "",

                "why": {
                    "title":
                        "Return planning",
                    "explanation":
                        (
                            "Exact return time is "
                            "only shown when a reliable "
                            "transport result provides it."
                        ),
                    "score_metrics":
                        []
                }
            },

        "cost_breakdown":
            {
                "hotel_total_try":
                    hotel_total,

                "transport_total_try":
                    transport_total,

                "food_budget_total_try":
                    None,

                "activities_and_transfers_try":
                    None,

                "grand_total_try":
                    grand_total
            },

        "sources":
            sources,

        "data_warnings":
            warnings
    }

    return JSONResponse(
        content={
            "success": True,
            "data": response
        }
    )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )