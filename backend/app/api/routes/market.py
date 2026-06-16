from fastapi import APIRouter

from backend.app.models.market import MarketValuationResponse
from backend.app.services.market_valuation_service import MarketValuationService


router = APIRouter()
service = MarketValuationService()


@router.get("/valuation", response_model=MarketValuationResponse)
def market_valuation() -> MarketValuationResponse:
    return service.analyze()
