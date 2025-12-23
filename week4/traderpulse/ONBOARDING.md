# Developer Onboarding

Welcome to TraderPulse! This guide will help you set up your local development environment.

## Prerequisites

- Python 3.12+
- Node.js 20+
- Git

## Setup Steps

### 1. Clone & Config

```bash
git clone <repo_url>
cd traderpulse
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Create `.env`:
```env
ALPHA_VANTAGE_KEY=demo
GEMINI_API_KEY=demo
CORS_ORIGINS=http://localhost:3000
```

Run Server:
```bash
uvicorn backend.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
```

Run Dev Server:
```bash
npm run dev
```
Access at [http://localhost:3000](http://localhost:3000).

## Running Tests

**Backend**:
```bash
cd backend
pytest
```

**Frontend**:
```bash
cd frontend
npx vitest
```

## Troubleshooting

- **CORS Errors**: Ensure `CORS_ORIGINS` in `backend/.env` matches your frontend URL.
- **API Errors**: Check if your API Keys are valid.
