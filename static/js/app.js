const state = {
  lang: "tr",
  currentData: null,
  checkingRoute: false,
  lastRouteCheckKey: ""
};

const I18N = {
  tr: {
    title: "VoyageAI Türkiye",
    subtitle: "Canlı web araması ile doğrulanmış seyahat planı",
    search: "Canlı Ara & Planla",
    searching: "Canlı veriler aranıyor...",
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
    exact: "Doğrudan rezervasyon",
    source: "Kaynak",
    warning: "Uyarı",
    noData: "Sonuç görmek için arama yapın.",
    unavailable: "Doğrulanmış veri bulunamadı.",
    map: "Haritada aç",
    reason: "Neden seçildi?"
  },
  en: {
    title: "VoyageAI Türkiye",
    subtitle: "Travel planning powered by live web-grounded search",
    search: "Search Live & Plan",
    searching: "Searching live data...",
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
    exact: "Direct booking",
    source: "Source",
    warning: "Warning",
    noData: "Search to see results.",
    unavailable: "No citation-verified data found.",
    map: "Open map",
    reason: "Why selected?"
  },
  ar: {
    title: "VoyageAI Türkiye",
    subtitle: "خطة سفر مبنية على بحث مباشر وموثّق من الويب",
    search: "ابحث الآن وخطط",
    searching: "جارٍ البحث المباشر...",
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
    exact: "حجز مباشر",
    source: "المصدر",
    warning: "تنبيه",
    noData: "ابدأ البحث لرؤية النتائج.",
    unavailable: "لم يتم العثور على بيانات موثقة.",
    map: "فتح الخريطة",
    reason: "سبب الاختيار"
  }
};

const cityNames = [
  "Adana","Adıyaman","Afyonkarahisar","Ağrı","Aksaray","Amasya","Ankara","Antalya","Ardahan","Artvin","Aydın","Balıkesir","Bartın","Batman","Bayburt","Bilecik","Bingöl","Bitlis","Bolu","Burdur","Bursa","Çanakkale","Çankırı","Çorum","Denizli","Diyarbakır","Düzce","Edirne","Elazığ","Erzincan","Erzurum","Eskişehir","Gaziantep","Giresun","Gümüşhane","Hakkâri","Hatay","Iğdır","Isparta","İstanbul","İzmir","Kahramanmaraş","Karabük","Karaman","Kars","Kastamonu","Kayseri","Kırıkkale","Kırklareli","Kırşehir","Kilis","Kocaeli","Konya","Kütahya","Malatya","Manisa","Mardin","Mersin","Muğla","Muş","Nevşehir","Niğde","Ordu","Osmaniye","Rize","Sakarya","Samsun","Siirt","Sinop","Sivas","Şanlıurfa","Şırnak","Tekirdağ","Tokat","Trabzon","Tunceli","Uşak","Van","Yalova","Yozgat","Zonguldak"
];

const $ = (id) => document.getElementById(id);
const t = () => I18N[state.lang];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function money(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return "—";
  return `${Number(value).toLocaleString(undefined, { maximumFractionDigits: 0 })} TRY`;
}

function sourceButtons(sources = [], exactLabel = false) {
  const unique = [];
  const seen = new Set();
  for (const s of sources || []) {
    if (!s?.url || seen.has(s.url)) continue;
    seen.add(s.url);
    unique.push(s);
  }
  return unique.slice(0, 8).map(s => `
    <a href="${escapeHtml(s.url)}" target="_blank" rel="noopener noreferrer" class="source-chip">
      <i class="fa-solid fa-arrow-up-right-from-square"></i>
      ${escapeHtml(s.title || t().source)}
    </a>`).join("");
}

function applyLanguage() {
  const lang = state.lang;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const key = el.dataset.i18n;
    if (t()[key]) el.textContent = t()[key];
  });
  if (state.currentData) render(state.currentData);
}

function fillCities() {
  const origin = $("origin");
  const destination = $("destination");
  for (const city of cityNames) {
    const a = document.createElement("option");
    a.value = city; a.textContent = city; origin.appendChild(a);
    const b = document.createElement("option");
    b.value = city; b.textContent = city; destination.appendChild(b);
  }
  origin.value = "Bursa";
  destination.value = "İstanbul";
}

function showToast(message, type = "error") {
  const existing = $("toast");
  if (existing) existing.remove();
  const el = document.createElement("div");
  el.id = "toast";
  el.className = `toast ${type}`;
  el.innerHTML = `<i class="fa-solid ${type === "error" ? "fa-circle-exclamation" : "fa-circle-check"}"></i><span>${escapeHtml(message)}</span>`;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 9000);
}

async function api(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  let json = null;
  try { json = await res.json(); } catch { /* ignored */ }
  if (!res.ok || !json?.success) {
    throw new Error(json?.error || `HTTP ${res.status}`);
  }
  return json.data;
}

function collectPayload() {
  const children = Number($("children_count").value || 0);
  return {
    origin: $("origin").value,
    destination: $("destination").value,
    start_date: $("start_date").value,
    nights: Number($("nights").value || 3),
    adults_count: Number($("adults_count").value || 2),
    children_count: children,
    child_age: children > 0 ? Number($("child_age").value || 10) : null,
    rooms_count: Number($("rooms_count").value || 1),
    transport_mode: $("transport_mode").value,
    budget_type: $("budget_mode").value,
    budget_amount_try: $("budget_amount_try").value ? Number($("budget_amount_try").value) : null,
    hotel_min_rating: Number($("hotel_min_rating").value || 8),
    hotel_location: $("hotel_location").value,
    amenities: [...document.querySelectorAll("input[name='amenity']:checked")].map(x => x.value),
    meal_board: $("meal_board").value,
    special_notes: $("special_notes").value.trim(),
    language: state.lang
  };
}

async function checkTransportLive() {
  const mode = $("transport_mode").value;
  const origin = $("origin").value;
  const destination = $("destination").value;
  const date = $("start_date").value;
  if (!mode || origin === destination || !date) return;

  const key = `${origin}|${destination}|${mode}|${date}`;
  if (state.lastRouteCheckKey === key || state.checkingRoute) return;
  state.checkingRoute = true;
  state.lastRouteCheckKey = key;
  const banner = $("routeStatus");
  banner.className = "status loading";
  banner.textContent = `${t().searching}`;

  try {
    const result = await api("/api/check-transport", {
      origin,
      destination,
      transport_mode: mode,
      date,
      adults_count: Number($("adults_count").value || 2),
      children_count: Number($("children_count").value || 0),
      language: "en"
    });
    if (result.is_feasible) {
      banner.className = "status success";
      banner.textContent = result.carrier_summary || "Live transport option found.";
    } else {
      banner.className = "status warning";
      banner.textContent = result.warning || t().unavailable;
    }
  } catch (err) {
    banner.className = "status warning";
    banner.textContent = "Live availability check could not be verified yet.";
  } finally {
    state.checkingRoute = false;
  }
}

function renderWhy(why) {
  if (!why) return "";
  const metrics = (why.score_metrics || []).map(x => `<span class="metric">${escapeHtml(x)}</span>`).join("");
  return `<div class="why"><strong>${escapeHtml(why.title || t().reason)}</strong><p>${escapeHtml(why.explanation || "")}</p><div>${metrics}</div></div>`;
}

function renderHotel(hotel) {
  if (!hotel?.verified) {
    return `<section class="card"><div class="section-title"><span>${t().hotel}</span></div><div class="empty">${t().unavailable}</div></section>`;
  }
  const links = (hotel.booking_links || []).filter(x => x?.url);
  const booking = links.length ? links.map(l => `
    <a class="primary-link" href="${escapeHtml(l.url)}" target="_blank" rel="noopener noreferrer">
      ${l.exact_parameters_supported ? `🔗 ${t().exact}` : `🔎 ${t().book}`}
      <span>${escapeHtml(l.provider_name)}</span>
    </a>`).join("") : sourceButtons(hotel.sources);
  return `<section class="card">
    <div class="section-title"><span>${t().hotel}</span><span class="verified">✓ Verified source</span></div>
    <h3>${escapeHtml(hotel.name)}</h3>
    <div class="hotel-meta">${hotel.stars ?? "—"}★ · ${hotel.aggregated_rating_10 ?? "—"}/10 · ${money(hotel.price_per_room_per_night_try)} / room-night</div>
    <div class="chips">
      <span class="chip">${escapeHtml(hotel.meal_board_type || "Meal plan unavailable")}</span>
      <span class="chip">${escapeHtml(hotel.location_tag || "Location verified from source")}</span>
      ${hotel.has_pool ? `<span class="chip">Pool</span>` : ""}
      ${hotel.has_private_beach ? `<span class="chip">Beach</span>` : ""}
      ${hotel.has_aquapark ? `<span class="chip">Aquapark</span>` : ""}
      ${hotel.has_spa ? `<span class="chip">Spa</span>` : ""}
    </div>
    <p class="address">${escapeHtml(hotel.address || "")}</p>
    ${renderWhy(hotel.why)}
    <div class="link-row">${booking}</div>
    <div class="source-wrap"><small>${t().sources}</small><div class="link-row">${sourceButtons(hotel.sources)}</div></div>
  </section>`;
}

function renderTransport(trans) {
  return `<section class="card">
    <div class="section-title"><span>${t().transportPlan}</span>${trans?.verified ? `<span class="verified">✓ Verified source</span>` : ""}</div>
    <h3>${escapeHtml(trans?.carrier_summary || trans?.mode || "")}</h3>
    ${!trans?.is_feasible ? `<div class="warning-box">${escapeHtml(trans?.feasibility_warning || t().unavailable)}</div>` : ""}
    <div class="transport-grid">
      <div><small>Departure</small><strong>${escapeHtml(trans?.departure_time || "—")}</strong></div>
      <div><small>Arrival</small><strong>${escapeHtml(trans?.arrival_time || "—")}</strong></div>
      <div><small>Duration</small><strong>${escapeHtml(trans?.duration || "—")}</strong></div>
      <div><small>Total</small><strong>${money(trans?.total_transport_cost_try)}</strong></div>
    </div>
    <p class="route-text">${escapeHtml(trans?.origin_terminal || "")} → ${escapeHtml(trans?.destination_terminal || "")}</p>
    ${renderWhy(trans?.why)}
    <div class="link-row">${sourceButtons(trans?.booking_links || trans?.sources || [])}</div>
  </section>`;
}

function renderActivity(a) {
  return `<article class="item-card">
    <div class="item-top"><span class="time">${escapeHtml(a.time_slot)}</span><strong>${escapeHtml(a.place_name)}</strong></div>
    <div class="muted">${escapeHtml(a.category)} · ${escapeHtml(a.address || "")}</div>
    <div class="muted">${escapeHtml(a.transport_mode || "")} · ${money(a.transport_cost_try)} · Entry ${money(a.entry_ticket_adult_try)}</div>
    ${a.map_url ? `<a href="${escapeHtml(a.map_url)}" target="_blank" rel="noopener noreferrer" class="map-link">📍 ${t().map}</a>` : ""}
    ${renderWhy(a.why)}
    <div class="link-row">${sourceButtons((a.source_urls || []).map(u => ({url:u,title:t().source})))}</div>
  </article>`;
}

function renderRestaurant(r) {
  return `<article class="item-card">
    <div class="item-top"><span class="meal-tag">${escapeHtml(r.meal_type)}</span><strong>${escapeHtml(r.restaurant_name)}</strong></div>
    <div class="muted">${escapeHtml(r.cuisine)} · ${escapeHtml(r.address || "")}</div>
    <div class="muted">${money(r.estimated_cost_per_adult_try)}/adult · ★ ${r.aggregated_rating_10 ?? "—"}/10</div>
    ${r.map_url ? `<a href="${escapeHtml(r.map_url)}" target="_blank" rel="noopener noreferrer" class="map-link">📍 ${t().map}</a>` : ""}
    ${renderWhy(r.why)}
    <div class="link-row">${sourceButtons((r.source_urls || []).map(u => ({url:u,title:t().source})))}</div>
  </article>`;
}

function renderDay(day) {
  return `<section class="day-card">
    <div class="day-head"><div><span>Day ${day.day_number}</span><h3>${escapeHtml(day.day_title)}</h3></div><span class="date-badge">${escapeHtml(day.calendar_date)}</span></div>
    <p class="banner">${escapeHtml(day.breakfast_banner || "")}</p>
    <div class="items">${(day.activities || []).map(renderActivity).join("")}</div>
    <div class="items">${(day.restaurants || []).map(renderRestaurant).join("")}</div>
  </section>`;
}

function renderDeparture(dep) {
  if (!dep) return "";
  const meal = dep.recommended_final_meal || dep.lunch_spot_near_hub;
  return `<section class="card">
    <div class="section-title"><span>${t().returnDay}</span></div>
    <div class="timeline">
      <div><small>Checkout</small><strong>${escapeHtml(dep.checkout_time || "12:00")}</strong></div>
      <div><small>Lunch</small><strong>${escapeHtml(dep.time_spent_at_lunch || "—")}</strong></div>
      <div><small>Transit to hub</small><strong>${escapeHtml(String(dep.transit_time_to_hub_mins || 0))} min</strong></div>
      <div><small>Safety buffer</small><strong>${escapeHtml(String(dep.required_safety_buffer_mins || 0))} min</strong></div>
      <div><small>Departure</small><strong>${escapeHtml(dep.return_departure_time || "—")}</strong></div>
      <div><small>Home arrival</small><strong>${escapeHtml(dep.arrival_at_home_time || "—")}</strong></div>
    </div>
    ${meal ? `<div class="item-card"><strong>${escapeHtml(meal.restaurant_name)}</strong><div class="muted">${escapeHtml(meal.address || "")}</div>${meal.map_url ? `<a href="${escapeHtml(meal.map_url)}" target="_blank" rel="noopener noreferrer" class="map-link">📍 ${t().map}</a>` : ""}</div>` : ""}
    ${renderWhy(dep.why)}
  </section>`;
}

function render(data) {
  state.currentData = data;
  $("results").classList.remove("hidden");
  $("emptyState").classList.add("hidden");
  $("routeTitle").textContent = `${data.origin_city} → ${data.destination_city}`;
  $("dateTitle").textContent = `${data.start_date} → ${data.end_date}`;
  $("costTitle").textContent = money(data.grand_total_trip_cost_try);
  $("resultWarnings").innerHTML = (data.data_warnings || []).map(w => `<div class="warning-box">⚠️ ${escapeHtml(w)}</div>`).join("");
  $("hotelArea").innerHTML = renderHotel(data.hotel);
  $("transportArea").innerHTML = renderTransport(data.transportation);
  $("daysArea").innerHTML = (data.daily_schedule || []).map(renderDay).join("");
  $("departureArea").innerHTML = renderDeparture(data.departure_day_buffer);
  $("sourcesArea").innerHTML = sourceButtons(data.sources || []);
}

async function submitSearch(e) {
  e.preventDefault();
  const btn = $("searchBtn");
  const oldText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> ${t().searching}`;
  $("loading").classList.remove("hidden");
  $("emptyState").classList.add("hidden");
  $("results").classList.add("hidden");
  try {
    if (!$('start_date').value) throw new Error("Please choose a start date.");
    if ($('origin').value === $('destination').value) throw new Error("Departure and destination must be different.");
    const data = await api("/api/plan-trip", collectPayload());
    render(data);
  } catch (err) {
    showToast(err.message, "error");
    $("emptyState").classList.remove("hidden");
  } finally {
    btn.disabled = false;
    btn.innerHTML = oldText;
    $("loading").classList.add("hidden");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  fillCities();
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 7);
  $("start_date").value = tomorrow.toISOString().slice(0,10);
  $("start_date").min = new Date().toISOString().slice(0,10);
  $("langSelector").addEventListener("change", e => { state.lang = e.target.value; applyLanguage(); });
  $("tripForm").addEventListener("submit", submitSearch);
  ["origin","destination","start_date","transport_mode"].forEach(id => $(id).addEventListener("change", () => {
    state.lastRouteCheckKey = "";
    checkTransportLive();
  }));
  $("children_count").addEventListener("input", () => {
    $("childAgeWrap").classList.toggle("hidden", Number($("children_count").value || 0) === 0);
  });
  applyLanguage();
  checkTransportLive();
});
