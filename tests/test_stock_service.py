from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from backend.app.models.stock import StockHistoryPoint
from backend.app.services.providers.base import ProviderHistoryData, ProviderSummaryData
from backend.app.services.providers.nse_provider import NSEProvider
from backend.app.services.providers.yahoo_chart_provider import YahooChartProvider
from backend.app.services.providers.yfinance_provider import YFinanceProvider
from backend.app.services.stock_service import StockDataError, StockService


@pytest.fixture
def stock_service() -> StockService:
    return StockService()


def test_normalize_symbol_adds_nse_suffix(stock_service: StockService) -> None:
    assert stock_service.normalize_symbol("tcs") == "TCS.NS"


def test_normalize_symbol_keeps_existing_suffix(stock_service: StockService) -> None:
    assert stock_service.normalize_symbol("TCS.NS") == "TCS.NS"


def test_normalize_symbol_rejects_empty_input(stock_service: StockService) -> None:
    with pytest.raises(StockDataError):
        stock_service.normalize_symbol("   ")


@patch.object(NSEProvider, "search", return_value=[])
@patch.object(YFinanceProvider, "search", return_value=[])
def test_search_local_popular_stocks(_mock_yahoo: MagicMock, _mock_nse: MagicMock, stock_service: StockService) -> None:
    response = stock_service.search_stocks("reliance", limit=5)
    assert response.query == "reliance"
    assert any(result.symbol == "RELIANCE" for result in response.results)


@patch("backend.app.services.providers.yfinance_provider.yf.Ticker")
def test_get_stock_summary(mock_ticker_class: MagicMock, stock_service: StockService) -> None:
    stock_service._summary_providers = [YFinanceProvider()]

    mock_ticker = MagicMock()
    mock_ticker.info = {
        "longName": "Tata Consultancy Services Ltd",
        "exchange": "NSI",
        "currency": "INR",
        "currentPrice": 4000.0,
        "previousClose": 3950.0,
        "dayHigh": 4020.0,
        "dayLow": 3940.0,
        "volume": 1000000,
        "marketCap": 1500000000000,
        "trailingPE": 28.5,
        "sector": "Technology",
        "industry": "IT Services",
        "website": "https://www.tcs.com",
    }
    mock_ticker.fast_info = {}
    mock_ticker_class.return_value = mock_ticker

    summary = stock_service.get_stock_summary("TCS")

    assert summary.symbol == "TCS.NS"
    assert summary.company_name == "Tata Consultancy Services Ltd"
    assert summary.current_price == 4000.0
    assert summary.data_source == "yfinance"
    assert "Technology" in summary.beginner_summary


@patch("backend.app.services.providers.yfinance_provider.yf.Ticker")
def test_get_stock_history(mock_ticker_class: MagicMock, stock_service: StockService) -> None:
    stock_service._history_providers = [YFinanceProvider()]

    mock_ticker = MagicMock()
    mock_ticker.history.return_value = pd.DataFrame(
        {
            "Open": [100.0, 101.0],
            "High": [102.0, 103.0],
            "Low": [99.0, 100.0],
            "Close": [101.0, 102.0],
            "Volume": [1000, 1100],
        },
        index=pd.to_datetime(["2025-01-01", "2025-01-02"]),
    )
    mock_ticker_class.return_value = mock_ticker

    history = stock_service.get_stock_history("INFY", period="1mo", interval="1d")

    assert history.symbol == "INFY.NS"
    assert len(history.prices) == 2
    assert history.prices[0].close == 101.0
    assert history.data_source == "yfinance"


def test_summary_falls_back_to_yahoo_chart(stock_service: StockService) -> None:
    yahoo_chart = YahooChartProvider()
    stock_service._summary_providers = [YFinanceProvider(), yahoo_chart]

    with patch.object(YFinanceProvider, "get_summary", return_value=None):
        with patch.object(
            YahooChartProvider,
            "get_summary",
            return_value=ProviderSummaryData(
                symbol="RELIANCE.NS",
                company_name="Reliance Industries Limited",
                exchange="NSE",
                currency="INR",
                current_price=1291.0,
                previous_close=1304.0,
                data_source="yahoo_chart_api",
            ),
        ):
            summary = stock_service.get_stock_summary("RELIANCE")

    assert summary.current_price == 1291.0
    assert summary.data_source == "yahoo_chart_api"


def test_history_falls_back_to_yahoo_chart(stock_service: StockService) -> None:
    stock_service._history_providers = [YFinanceProvider(), YahooChartProvider()]

    with patch.object(YFinanceProvider, "get_history", return_value=None):
        with patch.object(
            YahooChartProvider,
            "get_history",
            return_value=ProviderHistoryData(
                symbol="RELIANCE.NS",
                period="6mo",
                interval="1d",
                prices=[StockHistoryPoint(date="2025-01-01", close=1200.0)],
                data_source="yahoo_chart_api",
            ),
        ):
            history = stock_service.get_stock_history("RELIANCE", period="6mo", interval="1d")

    assert len(history.prices) == 1
    assert history.data_source == "yahoo_chart_api"
