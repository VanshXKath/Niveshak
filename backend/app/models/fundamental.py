from pydantic import BaseModel


class FundamentalMetric(BaseModel):
    name: str
    value: str | None
    interpretation: str | None = None


class FundamentalAnalysisResponse(BaseModel):
    symbol: str
    company_name: str
    metrics: list[FundamentalMetric]
    strengths: list[str]
    weaknesses: list[str]
    risks: list[str]
    opportunities: list[str]
    beginner_summary: str
