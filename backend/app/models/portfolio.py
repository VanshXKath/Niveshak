from pydantic import BaseModel, Field


class PortfolioHoldingInput(BaseModel):
    symbol: str
    quantity: float = Field(..., gt=0)
    avg_price: float = Field(..., gt=0)


class PortfolioHolding(BaseModel):
    id: int
    symbol: str
    quantity: float
    avg_price: float
    current_price: float | None = None
    market_value: float | None = None
    pnl: float | None = None
    pnl_percent: float | None = None
    sector: str | None = None


class PortfolioAnalysisResponse(BaseModel):
    holdings: list[PortfolioHolding]
    total_invested: float
    total_current_value: float
    total_pnl: float
    total_pnl_percent: float | None
    diversification_score: float
    risk_score: str
    sector_exposure: dict[str, float]
    recommendations: list[str]
    beginner_summary: str
