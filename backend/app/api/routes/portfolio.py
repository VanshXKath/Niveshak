from fastapi import APIRouter

from backend.app.models.portfolio import PortfolioAnalysisResponse, PortfolioHolding, PortfolioHoldingInput
from backend.app.services.portfolio_service import PortfolioService


router = APIRouter()
service = PortfolioService()


@router.post("/holdings", response_model=PortfolioHolding)
def add_holding(holding: PortfolioHoldingInput) -> PortfolioHolding:
    return service.add_holding(holding)


@router.delete("/holdings/{holding_id}")
def remove_holding(holding_id: int) -> dict[str, str]:
    service.remove_holding(holding_id)
    return {"status": "removed"}


@router.get("/analysis", response_model=PortfolioAnalysisResponse)
def portfolio_analysis() -> PortfolioAnalysisResponse:
    return service.analyze()
