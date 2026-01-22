# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TraderPulse is a real-time, AI-powered financial market analysis dashboard. It combines live market data from Yahoo Finance with sentiment analysis powered by Google Gemini Flash. The project follows a monorepo structure with a Python backend and Next.js frontend.

**Live Demo**: https://trader-pulse.vercel.app/

## Development Commands

### Backend (from `/backend`)

```bash
# Setup virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Run development server (auto-reload)
uvicorn main:app --reload --port 8000

# Run tests
pytest

# Run single test file
pytest tests/test_api.py -v
```

### Frontend (from `/frontend`)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run production build
npm run start

# Lint code
npm run lint

# Run tests
npx vitest

# Run single test
npx vitest TickerTape
```

### Full Stack (Docker)

```bash
# From project root (requires GEMINI_API_KEY in backend/.env)
docker-compose up --build

# Access points:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/api/v1
# API Docs: http://localhost:8000/docs
```

## Architecture

### System Flow

```
Next.js Frontend → FastAPI Backend → Yahoo Finance (yfinance)
                                   → Google Gemini API
```

### Backend Structure (`/backend`)

- **`main.py`**: FastAPI app entry point, CORS config
- **`config.py`**: Pydantic Settings for environment variables (GEMINI_API_KEY, CORS_ORIGINS)
- **`routers/`**: HTTP route handlers (validation, status codes only)
- **`services/`**: Business logic layer
  - `market_service.py`: Yahoo Finance integration via yfinance
  - `ai_service.py`: Gemini AI sentiment analysis
- **`tests/`**: pytest tests

**Key pattern**: Routers handle HTTP concerns; Services handle domain logic. This separation enables testing business logic without HTTP mocking.

### Frontend Structure (`/frontend`)

- **`src/app/`**: Next.js 16 App Router pages and layouts
- **`src/components/ui/`**: Shadcn/UI components (owned, not imported)
- **`src/components/dashboard/`**: Domain components (TickerTape, MarketChart, SentimentWidget)
- **`src/lib/`**: Utilities and helpers

**Key patterns**:
- Most dashboard widgets are Client Components (`'use client'`) for interactivity
- SWR handles server state (polling, caching, revalidation)
- Tailwind CSS v4 for utility-first styling

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stocks/{symbol}` | Real-time price data + 1-month history |
| GET | `/api/v1/sentiment/{symbol}` | AI sentiment analysis (Bullish/Bearish/Neutral) |
| GET | `/api/v1/gamification/status` | Mock gamification data |
| GET | `/` | Health check |

## Environment Variables

### Backend (`backend/.env`)
```
GEMINI_API_KEY=your-google-gemini-api-key
CORS_ORIGINS=http://localhost:3000
```

### Frontend (Vercel or `.env.local`)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Tech Stack

- **Backend**: FastAPI, Pydantic, yfinance, google-genai, pytest
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS v4, SWR, Recharts, Shadcn/UI
- **Testing**: pytest + pytest-asyncio (backend), Vitest + Testing Library (frontend)

## Deployment

- **Backend**: Google Cloud Run with Secret Manager for GEMINI_API_KEY
- **Frontend**: Vercel (root directory: `frontend`, env: NEXT_PUBLIC_API_URL)
