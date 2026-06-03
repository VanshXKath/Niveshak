from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import stocks
from backend.app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    description="Phase 1 backend for an AI-powered Indian stock market screener.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "Stock Screener backend is running.",
    }


app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])