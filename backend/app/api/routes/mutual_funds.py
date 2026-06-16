from fastapi import APIRouter

from backend.app.models.mutual_fund import MutualFundRecommendationRequest, MutualFundRecommendationResponse
from backend.app.services.mutual_fund_service import MutualFundService


router = APIRouter()
service = MutualFundService()


@router.post("/recommend", response_model=MutualFundRecommendationResponse)
def recommend_funds(request: MutualFundRecommendationRequest) -> MutualFundRecommendationResponse:
    return service.recommend(request)
