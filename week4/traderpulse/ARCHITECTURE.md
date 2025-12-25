# System Architecture

## Overview

TraderPulse follows a clean, decoupled architecture:
- **Backend**: FastAPI (Python 3.12+) serving REST APIs.
- **Frontend**: Next.js 16 (React Server Components + Client Components) with shadcn/ui.
- **External Services**: Yahoo Finance (Market Data), Google Gemini (AI).

## System Data Flow

```mermaid
graph TD
    Client[Next.js Frontend] -->|REST API| API[FastAPI Backend]
    API -->|Internal Call| YF[Yahoo Finance Library]
    API -->|HTTP Request| Gemini[Gemini 3 Flash API]
    
    subgraph Backend Services
        API --> MarketService
        API --> AIService
    end
    
    MarketService --> YF
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
    API->>API: Fetch Market Data Context (via yfinance)
    API->>Gemini: Send Data + Prompt
    Gemini-->>API: JSON: {sentiment, justification}
    API-->>Frontend: Return Analysis
    Frontend-->>User: Display Widget
```

## Component Architecture

For detailed breakdown of the internal architecture of each component, please refer to:

- **[Backend Architecture](./backend/ARCHITECTURE.md)**: Service layer patterns, Pydantic models, and API design.
- **[Frontend Architecture](./frontend/ARCHITECTURE.md)**: App Router structure, Client/Server components, and State Management.
