from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings

app = FastAPI(
    title="Decoupled Boilerplate Backend",
    version="1.0.0",
    description="Backend API running on Python 3.14"
)

# CORS Configuration
origins = [
    str(settings.FRONTEND_URL).rstrip("/"),
    "http://localhost:3000", # Development fallback
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint returning system status.
    """
    return {
        "status": "active",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=True)
