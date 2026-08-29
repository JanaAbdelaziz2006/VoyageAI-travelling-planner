# VoyageAI Hybrid Travel Planner 🌍✈️

**VoyageAI** is a robust, intelligent, and flexible hybrid travel planning backend and web application built with **FastAPI**, **SerpApi**, and optional **Google Gemini AI**. It automatically searches real-time hotel listings, local attractions, top-rated restaurants, transport operators, and transit routes to generate comprehensive, data-driven, and customizable itineraries.

---

## 🚀 Key Features

- **Hybrid Architecture:** Combines live data extraction via SerpApi (Google Hotels, Google Maps, Google Search, Google Maps Directions) with optional Gemini LLM intelligence for explanation and multi-lingual translation.
- **Smart Ranking Algorithms:** Advanced scoring system for hotels, restaurants, and transport options factoring in user ratings, review counts, pricing, distance, and requested amenities (e.g., pool, spa, beach).
- **Automated Itinerary Scheduling:** Automatically builds day-by-day travel schedules pairing top tourist attractions with premier local dining spots across the trip duration.
- **Door-to-Door Transfer Planning:** Calculates transit routes and summaries between transport terminals (bus stations, airports, train stations) and selected hotels using Google Maps Directions.
- **Strict Data Integrity & Guardrails:** Designed to prevent hallucination — if data or pricing is unavailable, it reports it transparently rather than inventing values.
- **Modern Web Frontend:** Clean, responsive UI with interactive forms and dynamic itinerary rendering.

---

## 🛠️ Project Structure

```text
voyageai_replacement-main/
│
├── main.py                # FastAPI application entry point & API endpoints
├── ai_engine.py           # Hybrid orchestration & optional Gemini explanation layer
├── search_engine.py       # SerpApi wrapper with local caching and error handling
├── ranking.py             # Algorithmic ranking for hotels, restaurants, & transport
├── requirements.txt       # Python package dependencies
├── .env.example           # Environment variables template
├── templates/
│   └── index.html         # Frontend user interface
└── static/
    ├── css/
    │   └── style.css      # Custom styling
    └── js/
        └── app.js         # Frontend interaction logic
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.10+ installed on your system.
- A valid [SerpApi](https://serpapi.com/) API key.
- (Optional) A Google Gemini API key if you want AI-generated explanations and translations.

### 2. Clone or Extract the Repository
Navigate to the project directory:
```bash
cd voyageai_replacement-main
```

### 3. Create a Virtual Environment & Install Dependencies
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root directory (or copy from `.env.example`):
```env
SERPAPI_KEY=your_serpapi_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.6-flash
SERPAPI_HL=en
SERPAPI_GL=tr
SERPAPI_CURRENCY=TRY
```

---

## 🏃‍♂️ Running the Application

Start the FastAPI development server using Uvicorn:
```bash
python main.py
```
*Alternatively:*
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Open your web browser and navigate to:
👉 **http://127.0.0.1:8000**

---

## 🔌 API Endpoints

### `GET /`
Serves the interactive frontend web application.

### `GET /api/health`
Returns system status, API configuration status (SerpApi & Gemini), and active model information.

### `POST /api/plan-trip`
Generates a comprehensive trip plan based on user criteria.

#### Request Body Example (`application/json`):
```json
{
  "origin": "Bursa",
  "destination": "Istanbul",
  "start_date": "2026-09-15",
  "nights": 3,
  "adults_count": 2,
  "children_count": 0,
  "rooms_count": 1,
  "transport_mode": "Bus",
  "budget_type": "cheapest_best",
  "hotel_min_rating": 8.0,
  "amenities": ["spa", "pool"],
  "meal_board": "breakfast_only",
  "language": "en"
}
```

---

## 📦 Caching Mechanism
To optimize API usage and reduce latency, `search_engine.py` implements a robust file-based caching system (`.cache/`) with SHA-256 hashed request parameters and configurable Time-To-Live (TTL) durations.

---

## 🛡️ License
Distributed under the MIT License. See `LICENSE` for more information.
