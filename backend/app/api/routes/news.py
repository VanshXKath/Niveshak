from fastapi import APIRouter

from backend.app.models.news import NewsSentimentResponse
from backend.app.services.news_service import NewsService


router = APIRouter()
service = NewsService()


@router.get("/{symbol}", response_model=NewsSentimentResponse)
def news_sentiment(symbol: str) -> NewsSentimentResponse:
    return service.analyze(symbol)
