from pydantic import BaseModel, Field


class MutualFundRecommendationRequest(BaseModel):
    goal: str = Field(..., examples=["wealth_creation", "tax_saving", "emergency_fund"])
    risk_appetite: str = Field(..., examples=["low", "moderate", "high"])
    investment_horizon_years: int = Field(..., ge=1, le=30)
    monthly_sip: float = Field(..., gt=0)


class FundRecommendation(BaseModel):
    category: str
    risk: str
    horizon_years: str
    example_funds: list[str]
    why: str
    suggested_sip: float


class MutualFundRecommendationResponse(BaseModel):
    profile_summary: str
    recommendations: list[FundRecommendation]
    beginner_summary: str
