from pydantic import BaseModel, Field


class WatchlistItem(BaseModel):
    id: int
    symbol: str
    notes: str | None = None


class WatchlistAddRequest(BaseModel):
    symbol: str
    notes: str | None = None


class AlertCreateRequest(BaseModel):
    symbol: str
    alert_type: str = Field(..., examples=["price_above", "price_below", "rsi_below", "rsi_above"])
    threshold: float
    message: str | None = None


class AlertItem(BaseModel):
    id: int
    symbol: str
    alert_type: str
    threshold: float | None
    message: str | None
    is_active: bool
    triggered: bool = False
    trigger_detail: str | None = None


class WatchlistIntelligenceResponse(BaseModel):
    watchlist: list[WatchlistItem]
    alerts: list[AlertItem]
    triggered_count: int
    beginner_summary: str
