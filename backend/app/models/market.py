from pydantic import BaseModel


class MarketValuationResponse(BaseModel):
    index_name: str
    current_pe: float | None
    historical_average_pe: float | None
    valuation_status: str
    explanation: str
    beginner_summary: str
