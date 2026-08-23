import json
import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, ConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"


class TravelAIError(Exception):
    pass


class Source(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = ""
    url: str
    type: str = "web"


class BookingLink(BaseModel):
    model_config = ConfigDict(extra="ignore")
    provider_name: str
    url: str
    kind: str = "source"
    exact_parameters_supported: bool = False


class WhyReason(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str = ""
    explanation: str = ""
    score_metrics: List[str] = Field(default_factory=list)


class HotelItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: str
    stars: Optional[int] = None
    aggregated_rating_10: Optional[float] = None
    reviews_count: Optional[int] = None
    total_hotel_cost_try: Optional[float] = None
    price_per_room_per_night_try: Optional[float] = None
    meal_board_type: str = ""
    distance_to_center_km: Optional[float] = None
    location_tag: str = ""
    has_private_beach: bool = False
    has_aquapark: bool = False
    has_pool: bool = False
    has_spa: bool = False
    address: str = ""
    booking_links: List[BookingLink] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    why: WhyReason = Field(default_factory=WhyReason)
    verified: bool = False


class TransportItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    mode: str
    is_feasible: bool = False
    feasibility_warning: Optional[str] = None
    carrier_summary: str = ""
    departure_time: str = ""
    arrival_time: str = ""
    origin_terminal: str = ""
    destination_terminal: str = ""
    duration: str = ""
    cost_per_adult_try: Optional[float] = None
    cost_per_child_try: Optional[float] = None
    total_transport_cost_try: Optional[float] = None
    booking_links: List[BookingLink] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    why: WhyReason = Field(default_factory=WhyReason)
    verified: bool = False


class ActivityItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    time_slot: str
    place_name: str
    category: str = ""
    address: str = ""
    distance_from_hotel_km: Optional[float] = None
    transport_mode: str = ""
    transport_cost_try: Optional[float] = None
    entry_ticket_adult_try: Optional[float] = None
    aggregated_rating_10: Optional[float] = None
    map_url: str = ""
    source_urls: List[str] = Field(default_factory=list)
    transit_card_tip: str = ""
    why: WhyReason = Field(default_factory=WhyReason)
    verified: bool = False


class RestaurantItem(BaseModel):
    model_config = ConfigDict(extra="ignore")
    meal_type: str
    restaurant_name: str
    cuisine: str = ""
    address: str = ""
    distance_from_hotel_km: Optional[float] = None
    estimated_cost_per_adult_try: Optional[float] = None
    estimated_cost_per_child_try: Optional[float] = None
    aggregated_rating_10: Optional[float] = None
    map_url: str = ""
    source_urls: List[str] = Field(default_factory=list)
    why: WhyReason = Field(default_factory=WhyReason)
    verified: bool = False


class DayPlan(BaseModel):
    model_config = ConfigDict(extra="ignore")
    day_number: int
    calendar_date: str
    day_title: str
    breakfast_banner: str = ""
    lunch_banner: str = ""
    dinner_banner: str = ""
    activities: List[ActivityItem] = Field(default_factory=list)
    restaurants: List[RestaurantItem] = Field(default_factory=list)


class DepartureDayBuffer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    departure_mode: str
    checkout_time: str = "12:00"
    lunch_spot_near_hub: Optional[RestaurantItem] = None
    time_spent_at_lunch: str = ""
    transit_time_to_hub_mins: int = 0
    required_safety_buffer_mins: int = 20
    return_departure_time: str = ""
    arrival_at_home_time: str = ""
    activities_before_departure: List[ActivityItem] = Field(default_factory=list)
    recommended_final_meal: Optional[RestaurantItem] = None
    distance_from_final_spot_to_terminal_km: Optional[float] = None
    transit_time_to_terminal_mins: Optional[int] = None
    why: WhyReason = Field(default_factory=WhyReason)


class TripCostBreakdown(BaseModel):
    model_config = ConfigDict(extra="ignore")
    hotel_total_try: Optional[float] = None
    transport_total_try: Optional[float] = None
    food_budget_total_try: Optional[float] = None
    activities_and_transfers_try: Optional[float] = None
    grand_total_try: Optional[float] = None


class TripPlanResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    destination_city: str
    origin_city: str
    adults_count: int
    children_count: int
    rooms_count: int
    total_travelers: int
    meal_board: str
    start_date: str
    end_date: str
    grand_total_trip_cost_try: Optional[float] = None
    transportation: TransportItem
    hotel: HotelItem
    daily_schedule: List[DayPlan]
    departure_day_buffer: DepartureDayBuffer
    cost_breakdown: TripCostBreakdown
    sources: List[Source] = Field(default_factory=list)
    data_warnings: List[str] = Field(default_factory=list)


class TravelAIEngine:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not self.gemini_key or self.gemini_key == "PASTE_YOUR_NEW_KEY_HERE":
            raise TravelAIError(
                "Gemini API key is not configured. Put your NEW key in .env as GEMINI_API_KEY=..."
            )

    def _request_gemini(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "model": GEMINI_MODEL,
            "input": prompt,
            "tools": [{"type": "google_search"}],
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": schema,
            },
            "generation_config": {
                "thinking_level": "medium",
            },
        }

        try:
            response = requests.post(
                GEMINI_ENDPOINT,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.gemini_key,
                },
                json=payload,
                timeout=180,
            )
        except requests.RequestException as exc:
            raise TravelAIError(f"Could not reach Gemini API: {exc}") from exc

        if response.status_code == 401:
            raise TravelAIError(
                "Gemini returned 401 Unauthorized. The key is invalid, revoked, or not authorized for this API. "
                "Create a fresh Gemini API key and put it in .env. The API uses the x-goog-api-key header."
            )
        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = response.text[:1000]
            raise TravelAIError(f"Gemini API error {response.status_code}: {detail}")

        try:
            body = response.json()
        except ValueError as exc:
            raise TravelAIError("Gemini returned a non-JSON response.") from exc

        text = self._extract_model_output_text(body)
        if not text:
            raise TravelAIError("Gemini returned no model output.")

        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            raise TravelAIError(f"Gemini returned invalid structured JSON: {exc}") from exc

        cited_urls = self._extract_citation_urls(body)
        self._attach_verified_citations(data, cited_urls)
        return data

    @staticmethod
    def _extract_model_output_text(body: Dict[str, Any]) -> str:
        for step in reversed(body.get("steps", [])):
            if step.get("type") != "model_output":
                continue
            for block in step.get("content", []):
                if block.get("type") == "text" and block.get("text"):
                    return block["text"].strip()
        return ""

    @staticmethod
    def _extract_citation_urls(body: Dict[str, Any]) -> List[Dict[str, str]]:
        results: List[Dict[str, str]] = []
        seen = set()
        for step in body.get("steps", []):
            if step.get("type") != "model_output":
                continue
            for block in step.get("content", []):
                for annotation in block.get("annotations", []) or []:
                    url = annotation.get("url")
                    title = annotation.get("title") or annotation.get("name") or "Source"
                    if url and url not in seen:
                        seen.add(url)
                        results.append({"url": url, "title": title})
        return results

    def _attach_verified_citations(self, data: Dict[str, Any], cited_urls: List[Dict[str, str]]) -> None:
        allowed = {x["url"]: x for x in cited_urls}
        data["sources"] = [
            {"url": x["url"], "title": x["title"], "type": "web"} for x in cited_urls
        ]

        def clean_link(link: Dict[str, Any]) -> Optional[Dict[str, Any]]:
            url = (link.get("url") or "").strip()
            if url not in allowed:
                return None
            link["url"] = url
            return link

        hotel = data.get("hotel") or {}
        hotel["booking_links"] = [
            cleaned for link in hotel.get("booking_links", [])
            if (cleaned := clean_link(link)) is not None
        ]
        hotel["sources"] = [
            {"url": u["url"], "title": allowed[u["url"]]["title"], "type": "web"}
            for u in hotel.get("sources", [])
            if u.get("url") in allowed
        ]
        hotel["verified"] = bool(hotel.get("name")) and bool(hotel["sources"])
        data["hotel"] = hotel

        transportation = data.get("transportation") or {}
        transportation["booking_links"] = [
            cleaned for link in transportation.get("booking_links", [])
            if (cleaned := clean_link(link)) is not None
        ]
        transportation["sources"] = [
            {"url": u["url"], "title": allowed[u["url"]]["title"], "type": "web"}
            for u in transportation.get("sources", [])
            if u.get("url") in allowed
        ]
        transportation["verified"] = bool(transportation.get("sources")) and bool(
            transportation.get("carrier_summary")
        )
        data["transportation"] = transportation

        for day in data.get("daily_schedule", []):
            for activity in day.get("activities", []):
                activity["source_urls"] = [u for u in activity.get("source_urls", []) if u in allowed]
                activity["map_url"] = self._maps_search_url(activity.get("place_name", ""), data.get("destination_city", ""))
                activity["verified"] = bool(activity.get("place_name")) and bool(activity["source_urls"])
            for restaurant in day.get("restaurants", []):
                restaurant["source_urls"] = [u for u in restaurant.get("source_urls", []) if u in allowed]
                restaurant["map_url"] = self._maps_search_url(restaurant.get("restaurant_name", ""), data.get("destination_city", ""))
                restaurant["verified"] = bool(restaurant.get("restaurant_name")) and bool(restaurant["source_urls"])

        data_warnings = list(data.get("data_warnings") or [])
        if not hotel.get("verified"):
            data_warnings.append("Hotel has no citation-verified source, so treat its details as unavailable.")
        if not transportation.get("verified"):
            data_warnings.append("Transportation has no citation-verified source, so treat its details as unavailable.")
        data["data_warnings"] = list(dict.fromkeys(data_warnings))

    @staticmethod
    def _maps_search_url(place: str, city: str) -> str:
        if not place:
            return ""
        query = quote(f"{place}, {city}")
        return f"https://www.google.com/maps/search/?api=1&query={query}"

    @staticmethod
    def _calculate_dates(start_date: str, nights: int) -> str:
        start = date.fromisoformat(start_date)
        return (start + timedelta(days=nights)).isoformat()

    @staticmethod
    def _sources_from_result(data: Dict[str, Any]) -> List[Dict[str, str]]:
        return list(data.get("sources") or [])

    def generate_plan(self, data: Dict[str, Any]) -> Dict[str, Any]:
        start_date = data["start_date"]
        end_date = self._calculate_dates(start_date, int(data["nights"]))
        language = {"tr": "Turkish", "en": "English", "ar": "Arabic"}.get(data.get("language"), "English")

        prompt = f"""
You are VoyageAI, a live travel SEARCHER and itinerary planner for Turkey.

This is NOT a creative-writing task. Search the live public web before deciding anything.
Use the Google Search tool in this request.

USER REQUEST
============
Origin: {data['origin']}
Destination: {data['destination']}
Start date: {start_date}
Return date: {end_date}
Nights: {data['nights']}
Adults: {data['adults_count']}
Children: {data['children_count']}
Child age: {data.get('child_age')}
Rooms: {data['rooms_count']}
Transport preference: {data['transport_mode']}
Budget mode: {data['budget_type']}
Budget amount TRY: {data.get('budget_amount_try')}
Minimum hotel rating: {data['hotel_min_rating']}/10
Hotel location preference: {data['hotel_location']}
Required hotel amenities: {data['amenities']}
Meal plan: {data['meal_board']}
Special notes: {data.get('special_notes', '')}
Output language: {language}

NON-NEGOTIABLE ACCURACY RULES
=============================
1. LIVE SEARCH ONLY. Do not use remembered examples or generic tourist templates.
2. NEVER invent a hotel, restaurant, attraction, station, route, ticket time, price, rating, address, availability, URL, phone number, or provider.
3. Every selected hotel, transport option, restaurant, and attraction must have at least one source URL that comes from the live search results.
4. A URL may be placed into booking_links or source_urls ONLY if it is a URL actually present in the grounded search results.
5. Never manufacture deep links by guessing query parameters.
6. If an exact direct reservation URL with the user's date/passengers/rooms/meal plan cannot be verified from the search result, set exact_parameters_supported=false and use the verified provider/source URL instead.
7. Do not pretend that a generic provider homepage is an exact reservation link.
8. Prices must be current to the searched result as closely as the source permits. If price or availability cannot be verified, return null instead of guessing.
9. Use the user's exact dates, traveler counts, room count and meal plan when searching hotel/transport availability.
10. Hotel filtering is mandatory: rating, location, amenities and meal plan must match the user's request. If no matching verified hotel is found, return an explicit warning instead of inventing one.
11. Rank candidates by a best-and-cheapest approach: quality/reputation + requirement match + price + practical location. Explain the score briefly.
12. For multiple-day stays, do NOT repeat the same attraction or restaurant unless there is no realistic alternative; rank distinct options for each day.
13. Search for actual places in the destination city. Never substitute a famous place from another city.
14. For restaurants, return real named businesses and a direct Google Maps search URL can be generated from the verified business name after the model returns; do not return generic category searches.
15. For transport, search actual schedules for the chosen date. If the route requires a transfer, represent the legs clearly. If the requested mode is impossible, set is_feasible=false.
16. For return day, work backward from the REAL return departure time: hotel checkout, lunch/activity, transfer time, and a safety buffer. Never invent a departure time.
17. For Own Car / Own EV, do not invent tolls or energy costs. Give only an estimate when you have sufficient searched distance/toll data; otherwise use null and explain.
18. Do NOT add filler content just to make the JSON complete.
19. All user-visible descriptive text must be written in {language}, but place names and company names should preserve their real official spelling when appropriate.
20. Output ONLY JSON matching the provided schema.

SEARCH PRIORITIES
=================
- Official operator websites first for transport schedules and reservation sources.
- Official hotel site or reputable booking provider pages for hotel facts.
- Google/search-indexed business pages for restaurants and attractions.
- Prefer current pages that explicitly mention the destination, date, provider and relevant conditions.

ITINERARY RULES
===============
- Day 1 should fit realistically around arrival time.
- Each day must have different realistic attractions/restaurants where possible.
- Do not schedule a place before it opens or after it closes if the searched information provides opening hours.
- Keep travel time between activities realistic.
- The departure day must be planned around the actual return departure time and required safety buffer.
- The plan should mention the source-backed transport times and costs.

IMPORTANT
=========
You have access to live Google Search grounding in this request. Use it. If the web does not provide enough evidence, say so in data_warnings instead of filling the gaps from memory.
"""

        schema = self._plan_schema()
        result = self._request_gemini(prompt, schema)
        result["start_date"] = start_date
        result["end_date"] = end_date

        try:
            validated = TripPlanResponse.model_validate(result)
        except ValidationError as exc:
            raise TravelAIError(f"Gemini returned data that failed validation: {exc}") from exc

        return validated.model_dump()

    @staticmethod
    def _plan_schema() -> Dict[str, Any]:
        why = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "explanation": {"type": "string"},
                "score_metrics": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["title", "explanation", "score_metrics"],
        }
        booking = {
            "type": "object",
            "properties": {
                "provider_name": {"type": "string"},
                "url": {"type": ["string", "null"]},
                "kind": {"type": "string"},
                "exact_parameters_supported": {"type": "boolean"},
            },
            "required": ["provider_name", "url", "kind", "exact_parameters_supported"],
        }
        source = {
            "type": "object",
            "properties": {"title": {"type": "string"}, "url": {"type": "string"}, "type": {"type": "string"}},
            "required": ["title", "url", "type"],
        }
        hotel = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "stars": {"type": ["integer", "null"]},
                "aggregated_rating_10": {"type": ["number", "null"]},
                "reviews_count": {"type": ["integer", "null"]},
                "total_hotel_cost_try": {"type": ["number", "null"]},
                "price_per_room_per_night_try": {"type": ["number", "null"]},
                "meal_board_type": {"type": "string"},
                "distance_to_center_km": {"type": ["number", "null"]},
                "location_tag": {"type": "string"},
                "has_private_beach": {"type": "boolean"},
                "has_aquapark": {"type": "boolean"},
                "has_pool": {"type": "boolean"},
                "has_spa": {"type": "boolean"},
                "address": {"type": "string"},
                "booking_links": {"type": "array", "items": booking},
                "sources": {"type": "array", "items": source},
                "why": why,
                "verified": {"type": "boolean"},
            },
            "required": [
                "name", "stars", "aggregated_rating_10", "reviews_count", "total_hotel_cost_try",
                "price_per_room_per_night_try", "meal_board_type", "distance_to_center_km", "location_tag",
                "has_private_beach", "has_aquapark", "has_pool", "has_spa", "address", "booking_links",
                "sources", "why", "verified"
            ],
        }
        transport = {
            "type": "object",
            "properties": {
                "mode": {"type": "string"},
                "is_feasible": {"type": "boolean"},
                "feasibility_warning": {"type": ["string", "null"]},
                "carrier_summary": {"type": "string"},
                "departure_time": {"type": "string"},
                "arrival_time": {"type": "string"},
                "origin_terminal": {"type": "string"},
                "destination_terminal": {"type": "string"},
                "duration": {"type": "string"},
                "cost_per_adult_try": {"type": ["number", "null"]},
                "cost_per_child_try": {"type": ["number", "null"]},
                "total_transport_cost_try": {"type": ["number", "null"]},
                "booking_links": {"type": "array", "items": booking},
                "sources": {"type": "array", "items": source},
                "why": why,
                "verified": {"type": "boolean"},
            },
            "required": [
                "mode", "is_feasible", "feasibility_warning", "carrier_summary", "departure_time", "arrival_time",
                "origin_terminal", "destination_terminal", "duration", "cost_per_adult_try", "cost_per_child_try",
                "total_transport_cost_try", "booking_links", "sources", "why", "verified"
            ],
        }
        activity = {
            "type": "object",
            "properties": {
                "time_slot": {"type": "string"},
                "place_name": {"type": "string"},
                "category": {"type": "string"},
                "address": {"type": "string"},
                "distance_from_hotel_km": {"type": ["number", "null"]},
                "transport_mode": {"type": "string"},
                "transport_cost_try": {"type": ["number", "null"]},
                "entry_ticket_adult_try": {"type": ["number", "null"]},
                "aggregated_rating_10": {"type": ["number", "null"]},
                "map_url": {"type": "string"},
                "source_urls": {"type": "array", "items": {"type": "string"}},
                "transit_card_tip": {"type": "string"},
                "why": why,
                "verified": {"type": "boolean"},
            },
            "required": [
                "time_slot", "place_name", "category", "address", "distance_from_hotel_km", "transport_mode",
                "transport_cost_try", "entry_ticket_adult_try", "aggregated_rating_10", "map_url", "source_urls",
                "transit_card_tip", "why", "verified"
            ],
        }
        restaurant = {
            "type": "object",
            "properties": {
                "meal_type": {"type": "string"},
                "restaurant_name": {"type": "string"},
                "cuisine": {"type": "string"},
                "address": {"type": "string"},
                "distance_from_hotel_km": {"type": ["number", "null"]},
                "estimated_cost_per_adult_try": {"type": ["number", "null"]},
                "estimated_cost_per_child_try": {"type": ["number", "null"]},
                "aggregated_rating_10": {"type": ["number", "null"]},
                "map_url": {"type": "string"},
                "source_urls": {"type": "array", "items": {"type": "string"}},
                "why": why,
                "verified": {"type": "boolean"},
            },
            "required": [
                "meal_type", "restaurant_name", "cuisine", "address", "distance_from_hotel_km",
                "estimated_cost_per_adult_try", "estimated_cost_per_child_try", "aggregated_rating_10", "map_url",
                "source_urls", "why", "verified"
            ],
        }
        day = {
            "type": "object",
            "properties": {
                "day_number": {"type": "integer"},
                "calendar_date": {"type": "string"},
                "day_title": {"type": "string"},
                "breakfast_banner": {"type": "string"},
                "lunch_banner": {"type": "string"},
                "dinner_banner": {"type": "string"},
                "activities": {"type": "array", "items": activity},
                "restaurants": {"type": "array", "items": restaurant},
            },
            "required": ["day_number", "calendar_date", "day_title", "breakfast_banner", "lunch_banner", "dinner_banner", "activities", "restaurants"],
        }
        departure = {
            "type": "object",
            "properties": {
                "departure_mode": {"type": "string"},
                "checkout_time": {"type": "string"},
                "lunch_spot_near_hub": {"type": ["object", "null"], "properties": restaurant["properties"], "required": restaurant["required"]},
                "time_spent_at_lunch": {"type": "string"},
                "transit_time_to_hub_mins": {"type": "integer"},
                "required_safety_buffer_mins": {"type": "integer"},
                "return_departure_time": {"type": "string"},
                "arrival_at_home_time": {"type": "string"},
                "activities_before_departure": {"type": "array", "items": activity},
                "recommended_final_meal": {"type": ["object", "null"], "properties": restaurant["properties"], "required": restaurant["required"]},
                "distance_from_final_spot_to_terminal_km": {"type": ["number", "null"]},
                "transit_time_to_terminal_mins": {"type": ["integer", "null"]},
                "why": why,
            },
            "required": [
                "departure_mode", "checkout_time", "lunch_spot_near_hub", "time_spent_at_lunch",
                "transit_time_to_hub_mins", "required_safety_buffer_mins", "return_departure_time", "arrival_at_home_time",
                "activities_before_departure", "recommended_final_meal", "distance_from_final_spot_to_terminal_km",
                "transit_time_to_terminal_mins", "why"
            ],
        }
        return {
            "type": "object",
            "properties": {
                "destination_city": {"type": "string"},
                "origin_city": {"type": "string"},
                "adults_count": {"type": "integer"},
                "children_count": {"type": "integer"},
                "rooms_count": {"type": "integer"},
                "total_travelers": {"type": "integer"},
                "meal_board": {"type": "string"},
                "start_date": {"type": "string"},
                "end_date": {"type": "string"},
                "grand_total_trip_cost_try": {"type": ["number", "null"]},
                "transportation": transport,
                "hotel": hotel,
                "daily_schedule": {"type": "array", "items": day},
                "departure_day_buffer": departure,
                "cost_breakdown": {
                    "type": "object",
                    "properties": {
                        "hotel_total_try": {"type": ["number", "null"]},
                        "transport_total_try": {"type": ["number", "null"]},
                        "food_budget_total_try": {"type": ["number", "null"]},
                        "activities_and_transfers_try": {"type": ["number", "null"]},
                        "grand_total_try": {"type": ["number", "null"]},
                    },
                    "required": ["hotel_total_try", "transport_total_try", "food_budget_total_try", "activities_and_transfers_try", "grand_total_try"],
                },
                "sources": {"type": "array", "items": source},
                "data_warnings": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "destination_city", "origin_city", "adults_count", "children_count", "rooms_count", "total_travelers",
                "meal_board", "start_date", "end_date", "grand_total_trip_cost_try", "transportation", "hotel",
                "daily_schedule", "departure_day_buffer", "cost_breakdown", "sources", "data_warnings"
            ],
        }

#http://127.0.0.1:8000