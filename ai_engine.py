import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = BASE_DIR / ".serpapi_cache"
CACHE_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "serpapi").strip()
SERPAPI_URL = "https://serpapi.com/search.json"

SERPAPI_LOCATION = os.getenv(
    "SERPAPI_LOCATION",
    "Turkey"
)

SERPAPI_HL = os.getenv(
    "SERPAPI_HL",
    "en"
)

SERPAPI_GL = os.getenv(
    "SERPAPI_GL",
    "tr"
)

SERPAPI_CURRENCY = os.getenv(
    "SERPAPI_CURRENCY",
    "TRY"
)


class SearchEngineError(Exception):
    pass


class SerpApiSearchEngine:

    def __init__(self):
        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent": (
                "VoyageAI Travel Planner/1.0"
            )
        })

    # ---------------------------------------------------------
    # CACHE
    # ---------------------------------------------------------

    def _cache_file(
        self,
        prefix: str,
        params: Dict[str, Any]
    ) -> Path:

        raw = json.dumps(
            params,
            sort_keys=True,
            ensure_ascii=False
        )

        digest = hashlib.sha256(
            raw.encode("utf-8")
        ).hexdigest()[:32]

        return (
            CACHE_DIR
            / f"{prefix}_{digest}.json"
        )

    def _read_cache(
        self,
        path: Path,
        max_age_seconds: int = 3600
    ) -> Optional[Dict[str, Any]]:

        try:

            age = (
                time.time()
                - path.stat().st_mtime
            )

            if age > max_age_seconds:
                return None

            return json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

        except Exception:
            return None

    def _write_cache(
        self,
        path: Path,
        data: Dict[str, Any]
    ):

        try:

            path.write_text(
                json.dumps(
                    data,
                    ensure_ascii=False
                ),
                encoding="utf-8"
            )

        except Exception:
            pass

    # ---------------------------------------------------------
    # SERPAPI REQUEST
    # ---------------------------------------------------------

    def _request(
        self,
        params: Dict[str, Any],
        cache_prefix: str,
        cache_hours: int = 1
    ) -> Dict[str, Any]:

        if not SERPAPI_KEY:
            raise SearchEngineError(
                "SERPAPI_KEY is missing."
            )

        request_params = dict(params)

        request_params["api_key"] = (
            SERPAPI_KEY
        )

        request_params.setdefault(
            "hl",
            SERPAPI_HL
        )

        request_params.setdefault(
            "gl",
            SERPAPI_GL
        )

        cache_path = self._cache_file(
            cache_prefix,
            request_params
        )

        cached = self._read_cache(
            cache_path,
            max_age_seconds=cache_hours * 3600
        )

        if cached:
            return cached

        try:

            response = self.session.get(
                SERPAPI_URL,
                params=request_params,
                timeout=90
            )

        except requests.RequestException as exc:

            raise SearchEngineError(
                f"SerpApi connection error: {exc}"
            ) from exc

        try:
            data = response.json()
        except Exception:

            raise SearchEngineError(
                f"SerpApi returned invalid JSON "
                f"(HTTP {response.status_code})."
            )

        if response.status_code == 401:

            raise SearchEngineError(
                "SerpApi API key is invalid."
            )

        if response.status_code == 429:

            raise SearchEngineError(
                "SerpApi rate limit reached. "
                "The free plan allows a limited number "
                "of searches per hour."
            )

        if response.status_code >= 400:

            raise SearchEngineError(
                "SerpApi error "
                f"{response.status_code}: "
                f"{data.get('error', data)}"
            )

        if data.get("error"):

            raise SearchEngineError(
                f"SerpApi error: "
                f"{data['error']}"
            )

        self._write_cache(
            cache_path,
            data
        )

        return data

    # =========================================================
    # HOTELS
    # =========================================================

    def search_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        adults: int,
        children: int,
        children_ages: Optional[List[int]],
        rooms: int,
        min_rating: float,
        location_preference: str,
        amenities: List[str]
    ) -> List[Dict[str, Any]]:

        query = (
            f"hotels in {destination}, Turkey"
        )

        params = {
            "engine": "google_hotels",
            "q": query,
            "check_in_date": check_in,
            "check_out_date": check_out,
            "adults": adults,
            "children": children,
            "rooms": rooms,
            "currency": SERPAPI_CURRENCY,
            "gl": SERPAPI_GL,
            "hl": SERPAPI_HL,
            "sort_by": "3",
        }

        if children > 0 and children_ages:
            params["children_ages"] = ",".join(
                str(x)
                for x in children_ages
            )

        # Google Hotels rating filter
        if min_rating >= 9:
            params["rating"] = "9"
        elif min_rating >= 8:
            params["rating"] = "8"
        elif min_rating >= 7:
            params["rating"] = "7"

        data = self._request(
            params,
            "hotels",
            cache_hours=1
        )

        properties = (
            data.get("properties")
            or []
        )

        results = []

        for position, hotel in enumerate(
            properties,
            start=1
        ):

            rate_per_night = self._number(
                hotel.get(
                    "rate_per_night",
                    {}
                ).get("extracted_lowest")
            )

            total_rate = self._number(
                hotel.get(
                    "total_rate",
                    {}
                ).get("extracted_lowest")
            )

            rating = self._number(
                hotel.get("overall_rating")
            )

            if (
                rating is not None
                and rating < min_rating
            ):
                continue

            amenity_text = " ".join(
                hotel.get(
                    "amenities",
                    []
                )
            ).lower()

            # Search/filter requested amenities
            requested = [
                str(x).lower()
                for x in amenities
            ]

            amenity_match = True

            for required in requested:

                if required in {
                    "pool",
                    "beach",
                    "spa",
                    "aquapark"
                }:

                    aliases = {
                        "pool": [
                            "pool",
                            "swimming pool"
                        ],
                        "beach": [
                            "beach",
                            "private beach",
                            "beachfront"
                        ],
                        "spa": [
                            "spa",
                            "sauna",
                            "turkish bath"
                        ],
                        "aquapark": [
                            "water park",
                            "aquapark",
                            "water slide"
                        ]
                    }

                    if not any(
                        alias in amenity_text
                        for alias in aliases[
                            required
                        ]
                    ):
                        amenity_match = False
                        break

            if not amenity_match:
                continue

            hotel_id = str(
                hotel.get(
                    "property_token"
                    or hotel.get(
                        "data_id"
                    )
                    or position
                )
            )

            link = (
                hotel.get("link")
                or hotel.get("hotel_link")
                or ""
            )

            results.append({
                "candidate_id": (
                    f"hotel_{hotel_id}"
                ),
                "rank_position": position,
                "name": (
                    hotel.get("name")
                    or ""
                ),
                "rating": rating,
                "reviews": hotel.get(
                    "reviews"
                ),
                "stars": self._number(
                    hotel.get("hotel_class")
                ),
                "price_per_night_try":
                    rate_per_night,
                "total_price_try":
                    total_rate,
                "currency": SERPAPI_CURRENCY,
                "amenities":
                    hotel.get(
                        "amenities",
                        []
                    ),
                "address":
                    hotel.get(
                        "address",
                        ""
                    ),
                "gps":
                    hotel.get(
                        "gps_coordinates",
                        {}
                    ),
                "link": link,
                "images":
                    hotel.get(
                        "images",
                        []
                    ),
                "description":
                    hotel.get(
                        "description",
                        ""
                    ),
                "source": "Google Hotels via SerpApi",
            })

        return results

    # =========================================================
    # LOCAL / MAP SEARCH
    # =========================================================

    def search_local(
        self,
        query: str,
        location: str,
        cache_prefix: str
    ) -> List[Dict[str, Any]]:

        params = {
            "engine": "google_maps",
            "type": "search",
            "q": query,
            "location": f"{location}, Turkey",
            "m": 15000,
            "hl": SERPAPI_HL,
           "gl": SERPAPI_GL,
        }

        data = self._request(
            params,
            cache_prefix,
            cache_hours=24
        )

        rows = (
            data.get(
                "local_results"
            )
            or []
        )

        results = []

        for position, item in enumerate(
            rows,
            start=1
        ):

            rating = self._number(
                item.get("rating")
            )

            reviews = self._integer(
                item.get("reviews")
            )

            price = item.get(
                "price"
            )

            gps = item.get(
                "gps_coordinates"
            ) or {}

            links = item.get(
                "links"
            ) or {}

            results.append({
                "candidate_id": (
                    f"local_{cache_prefix}_"
                    f"{position}_"
                    f"{item.get('data_id', '')}"
                ),
                "rank_position": position,
                "name": (
                    item.get("title")
                    or ""
                ),
                "rating": rating,
                "reviews": reviews,
                "price": price,
                "type": (
                    item.get("type")
                    or ""
                ),
                "address": (
                    item.get("address")
                    or ""
                ),
                "description": (
                    item.get("description")
                    or ""
                ),
                "hours": (
                    item.get("hours")
                    or ""
                ),
                "gps": gps,
                "website": (
                    links.get(
                        "website"
                    )
                    if isinstance(
                        links,
                        dict
                    )
                    else ""
                ),
                "place_link": (
                    item.get(
                        "link"
                    )
                    or ""
                ),
                "data_id": (
                    item.get(
                        "data_id"
                    )
                    or ""
                ),
                "source": (
                    "Google Maps via SerpApi"
                ),
            })

        return results

    # =========================================================
    # RESTAURANTS
    # =========================================================

    def search_restaurants(
        self,
        destination: str,
        special_notes: str = ""
    ) -> List[Dict[str, Any]]:

        extra = ""

        if special_notes:
            extra = (
                f" {special_notes}"
            )

        return self.search_local(
            query=(
                f"best restaurants in "
                f"{destination} Turkey"
                f"{extra}"
            ),
            location=destination,
            cache_prefix="restaurants"
        )

    # =========================================================
    # ATTRACTIONS
    # =========================================================

    def search_attractions(
        self,
        destination: str
    ) -> List[Dict[str, Any]]:

        results = self.search_local(
            query=(
                f"best tourist attractions "
                f"and places to visit in "
                f"{destination} Turkey"
            ),
            location=destination,
            cache_prefix="attractions"
        )

        return results

    # =========================================================
    # TRANSPORT SEARCH
    # =========================================================

    def search_transport(
        self,
        origin: str,
        destination: str,
        date: str,
        mode: str
    ) -> List[Dict[str, Any]]:

        mode_map = {
            "Bus": "bus",
            "Plane": "flight",
            "Train": "train",
            "Passenger Ferry": (
                "passenger ferry"
            ),
            "Car Ferry": (
                "car ferry"
            ),
        }

        mode_name = mode_map.get(
            mode,
            mode.lower()
        )

        query = (
            f"{origin} to {destination} "
            f"{mode_name} "
            f"{date} companies prices"
        )

        params = {
            "engine": "google",
            "q": query,
            "location": (
                f"{origin}, Turkey"
            ),
            "hl": SERPAPI_HL,
            "gl": SERPAPI_GL,
            "num": 10,
        }

        data = self._request(
            params,
            "transport",
            cache_hours=1
        )

        organic = (
            data.get(
                "organic_results"
            )
            or []
        )

        local = (
            data.get(
                "local_results"
            )
            or []
        )

        candidates = []

        for position, item in enumerate(
            organic,
            start=1
        ):

            title = (
                item.get("title")
                or ""
            )

            snippet = (
                item.get("snippet")
                or ""
            )

            text = (
                title
                + " "
                + snippet
            )

            company = (
                self._extract_company(
                    title,
                    text,
                    mode
                )
            )

            price = self._extract_price(
                text
            )

            candidates.append({
                "candidate_id": (
                    f"transport_search_{position}"
                ),
                "position": position,
                "company": company,
                "title": title,
                "snippet": snippet,
                "price_try": price,
                "link": item.get(
                    "link",
                    ""
                ),
                "source": "Google Search via SerpApi",
            })

        for position, item in enumerate(
            local,
            start=1
        ):

            candidates.append({
                "candidate_id": (
                    f"transport_local_{position}"
                ),
                "position": position,
                "company": (
                    item.get(
                        "title"
                    )
                    or ""
                ),
                "title": (
                    item.get(
                        "title"
                    )
                    or ""
                ),
                "snippet": (
                    item.get(
                        "description"
                    )
                    or ""
                ),
                "price_try": self._number(
                    item.get(
                        "price"
                    )
                ),
                "link": (
                    item.get(
                        "link"
                    )
                    or ""
                ),
                "source": "Google Maps via SerpApi",
            })

        return candidates

    # =========================================================
    # HELPERS
    # =========================================================

    @staticmethod
    def _number(
        value: Any
    ) -> Optional[float]:

        if value is None:
            return None

        try:
            return float(value)
        except (
            ValueError,
            TypeError
        ):
            return None

    @staticmethod
    def _integer(
        value: Any
    ) -> Optional[int]:

        if value is None:
            return None

        if isinstance(
            value,
            int
        ):
            return value

        if isinstance(
            value,
            float
        ):
            return int(value)

        match = re.search(
            r"\d[\d,]*",
            str(value)
        )

        if not match:
            return None

        try:
            return int(
                match.group(
                    0
                ).replace(
                    ",",
                    ""
                )
            )
        except ValueError:
            return None

    @staticmethod
    def _extract_price(
        text: str
    ) -> Optional[float]:

        if not text:
            return None

        patterns = [
            r"(\d[\d,.]*)\s*(?:₺|TRY|TL)",
            r"TRY\s*(\d[\d,.]*)",
            r"TL\s*(\d[\d,.]*)",
        ]

        for pattern in patterns:

            match = re.search(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            if not match:
                continue

            raw = (
                match.group(1)
                .replace(
                    ",",
                    ""
                )
            )

            try:
                return float(
                    raw
                )
            except ValueError:
                continue

        return None

    @staticmethod
    def _extract_company(
        title: str,
        text: str,
        mode: str
    ) -> str:

        known = [
            "Kamil Koç",
            "Metro Turizm",
            "Pamukkale",
            "FlixBus",
            "Pegasus",
            "Turkish Airlines",
            "AJet",
            "TCDD",
            "İDO",
            "BUDO",
            "GESTAŞ",
            "Obilet",
        ]

        combined = (
            title
            + " "
            + text
        ).lower()

        for company in known:

            if company.lower() in combined:
                return company

        return (
            title[:100]
            if title
            else "Unknown operator"
        )

    # =========================================================
    # SCORE / RANK
    # =========================================================

    @staticmethod
    def hotel_score(
        hotel: Dict[str, Any],
        min_rating: float,
        requested_amenities: List[str]
    ) -> float:

        score = 0.0

        rating = (
            hotel.get("rating")
            or 0
        )

        price = (
            hotel.get(
                "total_price_try"
            )
        )

        reviews = (
            hotel.get("reviews")
            or 0
        )

        if rating >= min_rating:
            score += (
                40
                + rating * 5
            )
        else:
            score -= 100

        if price is not None:
            # Cheaper gets better score
            score += max(
                0,
                30_000
                / max(
                    price,
                    1
                )
            )

        score += min(
            reviews / 100,
            10
        )

        amenities_text = (
            " ".join(
                hotel.get(
                    "amenities",
                    []
                )
            ).lower()
        )

        for amenity in requested_amenities:

            aliases = {
                "pool": [
                    "pool",
                    "swimming"
                ],
                "beach": [
                    "beach",
                    "beachfront"
                ],
                "spa": [
                    "spa",
                    "sauna"
                ],
                "aquapark": [
                    "water park",
                    "water slide",
                    "aquapark"
                ]
            }

            terms = aliases.get(
                amenity,
                [amenity]
            )

            if any(
                x in amenities_text
                for x in terms
            ):
                score += 12

        return score

    @staticmethod
    def local_score(
        item: Dict[str, Any]
    ) -> float:

        rating = (
            item.get("rating")
            or 0
        )

        reviews = (
            item.get("reviews")
            or 0
        )

        return (
            rating * 10
            + min(
                reviews / 100,
                15
            )
        )

    @staticmethod
    def transport_score(
        item: Dict[str, Any]
    ) -> float:

        price = (
            item.get(
                "price_try"
            )
        )

        score = 0.0

        if price is not None:
            score += (
                10_000
                / max(
                    price,
                    1
                )
            )

        # Google result position is weak evidence,
        # so it only receives a small bonus.
        position = (
            item.get(
                "position"
            )
            or 50
        )

        score += max(
            0,
            10 - position * 0.2
        )

        return score