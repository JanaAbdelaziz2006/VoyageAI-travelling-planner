const state = {
    lang: "tr",
    currentData: null
};


const THEMES = [
    "midnight",
    "ocean",
    "lavender",
    "sunset"
];

function applyTheme(theme) {

    if (!THEMES.includes(theme)) {
        theme = "midnight";
    }

    document.body.dataset.theme =
        theme;

    localStorage.setItem(
        "voyageai-theme",
        theme
    );
}


const I18N = {

    en: {

        headerSubtitle:
            "Real travel search, ranking & planning",

        languageTurkish:
            "Turkish",

        languageEnglish:
            "English",

        languageArabic:
            "Arabic",

        themeMidnight:
            "Midnight",

        themeOcean:
            "Ocean",

        themeLavender:
            "Lavender",

        themeSunset:
            "Sunset",

        dark:
            "Dark",

        bright:
            "Bright",

        tripSearch:
            "Trip Search",

        departure:
            "Departure",

        destination:
            "Destination",

        startDate:
            "Start date",

        adults:
            "Adults",

        children:
            "Children",

        rooms:
            "Rooms",

        nights:
            "Nights",

        childAge:
            "Child age",

        transport:
            "Transport",

        bus:
            "Bus",

        plane:
            "Plane",

        train:
            "Train",

        passengerFerry:
            "Passenger Ferry",

        carFerry:
            "Car Ferry",

        ownCar:
            "Own Car",

        ownEV:
            "Own EV",

        budgetStrategy:
            "Budget strategy",

        bestCheapest:
            "Best + Cheapest",

        customBudget:
            "Custom budget",

        budgetTRY:
            "Budget TRY",

        optional:
            "Optional",

        minimumHotelRating:
            "Minimum hotel rating",

        hotelLocation:
            "Hotel location",

        cityCenter:
            "City center",

        nearSea:
            "Near sea",

        natureMountain:
            "Nature / mountain",

        quietArea:
            "Quiet area",

        hotelAmenities:
            "Hotel amenities",

        pool:
            "Pool",

        spa:
            "Spa",

        beach:
            "Beach",

        aquapark:
            "Aquapark",

        mealPlan:
            "Meal plan",

        breakfastOnly:
            "Breakfast only",

        roomOnly:
            "Room only",

        halfBoard:
            "Half board",

        fullBoard:
            "Full board",

        allInclusive:
            "All inclusive",

        specialNotes:
            "Special notes",

        specialNotesPlaceholder:
            "Family trip, local food, etc.",

        search:
            "Search & Plan",

        searching:
            "Searching live data...",

        emptyState:
            "Enter your trip requirements and search.",

        loading:
            "Searching hotels, restaurants, attractions, transport and routes...",

        travelPlan:
            "Travel Plan",

        total:
            "Total",

        dailyPlan:
            "Daily Plan",

        sources:
            "Sources",

        recommendedHotel:
            "Recommended Hotel",

        noVerifiedHotel:
            "No verified hotel result was returned.",

        rating:
            "Rating",

        reviews:
            "Reviews",

        googleHotels:
            "Google Hotels",

        perRoomNight:
            "Per room/night",

        openHotelSource:
            "Open hotel source",

        transportTitle:
            "Transport",

        routeChecked:
            "Route checked",

        noVerifiedOperator:
            "No verified operator",

        openTransportSource:
            "Open transport source",

        hotelTransport:
            "Hotel ↔ Transport",

        stationToHotel:
            "Station / terminal → hotel",

        hotelToStation:
            "Hotel → station / terminal",

        duration:
            "Duration",

        distance:
            "Distance",

        openGoogleMaps:
            "Open in Google Maps",

        day:
            "Day",

        lunch:
            "Lunch",

        dinner:
            "Dinner",

        breakfast:
            "Breakfast",

        ratingShort:
            "Rating",

        source:
            "Source",

        place:
            "Place",

        restaurant:
            "Restaurant",

        transport:
            "Transport",

        noHotelCandidate:
            "No hotel candidate was returned from Google Hotels.",

        noSpecificTransport:
            "No specific transport company could be verified.",

        priceUnavailable:
            "The selected hotel's current total price was not returned by the provider. No price was invented.",

        transportPriceUnavailable:
            "The selected transport company was found, but a current ticket price was not returned by the provider.",

        noTicketPrice:
            "The operator was found, but no current ticket price was returned by the search.",

        differentPlaces:
            "Departure and destination must be different.",

        chooseStartDate:
            "Please choose a start date.",

        map:
            "Open in Google Maps",

        routeFeasible:
            "The route appears feasible, but a specific operator could not be verified from the current search results.",

        noRoute:
            "No verified {mode} route was returned for {origin} → {destination}.",

        missingHotelFeatures:
            "Not all requested hotel features were available together in the verified search results. The system selected the highest-ranked practical match instead of inventing a hotel.",

        breakfastAccordingToMealPlan:
            "Breakfast according to the selected meal plan.",

        lunchRecommended:
            "Lunch at the recommended ranked restaurant.",

        dinnerAccordingToMealPlan:
            "Dinner according to the selected meal plan.",

        exactReturnTiming:
            "Exact return timing is shown only when a verified departure time is available.",

        hotelExplanation:
            "Explain why this hotel was selected based only on the supplied facts.",

        transportExplanation:
            "Explain why this transport option was selected based only on the supplied facts.",

        arrivalExplanation:
            "Explain the arrival transfer using only the supplied verified route facts.",

        departureExplanation:
            "Explain the departure transfer using only the supplied verified route facts."
    },


    tr: {

        headerSubtitle:
            "Gerçek seyahat araması, sıralama ve planlama",

        languageTurkish:
            "Türkçe",

        languageEnglish:
            "İngilizce",

        languageArabic:
            "Arapça",

        themeMidnight:
            "Gece",

        themeOcean:
            "Okyanus",

        themeLavender:
            "Lavanta",

        themeSunset:
            "Gün Batımı",

        dark:
            "Koyu",

        bright:
            "Açık",

        tripSearch:
            "Seyahat Arama",

        departure:
            "Kalkış",

        destination:
            "Varış",

        startDate:
            "Başlangıç tarihi",

        adults:
            "Yetişkin",

        children:
            "Çocuk",

        rooms:
            "Odalar",

        nights:
            "Gece",

        childAge:
            "Çocuk yaşı",

        transport:
            "Ulaşım",

        bus:
            "Otobüs",

        plane:
            "Uçak",

        train:
            "Tren",

        passengerFerry:
            "Yolcu Feribotu",

        carFerry:
            "Arabalı Feribot",

        ownCar:
            "Kendi Arabam",

        ownEV:
            "Kendi Elektrikli Arabam",

        budgetStrategy:
            "Bütçe stratejisi",

        bestCheapest:
            "En İyi + En Ucuz",

        customBudget:
            "Özel bütçe",

        budgetTRY:
            "Bütçe TRY",

        optional:
            "İsteğe bağlı",

        minimumHotelRating:
            "Minimum otel puanı",

        hotelLocation:
            "Otel konumu",

        cityCenter:
            "Şehir merkezi",

        nearSea:
            "Denize yakın",

        natureMountain:
            "Doğa / dağ",

        quietArea:
            "Sessiz bölge",

        hotelAmenities:
            "Otel olanakları",

        pool:
            "Havuz",

        spa:
            "Spa",

        beach:
            "Plaj",

        aquapark:
            "Aquapark",

        mealPlan:
            "Yemek planı",

        breakfastOnly:
            "Sadece kahvaltı",

        roomOnly:
            "Sadece oda",

        halfBoard:
            "Yarım pansiyon",

        fullBoard:
            "Tam pansiyon",

        allInclusive:
            "Her şey dahil",

        specialNotes:
            "Özel notlar",

        specialNotesPlaceholder:
            "Aile gezisi, yerel yemekler vb.",

        search:
            "Ara & Planla",

        searching:
            "Canlı veriler aranıyor...",

        emptyState:
            "Seyahat gereksinimlerinizi girin ve arayın.",

        loading:
            "Oteller, restoranlar, turistik yerler, ulaşım ve rotalar aranıyor...",

        travelPlan:
            "Seyahat Planı",

        total:
            "Toplam",

        dailyPlan:
            "Günlük Plan",

        sources:
            "Kaynaklar",

        recommendedHotel:
            "Önerilen Otel",

        noVerifiedHotel:
            "Doğrulanmış bir otel sonucu döndürülmedi.",

        rating:
            "Puan",

        reviews:
            "Yorum",

        googleHotels:
            "Google Hotels",

        perRoomNight:
            "Oda/gece",

        openHotelSource:
            "Otel kaynağını aç",

        transportTitle:
            "Ulaşım",

        routeChecked:
            "Rota kontrol edildi",

        noVerifiedOperator:
            "Doğrulanmış operatör yok",

        openTransportSource:
            "Ulaşım kaynağını aç",

        hotelTransport:
            "Otel ↔ Ulaşım",

        stationToHotel:
            "İstasyon / terminal → otel",

        hotelToStation:
            "Otel → istasyon / terminal",

        duration:
            "Süre",

        distance:
            "Mesafe",

        openGoogleMaps:
            "Google Maps'te aç",

        day:
            "Gün",

        lunch:
            "Öğle yemeği",

        dinner:
            "Akşam yemeği",

        breakfast:
            "Kahvaltı",

        ratingShort:
            "Puan",

        source:
            "Kaynak",

        place:
            "Yer",

        restaurant:
            "Restoran",

        noHotelCandidate:
            "Google Hotels'tan otel adayı döndürülmedi.",

        noSpecificTransport:
            "Belirli bir ulaşım şirketi doğrulanamadı.",

        priceUnavailable:
            "Seçilen otelin güncel toplam fiyatı sağlayıcı tarafından döndürülmedi. Fiyat uydurulmadı.",

        transportPriceUnavailable:
            "Seçilen ulaşım şirketi bulundu ancak güncel bilet fiyatı sağlayıcı tarafından döndürülmedi.",

        noTicketPrice:
            "Operatör bulundu ancak aramada güncel bilet fiyatı döndürülmedi.",

        differentPlaces:
            "Kalkış ve varış noktaları farklı olmalıdır.",

        chooseStartDate:
            "Lütfen bir başlangıç tarihi seçin.",

        map:
            "Google Maps'te aç",

        routeFeasible:
            "Rota uygun görünüyor ancak mevcut arama sonuçlarından belirli bir operatör doğrulanamadı.",

        noRoute:
            "{origin} → {destination} için doğrulanmış {mode} rotası döndürülmedi.",

        missingHotelFeatures:
            "İstenen tüm otel özellikleri doğrulanmış arama sonuçlarında aynı anda bulunamadı. Sistem bir otel uydurmak yerine en yüksek sıralı pratik eşleşmeyi seçti.",

        breakfastAccordingToMealPlan:
            "Seçilen yemek planına göre kahvaltı.",

        lunchRecommended:
            "Önerilen sıralanmış restoranda öğle yemeği.",

        dinnerAccordingToMealPlan:
            "Seçilen yemek planına göre akşam yemeği.",

        exactReturnTiming:
            "Kesin dönüş zamanı yalnızca doğrulanmış bir kalkış saati mevcut olduğunda gösterilir.",

        hotelExplanation:
            "Yalnızca sağlanan gerçek bilgilere dayanarak bu otelin neden seçildiğini açıkla.",

        transportExplanation:
            "Yalnızca sağlanan gerçek bilgilere dayanarak bu ulaşım seçeneğinin neden seçildiğini açıkla.",

        arrivalExplanation:
            "Yalnızca sağlanan doğrulanmış rota bilgilerini kullanarak varış transferini açıkla.",

        departureExplanation:
            "Yalnızca sağlanan doğrulanmış rota bilgilerini kullanarak dönüş transferini açıkla."
    },


    ar: {

        headerSubtitle:
            "بحث حقيقي عن السفر وترتيبه وتخطيطه",

        languageTurkish:
            "التركية",

        languageEnglish:
            "الإنجليزية",

        languageArabic:
            "العربية",

        themeMidnight:
            "ليلي",

        themeOcean:
            "محيطي",

        themeLavender:
            "لافندر",

        themeSunset:
            "غروب",

        dark:
            "داكن",

        bright:
            "فاتح",

        tripSearch:
            "البحث عن رحلة",

        departure:
            "المغادرة",

        destination:
            "الوجهة",

        startDate:
            "تاريخ البدء",

        adults:
            "البالغون",

        children:
            "الأطفال",

        rooms:
            "الغرف",

        nights:
            "الليالي",

        childAge:
            "عمر الطفل",

        transport:
            "وسيلة النقل",

        bus:
            "حافلة",

        plane:
            "طائرة",

        train:
            "قطار",

        passengerFerry:
            "عبّارة ركاب",

        carFerry:
            "عبّارة سيارات",

        ownCar:
            "سيارتي الخاصة",

        ownEV:
            "سيارتي الكهربائية الخاصة",

        budgetStrategy:
            "استراتيجية الميزانية",

        bestCheapest:
            "الأفضل + الأرخص",

        customBudget:
            "ميزانية مخصصة",

        budgetTRY:
            "الميزانية بالليرة التركية",

        optional:
            "اختياري",

        minimumHotelRating:
            "الحد الأدنى لتقييم الفندق",

        hotelLocation:
            "موقع الفندق",

        cityCenter:
            "وسط المدينة",

        nearSea:
            "بالقرب من البحر",

        natureMountain:
            "الطبيعة / الجبال",

        quietArea:
            "منطقة هادئة",

        hotelAmenities:
            "مرافق الفندق",

        pool:
            "مسبح",

        spa:
            "سبا",

        beach:
            "شاطئ",

        aquapark:
            "أكوابارك",

        mealPlan:
            "خطة الوجبات",

        breakfastOnly:
            "الإفطار فقط",

        roomOnly:
            "الغرفة فقط",

        halfBoard:
            "نصف إقامة",

        fullBoard:
            "إقامة كاملة",

        allInclusive:
            "شامل كليًا",

        specialNotes:
            "ملاحظات خاصة",

        specialNotesPlaceholder:
            "رحلة عائلية، أطعمة محلية، إلخ.",

        search:
            "ابحث وخطط",

        searching:
            "جارٍ البحث عن البيانات المباشرة...",

        emptyState:
            "أدخل متطلبات رحلتك ثم ابحث.",

        loading:
            "جارٍ البحث عن الفنادق والمطاعم والمعالم ووسائل النقل والطرق...",

        travelPlan:
            "خطة السفر",

        total:
            "الإجمالي",

        dailyPlan:
            "الخطة اليومية",

        sources:
            "المصادر",

        recommendedHotel:
            "الفندق المقترح",

        noVerifiedHotel:
            "لم يتم العثور على نتيجة فندق موثوقة.",

        rating:
            "التقييم",

        reviews:
            "التقييمات",

        googleHotels:
            "Google Hotels",

        perRoomNight:
            "للغرفة / الليلة",

        openHotelSource:
            "فتح مصدر الفندق",

        transportTitle:
            "وسيلة النقل",

        routeChecked:
            "تم التحقق من الطريق",

        noVerifiedOperator:
            "لا يوجد مشغل موثوق",

        openTransportSource:
            "فتح مصدر النقل",

        hotelTransport:
            "الفندق ↔ النقل",

        stationToHotel:
            "المحطة / المبنى → الفندق",

        hotelToStation:
            "الفندق → المحطة / المبنى",

        duration:
            "المدة",

        distance:
            "المسافة",

        openGoogleMaps:
            "فتح في خرائط Google",

        day:
            "اليوم",

        lunch:
            "الغداء",

        dinner:
            "العشاء",

        breakfast:
            "الإفطار",

        ratingShort:
            "التقييم",

        source:
            "المصدر",

        place:
            "المكان",

        restaurant:
            "المطعم",

        noHotelCandidate:
            "لم يتم إرجاع أي فندق من Google Hotels.",

        noSpecificTransport:
            "تعذر التحقق من شركة نقل محددة.",

        priceUnavailable:
            "لم يُرجع المزود السعر الإجمالي الحالي للفندق المختار. لم يتم اختراع أي سعر.",

        transportPriceUnavailable:
            "تم العثور على شركة النقل المختارة، ولكن لم يُرجع المزود سعر تذكرة حاليًا.",

        noTicketPrice:
            "تم العثور على المشغل، ولكن لم يتم إرجاع سعر التذكرة الحالي من البحث.",

        differentPlaces:
            "يجب أن تكون نقطة المغادرة والوجهة مختلفتين.",

        chooseStartDate:
            "يرجى اختيار تاريخ البدء.",

        map:
            "فتح في خرائط Google",

        routeFeasible:
            "يبدو أن الطريق ممكن، ولكن تعذر التحقق من مشغل محدد من نتائج البحث الحالية.",

        noRoute:
            "لم يتم العثور على طريق {mode} موثوق من {origin} إلى {destination}.",

        missingHotelFeatures:
            "لم تتوفر جميع مرافق الفندق المطلوبة معًا في نتائج البحث الموثوقة. اختار النظام أفضل تطابق عملي بدلًا من اختراع فندق.",

        breakfastAccordingToMealPlan:
            "الإفطار وفقًا لخطة الوجبات المختارة.",

        lunchRecommended:
            "الغداء في المطعم الموصى به والأعلى ترتيبًا.",

        dinnerAccordingToMealPlan:
            "العشاء وفقًا لخطة الوجبات المختارة.",

        exactReturnTiming:
            "يظهر وقت العودة الدقيق فقط عند توفر وقت مغادرة موثوق.",

        hotelExplanation:
            "اشرح سبب اختيار هذا الفندق اعتمادًا فقط على المعلومات المقدمة.",

        transportExplanation:
            "اشرح سبب اختيار وسيلة النقل هذه اعتمادًا فقط على المعلومات المقدمة.",

        arrivalExplanation:
            "اشرح انتقال الوصول باستخدام معلومات الطريق الموثوقة المقدمة فقط.",

        departureExplanation:
            "اشرح انتقال المغادرة باستخدام معلومات الطريق الموثوقة المقدمة فقط."
    }

};


function translate(
    key,
    replacements = {}
) {

    let text =
        I18N[
            state.lang
        ]?.[
            key
        ]
        ||
        I18N.en[key]
        ||
        key;


    Object.entries(
        replacements
    ).forEach(
        ([name, value]) => {

            text =
                text.replaceAll(
                    `{${name}}`,
                    String(value)
                );

        }
    );


    return text;
}


function applyLanguage() {

    document.documentElement.lang =
        state.lang;

    document.documentElement.dir =
        state.lang === "ar"
        ?
            "rtl"
        :
            "ltr";


    document
        .querySelectorAll(
            "[data-i18n]"
        )
        .forEach(
            element => {

                const key =
                    element.dataset.i18n;

                element.textContent =
                    translate(key);

            }
        );


    document
        .querySelectorAll(
            "[data-i18n-placeholder]"
        )
        .forEach(
            element => {

                const key =
                    element.dataset.i18nPlaceholder;

                element.placeholder =
                    translate(key);

            }
        );


    const langSelector =
        $("langSelector");


    if (langSelector) {

        langSelector
            .querySelector(
                'option[value="tr"]'
            )
            .textContent =
            translate(
                "languageTurkish"
            );

        langSelector
            .querySelector(
                'option[value="en"]'
            )
            .textContent =
            translate(
                "languageEnglish"
            );

        langSelector
            .querySelector(
                'option[value="ar"]'
            )
            .textContent =
            translate(
                "languageArabic"
            );
    }


    const themeLabels = {
        midnight:
            "themeMidnight",

        ocean:
            "themeOcean",

        lavender:
            "themeLavender",

        sunset:
            "themeSunset"
    };


    const themeSelector =
        $("themeSelector");


    if (themeSelector) {

        Object.entries(
            themeLabels
        ).forEach(
            ([value, key]) => {

                const option =
                    themeSelector.querySelector(
                        `option[value="${value}"]`
                    );

                if (option) {

                    option.textContent =
                        translate(key);

                }

            }
        );
    }


    const mode =
        document.body.dataset.mode
        || "dark";


    updateModeText(
        mode
    );


    if (
        state.currentData
    ) {

        render(
            state.currentData
        );

    }
}


function updateModeText(
    mode
) {

    const icon =
        $("modeToggleIcon");

    const text =
        $("modeToggleText");

    const toggle =
        $("modeToggle");


    if (
        !icon ||
        !text ||
        !toggle
    ) {
        return;
    }


    const isLight =
        mode === "light";


    toggle.classList.toggle(
        "is-light",
        isLight
    );


    toggle.setAttribute(
        "aria-pressed",
        String(
            isLight
        )
    );


    icon.textContent =
        isLight
        ?
            "☀"
        :
            "☾";


    text.textContent =
        isLight
        ?
            translate("bright")
        :
            translate("dark");
}


function applyMode(
    mode
) {

    if (
        mode !== "light"
        &&
        mode !== "dark"
    ) {

        mode = "dark";

    }


    document.body.dataset.mode =
        mode;


    localStorage.setItem(
        "voyageai-mode",
        mode
    );


    updateModeText(
        mode
    );
}


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
    document.getElementById(
        id
    );


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
            Number(value)
        )
    ) {

        return "—";

    }


    return (
        Number(
            value
        ).toLocaleString(
            state.lang === "ar"
            ?
                "ar"
            :
                state.lang
        )
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
                        || translate("source")
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
            ?
                Number(
                    $("child_age").value
                    || 1
                )
            :
                null,

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
                    ${translate(
                        "recommendedHotel"
                    )}
                </h3>

                <p class="muted">
                    ${translate(
                        "noVerifiedHotel"
                    )}
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

                        ${translate(
                            "rating"
                        )}:
                        ${hotel.rating ?? "—"}

                        ·

                        ${translate(
                            "reviews"
                        )}:
                        ${hotel.reviews ?? "—"}

                    </p>

                </div>


                <span class="verified">
                    ✓ ${translate(
                        "googleHotels"
                    )}
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

                ${translate(
                    "perRoomNight"
                )}:

                <strong>
                    ${fmtPrice(
                        hotel.price_per_room_per_night_try
                    )}
                </strong>

            </p>


            <p class="price">

                ${translate(
                    "total"
                )}:

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
                    ${translate(
                        "openHotelSource"
                    )}
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
                    ${translate(
                        "transportTitle"
                    )}
                </h3>

                ${
                    transport.verified_route

                    ?

                    `
                    <span class="verified">
                        ✓ ${translate(
                            "routeChecked"
                        )}
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
                    ${translate(
                        "noVerifiedOperator"
                    )}
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

                    ${translate(
                        "noTicketPrice"
                    )}

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
                    ${translate(
                        "openTransportSource"
                    )}
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
                ${translate(
                    "hotelTransport"
                )}
            </h3>


            ${
                transfer.to_hotel

                ?

                `
                <div class="item">

                    <strong>
                        ${translate(
                            "stationToHotel"
                        )}
                    </strong>

                    <p class="muted">

                        ${translate(
                            "duration"
                        )}:
                        ${esc(
                            transfer.to_hotel.duration
                        )}

                        ·

                        ${translate(
                            "distance"
                        )}:
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
                            ${translate(
                                "openGoogleMaps"
                            )}
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
                        ${translate(
                            "hotelToStation"
                        )}
                    </strong>

                    <p class="muted">

                        ${translate(
                            "duration"
                        )}:
                        ${esc(
                            transfer.from_hotel.duration
                        )}

                        ·

                        ${translate(
                            "distance"
                        )}:
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
                            ${translate(
                                "openGoogleMaps"
                            )}
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
                    ${translate(
                        "day"
                    )}
                    ${day.day_number}
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
                    ||
                    translate(
                        "breakfastAccordingToMealPlan"
                    )
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

                                ${translate(
                                    "ratingShort"
                                )}:

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
                                    ${translate(
                                        "openGoogleMaps"
                                    )}
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
                                    ||
                                    translate(
                                        "lunch"
                                    )
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

                                ${translate(
                                    "ratingShort"
                                )}:

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
                                    ${translate(
                                        "openGoogleMaps"
                                    )}
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
                                ||
                                0
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

                    localStorage.setItem(
                        "voyageai-language",
                        state.lang
                    );

                    applyLanguage();

                }
            );


        $("themeSelector")
            .addEventListener(
                "change",
                event => {

                    applyTheme(
                        event.target.value
                    );

                }
            );


        const savedTheme =
            localStorage.getItem(
                "voyageai-theme"
            )
            || "midnight";


        $("themeSelector").value =
            savedTheme;


        applyTheme(
            savedTheme
        );


        $("modeToggle")
            .addEventListener(
                "click",
                () => {

                    const currentMode =
                        document.body.dataset.mode
                        || "dark";


                    applyMode(
                        currentMode === "dark"
                        ?
                            "light"
                        :
                            "dark"
                    );

                }
            );


        const savedMode =
            localStorage.getItem(
                "voyageai-mode"
            )
            || "dark";


        applyMode(
            savedMode
        );


        const savedLanguage =
            localStorage.getItem(
                "voyageai-language"
            )
            || "tr";


        if (
            I18N[
                savedLanguage
            ]
        ) {

            state.lang =
                savedLanguage;

        }


        $("langSelector").value =
            state.lang;


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
                            translate(
                                "differentPlaces"
                            )
                        );

                        return;

                    }


                    if (
                        !$("start_date").value
                    ) {

                        alert(
                            translate(
                                "chooseStartDate"
                            )
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
                        translate(
                            "searching"
                        );


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
                            translate(
                                "search"
                            );

                    }

                }
            );


        applyLanguage();

    }
);