from __future__ import annotations

import math
from typing import Any

import pandas as pd
import yfinance as yf

from backend.app.models.stock import StockHistoryPoint, StockSearchResult
from backend.app.services.providers.base import ProviderHistoryData, ProviderSummaryData


class YFinanceProvider:
    """Primary provider using the yfinance Python library."""

    name = "yfinance"

    def get_summary(self, symbol: str) -> ProviderSummaryData | None:
        ticker = yf.Ticker(symbol)
        info = self._get_ticker_info(ticker)
        fast_info = self._get_fast_info(ticker)

        current_price = self._safe_float(
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or self._fast_info_value(fast_info, "last_price")
        )
        if not info and current_price is None:
            return None

        return ProviderSummaryData(
            symbol=symbol,
            company_name=info.get("longName") or info.get("shortName") or symbol,
            exchange=info.get("exchange") or self._fast_info_value(fast_info, "exchange"),
            currency=info.get("currency") or self._fast_info_value(fast_info, "currency"),
            current_price=current_price,
            previous_close=self._safe_float(
                info.get("previousClose") or self._fast_info_value(fast_info, "previous_close")
            ),
            day_high=self._safe_float(info.get("dayHigh") or self._fast_info_value(fast_info, "day_high")),
            day_low=self._safe_float(info.get("dayLow") or self._fast_info_value(fast_info, "day_low")),
            volume=self._safe_int(info.get("volume") or self._fast_info_value(fast_info, "last_volume")),
            market_cap=self._safe_int(info.get("marketCap") or self._fast_info_value(fast_info, "market_cap")),
            pe_ratio=self._safe_float(info.get("trailingPE")),
            sector=info.get("sector"),
            industry=info.get("industry"),
            website=info.get("website"),
            data_source=self.name,
        )

    def get_history(self, symbol: str, period: str, interval: str) -> ProviderHistoryData | None:
        ticker = yf.Ticker(symbol)
        try:
            history = ticker.history(period=period, interval=interval)
        except Exception:
            return None

        if history.empty:
            return None

        history_table = history.reset_index()
        date_column = next(
            (name for name in ("Date", "Datetime", "date", "datetime") if name in history_table.columns),
            history_table.columns[0],
        )

        prices = [
            StockHistoryPoint(
                date=pd.Timestamp(row[date_column]).strftime("%Y-%m-%d"),
                open=self._safe_float(row.get("Open")),
                high=self._safe_float(row.get("High")),
                low=self._safe_float(row.get("Low")),
                close=self._safe_float(row.get("Close")),
                volume=self._safe_int(row.get("Volume")),
            )
            for _, row in history_table.iterrows()
        ]

        return ProviderHistoryData(
            symbol=symbol,
            period=period,
            interval=interval,
            prices=prices,
            data_source=self.name,
        )

    def search(self, query: str, limit: int) -> list[StockSearchResult]:
        try:
            search = yf.Search(query, max_results=limit)
            quotes = getattr(search, "quotes", None) or []
        except Exception:
            return []

        results: list[StockSearchResult] = []
        for quote in quotes:
            if not isinstance(quote, dict):
                continue

            symbol = str(quote.get("symbol", "")).upper()
            if not symbol.endswith(".NS"):
                continue

            base_symbol = symbol.replace(".NS", "")
            results.append(
                StockSearchResult(
                    symbol=base_symbol,
                    name=str(quote.get("shortname") or quote.get("longname") or base_symbol),
                    exchange=quote.get("exchange"),
                    quote_type=quote.get("quoteType"),
                )
            )

        return results

    def _get_ticker_info(self, ticker: yf.Ticker) -> dict[str, Any]:
        try:
            return ticker.info or {}
        except Exception:
            return {}

    def _get_fast_info(self, ticker: yf.Ticker) -> Any:
        try:
            return ticker.fast_info
        except Exception:
            return {}

    def _fast_info_value(self, fast_info: Any, key: str) -> Any:
        if not fast_info:
            return None
        try:
            return fast_info[key]
        except Exception:
            return None

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
        if value is None or pd.isna(value):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
