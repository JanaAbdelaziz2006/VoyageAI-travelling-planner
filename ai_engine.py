import json
import os
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Dict

import requests
from dotenv import load_dotenv

from ranking import (
    rank_hotels,
    rank_local,
    rank_transport,
    distinct_schedule
)

from search_engine import (
    SerpApi,
    SearchError
)


BASE_DIR = Path(__file__).resolve().parent

load_dotenv(
    BASE_DIR / ".env"
)


GEMINI_KEY = os.getenv(
    "GEMINI_API_KEY",
    ""
).strip()


GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
).strip()


GEMINI_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/"
    f"{GEMINI_MODEL}:generateContent"
)


class AIPlanError(Exception):
    pass


# =========================================================
# LANGUAGE / TRANSLATION HELPERS
# =========================================================

LANGUAGE_NAMES = {
    "tr": "Turkish",
    "en": "English",
    "ar": "Arabic"
}


TRANSLATIONS = {

    "en": {

        "missing_hotel_features":
            (
                "Not all requested hotel features were "
                "available together in the verified search "
                "results. The system selected the "
                "highest-ranked practical match instead "
                "of inventing a hotel."
            ),

        "no_hotel_candidate":
            (
                "No hotel candidate was returned from "
                "Google Hotels."
            ),

        "no_verified_transport":
            (
                "No specific transport company could "
                "be verified."
            ),

        "route_feasible_unverified":
            (
                "The route appears feasible, but a "
                "specific operator could not be verified "
                "from the current search results."
            ),

        "hotel_price_missing":
            (
                "The selected hotel's current total price "
                "was not returned by the provider. "
                "No price was invented."
            ),

        "transport_price_missing":
            (
                "The selected transport company was found, "
                "but a current ticket price was not returned "
                "by the provider."
            ),

        "day_title":
            "Day {day} in {destination}",

        "breakfast":
            (
                "Breakfast according to the selected "
                "meal plan."
            ),

        "lunch":
            (
                "Lunch at the recommended ranked restaurant."
            ),

        "dinner":
            (
                "Dinner according to the selected "
                "meal plan."
            ),

        "return_timing":
            (
                "Exact return timing is shown only when "
                "a verified departure time is available."
            ),

    },


    "tr": {

        "missing_hotel_features":
            (
                "İstenen tüm otel özellikleri doğrulanmış "
                "arama sonuçlarında aynı anda bulunamadı. "
                "Sistem bir otel uydurmak yerine en yüksek "
                "sıralı pratik eşleşmeyi seçti."
            ),

        "no_hotel_candidate":
            (
                "Google Hotels'tan otel adayı döndürülmedi."
            ),

        "no_verified_transport":
            (
                "Belirli bir ulaşım şirketi doğrulanamadı."
            ),

        "route_feasible_unverified":
            (
                "Rota uygun görünüyor ancak mevcut arama "
                "sonuçlarından belirli bir operatör doğrulanamadı."
            ),

        "hotel_price_missing":
            (
                "Seçilen otelin güncel toplam fiyatı sağlayıcı "
                "tarafından döndürülmedi. Fiyat uydurulmadı."
            ),

        "transport_price_missing":
            (
                "Seçilen ulaşım şirketi bulundu ancak güncel "
                "bilet fiyatı sağlayıcı tarafından döndürülmedi."
            ),

        "day_title":
            "{destination} — {day}. Gün",

        "breakfast":
            (
                "Seçilen yemek planına göre kahvaltı."
            ),

        "lunch":
            (
                "Önerilen sıralanmış restoranda öğle yemeği."
            ),

        "dinner":
            (
                "Seçilen yemek planına göre akşam yemeği."
            ),

        "return_timing":
            (
                "Kesin dönüş zamanı yalnızca doğrulanmış bir "
                "kalkış saati mevcut olduğunda gösterilir."
            ),

    },


    "ar": {

        "missing_hotel_features":
            (
                "لم تتوفر جميع مرافق الفندق المطلوبة معًا "
                "في نتائج البحث الموثوقة. اختار النظام أفضل "
                "تطابق عملي بدلًا من اختراع فندق."
            ),

        "no_hotel_candidate":
            (
                "لم يتم إرجاع أي فندق من Google Hotels."
            ),

        "no_verified_transport":
            (
                "تعذر التحقق من شركة نقل محددة."
            ),

        "route_feasible_unverified":
            (
                "يبدو أن الطريق ممكن، ولكن تعذر التحقق من "
                "مشغل محدد من نتائج البحث الحالية."
            ),

        "hotel_price_missing":
            (
                "لم يُرجع المزود السعر الإجمالي الحالي للفندق "
                "المختار. لم يتم اختراع أي سعر."
            ),

        "transport_price_missing":
            (
                "تم العثور على شركة النقل المختارة، ولكن "
                "لم يُرجع المزود سعر تذكرة حاليًا."
            ),

        "day_title":
            "اليوم {day} في {destination}",

        "breakfast":
            (
                "الإفطار وفقًا لخطة الوجبات المختارة."
            ),

        "lunch":
            (
                "الغداء في المطعم الموصى به والأعلى ترتيبًا."
            ),

        "dinner":
            (
                "العشاء وفقًا لخطة الوجبات المختارة."
            ),

        "return_timing":
            (
                "يظهر وقت العودة الدقيق فقط عند توفر وقت "
                "مغادرة موثوق."
            ),

    }

}


def normalize_language(
    value: Any
) -> str:

    language = (
        str(value or "")
        .strip()
        .lower()
    )

    if language not in {
        "tr",
        "en",
        "ar"
    }:

        return "en"

    return language


def tr(
    language: str,
    key: str,
    **kwargs
) -> str:

    language = normalize_language(
        language
    )

    text = (
        TRANSLATIONS
        .get(language, {})
        .get(
            key
        )
    )

    if text is None:

        text = (
            TRANSLATIONS["en"]
            .get(
                key,
                key
            )
        )

    return text.format(
        **kwargs
    )


class HybridEngine:

    def __init__(self):

        self.search = SerpApi()


    # =========================================================
    # OPTIONAL GEMINI
    # =========================================================

    def _gemini(
        self,
        prompt: str
    ):

        # Gemini is optional.
        # Search results remain usable without it.

        if not GEMINI_KEY:

            return {}


        payload = {

            "contents": [

                {
                    "parts": [

                        {
                            "text":
                                prompt
                        }

                    ]
                }

            ],

            "generationConfig": {

                "temperature":
                    0.1,

                "responseMimeType":
                    "application/json"

            }

        }


        try:

            response = requests.post(

                GEMINI_URL,

                headers={

                    "Content-Type":
                        "application/json",

                    "x-goog-api-key":
                        GEMINI_KEY

                },

                json=payload,

                timeout=90

            )


        except requests.RequestException:

            # Do not break the travel search
            # because optional AI is unavailable.

            return {}


        if response.status_code == 429:

            return {}


        if response.status_code >= 400:

            return {}


        try:

            body = response.json()

            text = (
                body[
                    "candidates"
                ][
                    0
                ][
                    "content"
                ][
                    "parts"
                ][
                    0
                ][
                    "text"
                ]
            )

            return json.loads(
                text
            )


        except Exception:

            return {}


    # =========================================================
    # GOOGLE MAPS URL
    # =========================================================

    @staticmethod
    def maps_url(
        name,
        city
    ):

        from urllib.parse import quote

        return (
            "https://www.google.com/maps/search/"
            "?api=1&query="
            + quote(
                f"{name}, {city}"
            )
        )


    # =========================================================
    # MAIN
    # =========================================================

    def plan(
        self,
        data: Dict[str, Any]
    ):

        language = normalize_language(
            data.get(
                "language"
            )
        )


        start = date.fromisoformat(
            data[
                "start_date"
            ]
        )


        end = (
            start
            + timedelta(
                days=data[
                    "nights"
                ]
            )
        )


        end_date = end.isoformat()


        children = data[
            "children_count"
        ]


        child_ages = (

            [
                data[
                    "child_age"
                ]
                for _ in range(
                    children
                )
            ]

            if (
                children
                and data.get(
                    "child_age"
                )
                is not None
            )

            else []

        )


        # =====================================================
        # HOTELS
        # =====================================================

        hotels = self.search.hotels(

            data[
                "destination"
            ],

            start.isoformat(),

            end_date,

            data[
                "adults_count"
            ],

            children,

            child_ages,

            data[
                "rooms_count"
            ]

        )


        ranked_hotels = rank_hotels(

            hotels,

            data[
                "amenities"
            ]

        )


        selected_hotel = (

            ranked_hotels[0]

            if ranked_hotels

            else None

        )


        hotel_warning = ""


        if selected_hotel:

            requested = data[
                "amenities"
            ]


            matched = selected_hotel.get(
                "amenity_matches",
                0
            )


            if (
                requested
                and matched
                < len(requested)
            ):

                hotel_warning = tr(
                    language,
                    "missing_hotel_features"
                )


        # =====================================================
        # RESTAURANTS
        # =====================================================

        restaurants = self.search.local(

            (
                "best restaurants in "
                f"{data['destination']} Turkey"
            ),

            data[
                "destination"
            ],

            "restaurants"

        )


        ranked_restaurants = rank_local(
            restaurants
        )


        # =====================================================
        # ATTRACTIONS
        # =====================================================

        places = self.search.local(

            (
                "best tourist attractions "
                "and places to visit in "
                f"{data['destination']} Turkey"
            ),

            data[
                "destination"
            ],

            "attractions"

        )


        ranked_places = rank_local(
            places
        )


        # =====================================================
        # TRANSPORT
        # =====================================================

        transport_mode = data[
            "transport_mode"
        ]


        transport_candidates = []

        transport_feasible = True

        transport_warning = ""

        directions_summary = None


        if transport_mode in {

            "Bus",
            "Train",
            "Passenger Ferry",
            "Car Ferry"

        }:

            preference = {

                "Bus":
                    "bus",

                "Train":
                    "train",

                "Passenger Ferry":
                    None,

                "Car Ferry":
                    None

            }.get(
                transport_mode
            )


            # First check whether the requested
            # transport type is actually possible.

            directions = self.search.directions(

                (
                    data["origin"]
                    + ", Turkey"
                ),

                (
                    data["destination"]
                    + ", Turkey"
                ),

                prefer=preference,

                travel_mode="3"

            )


            directions_summary = (
                self.search.directions_summary(
                    directions
                )
            )


            if not directions_summary:

                transport_feasible = False

                transport_warning = tr(
                    language,
                    "no_route",
                    mode=transport_mode,
                    origin=data["origin"],
                    destination=data["destination"]
                )

            if transport_feasible:

                transport_candidates = (

                    self.search.google_search(

                        (
                            f"{data['origin']} to "
                            f"{data['destination']} "
                            f"{transport_mode} "
                            f"{start.isoformat()} "
                            "companies tickets"
                        ),

                        (
                            "transport_"
                            + transport_mode
                        ),

                        10

                    )

                )


        elif transport_mode == "Plane":

            transport_candidates = (

                self.search.google_search(

                    (
                        f"{data['origin']} to "
                        f"{data['destination']} "
                        f"flight airlines "
                        f"{start.isoformat()}"
                    ),

                    "transport_plane",

                    10

                )

            )


        transport_ranked = rank_transport(
            transport_candidates
        )


        selected_transport = (

            transport_ranked[0]

            if transport_ranked

            else None

        )


        if (
            transport_feasible
            and not selected_transport
            and transport_mode
            not in {
                "Own Car",
                "Own EV"
            }
        ):

            transport_warning = tr(
                language,
                "route_feasible_unverified"
            )


        # =====================================================
        # HOTEL TRANSFER ROUTES
        # =====================================================

        to_hotel = None

        from_hotel = None


        if selected_hotel:

            hotel_target = (

                selected_hotel.get(
                    "address"
                )

                or

                selected_hotel.get(
                    "name"
                )
                + ", "
                + data[
                    "destination"
                ]
                + ", Turkey"

            )


            terminal_name = {

                "Bus":
                    (
                        "main intercity bus "
                        "station "
                    ),

                "Train":
                    (
                        "main railway station "
                    ),

                "Passenger Ferry":
                    (
                        "passenger ferry terminal "
                    ),

                "Car Ferry":
                    (
                        "car ferry terminal "
                    ),

                "Plane":
                    (
                        "main airport "
                    )

            }.get(

                transport_mode,

                "main transport terminal "

            )


            terminal_target = (

                terminal_name
                + data[
                    "destination"
                ]
                + ", Turkey"

            )


            preference = (

                "bus,subway,train"

                if transport_mode
                in {
                    "Bus",
                    "Train"
                }

                else None

            )


            to_hotel_data = (
                self.search.directions(

                    terminal_target,

                    hotel_target,

                    prefer=preference,

                    travel_mode="3"

                )
            )


            from_hotel_data = (
                self.search.directions(

                    hotel_target,

                    terminal_target,

                    prefer=preference,

                    travel_mode="3"

                )
            )


            to_hotel = (
                self.search.directions_summary(
                    to_hotel_data
                )
            )


            from_hotel = (
                self.search.directions_summary(
                    from_hotel_data
                )
            )


        # =====================================================
        # DAILY SCHEDULE
        # =====================================================

        day_pairs = distinct_schedule(

            ranked_places,

            ranked_restaurants,

            data[
                "nights"
            ]

        )


        daily_schedule = []


        for day_number, (
            day_places,
            day_restaurants
        ) in enumerate(

            day_pairs,

            start=1

        ):

            calendar_date = (

                start
                + timedelta(
                    days=day_number - 1
                )

            ).isoformat()


            activities = []


            for index, place in enumerate(
                day_places
            ):

                activities.append({

                    "candidate_id":
                        place[
                            "candidate_id"
                        ],

                    "time_slot":
                        (
                            "10:00"
                            if index == 0
                            else "15:00"
                        ),

                    "place_name":
                        place[
                            "name"
                        ],

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
                        (
                            place.get(
                                "link"
                            )
                            or
                            self.maps_url(
                                place[
                                    "name"
                                ],

                                data[
                                    "destination"
                                ]
                            )
                        ),

                    "source_url":
                        place.get(
                            "link",
                            ""
                        )

                })


            restaurant_results = []


            for restaurant in day_restaurants:

                restaurant_results.append({

                    "candidate_id":
                        restaurant[
                            "candidate_id"
                        ],

                    "meal_type":
                        tr(
                            language,
                            "lunch"
                        ),

                    "restaurant_name":
                        restaurant[
                            "name"
                        ],

                    "cuisine":
                        restaurant.get(
                            "type",
                            ""
                        ),

                    "address":
                        restaurant.get(
                            "address",
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

                    "price_level":
                        restaurant.get(
                            "price_level"
                        ),

                    "map_url":
                        (
                            restaurant.get(
                                "link"
                            )
                            or
                            self.maps_url(
                                restaurant[
                                    "name"
                                ],

                                data[
                                    "destination"
                                ]
                            )
                        ),

                    "source_url":
                        restaurant.get(
                            "link",
                            ""
                        )

                })


            daily_schedule.append({

                "day_number":
                    day_number,

                "calendar_date":
                    calendar_date,

                "day_title":
                    tr(
                        language,
                        "day_title",
                        day=day_number,
                        destination=data["destination"]
                    ),

                "breakfast_banner":
                    tr(
                        language,
                        "breakfast"
                    ),

                "lunch_banner":
                    tr(
                        language,
                        "lunch"
                    ),

                "dinner_banner":
                    tr(
                        language,
                        "dinner"
                    ),

                "activities":
                    activities,

                "restaurants":
                    restaurant_results

            })


        # =====================================================
        # OPTIONAL GEMINI EXPLANATIONS / TRANSLATION
        # =====================================================

        ai = {}


        if GEMINI_KEY:

            language_name = LANGUAGE_NAMES[
                language
            ]


            prompt = f"""

You are the explanation and translation layer
of VoyageAI.

The user's selected language is:
{language_name}

IMPORTANT RULES:

1. Return all explanatory prose in {language_name}.
2. Keep the product name "VoyageAI" exactly as "VoyageAI".
3. Do not translate or alter official proper names,
   including actual hotel names, restaurant names,
   attraction names, transport company names,
   brand names, URLs, addresses, airport names,
   and station names.
4. Generic descriptive words may be translated.
5. Do not invent factual information.
6. Do not invent prices, ratings, reviews, addresses,
   routes, opening hours, companies, or URLs.
7. Use only the information supplied below.
8. If information is unavailable, say so in {language_name}.
9. Return valid JSON only.

Your task is to:

- explain why the hotel was selected;
- explain why the transport was selected;
- explain the arrival transfer;
- explain the departure transfer.

DATA:

{json.dumps({

    "hotel":
        selected_hotel,

    "transport":
        selected_transport,

    "transport_feasible":
        transport_feasible,

    "transport_warning":
        transport_warning,

    "daily_schedule":
        daily_schedule,

    "hotel_warning":
        hotel_warning,

    "to_hotel":
        to_hotel,

    "from_hotel":
        from_hotel

}, ensure_ascii=False)}

Return exactly this JSON structure:

{{
    "hotel_explanation": "",
    "transport_explanation": "",
    "arrival_transfer_explanation": "",
    "departure_transfer_explanation": ""
}}

"""


            ai = self._gemini(
                prompt
            )


        # =====================================================
        # WARNINGS
        # =====================================================

        warnings = []


        if hotel_warning:

            warnings.append(
                hotel_warning
            )


        if not selected_hotel:

            warnings.append(
                tr(
                    language,
                    "no_hotel_candidate"
                )
            )


        if not transport_feasible:

            warnings.append(
                transport_warning
            )


        elif (
            transport_mode
            not in {
                "Own Car",
                "Own EV"
            }
            and not selected_transport
        ):

            warnings.append(
                tr(
                    language,
                    "no_verified_transport"
                )
            )


        if (
            selected_hotel
            and
            selected_hotel.get(
                "total_price_try"
            ) is None
        ):

            warnings.append(
                tr(
                    language,
                    "hotel_price_missing"
                )
            )


        if (
            selected_transport
            and
            selected_transport.get(
                "price_try"
            ) is None
        ):

            warnings.append(
                tr(
                    language,
                    "transport_price_missing"
                )
            )


        # =====================================================
        # COST
        # =====================================================

        hotel_total = (

            selected_hotel.get(
                "total_price_try"
            )

            if selected_hotel

            else None

        )


        transport_price = (

            selected_transport.get(
                "price_try"
            )

            if selected_transport

            else None

        )


        grand_total = None


        values = [

            hotel_total,

            transport_price

        ]


        numeric_values = [

            value

            for value in values

            if isinstance(
                value,
                (int, float)
            )

        ]


        if numeric_values:

            grand_total = sum(
                numeric_values
            )


        # =====================================================
        # SOURCES
        # =====================================================

        sources = []


        if (
            selected_hotel
            and selected_hotel.get(
                "link"
            )
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
                "link"
            ):

                sources.append({

                    "title":
                        place.get(
                            "name",
                            "Place"
                        ),

                    "url":
                        place[
                            "link"
                        ]

                })


        for restaurant in ranked_restaurants[:10]:

            if restaurant.get(
                "link"
            ):

                sources.append({

                    "title":
                        restaurant.get(
                            "name",
                            "Restaurant"
                        ),

                    "url":
                        restaurant[
                            "link"
                        ]

                })


        if (
            selected_transport
            and
            selected_transport.get(
                "link"
            )
        ):

            sources.append({

                "title":
                    (
                        selected_transport.get(
                            "company"
                        )
                        or
                        selected_transport.get(
                            "title"
                        )
                        or
                        "Transport"
                    ),

                "url":
                    selected_transport[
                        "link"
                    ]

            })


        # =====================================================
        # FINAL RESULT
        # =====================================================

        return {

            "origin_city":
                data[
                    "origin"
                ],

            "destination_city":
                data[
                    "destination"
                ],

            "start_date":
                start.isoformat(),

            "end_date":
                end_date,

            "adults_count":
                data[
                    "adults_count"
                ],

            "children_count":
                data[
                    "children_count"
                ],

            "rooms_count":
                data[
                    "rooms_count"
                ],

            "total_travelers":
                (
                    data[
                        "adults_count"
                    ]
                    +
                    data[
                        "children_count"
                    ]
                ),

            "meal_board":
                data[
                    "meal_board"
                ],

            "grand_total_trip_cost_try":
                grand_total,


            "hotel": {

                "name":
                    (
                        selected_hotel.get(
                            "name",
                            ""
                        )
                        if selected_hotel
                        else ""
                    ),

                "rating":
                    (
                        selected_hotel.get(
                            "rating"
                        )
                        if selected_hotel
                        else None
                    ),

                "reviews":
                    (
                        selected_hotel.get(
                            "reviews"
                        )
                        if selected_hotel
                        else None
                    ),

                "stars":
                    (
                        selected_hotel.get(
                            "stars"
                        )
                        if selected_hotel
                        else None
                    ),

                "price_per_room_per_night_try":
                    (
                        selected_hotel.get(
                            "price_per_night_try"
                        )
                        if selected_hotel
                        else None
                    ),

                "total_hotel_cost_try":
                    hotel_total,

                "amenities":
                    (
                        selected_hotel.get(
                            "amenities",
                            []
                        )
                        if selected_hotel
                        else []
                    ),

                "address":
                    (
                        selected_hotel.get(
                            "address",
                            ""
                        )
                        if selected_hotel
                        else ""
                    ),

                "link":
                    (
                        selected_hotel.get(
                            "link",
                            ""
                        )
                        if selected_hotel
                        else ""
                    ),

                "verified":
                    bool(
                        selected_hotel
                    ),

                "ranking_score":
                    (
                        selected_hotel.get(
                            "ranking_score"
                        )
                        if selected_hotel
                        else None
                    ),

                "why":
                    ai.get(
                        "hotel_explanation",
                        ""
                    )

            },


            "transportation": {

                "mode":
                    transport_mode,

                "verified_route":
                    transport_feasible,

                "company":
                    (
                        selected_transport.get(
                            "company",
                            ""
                        )
                        if selected_transport
                        else ""
                    ),

                "title":
                    (
                        selected_transport.get(
                            "title",
                            ""
                        )
                        if selected_transport
                        else ""
                    ),

                "snippet":
                    (
                        selected_transport.get(
                            "snippet",
                            ""
                        )
                        if selected_transport
                        else ""
                    ),

                "price_try":
                    transport_price,

                "link":
                    (
                        selected_transport.get(
                            "link",
                            ""
                        )
                        if selected_transport
                        else ""
                    ),

                "verified_operator":
                    bool(
                        selected_transport
                    ),

                "why":
                    ai.get(
                        "transport_explanation",
                        ""
                    ),

                "feasibility_warning":
                    transport_warning

            },


            "transfer_plan": {

                "to_hotel":
                    to_hotel,

                "from_hotel":
                    from_hotel,

                "arrival_explanation":
                    ai.get(
                        "arrival_transfer_explanation",
                        ""
                    ),

                "departure_explanation":
                    ai.get(
                        "departure_transfer_explanation",
                        ""
                    )

            },


            "daily_schedule":
                daily_schedule,


            "departure_day_buffer": {

                "checkout_time":
                    (
                        selected_hotel.get(
                            "check_out_time"
                        )
                        if selected_hotel
                        else "12:00"
                    ),

                "return_departure_time":
                    "",

                "arrival_at_home_time":
                    "",

                "explanation":
                    tr(
                        language,
                        "return_timing"
                    )

            },


            "cost_breakdown": {

                "hotel_total_try":
                    hotel_total,

                "transport_total_try":
                    transport_price,

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
                list(
                    dict.fromkeys(
                        warnings
                    )
                ),


            "candidate_counts": {

                "hotels":
                    len(
                        hotels
                    ),

                "restaurants":
                    len(
                        restaurants
                    ),

                "places":
                    len(
                        places
                    ),

                "transport":
                    len(
                        transport_candidates
                    )

            }

        }