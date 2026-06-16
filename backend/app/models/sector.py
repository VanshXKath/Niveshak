from pydantic import BaseModel


class SectorPerformance(BaseModel):
    sector: str
    average_change_percent: float | None
    momentum_score: float
    rank: int
    top_stock: str | None
    explanation: str


class SectorAnalysisResponse(BaseModel):
    period: str
    sectors: list[SectorPerformance]
    strongest_sector: str | None
    weakest_sector: str | None
    beginner_summary: str
