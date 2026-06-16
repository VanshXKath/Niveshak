from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Any

import requests

from backend.app.models.stock import StockHistoryPoint, StockSearchResult
from backend.app.services.providers.base import ProviderHistoryData, ProviderSummaryData

NSE_HOME = "https://www.nseindia.com"
NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}


class NSEProvider:
    """Official NSE India JSON APIs. May be blocked in some networks but works for many users."""

    name = "nse_india"

    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update(NSE_HEADERS)

    def get_summary(self, symbol: str) -> ProviderSummaryData | None:
        payload = self._quote_equity(self._base_symbol(symbol))
        if payload is None:
            return None

        info = payload.get("info", {})
        price_info = payload.get("priceInfo", {})
        metadata = payload.get("metadata", {})
        current_price = self._safe_float(price_info.get("lastPrice"))
        if current_price is None:
            return None

        day_range = price_info.get("intraDayHighLow") or {}
        return ProviderSummaryData(
            symbol=f"{self._base_symbol(symbol)}.NS",
            company_name=info.get("companyName") or self._base_symbol(symbol),
            exchange="NSE",
            currency="INR",
            current_price=current_price,
            previous_close=self._safe_float(price_info.get("previousClose")),
            day_high=self._safe_float(day_range.get("max")),
            day_low=self._safe_float(day_range.get("min")),
            industry=metadata.get("industry") or info.get("industry"),
            data_source=self.name,
        )

    def get_history(self, symbol: str, period: str, interval: str) -> ProviderHistoryData | None:
        if interval not in {"1d", "1wk", "1mo"}:
            return None

        base_symbol = self._base_symbol(symbol)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=self._period_to_days(period))
        url = (
            f"{NSE_HOME}/api/historical/cm/equity"
            f"?symbol={base_symbol}&series=%5B%22EQ%22%5D"
            f"&from={from_date.strftime('%d-%m-%Y')}&to={to_date.strftime('%d-%m-%Y')}"
        )

        payload = self._get_json(url)
        if payload is None:
            return None

        rows = payload.get("data") or []
        prices = [
            StockHistoryPoint(
                date=row.get("CH_TIMESTAMP", "")[:10],
                open=self._safe_float(row.get("CH_OPENING_PRICE")),
                high=self._safe_float(row.get("CH_TRADE_HIGH_PRICE")),
                low=self._safe_float(row.get("CH_TRADE_LOW_PRICE")),
                close=self._safe_float(row.get("CH_CLOSING_PRICE")),
                volume=self._safe_int(row.get("CH_TOT_TRADED_QTY")),
            )
            for row in rows
            if row.get("CH_TIMESTAMP")
        ]

        if not prices:
            return None

        return ProviderHistoryData(
            symbol=f"{base_symbol}.NS",
            period=period,
            interval=interval,
            prices=prices,
            data_source=self.name,
        )

    def search(self, query: str, limit: int) -> list[StockSearchResult]:
        payload = self._get_json(f"{NSE_HOME}/api/search/autocomplete?q={query.strip()}")
        if not isinstance(payload, list):
            return []

        results: list[StockSearchResult] = []
        for item in payload:
            if not isinstance(item, dict):
                continue
            symbol = str(item.get("symbol", "")).upper()
            if not symbol:
                continue
            results.append(
                StockSearchResult(
                    symbol=symbol,
                    name=str(item.get("name") or item.get("symbol")),
                    exchange="NSE",
                    quote_type=item.get("type"),
                )
            )
            if len(results) >= limit:
                break

        return results

    def _quote_equity(self, symbol: str) -> dict[str, Any] | None:
        return self._get_json(f"{NSE_HOME}/api/quote-equity?symbol={symbol}")

    def _get_json(self, url: str) -> dict[str, Any] | list[Any] | None:
        try:
            self._session.get(NSE_HOME, timeout=15)
            response = self._session.get(url, timeout=20)
            if response.status_code != 200:
                return None
            return response.json()
        except Exception:
            return None

    def _base_symbol(self, symbol: str) -> str:
        cleaned = symbol.strip().upper()
        return cleaned.replace(".NS", "")

    def _period_to_days(self, period: str) -> int:
        mapping = {"1mo": 31, "3mo": 93, "6mo": 186, "1y": 365, "5y": 365 * 5}
        return mapping.get(period, 186)

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
