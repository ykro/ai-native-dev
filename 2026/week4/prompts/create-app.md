**Objective:**
Develop **TraderPulse**, a high-performance SaaS dashboard for real-time market analysis. The application must feature a decoupled architecture with a **FastAPI** backend (Python 3.12+) and a **Next.js 16** frontend, integrated with **Yahoo Finance** for data and **Gemini 3 Flash** for AI-driven sentiment analysis.

**Technical Requirements:**

*   **Backend:** FastAPI, Uvicorn, Python 3.12+, `python-dotenv` for config.
*   **Frontend:** Next.js 16 (App Router), Tailwind CSS, **shadcn/ui**, **Lucide React** (Icons).
*   **AI:** Gemini 3 Flash via `google-genai` SDK.
*   **API Data:** Yahoo Finance (via `yfinance` library).
*   **Language:** UI and alerts in **Spanish**; code, variables, and documentation in **English**.
*   **Persistence (Optional/Mock):** Memory-based cache or mock layer only for user points (gamification).
*   **Error Handling:**
    *   Do NOT return mock/fallback data for market or AI services.
    *   If Yahoo Finance or Gemini fails or cannot find a symbol, the API must return the appropriate HTTP error code (e.g., 404 Not Found) immediately.
    *   Frontend must handle these errors using **Sonner** toast notifications.

**1. Backend Architecture (FastAPI + Python 3.12+):**

*   **Directory:** `/backend`
*   **Core Logic:**
    *   `services/market_service.py`: Wrapper for **yfinance** to fetch real-time quotes (`fast_info`) and historical data.
    *   `services/ai_service.py`: Logic to send market headlines/data to **Gemini 3 Flash** and retrieve a structured sentiment analysis (Bullish/Bearish/Neutral) and a brief justification in Spanish.
*   **Endpoints:**
    *   `GET /api/v1/stocks/{symbol}`: Returns current price, change, and volume.
    *   `GET /api/v1/sentiment/{symbol}`: Returns the AI-generated sentiment analysis.
    *   `GET /api/v1/gamification/status`: Returns mock data for user points and badges.
*   **Security:** Validate API Keys using Pydantic Settings and implement strict CORS for the frontend production URL.
*   **Testing:** Independent suite using **Pytest** covering service logic and endpoint responses.
*   **Environment Validation:** Ensure `GEMINI_API_KEY` is present before execution.

**2. Frontend Architecture (Next.js 16):**

*   **Directory:** `/frontend`
*   **UI/UX (Modern & Attractive):**    
    *   **Main Dashboard:** A dark-themed layout featuring a real-time **Ticker Tape** (clicking a symbol must update the main chart and sentiment analysis) and a grid of cards for watched stocks/crypto.    
    *   **Market Charts:** Integrate a lightweight charting library (**Recharts**) to visualize price trends.
    *   **AI Sentiment Widget:** A dedicated section that displays the Gemini analysis with color-coded indicators.
    *   **Gamification Sidebar:** A small dashboard showing "Nivel de Inversionista" and "Puntos de Análisis".
*   **State Management:**
    *   Use React Server Components for initial shell.
    *   Use Client Components with **SWR** for real-time polling (e.g., every 60s).
    *   Immutable data patterns for state updates.
*   **Notifications:** Use **Sonner** for displaying error toasts (e.g., "Stock not found").
*   **Testing:** Independent suite using **Vitest** for UI components and data-fetching hooks.
*   **Code Quality:** Setup **ESLint** (Frontend) and **Ruff** (Backend) for linting and formatting.

**3. Infrastructure & DevOps:**

*   **Backend Docker:** Optimized `Dockerfile` for **Google Cloud Run** using Python 3.12-slim.
*   **Frontend Config:** Optimized configuration for Vercel deployment. Additionally, create a `Dockerfile` for the frontend to strictly support the local docker-compose workflow.
*   **Environment Validation:** Use **Zod** (Frontend) and **Pydantic** (Backend) to ensure `GEMINI_API_KEY` (and others) are present before execution.
*   **Local Dev:** `docker-compose.yml` orchestrating both services with hot-reload.

**4. Documentation (Critical Requirement):**

*   **Philosophy:** Documentation must be comprehensive enough to serve as a **Developer Handbook**. A new engineer should be able to understand the codebase, context, and workflows without asking questions.
*   **Structure:** Implement a "Hub & Spoke" documentation model.
    *   **Root**: `README.md` (Overview), `ONBOARDING.md` (Hub linking to sub-guides), `ARCHITECTURE.md` (High-level System Flow).
    *   **Components**: Create specific `README`, `ONBOARDING`, and `ARCHITECTURE` files inside both `/backend` and `/frontend` directories.
*   **Content Requirements:**
    *   **Onboarding Guides:** Must include "Quick Start", "Project Structure Deep Dive" (explaining every key folder), "Common Workflows" (e.g., "How to add an Endpoint"), and "Debugging" (VS Code `launch.json` configs).
    *   **Architecture Guides:** Must include **Mermaid** diagrams and a "Key Architectural Decisions" (ADR) section explaining the *why* behind choices (e.g., "Why FastAPI?", "Why SWR?").
    *   **READMEs:** Detailed feature lists, API references (Backend), and Component libraries (Frontend).