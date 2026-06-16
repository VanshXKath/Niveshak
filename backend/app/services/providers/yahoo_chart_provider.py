from __future__ import annotations

import math
from datetime import datetime
from typing import Any

import requests

from backend.app.models.stock import StockHistoryPoint, StockSearchResult
from backend.app.services.providers.base import ProviderHistoryData, ProviderSummaryData

YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


class YahooChartProvider:
    """Direct Yahoo Finance chart API — often works when the yfinance library is rate-limited."""

    name = "yahoo_chart_api"

    def get_summary(self, symbol: str) -> ProviderSummaryData | None:
        payload = self._fetch_chart(symbol=symbol, period="5d", interval="1d")
        if payload is None:
            return None

        meta = payload["meta"]
        current_price = self._safe_float(meta.get("regularMarketPrice"))
        if current_price is None:
            return None

        return ProviderSummaryData(
            symbol=symbol,
            company_name=meta.get("longName") or meta.get("shortName") or symbol,
            exchange=meta.get("fullExchangeName") or meta.get("exchangeName"),
            currency=meta.get("currency"),
            current_price=current_price,
            previous_close=self._safe_float(meta.get("chartPreviousClose") or meta.get("previousClose")),
            day_high=self._safe_float(meta.get("regularMarketDayHigh")),
            day_low=self._safe_float(meta.get("regularMarketDayLow")),
            volume=self._safe_int(meta.get("regularMarketVolume")),
            data_source=self.name,
        )

    def get_history(self, symbol: str, period: str, interval: str) -> ProviderHistoryData | None:
        payload = self._fetch_chart(symbol=symbol, period=period, interval=interval)
        if payload is None:
            return None

        prices = self._parse_prices(payload)
        if not prices:
            return None

        return ProviderHistoryData(
            symbol=symbol,
            period=period,
            interval=interval,
            prices=prices,
            data_source=self.name,
        )

    def search(self, query: str, limit: int) -> list[StockSearchResult]:
        return []

    def _fetch_chart(self, symbol: str, period: str, interval: str) -> dict[str, Any] | None:
        try:
            response = requests.get(
                YAHOO_CHART_URL.format(symbol=symbol),
                params={"range": period, "interval": interval},
                headers=DEFAULT_HEADERS,
                timeout=5,
            )
            response.raise_for_status()
            results = response.json().get("chart", {}).get("result") or []
            if not results:
                return None
            return results[0]
        except Exception:
            return None

    def _parse_prices(self, payload: dict[str, Any]) -> list[StockHistoryPoint]:
        timestamps = payload.get("timestamp") or []
        quote = (payload.get("indicators", {}).get("quote") or [{}])[0]
        prices: list[StockHistoryPoint] = []

        for index, timestamp in enumerate(timestamps):
            close = self._value_at(quote.get("close"), index)
            if close is None:
                continue

            prices.append(
                StockHistoryPoint(
                    date=datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d"),
                    open=self._value_at(quote.get("open"), index),
                    high=self._value_at(quote.get("high"), index),
                    low=self._value_at(quote.get("low"), index),
                    close=close,
                    volume=self._safe_int(self._value_at(quote.get("volume"), index)),
                )
            )

        return prices

    def _value_at(self, values: list[Any] | None, index: int) -> float | None:
        if not values or index >= len(values):
            return None
        return self._safe_float(values[index])

    def _safe_float(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        if math.isnan(number) or math.isinf(number):
            return None
        return round(number, 2)

    def _safe_int(self, value: Any) -> int | None:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
