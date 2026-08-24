const state = {
    lang: "tr",
    currentData: null
};


const I18N = {

    tr: {
        search:
            "Ara & Planla",

        searching:
            "Canlı veriler aranıyor...",

        map:
            "Google Maps'te aç"
    },

    en: {
        search:
            "Search & Plan",

        searching:
            "Searching live data...",

        map:
            "Open in Google Maps"
    },

    ar: {
        search:
            "ابحث وخطط",

        searching:
            "جارٍ البحث المباشر...",

        map:
            "فتح في خرائط Google"
    }

};


const cities = [

    "Adana",
    "Adıyaman",
    "Afyonkarahisar",
    "Ağrı",
    "Aksaray",
    "Amasya",
    "Ankara",
    "Antalya",
    "Ardahan",
    "Artvin",
    "Aydın",
    "Balıkesir",
    "Bartın",
    "Batman",
    "Bayburt",
    "Bilecik",
    "Bingöl",
    "Bitlis",
    "Bolu",
    "Burdur",
    "Bursa",
    "Çanakkale",
    "Çankırı",
    "Çorum",
    "Denizli",
    "Diyarbakır",
    "Düzce",
    "Edirne",
    "Elazığ",
    "Erzincan",
    "Erzurum",
    "Eskişehir",
    "Gaziantep",
    "Giresun",
    "Gümüşhane",
    "Hakkâri",
    "Hatay",
    "Iğdır",
    "Isparta",
    "İstanbul",
    "İzmir",
    "Kahramanmaraş",
    "Karabük",
    "Karaman",
    "Kars",
    "Kastamonu",
    "Kayseri",
    "Kırıkkale",
    "Kırklareli",
    "Kırşehir",
    "Kilis",
    "Kocaeli",
    "Konya",
    "Kütahya",
    "Malatya",
    "Manisa",
    "Mardin",
    "Mersin",
    "Muğla",
    "Muş",
    "Nevşehir",
    "Niğde",
    "Ordu",
    "Osmaniye",
    "Rize",
    "Sakarya",
    "Samsun",
    "Siirt",
    "Sinop",
    "Sivas",
    "Şanlıurfa",
    "Şırnak",
    "Tekirdağ",
    "Tokat",
    "Trabzon",
    "Tunceli",
    "Uşak",
    "Van",
    "Yalova",
    "Yozgat",
    "Zonguldak"

];


const $ = (
    id
) =>
    document.getElementById(id);


const t = () =>
    I18N[
        state.lang
    ];


function esc(
    value
) {

    return String(
        value ?? ""
    )
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}


function fmtPrice(
    value
) {

    if (
        value === null
        ||
        value === undefined
        ||
        Number.isNaN(
            Number(
                value
            )
        )
    ) {

        return "—";

    }


    return (
        Number(
            value
        ).toLocaleString()
        + " TRY"
    );
}


function sourceLinks(
    items = []
) {

    const seen =
        new Set();


    return items

        .filter(
            item =>
                item?.url
                &&
                !seen.has(
                    item.url
                )
                &&
                seen.add(
                    item.url
                )
        )

        .slice(
            0,
            10
        )

        .map(
            item =>
                `
                <a
                    class="source-chip"
                    target="_blank"
                    rel="noopener"
                    href="${esc(
                        item.url
                    )}"
                >
                    ${esc(
                        item.title
                        || "Source"
                    )}
                </a>
                `
        )

        .join("");
}


async function api(
    path,
    payload
) {

    const response =
        await fetch(
            path,
            {
                method:
                    "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body:
                    JSON.stringify(
                        payload
                    )
            }
        );


    const body =
        await response
            .json()
            .catch(
                () => null
            );


    if (
        !response.ok
        ||
        !body?.success
    ) {

        throw new Error(
            body?.error
            ||
            `HTTP ${response.status}`
        );

    }


    return body.data;
}


function collectPayload() {

    const childrenCount =
        Number(
            $("children_count").value
            || 0
        );


    return {

        origin:
            $("origin").value,

        destination:
            $("destination").value,

        start_date:
            $("start_date").value,

        nights:
            Number(
                $("nights").value
                || 3
            ),

        adults_count:
            Number(
                $("adults_count").value
                || 2
            ),

        children_count:
            childrenCount,

        child_age:
            childrenCount
            ? Number(
                $("child_age").value
                || 1
            )
            : null,

        rooms_count:
            Number(
                $("rooms_count").value
                || 1
            ),

        transport_mode:
            $("transport_mode").value,

        budget_type:
            $("budget_mode").value,

        budget_amount_try:
            $("budget_amount_try").value
            ?
                Number(
                    $("budget_amount_try").value
                )
            :
                null,

        hotel_min_rating:
            Number(
                $("hotel_min_rating").value
                || 8
            ),

        hotel_location:
            $("hotel_location").value,

        amenities:
            [
                ...document.querySelectorAll(
                    "input[name='amenity']:checked"
                )
            ]
                .map(
                    input =>
                        input.value
                ),

        meal_board:
            $("meal_board").value,

        special_notes:
            $("special_notes").value
                .trim(),

        language:
            state.lang
    };
}


function renderHotel(
    hotel
) {

    if (
        !hotel
        ||
        !hotel.verified
    ) {

        return `
            <div class="card">

                <h3>
                    Recommended Hotel
                </h3>

                <p class="muted">
                    No verified hotel result
                    was returned.
                </p>

            </div>
        `;

    }


    return `
        <div class="card">

            <div class="row">

                <div>

                    <h3>
                        ${esc(
                            hotel.name
                        )}
                    </h3>

                    <p class="muted">

                        Rating:
                        ${hotel.rating ?? "—"}/10

                        ·

                        Reviews:
                        ${hotel.reviews ?? "—"}

                    </p>

                </div>


                <span class="verified">
                    ✓ Google Hotels
                </span>

            </div>


            <p class="muted">

                ${esc(
                    hotel.address
                    || ""
                )}

            </p>


            <div class="chips">

                ${
                    (
                        hotel.amenities
                        || []
                    )

                    .slice(
                        0,
                        12
                    )

                    .map(
                        amenity =>
                            `
                            <span class="chip">
                                ${esc(
                                    amenity
                                )}
                            </span>
                            `
                    )

                    .join("")
                }

            </div>


            <p class="muted">

                Per room/night:
                <strong>
                    ${fmtPrice(
                        hotel.price_per_room_per_night_try
                    )}
                </strong>

            </p>


            <p class="price">

                Total:
                ${fmtPrice(
                    hotel.total_hotel_cost_try
                )}

            </p>


            ${
                hotel.link

                ?

                `
                <a
                    class="primary-link"
                    target="_blank"
                    rel="noopener"
                    href="${esc(
                        hotel.link
                    )}"
                >
                    Open hotel source
                </a>
                `

                :

                ""
            }


            ${
                hotel.why

                ?

                `
                <div class="why">
                    ${esc(
                        hotel.why
                    )}
                </div>
                `

                :

                ""
            }

        </div>
    `;
}


function renderTransport(
    transport
) {

    if (!transport) {
        return "";
    }


    return `
        <div class="card">

            <div class="row">

                <h3>
                    Transport
                </h3>

                ${
                    transport.verified_route

                    ?

                    `
                    <span class="verified">
                        ✓ Route checked
                    </span>
                    `

                    :

                    ""
                }

            </div>


            ${
                transport.company

                ?

                `
                <h4>
                    ${esc(
                        transport.company
                    )}
                </h4>
                `

                :

                `
                <h4>
                    No verified operator
                </h4>
                `
            }


            ${
                transport.feasibility_warning

                ?

                `
                <div class="warning">

                    ${esc(
                        transport.feasibility_warning
                    )}

                </div>
                `

                :

                ""
            }


            ${
                transport.price_try !== null
                &&
                transport.price_try !== undefined

                ?

                `
                <p class="price">

                    ${fmtPrice(
                        transport.price_try
                    )}

                </p>
                `

                :

                `
                <div class="warning">

                    The operator was found,
                    but no current ticket price
                    was returned by the search.

                </div>
                `
            }


            ${
                transport.link

                ?

                `
                <a
                    class="primary-link"
                    target="_blank"
                    rel="noopener"
                    href="${esc(
                        transport.link
                    )}"
                >
                    Open transport source
                </a>
                `

                :

                ""
            }


            ${
                transport.why

                ?

                `
                <div class="why">

                    ${esc(
                        transport.why
                    )}

                </div>
                `

                :

                ""
            }

        </div>
    `;
}


function renderTransfers(
    transfer
) {

    if (!transfer) {
        return "";
    }


    return `
        <div class="card">

            <h3>
                Hotel ↔ Transport
            </h3>


            ${
                transfer.to_hotel

                ?

                `
                <div class="item">

                    <strong>
                        Station / terminal →
                        hotel
                    </strong>

                    <p class="muted">

                        Duration:
                        ${esc(
                            transfer.to_hotel.duration
                        )}

                        ·

                        Distance:
                        ${esc(
                            transfer.to_hotel.distance
                        )}

                    </p>

                    ${
                        transfer.to_hotel.link

                        ?

                        `
                        <a
                            class="map"
                            target="_blank"
                            rel="noopener"
                            href="${esc(
                                transfer.to_hotel.link
                            )}"
                        >
                            ${t().map}
                        </a>
                        `

                        :

                        ""
                    }

                </div>
                `

                :

                ""
            }


            ${
                transfer.from_hotel

                ?

                `
                <div class="item">

                    <strong>
                        Hotel →
                        station / terminal
                    </strong>

                    <p class="muted">

                        Duration:
                        ${esc(
                            transfer.from_hotel.duration
                        )}

                        ·

                        Distance:
                        ${esc(
                            transfer.from_hotel.distance
                        )}

                    </p>

                    ${
                        transfer.from_hotel.link

                        ?

                        `
                        <a
                            class="map"
                            target="_blank"
                            rel="noopener"
                            href="${esc(
                                transfer.from_hotel.link
                            )}"
                        >
                            ${t().map}
                        </a>
                        `

                        :

                        ""
                    }

                </div>
                `

                :

                ""
            }


            ${
                transfer.arrival_explanation

                ?

                `<p>
                    ${esc(
                        transfer.arrival_explanation
                    )}
                </p>`

                :

                ""
            }


            ${
                transfer.departure_explanation

                ?

                `<p>
                    ${esc(
                        transfer.departure_explanation
                    )}
                </p>`

                :

                ""
            }

        </div>
    `;
}


function renderDay(
    day
) {

    return `
        <div class="day">

            <div class="row">

                <h3>
                    Day ${day.day_number}
                    —
                    ${esc(
                        day.day_title
                    )}
                </h3>

                <span class="date">
                    ${esc(
                        day.calendar_date
                    )}
                </span>

            </div>


            <div class="banner">

                ${esc(
                    day.breakfast_banner
                )}

            </div>


            ${
                (
                    day.activities
                    || []
                )

                .map(
                    activity =>
                        `
                        <div class="item">

                            <strong>

                                ${esc(
                                    activity.time_slot
                                )}

                                ·

                                ${esc(
                                    activity.place_name
                                )}

                            </strong>


                            <p class="muted">

                                ${esc(
                                    activity.category
                                    || ""
                                )}

                                ·

                                ${esc(
                                    activity.address
                                    || ""
                                )}

                                ·

                                Rating:
                                ${activity.rating ?? "—"}

                            </p>


                            ${
                                activity.map_url

                                ?

                                `
                                <a
                                    class="map"
                                    target="_blank"
                                    rel="noopener"
                                    href="${esc(
                                        activity.map_url
                                    )}"
                                >
                                    📍
                                    ${t().map}
                                </a>
                                `

                                :

                                ""
                            }

                        </div>
                        `
                )

                .join("")
            }


            ${
                (
                    day.restaurants
                    || []
                )

                .map(
                    restaurant =>
                        `
                        <div class="item">

                            <strong>

                                ${esc(
                                    restaurant.meal_type
                                )}

                                ·

                                ${esc(
                                    restaurant.restaurant_name
                                )}

                            </strong>


                            <p class="muted">

                                ${esc(
                                    restaurant.cuisine
                                    || ""
                                )}

                                ·

                                ${esc(
                                    restaurant.address
                                    || ""
                                )}

                                ·

                                Rating:
                                ${restaurant.rating ?? "—"}

                            </p>


                            ${
                                restaurant.map_url

                                ?

                                `
                                <a
                                    class="map"
                                    target="_blank"
                                    rel="noopener"
                                    href="${esc(
                                        restaurant.map_url
                                    )}"
                                >
                                    📍
                                    ${t().map}
                                </a>
                                `

                                :

                                ""
                            }

                        </div>
                        `
                )

                .join("")
            }

        </div>
    `;
}


function render(
    data
) {

    state.currentData =
        data;


    $("emptyState")
        .classList
        .add(
            "hidden"
        );


    $("results")
        .classList
        .remove(
            "hidden"
        );


    $("routeTitle")
        .textContent =
        `${data.origin_city} → ${data.destination_city}`;


    $("dateTitle")
        .textContent =
        `${data.start_date} → ${data.end_date}`;


    $("costTitle")
        .textContent =
        fmtPrice(
            data.grand_total_trip_cost_try
        );


    $("warnings")
        .innerHTML = (
            data.data_warnings
            || []
        )

            .map(
                warning =>
                    `
                    <div class="warning">

                        ⚠️
                        ${esc(
                            warning
                        )}

                    </div>
                    `
            )

            .join("");


    $("hotelArea")
        .innerHTML =
        renderHotel(
            data.hotel
        );


    $("transportArea")
        .innerHTML =
        renderTransport(
            data.transportation
        );


    $("transferArea")
        .innerHTML =
        renderTransfers(
            data.transfer_plan
        );


    $("daysArea")
        .innerHTML = (
            data.daily_schedule
            || []
        )

            .map(
                renderDay
            )

            .join("");


    $("sources")
        .innerHTML =
        sourceLinks(
            data.sources
            || []
        );
}


document.addEventListener(
    "DOMContentLoaded",
    () => {


        cities.forEach(
            city => {

                $("origin").add(
                    new Option(
                        city,
                        city
                    )
                );


                $("destination").add(
                    new Option(
                        city,
                        city
                    )
                );

            }
        );


        $("origin").value =
            "Bursa";


        $("destination").value =
            "İstanbul";


        const startDate =
            new Date();


        startDate.setDate(
            startDate.getDate()
            + 7
        );


        $("start_date").value =
            startDate
                .toISOString()
                .slice(
                    0,
                    10
                );


        $("start_date").min =
            new Date()
                .toISOString()
                .slice(
                    0,
                    10
                );


        $("children_count")
            .addEventListener(
                "input",
                () => {

                    $("childAgeWrap")
                        .classList
                        .toggle(

                            "hidden",

                            Number(
                                $("children_count")
                                    .value
                                    || 0
                            ) === 0

                        );

                }
            );


        $("langSelector")
            .addEventListener(
                "change",
                event => {

                    state.lang =
                        event.target.value;

                    applyLanguage();

                }
            );


        $("hotel_min_rating")
            .addEventListener(
                "input",
                event => {

                    $("ratingValue")
                        .textContent =
                        event.target.value;

                }
            );


        $("tripForm")
            .addEventListener(
                "submit",
                async event => {

                    event.preventDefault();


                    if (
                        $("origin").value
                        ===
                        $("destination").value
                    ) {

                        alert(
                            "Departure and destination must be different."
                        );

                        return;

                    }


                    if (
                        !$("start_date").value
                    ) {

                        alert(
                            "Please choose a start date."
                        );

                        return;

                    }


                    $("loading")
                        .classList
                        .remove(
                            "hidden"
                        );


                    $("results")
                        .classList
                        .add(
                            "hidden"
                        );


                    $("searchBtn")
                        .disabled = true;


                    $("searchBtn")
                        .textContent =
                        t().searching;


                    try {

                        const result =
                            await api(
                                "/api/plan-trip",
                                collectPayload()
                            );


                        render(
                            result
                        );


                    } catch (
                        error
                    ) {

                        $("emptyState")
                            .classList
                            .remove(
                                "hidden"
                            );


                        alert(
                            error.message
                        );


                    } finally {

                        $("loading")
                            .classList
                            .add(
                                "hidden"
                            );


                        $("searchBtn")
                            .disabled = false;


                        $("searchBtn")
                            .textContent =
                            t().search;

                    }

                }
            );


        applyLanguage();

    }
);