from fastapi import APIRouter, HTTPException, Query

from backend.app.models.stock import StockHistoryResponse, StockSearchResponse, StockSummaryResponse
from backend.app.services.stock_service import StockDataError, StockService


router = APIRouter()
stock_service = StockService()


@router.get("/search", response_model=StockSearchResponse)
def search_stocks(
    q: str = Query(..., min_length=1, description="Company name or NSE symbol, e.g. reliance or TCS"),
    limit: int = Query(default=10, ge=1, le=25),
) -> StockSearchResponse:
    try:
        return stock_service.search_stocks(query=q, limit=limit)
    except StockDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{symbol}/summary", response_model=StockSummaryResponse)
def get_stock_summary(symbol: str) -> StockSummaryResponse:
    try:
        return stock_service.get_stock_summary(symbol)
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/{symbol}/history", response_model=StockHistoryResponse)
def get_stock_history(
    symbol: str,
    period: str = Query(default="6mo", description="Examples: 1mo, 3mo, 6mo, 1y, 5y"),
    interval: str = Query(default="1d", description="Examples: 1d, 1wk, 1mo"),
) -> StockHistoryResponse:
    try:
        return stock_service.get_stock_history(symbol=symbol, period=period, interval=interval)
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
