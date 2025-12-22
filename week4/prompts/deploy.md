**Objective:**
Deploy the **TraderPulse** SaaS to production. The backend (FastAPI + Python 3.14.2) will run on **Google Cloud Run**, pulling sensitive credentials from **Google Secret Manager**. The frontend (Next.js 16) will be hosted on **Vercel**.

**Technical Specs:**

* **Backend:** Python 3.14.2 (free-threading mode).
* **Security:** Google Secret Manager (GSM) for `ALPHA_VANTAGE_KEY` and `GEMINI_API_KEY`.
* **Frontend:** Next.js 16 (Vercel).

**Step 1: Google Secret Manager Setup**

1. **Secret Creation:** Create two secrets in GSM: `traderpulse-alpha-vantage` and `traderpulse-gemini-key`.
2. **Permissions:** Ensure the Cloud Run Service Account has the "Secret Manager Secret Accessor" role.
3. **Deployment Instruction:** When deploying the container to Cloud Run, **mount** these secrets as environment variables (`ALPHA_VANTAGE_KEY` and `GEMINI_API_KEY`) so the FastAPI code can read them via Pydantic Settings without them being visible in the Cloud Run configuration UI.

**Step 2: Backend Deployment (Cloud Run)**

1. **Build & Push:** Build the Docker image (Python 3.14-slim) and push it to Google Artifact Registry.
2. **Cloud Run Deploy:**
* Service name: `traderpulse-api`.
* Region: Select nearest.
* Resources: 512MiB RAM / 1 CPU.
* Secrets: Map GSM secrets to environment variables.
* Flag: `--allow-unauthenticated`.
* **Performance:** Ensure HTTP/2 is enabled.



**Step 3: Frontend Deployment (Vercel)**

1. **Configuration:** Set `NEXT_PUBLIC_API_URL` to the URL provided by Cloud Run.
2. **Deployment:** Run `vercel --prod`.

**Step 4: CORS Final Sync**

1. **Final Loop:** Once Vercel provides the production domain, update the Cloud Run environment variable `FRONTEND_URL` to that domain to lock down the CORS policy.

**Step 5: Smoke Test Documentation**

1. Verify `/api/v1/health` on Cloud Run.
2. Verify the Frontend-Backend-AI handshake on the Vercel URL.
