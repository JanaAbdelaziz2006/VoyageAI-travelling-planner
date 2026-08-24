from typing import Any, Dict, List


AMENITY_ALIASES = {

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
        "private beach",
        "seaside"
    ],

    "aquapark": [
        "water park",
        "water slide",
        "aquapark"
    ],
}


def _number(value):

    try:
        return float(value)

    except (
        TypeError,
        ValueError
    ):

        return None


def _review_score(
    reviews
):

    try:

        return min(
            float(reviews or 0)
            / 100,
            15
        )

    except (
        TypeError,
        ValueError
    ):

        return 0


def _amenity_text(
    item
):

    return " ".join(
        str(x)
        for x in (
            item.get(
                "amenities"
            )
            or []
        )
    ).casefold()


def amenity_match(
    hotel,
    requested
):

    text = _amenity_text(
        hotel
    )


    aliases = AMENITY_ALIASES.get(
        requested.casefold(),
        [
            requested.casefold()
        ]
    )


    return any(
        term in text
        for term in aliases
    )


def rank_hotels(
    hotels: List[Dict[str, Any]],
    requested: List[str]
):

    ranked = []

    seen = set()


    for hotel in hotels:

        candidate_id = (
            hotel.get(
                "candidate_id"
            )
        )


        if (
            not candidate_id
            or candidate_id in seen
        ):
            continue


        seen.add(
            candidate_id
        )


        rating = (
            _number(
                hotel.get(
                    "rating"
                )
            )
            or 0
        )


        price = (
            _number(
                hotel.get(
                    "total_price_try"
                )
            )
        )


        reviews = _review_score(
            hotel.get(
                "reviews"
            )
        )


        matched = sum(
            1
            for amenity
            in requested
            if amenity_match(
                hotel,
                amenity
            )
        )


        # Rating is the main quality component.
        score = (
            rating * 10
            + reviews
        )


        # Requested amenities are strongly preferred,
        # but they are NOT an all-or-nothing filter.
        score += (
            matched * 20
        )


        # Cheaper options get preference.
        if price is not None:

            score += (
                25000
                / max(
                    price,
                    1
                )
            )


        item = dict(
            hotel
        )


        item[
            "ranking_score"
        ] = round(
            score,
            4
        )


        item[
            "amenity_matches"
        ] = matched


        ranked.append(
            item
        )


    ranked.sort(
        key=lambda x: (
            x[
                "amenity_matches"
            ],

            x[
                "ranking_score"
            ],

            x.get(
                "rating"
            )
            or 0,

            -(
                x.get(
                    "total_price_try"
                )
                or 10**12
            )
        ),

        reverse=True
    )


    for index, hotel in enumerate(
        ranked,
        start=1
    ):

        hotel[
            "final_rank"
        ] = index


    return ranked


def rank_local(
    items: List[Dict[str, Any]]
):

    ranked = []

    seen = set()


    for item in items:

        candidate_id = (
            item.get(
                "candidate_id"
            )
        )


        if (
            not candidate_id
            or candidate_id in seen
        ):
            continue


        seen.add(
            candidate_id
        )


        rating = (
            _number(
                item.get(
                    "rating"
                )
            )
            or 0
        )


        reviews = _review_score(
            item.get(
                "reviews"
            )
        )


        price_level = (
            item.get(
                "price_level"
            )
        )


        price_score = 0


        if isinstance(
            price_level,
            (int, float)
        ):

            price_score = max(
                0,
                6 - float(
                    price_level
                )
            )


        copy_item = dict(
            item
        )


        copy_item[
            "ranking_score"
        ] = round(
            (
                rating * 10
                + reviews
                + price_score
            ),
            4
        )


        ranked.append(
            copy_item
        )


    ranked.sort(
        key=lambda x: (
            x[
                "ranking_score"
            ],

            x.get(
                "rating"
            )
            or 0,

            x.get(
                "reviews"
            )
            or 0
        ),

        reverse=True
    )


    for index, item in enumerate(
        ranked,
        start=1
    ):

        item[
            "final_rank"
        ] = index


    return ranked


def rank_transport(
    items: List[Dict[str, Any]]
):

    ranked = []

    seen = set()


    for item in items:

        candidate_id = (
            item.get(
                "candidate_id"
            )
        )


        if (
            not candidate_id
            or candidate_id in seen
        ):
            continue


        seen.add(
            candidate_id
        )


        price = (
            _number(
                item.get(
                    "price_try"
                )
            )
        )


        score = 0


        if price is not None:

            score += (
                10000
                / max(
                    price,
                    1
                )
            )


        position = (
            item.get(
                "position"
            )
            or 10
        )


        score += max(
            0,
            10 - (
                float(position)
                * 0.25
            )
        )


        copy_item = dict(
            item
        )


        copy_item[
            "ranking_score"
        ] = round(
            score,
            4
        )


        ranked.append(
            copy_item
        )


    ranked.sort(
        key=lambda x:
            x[
                "ranking_score"
            ],
        reverse=True
    )


    for index, item in enumerate(
        ranked,
        start=1
    ):

        item[
            "final_rank"
        ] = index


    return ranked


def distinct_schedule(
    places,
    restaurants,
    nights
):

    results = []

    place_index = 0
    restaurant_index = 0


    for _ in range(
        nights
    ):

        day_places = []
        day_restaurants = []


        for _ in range(2):

            if (
                place_index
                < len(places)
            ):

                day_places.append(
                    places[
                        place_index
                    ]
                )

                place_index += 1


        if (
            restaurant_index
            < len(
                restaurants
            )
        ):

            day_restaurants.append(
                restaurants[
                    restaurant_index
                ]
            )

            restaurant_index += 1


        results.append(
            (
                day_places,
                day_restaurants
            )
        )


    return results