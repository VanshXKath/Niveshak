from __future__ import annotations

import re
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import requests

from backend.app.models.news import NewsArticle, NewsSentimentResponse

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
POSITIVE_WORDS = {"growth", "profit", "beat", "surge", "record", "upgrade", "bullish", "expansion", "dividend", "strong"}
NEGATIVE_WORDS = {"loss", "fall", "drop", "decline", "fraud", "downgrade", "bearish", "weak", "probe", "default", "cut"}


class NewsService:
    def analyze(self, symbol: str, limit: int = 8) -> NewsSentimentResponse:
        base_symbol = symbol.strip().upper().replace(".NS", "")
        query = f"{base_symbol}+NSE+stock"
        articles = self._fetch_rss(query, limit=limit)

        if not articles:
            articles = [
                NewsArticle(
                    title=f"No live news returned for {base_symbol}",
                    source="NiveshakAI",
                    sentiment="neutral",
                    sentiment_score=0.0,
                    impact="Try again later — news feeds can be rate-limited.",
                )
            ]

        scores = [article.sentiment_score for article in articles]
        avg = sum(scores) / len(scores) if scores else 0.0
        overall = self._label(avg)
        summary = (
            f"Scanned {len(articles)} headlines for {base_symbol} (Groww/StockEdge-style news pulse). "
            f"Overall mood: {overall}. Average sentiment score: {avg:.2f}."
        )

        return NewsSentimentResponse(
            symbol=f"{base_symbol}.NS",
            overall_sentiment=overall,
            average_score=round(avg, 2),
            summary=summary,
            articles=articles,
        )

    def _fetch_rss(self, query: str, limit: int) -> list[NewsArticle]:
        try:
            response = requests.get(
                GOOGLE_NEWS_RSS.format(query=query),
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=20,
            )
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
        except Exception:
            return []

        articles: list[NewsArticle] = []
        for item in root.findall(".//item")[:limit]:
            title = (item.findtext("title") or "").strip()
            link = item.findtext("link")
            source = item.findtext("source")
            published = item.findtext("pubDate")
            if published:
                try:
                    published = parsedate_to_datetime(published).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pass
            score = self._score(title)
            articles.append(
                NewsArticle(
                    title=title,
                    source=source,
                    published=published,
                    link=link,
                    sentiment=self._label(score),
                    sentiment_score=score,
                    impact=self._impact(score),
                )
            )
        return articles

    def _score(self, text: str) -> float:
        words = set(re.findall(r"[a-zA-Z]+", text.lower()))
        pos = len(words & POSITIVE_WORDS)
        neg = len(words & NEGATIVE_WORDS)
        if pos == neg == 0:
            return 0.0
        return max(-1.0, min(1.0, (pos - neg) / max(pos + neg, 1)))

    def _label(self, score: float) -> str:
        if score > 0.15:
            return "positive"
        if score < -0.15:
            return "negative"
        return "neutral"

    def _impact(self, score: float) -> str:
        if score > 0.3:
            return "May support positive short-term sentiment."
        if score < -0.3:
            return "May create near-term selling pressure."
        return "Likely limited immediate price impact."
