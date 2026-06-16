from fastapi import APIRouter

from backend.app.models.watchlist import (
    AlertCreateRequest,
    AlertItem,
    WatchlistAddRequest,
    WatchlistIntelligenceResponse,
    WatchlistItem,
)
from backend.app.services.watchlist_service import WatchlistService


router = APIRouter()
service = WatchlistService()


@router.post("/items", response_model=WatchlistItem)
def add_watchlist_item(request: WatchlistAddRequest) -> WatchlistItem:
    return service.add(request)


@router.delete("/items/{item_id}")
def remove_watchlist_item(item_id: int) -> dict[str, str]:
    service.remove(item_id)
    return {"status": "removed"}


@router.post("/alerts", response_model=AlertItem)
def create_alert(request: AlertCreateRequest) -> AlertItem:
    return service.add_alert(request)


@router.get("/intelligence", response_model=WatchlistIntelligenceResponse)
def watchlist_intelligence() -> WatchlistIntelligenceResponse:
    return service.intelligence()
