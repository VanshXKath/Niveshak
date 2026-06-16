from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.routes import (
    chat,
    fundamental,
    market,
    mutual_funds,
    news,
    portfolio,
    sectors,
    stocks,
    technical,
    watchlist,
)
from backend.app.core.config import settings
from backend.app.db.database import init_db
from backend.app.web.pages import router as web_router

WEB_ROOT = Path(__file__).resolve().parents[2] / "web"

init_db()

app = FastAPI(
    title=settings.app_name,
    description="Full-feature AI-powered Indian stock market investment platform.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(WEB_ROOT / "static")), name="static")
app.include_router(web_router)
app.include_router(stocks.router, prefix="/api/stocks", tags=["stocks"])
app.include_router(technical.router, prefix="/api/technical", tags=["technical"])
app.include_router(fundamental.router, prefix="/api/fundamental", tags=["fundamental"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(market.router, prefix="/api/market", tags=["market"])
app.include_router(mutual_funds.router, prefix="/api/mutual-funds", tags=["mutual-funds"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(sectors.router, prefix="/api/sectors", tags=["sectors"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])


@app.get("/")
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard")


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {
        "status": "ok",
        "message": "NiveshakAI backend is running.",
        "version": "1.0.0",
    }
