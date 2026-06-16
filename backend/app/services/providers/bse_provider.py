from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import requests

from backend.app.models.stock import StockSearchResult
from backend.app.services.providers.base import ProviderHistoryData, ProviderSummaryData

BSE_API = "https://api.bseindia.com/BseIndiaAPI/api/getScripHeaderData/w"
BSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.bseindia.com/",
    "Accept": "application/json",
}
POPULAR_STOCKS_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "nse_popular_stocks.json"


class BSEProvider:
    """BSE India public API — useful when Yahoo sources fail for known Indian stocks."""

    name = "bse_india"

    def __init__(self) -> None:
        self._scrip_codes = self._load_scrip_codes()

    def get_summary(self, symbol: str) -> ProviderSummaryData | None:
        scrip_code = self._scrip_codes.get(self._base_symbol(symbol))
        if scrip_code is None:
            return None

        payload = self._fetch_header(scrip_code)
        if payload is None:
            return None

        rate = payload.get("CurrRate", {})
        company = payload.get("Cmpname", {})
        current_price = self._safe_float(rate.get("LTP"))
        if current_price is None:
            return None

        base_symbol = self._base_symbol(symbol)
        return ProviderSummaryData(
            symbol=f"{base_symbol}.NS",
            company_name=company.get("FullN") or company.get("SeriesN") or base_symbol,
            exchange="BSE",
            currency="INR",
            current_price=current_price,
            industry=company.get("Category"),
            data_source=self.name,
        )

    def get_history(self, symbol: str, period: str, interval: str) -> ProviderHistoryData | None:
        return None

    def search(self, query: str, limit: int) -> list[StockSearchResult]:
        return []

    def _fetch_header(self, scrip_code: str) -> dict[str, Any] | None:
        try:
            response = requests.get(
                BSE_API,
                params={"scripcode": scrip_code, "flag": "0", "Quotetype": "EQ"},
                headers=BSE_HEADERS,
                timeout=20,
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

    def _load_scrip_codes(self) -> dict[str, str]:
        try:
            with POPULAR_STOCKS_PATH.open(encoding="utf-8") as file:
                stocks = json.load(file)
        except (OSError, json.JSONDecodeError):
            return {}

        mapping: dict[str, str] = {}
        for stock in stocks:
            symbol = str(stock.get("symbol", "")).upper()
            scrip_code = stock.get("bse_scripcode")
            if symbol and scrip_code:
                mapping[symbol] = str(scrip_code)
        return mapping

    def _base_symbol(self, symbol: str) -> str:
        cleaned = symbol.strip().upper()
        return cleaned.replace(".NS", "")

    def _safe_float(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            number = float(str(value).replace(",", ""))
        except (TypeError, ValueError):
            return None
        if math.isnan(number) or math.isinf(number):
            return None
        return round(number, 2)
