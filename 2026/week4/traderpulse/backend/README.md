# TraderPulse Backend

The **TraderPulse Backend** is a robust, async-first REST API built with [FastAPI](https://fastapi.tiangolo.com/). It serves as the intelligent core of the platform, aggregating real-time market data and generating AI-powered sentiment analysis.

## 🌟 Features

- **Real-Time Market Data**: Proxies data from Yahoo Finance (`yfinance`) to provide sub-second price updates without managing complex WebSocket connections.
- **AI Sentiment Engine**: A dedicated integration with **Google Gemini 1.5 Flash** that analyzes market context to generate "Bullish", "Bearish", or "Neutral" signals with natural language justifications.
- **Resilient Architecture**: Built with Pydantic for strict data validation and robustness against external API failures.
- **CORS Enabled**: Configured to securely communicate with the Next.js frontend.

## 🔌 API Reference

### Market Data (`/api/v1/stocks`)

- **GET** `/stocks/{symbol}`
    - **Description**: Fetches real-time price, change percent, and volume for a given symbol (e.g., `AAPL`, `BTC-USD`).
    - **Response**:
        ```json
        {
          "symbol": "AAPL",
          "price": 150.25,
          "change": 1.25,
          "change_percent": 0.83,
          "volume": 50000000
        }
        ```

### AI Sentiment (`/api/v1/sentiment`)

- **GET** `/sentiment/{symbol}`
    - **Description**: Triggers a live inference call to Gemini 1.5 Flash. It feeds recent price action to the model and requests a sentiment assessment.
    - **Response**:
        ```json
        {
          "symbol": "AAPL",
          "sentiment": "bullish",
          "confidence": 0.85,
          "justification": "Strong upward momentum observed in the last trading session..."
        }
        ```

## 🛠️ Data Models

The application uses Pydantic models for all data exchange. Key models include:

- **`StockQuote`**: Represents a snapshot of a stock's price.
- **`SentimentAnalysis`**: The structural output from the AI model.

## 🚀 Deployment (Google Cloud Run)

The backend is designed to run serverless on Cloud Run.

### Prerequisites
- Google Cloud Project
- Service Account with `Secret Manager Secret Accessor` role.

### Steps
1.  **Secrets**: Create `traderpulse-gemini-key` in Google Secret Manager.
2.  **Deploy**:
    ```bash
    gcloud run deploy traderpulse-api \
      --source . \
      --region us-central1 \
      --allow-unauthenticated \
      --set-secrets="GEMINI_API_KEY=traderpulse-gemini-key:latest"
    ```

For setup and running instructions, please see the **[Onboarding Guide](./ONBOARDING.md)**.
