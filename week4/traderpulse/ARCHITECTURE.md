# Architecture Guide - TraderPulse

## Overview

TraderPulse follows a clean, decoupled architecture:
- **Backend**: FastAPI (Python 3.12+) serving REST APIs.
- **Frontend**: Next.js 16 (React Server Components + Client Components) with shadcn/ui.
- **External Services**: Alpha Vantage (Market Data), Google Gemini (AI).

## System Data Flow

```mermaid
graph TD
    Client[Next.js Frontend] -->|REST API| API[FastAPI Backend]
    API -->|HTTP Request| AV[Alpha Vantage API]
    API -->|HTTP Request| Gemini[Gemini 3 Flash API]
    
    subgraph Backend Services
        API --> MarketService
        API --> AIService
    end
    
    MarketService --> AV
    AIService --> Gemini
```

## AI Analysis Flow

```mermaid
sequenceDiagram
    participant User
    participant Frontend
    participant API as FastAPI
    participant Gemini
    
    User->>Frontend: Clicks "Analyze Sentiment"
    Frontend->>API: GET /api/v1/sentiment/{symbol}
    API->>API: Fetch Market Data Context
    API->>Gemini: Send Data + Prompt
    Gemini-->>API: JSON: {sentiment, justification}
    API-->>Frontend: Return Analysis
    Frontend-->>User: Display Widget
```

## Tech Stack Decisions

- **FastAPI**: High performance, native async support, perfect for IO-bound API proxying.
- **Next.js 16**: Latest features (App Router), server-side rendering for SEO and performance.
- **Tailwind + shadcn/ui**: Rapid UI development with accessible, beautiful components.
- **Gemini 3 Flash**: Low latency, high throughput model ideal for real-time user-facing applications.
