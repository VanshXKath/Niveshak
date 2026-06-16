from fastapi import APIRouter, HTTPException, Query

from backend.app.models.technical import TechnicalAnalysisResponse
from backend.app.services.stock_service import StockDataError
from backend.app.services.technical_service import TechnicalService


router = APIRouter()
service = TechnicalService()


@router.get("/{symbol}", response_model=TechnicalAnalysisResponse)
def technical_analysis(symbol: str, period: str = Query(default="6mo")) -> TechnicalAnalysisResponse:
    try:
        return service.analyze(symbol=symbol, period=period)
    except StockDataError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
