# Developer Onboarding Guide

Welcome to the team! This guide is designed to get you up and running with the **Decoupled Boilerplate** project as quickly as possible. It covers everything from prerequisites to your first code contribution.

## Project Overview

We are building a decoupled web application using a "Backend for Frontend" (BFF) pattern.
- **Frontend:** Next.js 16 (React) with Tailwind CSS v4 and shadcn/ui.
- **Backend:** FastAPI (Python 3.12+) optimized for performance.
- **Communication:** Strict HTTP REST API with CORS policies.

---

## Prerequisites

Ensure you have the following tools installed on your machine:

1.  **Python 3.12+**
    *   Verify: `python3 --version`
    *   *Note: The project is ready for Python 3.14 (free-threading support), but compatible with 3.12+.*
2.  **Node.js 20+** (LTS recommended)
    *   Verify: `node -v`
3.  **Git**
    *   Verify: `git --version`

---

## Installation & Setup

### 1. Backend (FastAPI)

The backend resides in the `/backend` directory.

1.  **Navigate to the directory:**
    ```bash
    cd backend
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies:**
    We use `pip install -e .` to install the package in editable mode.
    ```bash
    pip install -e ".[test]"
    ```
    *Troubleshooting:* If you see an error about "flat-layout", ensure your `pyproject.toml` has `[tool.setuptools] py-modules = ["main", "config"]`.

4.  **Configure Environment:**
    Create a `.env` file (optional, defaults are safe for dev):
    ```bash
    echo "FRONTEND_URL=http://localhost:3000" > .env
    ```

5.  **Start the Server:**
    ```bash
    uvicorn main:app --reload
    ```
    The API will be available at `http://localhost:8000`.
    *Health Check:* `http://localhost:8000/api/v1/health`

### 2. Frontend (Next.js)

The frontend resides in the `/frontend` directory.

1.  **Navigate to the directory:**
    ```bash
    cd frontend
    ```

2.  **Install Dependencies:**
    ```bash
    npm install
    ```

3.  **Configure Environment:**
    Copy the example environment file:
    ```bash
    cp .env.example .env.local
    ```
    *Note: Verify `NEXT_PUBLIC_API_URL` serves your backend (default: `http://localhost:8000`).*

4.  **Start the Development Server:**
    ```bash
    npm run dev
    ```
    The app will be available at `http://localhost:3000`.

---

## Architecture & Directory Structure

```mermaid
graph TD
    Root[Project Root]
    Root --> Backend[/backend/]
    Root --> Frontend[/frontend/]
    
    Backend --> Main[main.py (Entry Point)]
    Backend --> Config[config.py (Settings)]
    Backend --> Tests[tests/]
    
    Frontend --> App[app/ (Next.js App Router)]
    Frontend --> Components[components/ (shadcn/ui)]
    Frontend --> Lib[lib/ (Utils & Zod Env)]
```

### Key Concepts
- **BFF Pattern:** The frontend "owns" the user experience. The backend purely serves data.
- **Type Safety:** 
    - **Backend:** Pydantic models validate all inputs/outputs.
    - **Frontend:** Zod schemas validate environment vars and API responses.

---

## Development Workflow

### Running Tests
Always run tests before pushing changes.

*   **Backend:**
    ```bash
    cd backend
    pytest
    ```

*   **Frontend:**
    ```bash
    cd frontend
    npm test
    # or
    npx vitest run
    ```

### Common Tasks

**Adding a New Backend Endpoint:**
1.  Define the path and logic in `main.py` (or a dedicated router file).
2.  Use Pydantic models for request/response bodies.
3.  Add a test case in `tests/`.

**Adding a New Frontend Component:**
1.  Use shadcn to scaffold basic UI elements: `npx shadcn@latest add [component]`.
2.  Compose them in `components/`.
3.  Import into `app/page.tsx` or other routes.

---

## Troubleshooting

**Q: Frontend build fails with "Can't resolve 'tailwindcss-animate'"?**
A: Ensure you have `tailwindcss-animate` installed (`npm install tailwindcss-animate`) and that `globals.css` uses `@plugin "tailwindcss-animate";` (Tailwind v4 syntax), NOT `@import`.

**Q: Backend says "Module not found"?**
A: Make sure you activated the venv: `source venv/bin/activate`.

**Q: CORS Error in Browser?**
A: Check `backend/.env` or `config.py`. Ensure `FRONTEND_URL` matches your running frontend origin (usually `http://localhost:3000`).
