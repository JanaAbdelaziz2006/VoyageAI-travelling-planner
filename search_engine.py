import hashlib
import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
from dotenv import load_dotenv


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

CACHE_DIR = BASE_DIR / ".cache"
CACHE_DIR.mkdir(exist_ok=True)

load_dotenv(BASE_DIR / ".env")


SERPAPI_KEY = os.getenv(
    "SERPAPI_KEY",
    ""
).strip()

SERPAPI_URL = (
    "https://serpapi.com/search.json"
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


# ============================================================
# CUSTOM ERROR
# ============================================================

class SearchError(Exception):
    pass


# ============================================================
# CACHE HELPERS
# ============================================================

def _cache_path(
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
    ).hexdigest()[:24]

    return (
        CACHE_DIR
        / f"{prefix}_{digest}.json"
    )


def _read_cache(
    path: Path,
    max_age_seconds: int
):

    try:

        if (
            time.time()
            - path.stat().st_mtime
            > max_age_seconds
        ):
            return None

        return json.loads(
            path.read_text(
                encoding="utf-8"
            )
        )

    except Exception:

        return None


def _write_cache(
    path: Path,
    data: Any
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


# ============================================================
# SERPAPI CLASS
# ============================================================

class SerpApi:

    def __init__(self):

        self.session = requests.Session()

        self.session.headers.update({
            "User-Agent":
                "VoyageAI/Final-Hybrid-1.0"
        })


    # ========================================================
    # GENERIC REQUEST
    # ========================================================

    def request(
        self,
        params: Dict[str, Any],
        cache_key: str,
        cache_hours: int = 1
    ):

        if not SERPAPI_KEY:

            raise SearchError(
                "SERPAPI_KEY is missing in .env"
            )


        full_params = dict(params)

        full_params[
            "api_key"
        ] = SERPAPI_KEY


        full_params.setdefault(
            "hl",
            SERPAPI_HL
        )

        full_params.setdefault(
            "gl",
            SERPAPI_GL
        )


        cache_file = _cache_path(
            cache_key,
            full_params
        )


        cached = _read_cache(
            cache_file,
            cache_hours * 3600
        )


        if cached is not None:

            return cached


        try:

            response = self.session.get(
                SERPAPI_URL,
                params=full_params,
                timeout=90
            )

        except requests.RequestException as exc:

            raise SearchError(
                f"SerpApi connection error: {exc}"
            ) from exc


        try:

            data = response.json()

        except Exception as exc:

            raise SearchError(
                f"SerpApi returned invalid JSON "
                f"(HTTP {response.status_code})"
            ) from exc


        # ----------------------------------------------------
        # HTTP errors
        # ----------------------------------------------------

        if response.status_code == 401:

            raise SearchError(
                "SerpApi API key is invalid."
            )


        if response.status_code == 429:

            raise SearchError(
                "SerpApi rate limit reached. "
                "Please wait and try again."
            )


        if response.status_code >= 400:

            raise SearchError(
                f"SerpApi error "
                f"{response.status_code}: "
                f"{data}"
            )


        # ----------------------------------------------------
        # Google may return HTTP 200 with an error field
        # when the search produced no results.
        # Do not crash the whole application.
        # ----------------------------------------------------

        if data.get("error"):

            error_text = str(
                data["error"]
            )


            if (
                "hasn't returned any results"
                in error_text.lower()
            ):

                return data


            raise SearchError(
                f"SerpApi error: "
                f"{error_text}"
            )


        _write_cache(
            cache_file,
            data
        )


        return data


    # ========================================================
    # HOTELS
    # ========================================================

    def hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        adults: int,
        children: int,
        child_ages: Optional[List[int]],
        rooms: int
    ):

        common = {

            "engine":
                "google_hotels",

            "q":
                (
                    f"hotels in "
                    f"{destination}, Turkey"
                ),

            "check_in_date":
                check_in,

            "check_out_date":
                check_out,

            "adults":
                adults,

            "children":
                children,

            "rooms":
                rooms,

            "currency":
                SERPAPI_CURRENCY
        }


        if child_ages:

            common[
                "children_ages"
            ] = ",".join(
                str(x)
                for x in child_ages
            )


        # ----------------------------------------------------
        # Multiple searches:
        # 1. Highest rating
        # 2. Lowest price
        # 3. Broad fallback
        #
        # We merge their results.
        # ----------------------------------------------------

        searches = [

            {
                **common,
                "sort_by":
                    "8"
            },

            {
                **common,
                "sort_by":
                    "3"
            },

            {
                "engine":
                    "google_hotels",

                "q":
                    destination,

                "check_in_date":
                    check_in,

                "check_out_date":
                    check_out,

                "adults":
                    adults,

                "children":
                    children,

                "rooms":
                    rooms,

                "currency":
                    SERPAPI_CURRENCY
            }
        ]


        merged = []

        seen = set()


        for index, params in enumerate(
            searches
        ):

            try:

                response = self.request(
                    params,

                    (
                        f"hotel_search_"
                        f"{index}_"
                        f"{destination}"
                    ),

                    1
                )

            except SearchError as exc:

                # If only this particular Google search
                # returned no results, continue with the
                # other hotel searches.
                if (
                    "hasn't returned any results"
                    in str(exc).lower()
                ):

                    continue

                raise


            properties = (
                response.get(
                    "properties"
                )
                or []
            )


            for position, hotel in enumerate(
                properties,
                start=1
            ):

                token = (

                    hotel.get(
                        "property_token"
                    )

                    or hotel.get(
                        "name"
                    )

                    or f"hotel-{position}"
                )


                if token in seen:

                    continue


                seen.add(
                    token
                )


                nightly = (
                    hotel.get(
                        "rate_per_night"
                    )
                    or {}
                )


                total = (
                    hotel.get(
                        "total_rate"
                    )
                    or {}
                )


                link = (

                    hotel.get(
                        "link"
                    )

                    or hotel.get(
                        "hotel_link"
                    )

                    or ""
                )


                merged.append({

                    "candidate_id":
                        (
                            "hotel_"
                            + str(token)
                        ),

                    "name":
                        hotel.get(
                            "name",
                            ""
                        ),

                    "rating":
                        hotel.get(
                            "overall_rating"
                        ),

                    "reviews":
                        hotel.get(
                            "reviews"
                        ),

                    "stars":
                        hotel.get(
                            "hotel_class"
                        ),

                    "price_per_night_try":
                        nightly.get(
                            "extracted_lowest"
                        ),

                    "total_price_try":
                        total.get(
                            "extracted_lowest"
                        ),

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

                    "link":
                        link,

                    "description":
                        hotel.get(
                            "description",
                            ""
                        ),

                    "check_in_time":
                        hotel.get(
                            "check_in_time",
                            ""
                        ),

                    "check_out_time":
                        hotel.get(
                            "check_out_time",
                            ""
                        ),

                    "nearby_places":
                        hotel.get(
                            "nearby_places",
                            []
                        ),

                    "source":
                        "Google Hotels via SerpApi"
                })


        return merged


    # ========================================================
    # LOCAL / GOOGLE MAPS
    # ========================================================

    def local(
        self,
        query: str,
        location: str,
        cache_key: str
    ):

        params = {

            "engine":
                "google_maps",

            "type":
                "search",

            "q":
                query,

            "location":
                (
                    f"{location}, Turkey"
                ),

            # Required when location is supplied
            "z":
                12,

            "hl":
                SERPAPI_HL,

            "gl":
                SERPAPI_GL
        }


        data = self.request(
            params,
            cache_key,
            24
        )


        results = []


        for position, item in enumerate(
            data.get(
                "local_results"
            )
            or [],
            start=1
        ):

            links = (
                item.get(
                    "links"
                )
                or {}
            )


            results.append({

                "candidate_id":
                    (
                        f"{cache_key}_"
                        f"{item.get('data_id') or position}"
                    ),

                "name":
                    item.get(
                        "title",
                        ""
                    ),

                "rating":
                    item.get(
                        "rating"
                    ),

                "reviews":
                    item.get(
                        "reviews"
                    ),

                "price_level":
                    item.get(
                        "price"
                    ),

                "type":
                    item.get(
                        "type",
                        ""
                    ),

                "address":
                    item.get(
                        "address",
                        ""
                    ),

                "description":
                    item.get(
                        "description",
                        ""
                    ),

                "hours":
                    item.get(
                        "hours",
                        ""
                    ),

                "gps":
                    item.get(
                        "gps_coordinates",
                        {}
                    ),

                "website":
                    links.get(
                        "website",
                        ""
                    ),

                "link":
                    item.get(
                        "link",
                        ""
                    ),

                "source":
                    "Google Maps via SerpApi",

                "position":
                    position
            })


        return results


    # ========================================================
    # GOOGLE SEARCH
    # ========================================================

    def google_search(
        self,
        query: str,
        cache_key: str,
        num: int = 10
    ):

        params = {

            "engine":
                "google",

            "q":
                query,

            "num":
                num,

            "hl":
                SERPAPI_HL,

            "gl":
                SERPAPI_GL
        }


        data = self.request(
            params,
            cache_key,
            1
        )


        results = []


        for position, item in enumerate(
            data.get(
                "organic_results"
            )
            or [],
            start=1
        ):

            title = (
                item.get(
                    "title",
                    ""
                )
            )


            snippet = (
                item.get(
                    "snippet",
                    ""
                )
            )


            combined = (
                title
                + " "
                + snippet
            )


            results.append({

                "candidate_id":
                    (
                        f"{cache_key}_"
                        f"{position}"
                    ),

                "position":
                    position,

                "title":
                    title,

                "snippet":
                    snippet,

                "link":
                    item.get(
                        "link",
                        ""
                    ),

                "price_try":
                    self._extract_try_price(
                        combined
                    ),

                "company":
                    self._known_operator(
                        combined
                    ),

                "source":
                    "Google Search via SerpApi"
            })


        return results


    # ========================================================
    # GOOGLE MAPS DIRECTIONS
    # ========================================================

    def directions(
        self,
        start: str,
        end: str,
        prefer: Optional[str] = None,
        travel_mode: str = "3"
    ):

        params = {

            "engine":
                "google_maps_directions",

            "start_addr":
                start,

            "end_addr":
                end,

            "travel_mode":
                travel_mode,

            "hl":
                SERPAPI_HL,

            "gl":
                SERPAPI_GL
        }


        if prefer:

            params[
                "prefer"
            ] = prefer


        cache_key = (

            "directions_"
            + start
            + "|"
            + end
            + "|"
            + travel_mode
            + "|"
            + str(
                prefer or ""
            )
        )


        return self.request(
            params,
            cache_key,
            1
        )


    # ========================================================
    # DIRECTIONS SUMMARY
    # ========================================================

    @staticmethod
    def directions_summary(
        data
    ):

        if not data:

            return None


        directions = (
            data.get(
                "directions"
            )
            or []
        )


        if not directions:

            return None


        route = directions[0]


        return {

            "duration":
                route.get(
                    "duration",
                    ""
                ),

            "distance":
                route.get(
                    "distance",
                    ""
                ),

            "steps":
                route.get(
                    "steps",
                    []
                ),

            "summary":
                route.get(
                    "summary",
                    ""
                ),

            "link":
                route.get(
                    "link",
                    ""
                )
        }


    # ========================================================
    # PRICE EXTRACTION
    # ========================================================

    @staticmethod
    def _extract_try_price(
        text: str
    ):

        patterns = [

            r"(\d[\d.,]*)\s*(?:₺|TL|TRY)",

            r"(?:TL|TRY|₺)\s*(\d[\d.,]*)"
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
                    ".",
                    ""
                )

                .replace(
                    ",",
                    "."
                )
            )


            try:

                return float(
                    raw
                )

            except ValueError:

                continue


        return None


    # ========================================================
    # KNOWN TRANSPORT OPERATORS
    # ========================================================

    @staticmethod
    def _known_operator(
        text: str
    ):

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
            "GESTAŞ"
        ]


        lowered = text.casefold()


        for company in known:

            if (
                company.casefold()
                in lowered
            ):

                return company


        return ""