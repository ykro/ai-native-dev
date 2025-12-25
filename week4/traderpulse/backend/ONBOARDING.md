# Backend Developer Onboarding

Welcome to the TraderPulse Backend! This guide is designed to take you from "zero" to "shipping features" as quickly as possible. It covers setup, architecture, and common development workflows.

## 1. Quick Setup

### Prerequisites
- **Python 3.12+** (`python3 --version`)
- **Pip** (`pip --version`)

### Environment Setup
1.  **Clone & Navigate**:
    ```bash
    cd backend
    ```
2.  **Create Virtual Environment** (Critical for isolation):
    ```bash
    python3 -m venv .venv
    ```
3.  **Activate**:
    - MacOS/Linux: `source .venv/bin/activate`
    - Windows: `.venv\Scripts\Activate`
4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Environment Variables**:
    Create a `.env` file in `backend/`:
    ```env
    # Required: Get a free key from https://aistudio.google.com/
    GEMINI_API_KEY=your_key_here
    ```

### Run Server
```bash
uvicorn main:app --reload --port 8000
```
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 2. Understanding the Architecture

We use **FastAPI** because of its speed, native async support (crucial for calling external APIs like Yahoo Finance/Gemini without blocking), and automatic documentation.

### Key Concepts

- **Routers (`routers/`)**: The "Controller" layer.
    - Handles HTTP requests (GET, POST).
    - Validates inputs using Pydantic models.
    - Calls Services.
    - Returns HTTP responses or raises `HTTPException`.
    - **Rule**: No business logic here. Just routing and validation.

- **Services (`services/`)**: The "Business Logic" layer.
    - Contains the core logic (e.g., "Calculate sentiment", "Fetch stock price").
    - Interacts with external APIs/Databases.
    - **Rule**: Returns pure Python objects (dicts, lists, models), not HTTP responses.

- **Config (`config.py`)**: The "Settings" layer.
    - Uses `pydantic-settings` to load environment variables.
    - **Rule**: Never use `os.getenv()` directly in code. Always import `settings`.

## 3. Project Structure Deep Dive

```
backend/
├── .venv/               # Virtual environment (Git ignored)
├── .env                 # Secrets (Git ignored)
├── main.py              # Application entry point. Registers routers, CORS.
├── config.py            # Settings classes.
├── requirements.txt     # Dependency list.
├── routers/
│   └── api.py           # All endpoints currently live here.
├── services/
│   ├── market_service.py # Wraps `yfinance`.
│   └── ai_service.py     # Wraps `google-genai`.
└── tests/               # Pytest folder.
```

## 4. Common Workflows

### How to Add a New Endpoint?
1.  **Define the Goal**: e.g., "Get stock news".
2.  **Service Layer**: Add `get_stock_news(symbol)` to `market_service.py`.
3.  **Router Layer**: Add `@router.get("/stocks/{symbol}/news")` in `api.py`.
4.  **Link**: Call the service function from the router.

### How to Debug?
- **Print Debugging**: Simple `print()` works and shows up in the `uvicorn` console.
- **VS Code Debugger**:
    1.  Create a `.vscode/launch.json`:
    2.  Use "Python: FastAPI" configuration.
    3.  Set "Application" to `main.py`.

## 5. Coding Standards

- **Type Hints**: **Mandatory**. Use `str`, `int`, `dict`, `List[str]`, etc.
- **Async/Await**: **Mandatory** for IO-bound operations (API calls).
    - Start functions with `async def`.
    - Call async functions with `await`.
- **Error Handling**:
    - Services should return `None` or raise specific python exceptions.
    - Routers should catch these and raise `HTTPException(status_code=404, detailed=...)`.

## 6. Testing

We use `pytest`.
```bash
pytest
```
- Tests are located in `tests/`.
- We currently focus on integration tests that mock external calls or hit public APIs (be careful with rate limits).
