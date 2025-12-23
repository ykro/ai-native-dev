# TraderPulse

TraderPulse is a high-performance SaaS dashboard for real-time market analysis, featuring a decoupled architecture with a **FastAPI** backend and a **Next.js 16** frontend. It leverages **Gemini 3 Flash** for AI-driven sentiment analysis and **Alpha Vantage** for market data.

## Features

- **Real-time Market Data**: Track stocks and crypto with live updates.
- **AI Sentiment Analysis**: Get instant "Bullish/Bearish" analysis with justifications provided by Gemini AI.
- **Interactive Charts**: Visualize price trends with responsive charts.
- **Gamification**: Earn badges and points for analyzing markets (Mocked for Demo).

## Quick Start

The fastest way to run the full stack is using Docker Compose.

1.  **Prerequisites**: Docker Desktop installed.
2.  **Environment Variables**:
    Create a `.env` file in the `backend` directory:
    ```bash
    ALPHA_VANTAGE_KEY=your_key_here
    GEMINI_API_KEY=your_key_here
    ```
3.  **Run**:
    ```bash
    docker-compose up --build
    ```
4.  **Access**:
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design and diagrams.

## Development

See [ONBOARDING.md](./ONBOARDING.md) for a detailed developer guide.

## License

MIT
