from typing import Any, Dict, List, Tuple


def rank_hotels(
    hotels: List[Dict[str, Any]],
    min_rating: float,
    amenities: List[str]
) -> List[Dict[str, Any]]:

    ranked = []

    for hotel in hotels:

        rating = hotel.get("rating") or 0

        if rating < min_rating:
            continue

        score = 0.0

        # Rating
        score += rating * 5

        # Number of reviews
        reviews = hotel.get("reviews") or 0
        score += min(reviews / 100, 10)

        # Price
        total_price = hotel.get("total_price_try")

        if total_price is not None:
            # Lower price gets a higher score
            score += 40000 / max(total_price, 1)

        # Requested amenities
        amenity_text = " ".join(
            hotel.get("amenities", [])
        ).lower()

        aliases = {
            "pool": [
                "pool",
                "swimming pool"
            ],
            "spa": [
                "spa",
                "sauna",
                "turkish bath"
            ],
            "beach": [
                "beach",
                "beachfront",
                "private beach"
            ],
            "aquapark": [
                "water park",
                "water slide",
                "aquapark"
            ]
        }

        matched = 0

        for requested in amenities:

            terms = aliases.get(
                requested,
                [requested]
            )

            if any(
                term in amenity_text
                for term in terms
            ):
                matched += 1

        score += matched * 15

        copy_item = dict(hotel)

        copy_item["ranking_score"] = round(
            score,
            3
        )

        copy_item["amenity_matches"] = matched

        ranked.append(copy_item)

    ranked.sort(
        key=lambda x: x["ranking_score"],
        reverse=True
    )

    for index, hotel in enumerate(
        ranked,
        start=1
    ):
        hotel["final_rank"] = index

    return ranked


def rank_local_places(
    places: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    ranked = []

    for place in places:

        rating = place.get("rating") or 0
        reviews = place.get("reviews") or 0

        score = (
            rating * 10
            + min(reviews / 100, 20)
        )

        copy_item = dict(place)

        copy_item["ranking_score"] = round(
            score,
            3
        )

        ranked.append(copy_item)

    ranked.sort(
        key=lambda x: x["ranking_score"],
        reverse=True
    )

    for index, place in enumerate(
        ranked,
        start=1
    ):
        place["final_rank"] = index

    return ranked


def rank_transport(
    candidates: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    ranked = []

    for item in candidates:

        score = 0.0

        price = item.get("price_try")

        if price is not None:
            # Lower price gets a higher score
            score += 10000 / max(
                price,
                1
            )

        position = item.get(
            "position",
            10
        )

        # Slight bonus for higher-ranked search results
        score += max(
            0,
            10 - position
        )

        copy_item = dict(item)

        copy_item["ranking_score"] = round(
            score,
            3
        )

        ranked.append(copy_item)

    ranked.sort(
        key=lambda x: x["ranking_score"],
        reverse=True
    )

    for index, item in enumerate(
        ranked,
        start=1
    ):
        item["final_rank"] = index

    return ranked


def pick_distinct_days(
    ranked_places: List[Dict[str, Any]],
    ranked_restaurants: List[Dict[str, Any]],
    nights: int
) -> List[
    Tuple[
        List[Dict[str, Any]],
        List[Dict[str, Any]]
    ]
]:

    result = []

    place_index = 0
    restaurant_index = 0

    for _ in range(nights):

        day_places = []
        day_restaurants = []

        # Two different places per day
        for _ in range(2):

            if place_index < len(
                ranked_places
            ):

                day_places.append(
                    ranked_places[
                        place_index
                    ]
                )

                place_index += 1

        # One different restaurant per day
        if restaurant_index < len(
            ranked_restaurants
        ):

            day_restaurants.append(
                ranked_restaurants[
                    restaurant_index
                ]
            )

            restaurant_index += 1

        result.append(
            (
                day_places,
                day_restaurants
            )
        )

    return result