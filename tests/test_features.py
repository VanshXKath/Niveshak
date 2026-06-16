from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.main import app  # noqa: F401 — loads full app routes
from backend.app.models.mutual_fund import MutualFundRecommendationResponse
from backend.app.models.technical import IndicatorValue, TechnicalAnalysisResponse


client = TestClient(app)


@patch("backend.app.api.routes.technical.service.analyze")
def test_technical_endpoint(mock_analyze: MagicMock) -> None:
    mock_analyze.return_value = TechnicalAnalysisResponse(
        symbol="TCS.NS",
        trend="Bullish",
        trend_explanation="Uptrend",
        support_level=2100.0,
        resistance_level=2300.0,
        indicators=[IndicatorValue(name="RSI (14)", value=55.0, signal="neutral", explanation="Neutral zone")],
        beginner_summary="Sample technical summary.",
    )
    response = client.get("/api/technical/TCS")
    assert response.status_code == 200
    assert response.json()["trend"] == "Bullish"


@patch("backend.app.api.routes.mutual_funds.service.recommend")
def test_mutual_fund_endpoint(mock_recommend: MagicMock) -> None:
    mock_recommend.return_value = MutualFundRecommendationResponse(
        profile_summary="test",
        recommendations=[],
        beginner_summary="Educational only.",
    )
    response = client.post(
        "/api/mutual-funds/recommend",
        json={"goal": "wealth_creation", "risk_appetite": "moderate", "investment_horizon_years": 7, "monthly_sip": 5000},
    )
    assert response.status_code == 200


def test_market_valuation_endpoint() -> None:
    response = client.get("/api/market/valuation")
    assert response.status_code == 200
    assert "valuation_status" in response.json()


def test_watchlist_intelligence_endpoint() -> None:
    response = client.get("/api/watchlist/intelligence")
    assert response.status_code == 200
    assert "watchlist" in response.json()
