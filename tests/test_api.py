from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from backend.app.models.stock import StockHistoryPoint, StockHistoryResponse, StockSearchResponse, StockSearchResult, StockSummaryResponse


def test_health_check(client: TestClient) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload.get("version") == "1.0.0"


@patch("backend.app.api.routes.stocks.stock_service.search_stocks")
def test_search_endpoint(mock_search: MagicMock, client: TestClient) -> None:
    mock_search.return_value = StockSearchResponse(
        query="tcs",
        results=[StockSearchResult(symbol="TCS", name="Tata Consultancy Services Ltd", exchange="NSE")],
    )

    response = client.get("/api/stocks/search?q=tcs")

    assert response.status_code == 200
    payload = response.json()
    assert payload["query"] == "tcs"
    assert payload["results"][0]["symbol"] == "TCS"


@patch("backend.app.api.routes.stocks.stock_service.get_stock_summary")
def test_summary_endpoint(mock_summary: MagicMock, client: TestClient) -> None:
    mock_summary.return_value = StockSummaryResponse(
        symbol="RELIANCE.NS",
        company_name="Reliance Industries Ltd",
        current_price=2500.0,
        previous_close=2480.0,
        data_source="yfinance",
        beginner_summary="Sample summary.",
    )

    response = client.get("/api/stocks/RELIANCE/summary")

    assert response.status_code == 200
    assert response.json()["symbol"] == "RELIANCE.NS"


@patch("backend.app.api.routes.stocks.stock_service.get_stock_history")
def test_history_endpoint(mock_history: MagicMock, client: TestClient) -> None:
    mock_history.return_value = StockHistoryResponse(
        symbol="SBIN.NS",
        period="6mo",
        interval="1d",
        prices=[StockHistoryPoint(date="2025-01-01", close=700.0)],
        data_source="yahoo_chart_api",
    )

    response = client.get("/api/stocks/SBIN/history?period=6mo")

    assert response.status_code == 200
    assert response.json()["prices"][0]["close"] == 700.0
