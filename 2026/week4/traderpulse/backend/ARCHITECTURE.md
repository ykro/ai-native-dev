# Backend Architecture

## Directory Structure

```
backend/
├── main.py              # Application entry point, CORS config, global exception handling
├── config.py            # Pydantic Settings management (Env vars)
├── requirements.txt     # Python dependencies
├── routers/             # API Route Handlers
│   ├── api.py           # Agregates all endpoints (stocks, sentiment, etc.)
├── services/            # Business Logic Layer
│   ├── market_service.py # Yahoo Finance integration
│   ├── ai_service.py     # Gemini AI integration
└── tests/               # Automated tests
```

## Key Architectural Decisions

### 1. Framework: FastAPI & Async I/O
**Decision**: We chose **FastAPI** over Flask or Django.
**Reasoning**: TraderPulse is an I/O-bound application. It constantly fetches data from external APIs (Yahoo Finance, Google Gemini). FastAPI's native `async/await` support allows the server to handle concurrent requests efficiently without blocking the thread while waiting for external responses. This is critical for maintaining a responsive real-time dashboard.

### 2. Service Layer Pattern
**Decision**: Strict separation between `routers/` and `services/`.
**Reasoning**:
- **Routers**: Responsible *only* for HTTP specifics (parsing query params, validating headers, returning 404/200 codes).
- **Services**: Responsible *only* for domain logic and data fetching. They return pure Python objects.
- **Benefit**: This allows us to test business logic (e.g., sentiment calculation) in isolation without needing to mock HTTP requests or spin up a test client.

### 3. Data Validation: Pydantic Everywhere
**Decision**: Use Pydantic for both Configuration (`config.py`) and API Data Transfer Objects (DTOs).
**Reasoning**: "Fail Fast". We want the application to crash immediately on startup if an API key is missing (Config) or reject a request instantly if data is malformed (Routers). Pydantic guarantees that valid data enters our system.

### 4. Market Data: Yahoo Finance (`yfinance`)
**Decision**: Migrated from Alpha Vantage to `yfinance`.
**Reasoning**:
- **Problem**: Alpha Vantage's free tier (5 API calls/min) was insufficient for a real-time ticker tape application, causing frequent failures and a poor user experience.
- **Solution**: `yfinance` scrapes Yahoo Finance data. While not an official API, it offers higher throughput for our educational/demo use case and allows for real-time `fast_info` access without rate-limit blocking.

### 5. AI Engine: Gemini 3 Flash
**Decision**: Selected **Gemini 1.5 Flash** (via `google-genai`).
**Reasoning**: We needed a model with very low latency to provide "instant" sentiment analysis feedback to the user. "Flash" models are optimized for speed and cost, making them perfect for this high-frequency interaction compared to larger "Pro" models.
