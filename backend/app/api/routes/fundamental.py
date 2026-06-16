from fastapi import APIRouter, HTTPException

from backend.app.models.fundamental import FundamentalAnalysisResponse
from backend.app.services.fundamental_service import FundamentalService
from backend.app.services.stock_service import StockDataError


router = APIRouter()
service = FundamentalService()


@router.get("/{symbol}", response_model=FundamentalAnalysisResponse)
def fundamental_analysis(symbol: str) -> FundamentalAnalysisResponse:
    try:
        return service.analyze(symbol)
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
