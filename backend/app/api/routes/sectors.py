from fastapi import APIRouter, Query

from backend.app.models.sector import SectorAnalysisResponse
from backend.app.services.sector_service import SectorService


router = APIRouter()
service = SectorService()


@router.get("/analysis", response_model=SectorAnalysisResponse)
def sector_analysis(period: str = Query(default="3mo")) -> SectorAnalysisResponse:
    return service.analyze(period=period)
