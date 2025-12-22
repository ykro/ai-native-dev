**Objective:**
Develop **TraderPulse**, a high-performance SaaS dashboard for real-time market analysis. The application must feature a decoupled architecture with a **FastAPI** backend (Python 3.14.2) and a **Next.js 16** frontend, integrated with **Alpha Vantage** for data and **Gemini 3 Flash** for AI-driven sentiment analysis.

**Technical Requirements:**

* **Backend:** FastAPI using **Python 3.14.2** (with free-threading/no-GIL enabled).
* **Frontend:** Next.js 16 (App Router) with Tailwind CSS and **shadcn/ui**.
* **AI:** Gemini 3 Flash via `google-genai` SDK.
* **API Data:** Alpha Vantage API.
* **Language:** UI and alerts in **Spanish**; code, variables, and documentation in **English**.
* **Persistence (Optional/Mock):** For this stage, use a memory-based cache or a mock layer for user points (gamification).

**1. Backend Architecture (FastAPI + Python 3.14.2):**

* **Directory:** `/backend`
* **Core Logic:**
* `services/market_service.py`: Wrapper for Alpha Vantage to fetch real-time quotes and historical data.
* `services/ai_service.py`: Logic to send market headlines/data to **Gemini 3 Flash** and retrieve a structured sentiment analysis (Bullish/Bearish/Neutral) and a brief justification in Spanish.


* **Endpoints:**
* `GET /api/v1/stocks/{symbol}`: Returns current price, change, and volume.
* `GET /api/v1/sentiment/{symbol}`: Returns the AI-generated sentiment analysis.
* `GET /api/v1/gamification/status`: Returns mock data for user points and badges.


* **Security:** Validate API Keys using Pydantic Settings and implement strict CORS for the frontend production URL.
* **Testing:** Independent suite using **Pytest** covering service logic and endpoint responses.

**2. Frontend Architecture (Next.js 16):**

* **Directory:** `/frontend`
* **UI/UX (Modern & Attractive):**
* **Main Dashboard:** A dark-themed layout featuring a real-time "Ticker Tape" and a grid of cards for watched stocks/crypto.
* **Market Charts:** Integrate a lightweight charting library (e.g., Recharts) to visualize price trends.
* **AI Sentiment Widget:** A dedicated section that displays the Gemini analysis with color-coded indicators based on sentiment.
* **Gamification Sidebar:** A small dashboard showing "Nivel de Inversionista" and "Puntos de Análisis".


* **State Management:** Use React Server Components for initial data and Client Components with `SWR` or `React Query` for real-time updates.
* **Testing:** Independent suite using **Vitest** for UI components and data-fetching hooks.

**3. Infrastructure & DevOps:**

* **Backend Docker:** Optimized `Dockerfile` for **Google Cloud Run** using Python 3.14-slim.
* **Frontend Config:** Optimized configuration for **Vercel** deployment (environment variable management).
* **Environment Validation:** Use Zod (Frontend) and Pydantic (Backend) to ensure `ALPHA_VANTAGE_KEY` and `GEMINI_API_KEY` are present before execution.

**4. Documentation:**

* **README.md:** Full setup guide, including how to obtain the necessary API keys.
* **Architecture Guide:** **Mermaid** diagrams for:
1. **System Data Flow:** (Alpha Vantage -> FastAPI -> Frontend).
2. **AI Analysis Flow:** (Market Data -> Gemini 3 Flash -> Sentiment UI).


* **Onboarding:** A "Quick Start" guide for new developers to run the entire stack locally using `docker-compose`.
