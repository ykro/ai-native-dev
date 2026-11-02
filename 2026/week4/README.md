# Week 4: Deployment & The Future of Software Engineering

Welcome to the final week of the "AI Native Dev" course. This week we focus on **Delivery**. You will learn how to take your AI-infused application from `localhost` to **Production**, and we will discuss the shifting landscape of our profession.

## Topics Covered

*   **Architecture**: Decoupled Frontend (Next.js) & Backend (FastAPI).
*   **Deployment**: Validating architecture for Cloud Run (Backend) and Vercel (Frontend).
*   **Prompt-Driven Operations**: Using Agents to generate Dockerfiles and Deployment configs (Ops via Instruction).
*   **Secrets Management**: Securely handling API Keys (Google Secret Manager).
*   **Future of Software Engineering**: Agentic Dev, Code as Commodity, and the new "Architect" archetype.

## The AI Native Toolchain

*   **Google Cloud Run**: Serverless Container platform for Python Backend.
*   **Vercel**: Edge Platform for Next.js Frontend.
*   **Docker**: Containerization for consistent environments.
*   **Gemini 3 Flash**: Low-latency AI model for real-time sentiment analysis.

## Directory Structure

### `traderpulse/`
The Source Code for the Weekly Project.
*   **`backend/`**: FastAPI Service (Python 3.12).
*   **`frontend/`**: Next.js 16 Application.
*   **`assets/`**: Screenshots and media.

### `prompts/`
Contains the **Prompt Library** for this week.
*   **`create-app.md`**: Master prompt for generating the TraderPulse SaaS.
*   **`deploy.md`**: Step-by-step prompts for Cloud Run and Vercel deployment.

### `slides/`
Contains the **Course Materials**.
*   **`slides.md`**: The lecture slides in MARP Markdown format.

## The Challenge: Gamification

**Objective**: Implement a **Gamification System** into the deployed TraderPulse dashboard to increase user engagement.

**Context**: Users visit the dashboard but don't stay. We need a "hook".

**Definition of Done**:
- [ ] **Backend**: `/api/v1/gamification` endpoint returns points/badges.
- [ ] **Frontend**: Sidebar displays "Level" (e.g., "Analyst Lvl 1") and a Progress Bar.
- [ ] **Interaction**: Clicking a stock symbol updates the local points counter (Optimistic UI).
- [ ] **Notification**: Sonner Toast "XP Gained!" appears on analysis.
- [ ] **Production**: Successfully deployed to Vercel and Cloud Run.

## Resources

### Deployment
*   [Google Cloud Run Documentation](https://cloud.google.com/run/docs/quickstarts/deploy-container)
*   [Twelve-Factor App Methodology](https://12factor.net/)
*   [Vercel Deployment Guide](https://vercel.com/docs/deployments/overview)

### Future of Dev
*   [The End of Programming (Matt Welsh)](https://cacm.acm.org/magazines/2023/1/267976-the-end-of-programming/fulltext)
*   [Software 2.0 (Andrej Karpathy)](https://karpathy.medium.com/software-2-0-a8187158058c)
*   [Jevons Paradox in AI](https://en.wikipedia.org/wiki/Jevons_paradox)
