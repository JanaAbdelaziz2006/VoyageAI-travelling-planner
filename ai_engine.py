import json
import os
import time
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)
load_dotenv(BASE_DIR / ".env")

# FREE MODE:
# - One Gemini request per trip search
# - No Google Search grounding
# - Real public data comes from OpenStreetMap / Overpass
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.6-flash").strip()
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/interactions"

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OSRM_URL = "https://router.project-osrm.org/route/v1/driving"

APP_USER_AGENT = os.getenv(
    "APP_USER_AGENT",
    "VoyageAI/5.0 (local travel-planner prototype; contact=developer@example.com)",
)


class TravelAIError(Exception):
    pass


class Source(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = "OpenStreetMap"
    url: str
    type: str = "osm"


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

    candidate_id: str = ""
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
    price_verified: bool = False


class TransportItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    mode: str
    is_feasible: bool = False
    feasibility_warning: Optional[str] = None
    carrier_summary: str = ""
    candidate_id: str = ""
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
    price_verified: bool = False


class ActivityItem(BaseModel):
    model_config = ConfigDict(extra="ignore")

    candidate_id: str = ""
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

    candidate_id: str = ""
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


@dataclass
class CityGeo:
    display_name: str
    lat: float
    lon: float


def _safe_cache_name(prefix: str, value: str) -> Path:
    import hashlib

    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]
    return CACHE_DIR / f"{prefix}_{digest}.json"


def _read_cache(
    path: Path,
    max_age_seconds: int = 86400,
) -> Optional[Dict[str, Any]]:
    try:
        if time.time() - path.stat().st_mtime > max_age_seconds:
            return None

        return json.loads(path.read_text(encoding="utf-8"))

    except Exception:
        return None


def _write_cache(path: Path, data: Any) -> None:
    try:
        path.write_text(
            json.dumps(data, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:
        pass


class FreeDataLayer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": APP_USER_AGENT,
            }
        )

    def geocode_city(self, city: str) -> CityGeo:
        cache_path = _safe_cache_name(
            "geo",
            city.casefold().strip(),
        )

        cached = _read_cache(
            cache_path,
            max_age_seconds=7 * 86400,
        )

        if cached:
            return CityGeo(**cached)

        try:
            # Nominatim public service should not be hit faster than 1 req/sec.
            time.sleep(1.05)

            response = self.session.get(
                NOMINATIM_URL,
                params={
                    "q": f"{city}, Turkey",
                    "format": "jsonv2",
                    "limit": 1,
                    "countrycodes": "tr",
                },
                timeout=30,
            )

            response.raise_for_status()
            rows = response.json()

        except requests.RequestException as exc:
            raise TravelAIError(
                f"Could not geocode {city}: {exc}"
            ) from exc

        if not rows:
            raise TravelAIError(
                f"Could not locate {city} in Turkey using OpenStreetMap."
            )

        geo = CityGeo(
            display_name=rows[0].get(
                "display_name",
                city,
            ),
            lat=float(rows[0]["lat"]),
            lon=float(rows[0]["lon"]),
        )

        _write_cache(
            cache_path,
            geo.__dict__,
        )

        return geo

    def overpass_candidates(
        self,
        city: str,
        geo: CityGeo,
    ) -> Dict[str, List[Dict[str, Any]]]:

        cache_path = _safe_cache_name(
            "overpass",
            f"{city.casefold()}|{geo.lat:.4f}|{geo.lon:.4f}",
        )

        cached = _read_cache(
            cache_path,
            max_age_seconds=6 * 3600,
        )

        if cached:
            return cached

        query = f"""
[out:json][timeout:35];
(
  nwr(around:18000,{geo.lat},{geo.lon})[tourism=hotel];
  nwr(around:18000,{geo.lat},{geo.lon})[tourism=guest_house];
  nwr(around:18000,{geo.lat},{geo.lon})[amenity=restaurant];
  nwr(around:18000,{geo.lat},{geo.lon})[tourism=attraction];
  nwr(around:18000,{geo.lat},{geo.lon})[historic];
  nwr(around:18000,{geo.lat},{geo.lon})[amenity=bus_station];
  nwr(around:18000,{geo.lat},{geo.lon})[amenity=ferry_terminal];
  nwr(around:18000,{geo.lat},{geo.lon})[railway=station];
);
out center tags;
"""

        try:
            response = self.session.post(
                OVERPASS_URL,
                data=query,
                timeout=60,
            )

            if response.status_code == 429:
                raise TravelAIError(
                    "OpenStreetMap Overpass is temporarily busy. "
                    "Please wait a little and retry."
                )

            response.raise_for_status()

            elements = response.json().get(
                "elements",
                [],
            )

        except requests.RequestException as exc:
            raise TravelAIError(
                f"Could not query OpenStreetMap: {exc}"
            ) from exc

        result = {
            "hotels": [],
            "restaurants": [],
            "places": [],
            "transport": [],
        }

        seen: set[str] = set()

        for element in elements:
            tags = element.get("tags") or {}

            center = element.get("center") or {}

            lat = element.get(
                "lat",
                center.get("lat"),
            )

            lon = element.get(
                "lon",
                center.get("lon"),
            )

            name = (
                tags.get("name") or ""
            ).strip()

            if not name or lat is None or lon is None:
                continue

            kind = str(
                element.get("type", "n")
            )

            osm_id = (
                f"{kind}{element.get('id')}"
            )

            if osm_id in seen:
                continue

            seen.add(osm_id)

            record = {
                "id": osm_id,
                "name": name,
                "lat": float(lat),
                "lon": float(lon),
                "address": ", ".join(
                    x
                    for x in [
                        tags.get("addr:street"),
                        tags.get("addr:housenumber"),
                        tags.get("addr:city"),
                    ]
                    if x
                ),
                "website": (
                    tags.get("website")
                    or tags.get("contact:website")
                    or ""
                ),
                "phone": (
                    tags.get("phone")
                    or tags.get("contact:phone")
                    or ""
                ),
                "operator": (
                    tags.get("operator")
                    or tags.get("network")
                    or ""
                ),
                "stars": self._to_int(
                    tags.get("stars")
                ),
                "rating": self._to_float(
                    tags.get("rating")
                    or tags.get("stars:rating")
                ),
                "price": self._extract_price(tags),
                "cuisine": tags.get(
                    "cuisine",
                    "",
                ),
                "opening_hours": tags.get(
                    "opening_hours",
                    "",
                ),
                "description": tags.get(
                    "description",
                    "",
                ),
                "amenities": [],
                "osm_url": (
                    f"https://www.openstreetmap.org/"
                    f"{kind}/{element.get('id')}"
                ),
            }

            for key in [
                "swimming_pool",
                "pool",
                "spa",
                "water_park",
                "beach_resort",
            ]:
                if (
                    key in tags
                    or str(
                        tags.get(
                            "amenity",
                            "",
                        )
                    ).casefold()
                    == key
                ):
                    record["amenities"].append(key)

            if tags.get("leisure") == "water_park":
                record["amenities"].append(
                    "aquapark"
                )

            if tags.get("tourism") in {
                "hotel",
                "guest_house",
            }:
                result["hotels"].append(
                    record
                )

            elif tags.get("amenity") == "restaurant":
                result["restaurants"].append(
                    record
                )

            elif (
                tags.get("tourism")
                == "attraction"
                or "historic" in tags
            ):
                result["places"].append(
                    record
                )

            elif (
                tags.get("amenity")
                in {
                    "bus_station",
                    "ferry_terminal",
                }
                or tags.get("railway")
                == "station"
            ):
                result["transport"].append(
                    record
                )

        _write_cache(
            cache_path,
            result,
        )

        return result

    @staticmethod
    def _to_int(
        value: Any,
    ) -> Optional[int]:
        try:
            return int(float(value))
        except (
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _to_float(
        value: Any,
    ) -> Optional[float]:
        try:
            return float(value)
        except (
            TypeError,
            ValueError,
        ):
            return None

    @classmethod
    def _extract_price(
        cls,
        tags: Dict[str, Any],
    ) -> Optional[float]:

        for key in (
            "price",
            "price_level",
            "price_range",
        ):
            value = tags.get(key)

            if value is None:
                continue

            if isinstance(
                value,
                (int, float),
            ):
                return float(value)

            text = str(value).replace(
                ",",
                ".",
            )

            import re

            match = re.search(
                r"\d+(?:\.\d+)?",
                text,
            )

            if match:
                try:
                    return float(
                        match.group(0)
                    )
                except ValueError:
                    pass

        return None

    def road_route(
        self,
        origin: CityGeo,
        destination: CityGeo,
    ) -> Dict[str, Any]:

        key = (
            f"{origin.lat:.5f},{origin.lon:.5f}"
            f"|"
            f"{destination.lat:.5f},{destination.lon:.5f}"
        )

        cache_path = _safe_cache_name(
            "route",
            key,
        )

        cached = _read_cache(
            cache_path,
            max_age_seconds=7 * 86400,
        )

        if cached:
            return cached

        try:
            url = (
                f"{OSRM_URL}/"
                f"{origin.lon},{origin.lat};"
                f"{destination.lon},{destination.lat}"
            )

            response = self.session.get(
                url,
                params={
                    "overview": "false",
                },
                timeout=30,
            )

            response.raise_for_status()

            body = response.json()

        except requests.RequestException as exc:
            raise TravelAIError(
                f"Could not calculate the road route: {exc}"
            ) from exc

        routes = body.get(
            "routes"
        ) or []

        if not routes:
            raise TravelAIError(
                "No road route was returned "
                "for this origin/destination."
            )

        route = {
            "distance_km": round(
                routes[0]["distance"] / 1000,
                1,
            ),
            "duration_min": round(
                routes[0]["duration"] / 60
            ),
        }

        _write_cache(
            cache_path,
            route,
        )

        return route


class TravelAIEngine:

    def __init__(self):
        self.gemini_key = (
            os.getenv(
                "GEMINI_API_KEY",
                "",
            )
            .strip()
        )

        if (
            not self.gemini_key
            or self.gemini_key
            == "PASTE_YOUR_NEW_KEY_HERE"
        ):
            raise TravelAIError(
                "Gemini API key is not configured. "
                "Put your key in .env."
            )

        self.data = FreeDataLayer()

    def _request_gemini(
        self,
        prompt: str,
        schema: Dict[str, Any],
    ) -> Dict[str, Any]:

        payload = {
            "model": GEMINI_MODEL,
            "input": prompt,
            "response_format": {
                "type": "text",
                "mime_type": "application/json",
                "schema": schema,
            },
            "generation_config": {
                "thinking_level": "low",
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
                timeout=150,
            )

        except requests.RequestException as exc:
            raise TravelAIError(
                f"Could not reach Gemini API: {exc}"
            ) from exc

        if response.status_code == 429:
            raise TravelAIError(
                "Gemini Free Tier rate limit was reached. "
                "This version uses one Gemini request per trip search. "
                "Wait for the quota window to reset and try again."
            )

        if response.status_code == 401:
            raise TravelAIError(
                "Gemini returned 401. "
                "Check that the API key in .env is valid "
                "and belongs to this project."
            )

        if response.status_code == 404:
            raise TravelAIError(
                f"Gemini model '{GEMINI_MODEL}' is unavailable "
                "for this project. Check GEMINI_MODEL in .env."
            )

        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = response.text[:1000]

            raise TravelAIError(
                f"Gemini API error "
                f"{response.status_code}: {detail}"
            )

        try:
            body = response.json()

        except ValueError as exc:
            raise TravelAIError(
                "Gemini returned a non-JSON response."
            ) from exc

        text = self._extract_model_output_text(
            body
        )

        if not text:
            raise TravelAIError(
                "Gemini returned no model output."
            )

        try:
            return json.loads(text)

        except json.JSONDecodeError as exc:
            raise TravelAIError(
                f"Gemini returned invalid JSON: {exc}"
            ) from exc

    @staticmethod
    def _extract_model_output_text(
        body: Dict[str, Any],
    ) -> str:

        for step in reversed(
            body.get("steps", [])
        ):
            if step.get("type") != "model_output":
                continue

            for block in step.get(
                "content",
                [],
            ):
                if (
                    block.get("type")
                    == "text"
                    and block.get("text")
                ):
                    return block[
                        "text"
                    ].strip()

        for key in (
            "output_text",
            "text",
        ):
            if body.get(key):
                return str(
                    body[key]
                ).strip()

        return ""

    @staticmethod
    def _maps_search_url(
        place: str,
        city: str,
    ) -> str:

        if not place:
            return ""

        return (
            "https://www.google.com/maps/search/"
            "?api=1&query="
            + quote(
                place
                + ", "
                + city
            )
        )

    @staticmethod
    def _calculate_dates(
        start_date: str,
        nights: int,
    ) -> str:

        return (
            date.fromisoformat(
                start_date
            )
            + timedelta(
                days=nights
            )
        ).isoformat()

    def _candidate_pack(
        self,
        city: str,
        geo: CityGeo,
        candidates: Dict[str, List[Dict[str, Any]]],
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        amenities = {
            str(x).casefold()
            for x in data.get(
                "amenities",
                [],
            )
        }

        def hotel_score(
            c: Dict[str, Any],
        ) -> float:

            score = 0.0

            if c.get("stars"):
                score += min(
                    c["stars"],
                    5,
                ) * 10

            if c.get("rating"):
                score += min(
                    c["rating"],
                    10,
                ) * 4

            if c.get("price") is not None:
                score += 15

            listed = {
                x.casefold()
                for x in c.get(
                    "amenities",
                    [],
                )
            }

            score += (
                10
                * len(
                    amenities.intersection(
                        listed
                    )
                )
            )

            return score

        hotels = sorted(
            candidates["hotels"],
            key=hotel_score,
            reverse=True,
        )[:30]

        restaurants = candidates[
            "restaurants"
        ][:50]

        places = candidates[
            "places"
        ][:50]

        transport = candidates[
            "transport"
        ][:40]

        return {
            "hotels": hotels,
            "restaurants": restaurants,
            "places": places,
            "transport": transport,
        }

    def _build_result_from_ids(
        self,
        raw: Dict[str, Any],
        candidates: Dict[str, List[Dict[str, Any]]],
        data: Dict[str, Any],
        geo: CityGeo,
    ) -> TripPlanResponse:

        pools = {
            key: {
                item["id"]: item
                for item in value
            }
            for key, value in candidates.items()
        }

        warnings: List[str] = []

        hotel_sel = (
            raw.get("hotel", {})
        )

        hotel_c = pools[
            "hotels"
        ].get(
            hotel_sel.get(
                "candidate_id"
            )
        )

        if not hotel_c:

            warnings.append(
                "No OpenStreetMap-verified hotel "
                "matched the AI selection."
            )

            hotel = HotelItem(
                name="",
                verified=False,
            )

        else:

            listed = {
                x.casefold()
                for x in hotel_c.get(
                    "amenities",
                    [],
                )
            }

            hotel = HotelItem(
                candidate_id=hotel_c["id"],
                name=hotel_c["name"],
                stars=hotel_c.get("stars"),
                aggregated_rating_10=hotel_c.get(
                    "rating"
                ),
                price_per_room_per_night_try=hotel_c.get(
                    "price"
                ),
                total_hotel_cost_try=(
                    hotel_c.get(
                        "price"
                    )
                    * data["rooms_count"]
                    * data["nights"]
                    if hotel_c.get(
                        "price"
                    )
                    is not None
                    else None
                ),
                address=hotel_c.get(
                    "address",
                    "",
                ),
                has_pool=(
                    "pool" in listed
                    or "swimming_pool"
                    in listed
                ),
                has_spa=(
                    "spa" in listed
                ),
                has_aquapark=(
                    "aquapark"
                    in listed
                    or "water_park"
                    in listed
                ),
                has_private_beach=(
                    "private_beach"
                    in listed
                    or "beach_resort"
                    in listed
                ),
                location_tag=data.get(
                    "hotel_location",
                    "",
                ),
                booking_links=(
                    [
                        BookingLink(
                            provider_name=(
                                "Official website"
                            ),
                            url=hotel_c[
                                "website"
                            ],
                            kind="source",
                        )
                    ]
                    if hotel_c.get(
                        "website"
                    )
                    else []
                ),
                sources=[
                    Source(
                        title="OpenStreetMap",
                        url=hotel_c[
                            "osm_url"
                        ],
                        type="osm",
                    )
                ],
                why=WhyReason(
                    **(
                        hotel_sel.get(
                            "why"
                        )
                        or {}
                    )
                ),
                verified=True,
                price_verified=(
                    hotel_c.get(
                        "price"
                    )
                    is not None
                ),
            )

            if not hotel.price_verified:
                warnings.append(
                    "This free data source did not provide "
                    "a verified current hotel price, so the app "
                    "does not claim it is the absolute cheapest hotel."
                )

        trans_sel = (
            raw.get(
                "transportation",
                {},
            )
        )

        trans_c = pools[
            "transport"
        ].get(
            trans_sel.get(
                "candidate_id"
            )
        )

        if trans_c:

            transport = TransportItem(
                mode=data[
                    "transport_mode"
                ],
                is_feasible=True,
                carrier_summary=(
                    trans_c.get(
                        "operator"
                    )
                    or trans_c.get(
                        "name"
                    )
                ),
                candidate_id=trans_c[
                    "id"
                ],
                origin_terminal=trans_c.get(
                    "name",
                    "",
                ),
                destination_terminal="",
                booking_links=(
                    [
                        BookingLink(
                            provider_name=(
                                "Official website"
                            ),
                            url=trans_c[
                                "website"
                            ],
                            kind="source",
                        )
                    ]
                    if trans_c.get(
                        "website"
                    )
                    else []
                ),
                sources=[
                    Source(
                        title="OpenStreetMap",
                        url=trans_c[
                            "osm_url"
                        ],
                        type="osm",
                    )
                ],
                why=WhyReason(
                    **(
                        trans_sel.get(
                            "why"
                        )
                        or {}
                    )
                ),
                verified=True,
                price_verified=(
                    trans_c.get(
                        "price"
                    )
                    is not None
                ),
            )

        else:

            transport = TransportItem(
                mode=data[
                    "transport_mode"
                ],
                is_feasible=False,
                feasibility_warning=(
                    "No route/operator candidate "
                    "could be verified from the free "
                    "public data sources."
                ),
                why=WhyReason(
                    **(
                        trans_sel.get(
                            "why"
                        )
                        or {}
                    )
                ),
                verified=False,
            )

            warnings.append(
                "No free, route-specific transport operator "
                "data was verified. The app will not invent "
                "a company, time or ticket price."
            )

        if (
            transport.verified
            and not transport.price_verified
        ):
            warnings.append(
                "The transport operator is verified, "
                "but a current ticket price is not available "
                "from the free public data source; "
                "no cheapest-price claim is made."
            )

        days: List[DayPlan] = []

        used_place_ids: set[str] = set()
        used_restaurant_ids: set[str] = set()

        start = date.fromisoformat(
            data["start_date"]
        )

        raw_days = (
            raw.get(
                "daily_schedule"
            )
            or []
        )

        for idx in range(
            int(data["nights"])
        ):

            day_raw = (
                raw_days[idx]
                if idx < len(raw_days)
                else {}
            )

            activities: List[
                ActivityItem
            ] = []

            restaurants: List[
                RestaurantItem
            ] = []

            for act in day_raw.get(
                "activities",
                [],
            )[:3]:

                cand = pools[
                    "places"
                ].get(
                    act.get(
                        "candidate_id"
                    )
                )

                if (
                    not cand
                    or cand["id"]
                    in used_place_ids
                ):
                    continue

                used_place_ids.add(
                    cand["id"]
                )

                activities.append(
                    ActivityItem(
                        candidate_id=cand[
                            "id"
                        ],
                        time_slot=act.get(
                            "time_slot",
                            "",
                        ),
                        place_name=cand[
                            "name"
                        ],
                        category=(
                            cand.get(
                                "description"
                            )
                            or "Attraction"
                        ),
                        address=cand.get(
                            "address",
                            "",
                        ),
                        map_url=(
                            self._maps_search_url(
                                cand[
                                    "name"
                                ],
                                data[
                                    "destination"
                                ],
                            )
                        ),
                        source_urls=[
                            cand[
                                "osm_url"
                            ]
                        ],
                        why=WhyReason(
                            **(
                                act.get(
                                    "why"
                                )
                                or {}
                            )
                        ),
                        verified=True,
                    )
                )

            for r in day_raw.get(
                "restaurants",
                [],
            )[:3]:

                cand = pools[
                    "restaurants"
                ].get(
                    r.get(
                        "candidate_id"
                    )
                )

                if (
                    not cand
                    or cand["id"]
                    in used_restaurant_ids
                ):
                    continue

                used_restaurant_ids.add(
                    cand["id"]
                )

                restaurants.append(
                    RestaurantItem(
                        candidate_id=cand[
                            "id"
                        ],
                        meal_type=r.get(
                            "meal_type",
                            "Meal",
                        ),
                        restaurant_name=cand[
                            "name"
                        ],
                        cuisine=cand.get(
                            "cuisine",
                            "",
                        ),
                        address=cand.get(
                            "address",
                            "",
                        ),
                        estimated_cost_per_adult_try=(
                            cand.get(
                                "price"
                            )
                        ),
                        aggregated_rating_10=(
                            cand.get(
                                "rating"
                            )
                        ),
                        map_url=(
                            self._maps_search_url(
                                cand[
                                    "name"
                                ],
                                data[
                                    "destination"
                                ],
                            )
                        ),
                        source_urls=[
                            cand[
                                "osm_url"
                            ]
                        ],
                        why=WhyReason(
                            **(
                                r.get(
                                    "why"
                                )
                                or {}
                            )
                        ),
                        verified=True,
                    )
                )

            if not activities:
                warnings.append(
                    f"Day {idx + 1} has no distinct "
                    "verified attraction candidate "
                    "from the free source."
                )

            if not restaurants:
                warnings.append(
                    f"Day {idx + 1} has no distinct "
                    "verified restaurant candidate "
                    "from the free source."
                )

            day_date = (
                start
                + timedelta(
                    days=idx
                )
            ).isoformat()

            days.append(
                DayPlan(
                    day_number=idx + 1,
                    calendar_date=day_date,
                    day_title=(
                        day_raw.get(
                            "day_title"
                        )
                        or f"Day {idx + 1}"
                    ),
                    breakfast_banner=(
                        day_raw.get(
                            "breakfast_banner",
                            "",
                        )
                    ),
                    lunch_banner=(
                        day_raw.get(
                            "lunch_banner",
                            "",
                        )
                    ),
                    dinner_banner=(
                        day_raw.get(
                            "dinner_banner",
                            "",
                        )
                    ),
                    activities=activities,
                    restaurants=restaurants,
                )
            )

        if data[
            "transport_mode"
        ] in {
            "Own Car",
            "Own EV",
        }:

            origin_geo = (
                self.data.geocode_city(
                    data[
                        "origin"
                    ]
                )
            )

            route = self.data.road_route(
                origin_geo,
                geo,
            )

            warnings.append(
                "Road distance comes from "
                "OSRM/OpenStreetMap. HGS/toll "
                "and energy prices are estimates "
                "unless separately verified."
            )

        hotel_total = (
            hotel.total_hotel_cost_try
        )

        transport_total = (
            transport.total_transport_cost_try
        )

        food_total = None
        grand = None

        if (
            hotel_total is not None
            or transport_total is not None
        ):
            grand = sum(
                value
                for value in [
                    hotel_total,
                    transport_total,
                    food_total,
                ]
                if value is not None
            )

        return TripPlanResponse(
            destination_city=data[
                "destination"
            ],
            origin_city=data[
                "origin"
            ],
            adults_count=data[
                "adults_count"
            ],
            children_count=data[
                "children_count"
            ],
            rooms_count=data[
                "rooms_count"
            ],
            total_travelers=(
                data[
                    "adults_count"
                ]
                + data[
                    "children_count"
                ]
            ),
            meal_board=data[
                "meal_board"
            ],
            start_date=data[
                "start_date"
            ],
            end_date=(
                self._calculate_dates(
                    data[
                        "start_date"
                    ],
                    data[
                        "nights"
                    ],
                )
            ),
            grand_total_trip_cost_try=grand,
            transportation=transport,
            hotel=hotel,
            daily_schedule=days,
            departure_day_buffer=(
                DepartureDayBuffer(
                    departure_mode=data[
                        "transport_mode"
                    ],
                    why=WhyReason(
                        title="Return-day planning",
                        explanation=(
                            "Free mode does not invent "
                            "a ticket time. Use a verified "
                            "departure time when a provider "
                            "source supplies one."
                        ),
                    ),
                )
            ),
            cost_breakdown=(
                TripCostBreakdown(
                    hotel_total_try=hotel_total,
                    transport_total_try=transport_total,
                    grand_total_try=grand,
                )
            ),
            sources=[
                Source(
                    title="OpenStreetMap",
                    url=(
                        "https://www.openstreetmap.org/"
                    ),
                    type="osm",
                )
            ],
            data_warnings=list(
                dict.fromkeys(
                    warnings
                )
            ),
        )

    def generate_plan(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        start_date = data[
            "start_date"
        ]

        end_date = (
            self._calculate_dates(
                start_date,
                int(
                    data["nights"]
                ),
            )
        )

        language = {
            "tr": "Turkish",
            "en": "English",
            "ar": "Arabic",
        }.get(
            data.get("language"),
            "English",
        )

        dest_geo = (
            self.data.geocode_city(
                data[
                    "destination"
                ]
            )
        )

        candidates = (
            self.data.overpass_candidates(
                data[
                    "destination"
                ],
                dest_geo,
            )
        )

        packed = (
            self._candidate_pack(
                data[
                    "destination"
                ],
                dest_geo,
                candidates,
                data,
            )
        )

        if not any(
            packed.values()
        ):
            raise TravelAIError(
                "No verified OpenStreetMap "
                "candidates were found for "
                "this destination."
            )

        prompt = f"""
You are VoyageAI, a travel planner.
You are working in FREE MODE.

You receive verified candidate records from OpenStreetMap.
You MUST only choose candidate IDs that appear in those records.

You do NOT have live Google Search in this mode.

USER REQUEST

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
Minimum hotel rating: {data['hotel_min_rating']}
Hotel location: {data['hotel_location']}
Required amenities: {data['amenities']}
Meal plan: {data['meal_board']}
Special notes: {data.get('special_notes', '')}
Output language: {language}

FREE-MODE RULES

1. NEVER invent candidate IDs.
2. NEVER invent names.
3. NEVER invent prices.
4. NEVER invent ratings.
5. NEVER invent addresses.
6. NEVER invent operators.
7. NEVER invent opening hours.
8. NEVER invent URLs.
9. Choose only IDs from the supplied candidate lists.
10. A hotel is "best + cheapest" only if a verified price exists in the candidate data.
11. If no price exists, choose the best matching verified hotel and explicitly state that a cheapest claim is unavailable.
12. For transport, choose an operator/hub candidate only when its candidate record is relevant.
13. Do not invent a bus company, flight company, ferry company or train company.
14. Do not invent a departure time.
15. Do not invent an arrival time.
16. Do not invent a ticket price.
17. For activities and restaurants, use distinct candidate IDs across days whenever possible.
18. Prefer candidates matching the user's required amenities and location.
19. Prefer stronger ratings and richer public data.
20. Use score explanations that are based only on supplied candidate data.
21. Return JSON only.

CANDIDATE DATA

{json.dumps(
    packed,
    ensure_ascii=False
)}
"""

        why_schema = {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string"
                },
                "explanation": {
                    "type": "string"
                },
                "score_metrics": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                },
            },
            "required": [
                "title",
                "explanation",
                "score_metrics",
            ],
        }

        schema = {
            "type": "object",
            "properties": {

                "hotel": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string"
                        },
                        "why": why_schema,
                    },
                    "required": [
                        "candidate_id",
                        "why",
                    ],
                },

                "transportation": {
                    "type": "object",
                    "properties": {
                        "candidate_id": {
                            "type": "string"
                        },
                        "why": why_schema,
                    },
                    "required": [
                        "candidate_id",
                        "why",
                    ],
                },

                "daily_schedule": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {

                            "day_number": {
                                "type": "integer"
                            },

                            "day_title": {
                                "type": "string"
                            },

                            "breakfast_banner": {
                                "type": "string"
                            },

                            "lunch_banner": {
                                "type": "string"
                            },

                            "dinner_banner": {
                                "type": "string"
                            },

                            "activities": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {

                                        "candidate_id": {
                                            "type": "string"
                                        },

                                        "time_slot": {
                                            "type": "string"
                                        },

                                        "why": why_schema,
                                    },
                                    "required": [
                                        "candidate_id",
                                        "time_slot",
                                        "why",
                                    ],
                                },
                            },

                            "restaurants": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {

                                        "candidate_id": {
                                            "type": "string"
                                        },

                                        "meal_type": {
                                            "type": "string"
                                        },

                                        "why": why_schema,
                                    },
                                    "required": [
                                        "candidate_id",
                                        "meal_type",
                                        "why",
                                    ],
                                },
                            },
                        },
                        "required": [
                            "day_number",
                            "day_title",
                            "breakfast_banner",
                            "lunch_banner",
                            "dinner_banner",
                            "activities",
                            "restaurants",
                        ],
                    },
                },
            },
            "required": [
                "hotel",
                "transportation",
                "daily_schedule",
            ],
        }

        # EXACTLY ONE Gemini API request for the entire trip.
        raw = self._request_gemini(
            prompt,
            schema,
        )

        plan = self._build_result_from_ids(
            raw,
            candidates,
            data,
            dest_geo,
        )

        return plan.model_dump()
    
#http://127.0.0.1:8000