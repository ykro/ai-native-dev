**Objective:**
Generate a production-grade boilerplate demonstrating a decoupled architecture with a **Next.js 16** frontend and a **FastAPI** backend using **Python 3.14**. This project must focus on connectivity, security (CORS), environment validation, and independent deployment workflows (Vercel & Cloud Run).

**Technical Specifications:**

* **Backend:** FastAPI with Python 3.14 (optimized for free-threading/no-GIL).
* **Frontend:** Next.js 16 (App Router), Tailwind CSS, and shadcn/ui.
* **Deployment:** Dockerized backend (Google Cloud Run) and optimized frontend (Vercel).
* **Context:** Use **context7** to ensure the implementation follows the latest December 2025 standards for these frameworks.
* **Language:** UI and user-facing messages in **Spanish**; code, variables, and technical comments in **English**.

**1. Project Structure:**
Create two isolated directories: `/frontend` and `/backend`.

**2. Backend (FastAPI + Python 3.14):**

* **Directory:** `/backend`
* **Environment Validation:** Use **Pydantic Settings** (v2+) to validate required variables (e.g., `FRONTEND_URL`, `PORT`).
* **CORS:** Implement a middleware configuration that strictly allows the `FRONTEND_URL` for production and `localhost` for development.
* **Endpoint:** A single GET endpoint `/api/v1/health` that returns a structured JSON: `{ "status": "active", "version": "1.0.0", "environment": "development/production" }`.
* **DevOps:** * `Dockerfile`: Optimized multi-stage build using a Python 3.14-slim base image.
* Include a `scripts/smoke-test.sh` to verify the container starts correctly.


* **Testing:** Independent suite using **Pytest** and `httpx` to validate the health-check contract.

**3. Frontend (Next.js 16 + shadcn/ui):**

* **Directory:** `/frontend`
* **Environment Validation:** Use **Zod** to validate `NEXT_PUBLIC_API_URL` at build and runtime.
* **UI/UX:** A modern, minimalist dashboard state in **Spanish**.
* **Data Consumption:** * Implement a Server Component to fetch the `/health` status from the backend.
* Implement a Client Component using `shadcn/ui` (Badge and Card) to display the connection status and a "Reintentar" button.


* **Testing:** Independent suite using **Vitest** and **React Testing Library** to mock API responses and verify the UI states (Success, Loading, Error).

**4. Documentation & Onboarding:**

* **Root README.md:** * **Architecture Diagram:** Use **Mermaid** to show the decoupled flow: `Browser -> Vercel (Next.js) -> Cloud Run (FastAPI)`.
* **Onboarding Guide:** Step-by-step instructions for a new developer to set up Python 3.14, Node.js, and the necessary `.env` files.


* **Technical Docs:** Detailed explanation of the "BFF Pattern" (Backend for Frontend) and why we use Pydantic/Zod for system stability.