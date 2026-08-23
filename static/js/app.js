const state = {
  lang: "tr",
  currentData: null
};


const I18N = {

  tr: {
    title: "VoyageAI Türkiye",
    subtitle: "Ücretsiz doğrulanmış seyahat planı",
    search: "Ara & Planla",
    searching: "Veriler hazırlanıyor...",
    origin: "Kalkış",
    destination: "Varış",
    date: "Gidiş tarihi",
    nights: "Gece",
    adults: "Yetişkin",
    children: "Çocuk",
    childAge: "Çocuk yaşı",
    rooms: "Oda",
    transport: "Ulaşım",
    budget: "Bütçe",
    cheapest: "En iyi + en ucuz",
    custom: "Bütçe sınırı",
    minRating: "Min. otel puanı",
    location: "Otel konumu",
    amenities: "Gerekli olanaklar",
    meal: "Yemek planı",
    notes: "Özel notlar",
    hotel: "Önerilen otel",
    transportPlan: "Ulaşım planı",
    daily: "Günlük plan",
    returnDay: "Dönüş günü",
    sources: "Doğrulanmış kaynaklar",
    book: "Kaynağı aç",
    warning: "Uyarı",
    noData: "Sonuç görmek için arama yapın.",
    unavailable: "Doğrulanmış veri bulunamadı.",
    map: "Haritada aç",
    reason: "Neden seçildi?"
  },

  en: {
    title: "VoyageAI Türkiye",
    subtitle: "Free travel planning with verified public data",
    search: "Search & Plan",
    searching: "Preparing verified data...",
    origin: "Departure",
    destination: "Destination",
    date: "Start date",
    nights: "Nights",
    adults: "Adults",
    children: "Children",
    childAge: "Child age",
    rooms: "Rooms",
    transport: "Transport",
    budget: "Budget",
    cheapest: "Best + cheapest",
    custom: "Budget limit",
    minRating: "Min hotel rating",
    location: "Hotel location",
    amenities: "Required amenities",
    meal: "Meal plan",
    notes: "Special notes",
    hotel: "Recommended hotel",
    transportPlan: "Transport plan",
    daily: "Daily plan",
    returnDay: "Return day",
    sources: "Verified sources",
    book: "Open source",
    warning: "Warning",
    noData: "Search to see results.",
    unavailable: "No verified data found.",
    map: "Open map",
    reason: "Why selected?"
  },

  ar: {
    title: "VoyageAI Türkiye",
    subtitle: "خطة سفر مجانية مبنية على بيانات عامة موثقة",
    search: "ابحث وخطط",
    searching: "جارٍ تجهيز البيانات...",
    origin: "المغادرة",
    destination: "الوجهة",
    date: "تاريخ السفر",
    nights: "الليالي",
    adults: "البالغون",
    children: "الأطفال",
    childAge: "عمر الطفل",
    rooms: "الغرف",
    transport: "النقل",
    budget: "الميزانية",
    cheapest: "الأفضل + الأرخص",
    custom: "حد الميزانية",
    minRating: "أدنى تقييم للفندق",
    location: "موقع الفندق",
    amenities: "المرافق المطلوبة",
    meal: "خطة الوجبات",
    notes: "ملاحظات خاصة",
    hotel: "الفندق المقترح",
    transportPlan: "خطة النقل",
    daily: "الخطة اليومية",
    returnDay: "يوم العودة",
    sources: "المصادر الموثقة",
    book: "فتح المصدر",
    warning: "تنبيه",
    noData: "ابدأ البحث لرؤية النتائج.",
    unavailable: "لم يتم العثور على بيانات موثقة.",
    map: "فتح الخريطة",
    reason: "سبب الاختيار"
  }

};


const cityNames = [
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


const $ = id =>
  document.getElementById(id);


const t = () =>
  I18N[state.lang];


function escapeHtml(value) {

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


function money(value) {

  if (
    value == null
    || Number.isNaN(
      Number(value)
    )
  ) {
    return "—";
  }

  return `${Number(value).toLocaleString()} TRY`;
}


function sourceButtons(
  sources = []
) {

  const seen =
    new Set();

  return (
    sources || []
  )
    .filter(
      s =>
        s?.url
        && !seen.has(s.url)
        && seen.add(s.url)
    )
    .slice(0, 8)
    .map(
      s =>
        `
        <a
          href="${escapeHtml(s.url)}"
          target="_blank"
          rel="noopener noreferrer"
          class="source-chip"
        >
          ↗ ${escapeHtml(
            s.title
            || t().sources
          )}
        </a>
        `
    )
    .join("");
}


function applyLanguage() {

  document.documentElement.lang =
    state.lang;

  document.documentElement.dir =
    state.lang === "ar"
      ? "rtl"
      : "ltr";

  document
    .querySelectorAll(
      "[data-i18n]"
    )
    .forEach(
      el => {

        const key =
          el.dataset.i18n;

        if (t()[key]) {
          el.textContent =
            t()[key];
        }

      }
    );

  if (
    state.currentData
  ) {
    render(
      state.currentData
    );
  }
}


function fillCities() {

  for (
    const city of cityNames
  ) {

    $(
      "origin"
    ).append(
      new Option(
        city,
        city
      )
    );

    $(
      "destination"
    ).append(
      new Option(
        city,
        city
      )
    );
  }

  $(
    "origin"
  ).value = "Bursa";

  $(
    "destination"
  ).value = "İstanbul";
}


function showToast(
  message
) {

  const old =
    $("toast");

  if (old) {
    old.remove();
  }

  const el =
    document.createElement(
      "div"
    );

  el.id = "toast";

  el.className =
    "toast";

  el.textContent =
    message;

  document.body.appendChild(
    el
  );

  setTimeout(
    () => el.remove(),
    9000
  );
}


async function api(
  url,
  payload
) {

  const res =
    await fetch(
      url,
      {
        method: "POST",
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

  const json =
    await res
      .json()
      .catch(
        () => null
      );

  if (
    !res.ok
    || !json?.success
  ) {

    throw new Error(
      json?.error
      || `HTTP ${res.status}`
    );

  }

  return json.data;
}


function collectPayload() {

  const children =
    Number(
      $("children_count")
        .value || 0
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
        $("nights").value || 3
      ),

    adults_count:
      Number(
        $("adults_count")
          .value || 2
      ),

    children_count:
      children,

    child_age:
      children > 0
        ? Number(
            $("child_age")
              .value || 10
          )
        : null,

    rooms_count:
      Number(
        $("rooms_count")
          .value || 1
      ),

    transport_mode:
      $("transport_mode")
        .value,

    budget_type:
      $("budget_mode")
        .value,

    budget_amount_try:
      $("budget_amount_try")
        .value
        ? Number(
            $("budget_amount_try")
              .value
          )
        : null,

    hotel_min_rating:
      Number(
        $("hotel_min_rating")
          .value || 8
      ),

    hotel_location:
      $("hotel_location")
        .value,

    amenities:
      [
        ...document.querySelectorAll(
          "input[name='amenity']:checked"
        )
      ].map(
        x => x.value
      ),

    meal_board:
      $("meal_board")
        .value,

    special_notes:
      $("special_notes")
        .value
        .trim(),

    language:
      state.lang
  };
}


function renderWhy(
  why
) {

  if (!why) {
    return "";
  }

  return `
    <div class="why">
      <strong>
        ${escapeHtml(
          why.title
          || t().reason
        )}
      </strong>

      <p>
        ${escapeHtml(
          why.explanation
          || ""
        )}
      </p>

      <div>
        ${(why.score_metrics || [])
          .map(
            x =>
              `
              <span class="metric">
                ${escapeHtml(x)}
              </span>
              `
          )
          .join("")}
      </div>
    </div>
  `;
}


function renderHotel(
  hotel
) {

  if (
    !hotel?.verified
  ) {

    return `
      <section class="card">

        <div class="section-title">
          <span>
            ${t().hotel}
          </span>
        </div>

        <div class="empty">
          ${t().unavailable}
        </div>

      </section>
    `;
  }

  return `
    <section class="card">

      <div class="section-title">

        <span>
          ${t().hotel}
        </span>

        <span class="verified">
          ✓ OSM verified
        </span>

      </div>

      <h3>
        ${escapeHtml(
          hotel.name
        )}
      </h3>

      <div class="hotel-meta">

        ${hotel.stars ?? "—"}★

        ·

        ${hotel.aggregated_rating_10 ?? "—"}
        /10

        ·

        ${money(
          hotel.price_per_room_per_night_try
        )}
        / room-night

      </div>

      <p class="address">
        ${escapeHtml(
          hotel.address
          || ""
        )}
      </p>

      <div class="chips">

        <span class="chip">
          ${escapeHtml(
            hotel.location_tag
            || ""
          )}
        </span>

        ${
          hotel.has_pool
            ? `<span class="chip">Pool</span>`
            : ""
        }

        ${
          hotel.has_private_beach
            ? `<span class="chip">Beach</span>`
            : ""
        }

        ${
          hotel.has_aquapark
            ? `<span class="chip">Aquapark</span>`
            : ""
        }

        ${
          hotel.has_spa
            ? `<span class="chip">Spa</span>`
            : ""
        }

      </div>

      ${
        !hotel.price_verified
          ? `
            <div class="warning-box">

              No current verified price
              in the free public data source.

              The app does not claim this
              is the absolute cheapest hotel.

            </div>
          `
          : ""
      }

      ${renderWhy(
        hotel.why
      )}

      <div class="link-row">

        ${sourceButtons(
          hotel.sources
        )}

        ${sourceButtons(
          hotel.booking_links
        )}

      </div>

    </section>
  `;
}


function renderTransport(
  trans
) {

  return `
    <section class="card">

      <div class="section-title">

        <span>
          ${t().transportPlan}
        </span>

        ${
          trans?.verified
            ? `
              <span class="verified">
                ✓ OSM verified
              </span>
            `
            : ""
        }

      </div>

      <h3>
        ${escapeHtml(
          trans?.carrier_summary
          || trans?.mode
          || ""
        )}
      </h3>

      ${
        !trans?.verified
          ? `
            <div class="warning-box">
              ${escapeHtml(
                trans?.feasibility_warning
                || t().unavailable
              )}
            </div>
          `
          : ""
      }

      ${
        trans?.verified
        && !trans.price_verified
          ? `
            <div class="warning-box">

              Operator presence was verified,
              but a current ticket price was not
              found in the free public data.

              No cheapest-price claim is made.

            </div>
          `
          : ""
      }

      <div class="transport-grid">

        <div>
          <small>
            Departure
          </small>

          <strong>
            ${escapeHtml(
              trans?.departure_time
              || "—"
            )}
          </strong>
        </div>

        <div>

          <small>
            Arrival
          </small>

          <strong>
            ${escapeHtml(
              trans?.arrival_time
              || "—"
            )}
          </strong>

        </div>

        <div>

          <small>
            Duration
          </small>

          <strong>
            ${escapeHtml(
              trans?.duration
              || "—"
            )}
          </strong>

        </div>

        <div>

          <small>
            Total
          </small>

          <strong>
            ${money(
              trans?.total_transport_cost_try
            )}
          </strong>

        </div>

      </div>

      ${renderWhy(
        trans?.why
      )}

      <div class="link-row">

        ${sourceButtons(
          trans?.sources
        )}

        ${sourceButtons(
          trans?.booking_links
        )}

      </div>

    </section>
  `;
}


function renderActivity(
  a
) {

  return `
    <article class="item-card">

      <div class="item-top">

        <span class="time">
          ${escapeHtml(
            a.time_slot
          )}
        </span>

        <strong>
          ${escapeHtml(
            a.place_name
          )}
        </strong>

      </div>

      <div class="muted">

        ${escapeHtml(
          a.category
        )}

        ·

        ${escapeHtml(
          a.address
          || ""
        )}

      </div>

      ${
        a.map_url
          ? `
            <a
              href="${escapeHtml(
                a.map_url
              )}"
              target="_blank"
              rel="noopener noreferrer"
              class="map-link"
            >
              📍 ${t().map}
            </a>
          `
          : ""
      }

      ${renderWhy(
        a.why
      )}

      <div class="link-row">

        ${sourceButtons(
          (a.source_urls || [])
            .map(
              url => ({
                url,
                title:
                  "OpenStreetMap"
              })
            )
        )}

      </div>

    </article>
  `;
}


function renderRestaurant(
  r
) {

  return `
    <article class="item-card">

      <div class="item-top">

        <span class="meal-tag">
          ${escapeHtml(
            r.meal_type
          )}
        </span>

        <strong>
          ${escapeHtml(
            r.restaurant_name
          )}
        </strong>

      </div>

      <div class="muted">

        ${escapeHtml(
          r.cuisine
        )}

        ·

        ${escapeHtml(
          r.address
          || ""
        )}

      </div>

      <div class="muted">

        ${money(
          r.estimated_cost_per_adult_try
        )}

        / adult

        · ★

        ${
          r.aggregated_rating_10
          ?? "—"
        }

        /10

      </div>

      ${
        r.map_url
          ? `
            <a
              href="${escapeHtml(
                r.map_url
              )}"
              target="_blank"
              rel="noopener noreferrer"
              class="map-link"
            >
              📍 ${t().map}
            </a>
          `
          : ""
      }

      ${renderWhy(
        r.why
      )}

      <div class="link-row">

        ${sourceButtons(
          (r.source_urls || [])
            .map(
              url => ({
                url,
                title:
                  "OpenStreetMap"
              })
            )
        )}

      </div>

    </article>
  `;
}


function renderDay(
  day
) {

  return `
    <section class="day-card">

      <div class="day-head">

        <div>

          <span>
            Day ${day.day_number}
          </span>

          <h3>
            ${escapeHtml(
              day.day_title
            )}
          </h3>

        </div>

        <span class="date-badge">
          ${escapeHtml(
            day.calendar_date
          )}
        </span>

      </div>

      <p class="banner">
        ${escapeHtml(
          day.breakfast_banner
          || ""
        )}
      </p>

      <div class="items">

        ${(day.activities || [])
          .map(
            renderActivity
          )
          .join("")}

      </div>

      <div class="items">

        ${(day.restaurants || [])
          .map(
            renderRestaurant
          )
          .join("")}

      </div>

    </section>
  `;
}


function render(
  data
) {

  state.currentData =
    data;

  $("results")
    .classList
    .remove("hidden");

  $("emptyState")
    .classList
    .add("hidden");

  $("routeTitle")
    .textContent =
    `${data.origin_city} → ${data.destination_city}`;

  $("dateTitle")
    .textContent =
    `${data.start_date} → ${data.end_date}`;

  $("costTitle")
    .textContent =
    money(
      data.grand_total_trip_cost_try
    );

  $("resultWarnings")
    .innerHTML =
    (data.data_warnings || [])
      .map(
        w =>
          `
          <div class="warning-box">
            ⚠️
            ${escapeHtml(w)}
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

  $("daysArea")
    .innerHTML =
    (
      data.daily_schedule
      || []
    )
      .map(
        renderDay
      )
      .join("");

  $("sourcesArea")
    .innerHTML =
    sourceButtons(
      data.sources
      || []
    );
}


async function submitSearch(
  e
) {

  e.preventDefault();

  const btn =
    $("searchBtn");

  const old =
    btn.innerHTML;

  btn.disabled =
    true;

  btn.innerHTML =
    `
      <i class="fa-solid fa-spinner fa-spin"></i>
      ${t().searching}
    `;

  $("loading")
    .classList
    .remove("hidden");

  $("results")
    .classList
    .add("hidden");

  try {

    if (
      !$("start_date").value
    ) {
      throw new Error(
        "Please choose a start date."
      );
    }

    if (
      $("origin").value
      ===
      $("destination").value
    ) {
      throw new Error(
        "Departure and destination must be different."
      );
    }

    const data =
      await api(
        "/api/plan-trip",
        collectPayload()
      );

    render(
      data
    );

  } catch (err) {

    showToast(
      err.message
    );

    $("emptyState")
      .classList
      .remove("hidden");

  } finally {

    btn.disabled =
      false;

    btn.innerHTML =
      old;

    $("loading")
      .classList
      .add("hidden");
  }
}


document.addEventListener(
  "DOMContentLoaded",
  () => {

    fillCities();

    const tomorrow =
      new Date();

    tomorrow.setDate(
      tomorrow.getDate() + 7
    );

    $("start_date")
      .value =
      tomorrow
        .toISOString()
        .slice(
          0,
          10
        );

    $("start_date")
      .min =
      new Date()
        .toISOString()
        .slice(
          0,
          10
        );

    $("langSelector")
      .addEventListener(
        "change",
        e => {
          state.lang =
            e.target.value;

          applyLanguage();
        }
      );

    $("tripForm")
      .addEventListener(
        "submit",
        submitSearch
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
                  .value || 0
              ) === 0
            );

        }
      );

    applyLanguage();
  }
);