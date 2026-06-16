from pydantic import BaseModel


class NewsArticle(BaseModel):
    title: str
    source: str | None = None
    published: str | None = None
    link: str | None = None
    sentiment: str
    sentiment_score: float
    impact: str


class NewsSentimentResponse(BaseModel):
    symbol: str
    overall_sentiment: str
    average_score: float
    summary: str
    articles: list[NewsArticle]
