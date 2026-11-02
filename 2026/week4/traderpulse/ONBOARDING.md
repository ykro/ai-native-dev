# Developer Onboarding Hub

Welcome to the **TraderPulse** project! This document serves as the starting point for all new developers.

## 🚀 Quick Start (Docker)

If you just want to run the application without setting up local development environments:

1.  **Backend Config**: Create `backend/.env` (see [Backend Onboarding](./backend/ONBOARDING.md) for details).
2.  **Run**:
    ```bash
    docker-compose up --build
    ```
3.  **Access**:
    - Frontend: [http://localhost:3000](http://localhost:3000)
    - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🛠️ Local Development Setup

For active development, you should set up the backend and frontend separately. Please follow the detailed guides below:

### 1. Backend Setup (Python/FastAPI)
> Go to: **[Backend Onboarding Guide](./backend/ONBOARDING.md)**
- **Prerequisites**: Python 3.12+
- **Key Steps**: Virtual Env creation, Dependency installation, Environment Variables.

### 2. Frontend Setup (Next.js)
> Go to: **[Frontend Onboarding Guide](./frontend/ONBOARDING.md)**
- **Prerequisites**: Node.js 20+
- **Key Steps**: `npm install`, Environment Variables.

## 📚 Documentation Index

- **[Project README](./README.md)**: High-level overview.
- **[Architecture](./ARCHITECTURE.md)**: System design and diagrams.
