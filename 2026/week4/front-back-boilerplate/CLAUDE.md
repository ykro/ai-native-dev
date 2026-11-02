# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A decoupled Backend for Frontend (BFF) boilerplate with FastAPI backend and Next.js frontend. The two services are completely independent - backend serves only JSON APIs, frontend handles all UI rendering.

## Commands

### Backend (from `backend/` directory)

```bash
# Setup
python3 -m venv venv
source venv/bin/activate
pip install -e ".[test]"

# Run dev server (port 8000)
uvicorn main:app --reload

# Run tests
pytest

# Run single test
pytest tests/test_main.py::test_health_check -v
```

### Frontend (from `frontend/` directory)

```bash
# Setup
npm install

# Run dev server (port 3000)
npm run dev

# Run tests
npm test

# Run single test file
npx vitest tests/dashboard.test.tsx

# Run tests in watch mode
npx vitest --watch

# Lint
npm run lint

# Production build
npm run build && npm start
```

## Architecture

```
Browser → Next.js 16 (port 3000) → FastAPI (port 8000)
```

### Key Design Decisions

1. **Strict Decoupling**: Backend serves NO HTML. Frontend handles all rendering. They can be deployed and scaled independently.

2. **Type Safety at Runtime**:
   - Backend: Pydantic BaseSettings validates env vars at startup (`config.py`)
   - Frontend: Zod validates env vars and API responses at runtime (`lib/env.ts`)

3. **CORS**: Backend validates origins via middleware in `main.py`. Allowed origins come from `FRONTEND_URL` env var.

### Request Flow

1. Page loads `app/page.tsx` (Server Component)
2. Calls `getHealth()` which fetches from backend API
3. Backend validates CORS, returns JSON
4. Response rendered in `StatusCard` (Client Component with "use client")

### Component Architecture (Frontend)

- `app/` - Next.js App Router pages and layouts
- `components/ui/` - shadcn/ui base components (Card, Badge, Button)
- `components/` - Application components (StatusCard)
- `lib/env.ts` - Zod environment validation
- `lib/utils.ts` - `cn()` utility for Tailwind class merging

### Tech Stack

- **Frontend**: Next.js 16, React 19, Tailwind CSS v4, shadcn/ui, Vitest
- **Backend**: FastAPI, Pydantic v2, pytest, Python 3.12+

## Environment Variables

### Backend (`backend/.env`)
```
FRONTEND_URL=http://localhost:3000  # Required for CORS
```

### Frontend (`frontend/.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## API Endpoints

- `GET /api/v1/health` - Returns `{ status, version, environment }`

## Testing

- Backend tests use `httpx` with `TestClient` pattern
- Frontend tests use Vitest + Testing Library with jsdom
- Both can run independently without the other service running (use mocks)

## Styling

- Tailwind CSS v4 with `@tailwindcss/postcss` plugin
- OKLch color space variables in `globals.css`
- shadcn/ui "new-york" style variant
- Light/dark theme support via CSS variables
