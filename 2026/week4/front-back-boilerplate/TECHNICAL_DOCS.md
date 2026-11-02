# Technical Documentation

## Architecture Patterns

### Backend for Frontend (BFF) & Decoupling
We employ a strictly decoupled architecture where the Frontend and Backend are separate deployable units. 

- **Frontend (Next.js 16):** Acts as the consumer. It handles all UI/UX, routing, and user interaction. It communicates with the backend solely via HTTP APIs.
- **Backend (FastAPI):** Acts as the provider. It exposes a strict API contract. It does not serve any HTML, ensuring a clear separation of concerns.

This pattern allows:
- Independent scaling of Frontend and Backend.
- Ability to swap technologies easily (e.g., replace Frontend with a Mobile App).
- Clear team boundaries (Frontend Team vs Backend Team).

## Type Safety & Validation

We prioritize system stability through rigorous runtime validation using strictly typed schemas.

### Backend: Pydantic Maps
On the backend, we use **Pydantic** (v2) for settings management (`config.py`) and data validation.
- **Why?** It enforces type safety at runtime. If a required environment variable (like `FRONTEND_URL`) is missing or invalid, the application will refuse to start, preventing silent failures in production.

### Frontend: Zod
On the frontend, we use **Zod** (`lib/env.ts`) to validate environment variables and API responses.
- **Why?** TypeScript types are erased at runtime. Zod ensures that the data we receive from the API or environment matches our expectations *before* we use it, preventing crashes due to unexpected `null` or `undefined` values.

## Standards (Dec 2025)
- **Python 3.14:** Utilizing the latest optimization features (free-threading readiness).
- **Next.js 16:** Using the App Router and Server Components for optimal performance.
- **shadcn/ui:** For accessible, copy-pasteable component architecture.
