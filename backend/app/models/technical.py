from pydantic import BaseModel


class IndicatorValue(BaseModel):
    name: str
    value: float | None
    signal: str
    explanation: str


class TechnicalAnalysisResponse(BaseModel):
    symbol: str
    trend: str
    trend_explanation: str
    support_level: float | None
    resistance_level: float | None
    indicators: list[IndicatorValue]
    beginner_summary: str
