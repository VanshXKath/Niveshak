from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import pandas as pd

from backend.app.models.stock import (
    StockHistoryPoint,
    StockHistoryResponse,
    StockSearchResponse,
    StockSearchResult,
    StockSummaryResponse,
)
from backend.app.services.providers.base import ProviderHistoryData, ProviderSummaryData
from backend.app.services.providers.bse_provider import BSEProvider
from backend.app.services.providers.nse_provider import NSEProvider
from backend.app.services.providers.yahoo_chart_provider import YahooChartProvider
from backend.app.services.providers.yfinance_provider import YFinanceProvider

NSE_POPULAR_STOCKS_PATH = Path(__file__).resolve().parent.parent / "data" / "nse_popular_stocks.json"


class StockDataError(Exception):
    """Raised when stock data cannot be found or safely converted."""


class StockService:
    """Fetches stock data using multiple providers with automatic fallback."""

    def __init__(self) -> None:
        self._popular_stocks = self._load_popular_stocks()
        self._summary_providers = [
            YahooChartProvider(),
            YFinanceProvider(),
            NSEProvider(),
            BSEProvider(),
        ]
        self._history_providers = [
            YahooChartProvider(),
            YFinanceProvider(),
            NSEProvider(),
        ]
        self._search_providers = [
            YFinanceProvider(),
            NSEProvider(),
        ]

    def search_stocks(self, query: str, limit: int = 10) -> StockSearchResponse:
        cleaned_query = query.strip()
        if not cleaned_query:
            raise StockDataError("Please enter a company name or symbol to search.")

        limit = max(1, min(limit, 25))
        results: list[StockSearchResult] = []
        seen_symbols: set[str] = set()

        for provider in self._search_providers:
            for item in provider.search(cleaned_query, limit=limit):
                symbol = item.symbol
                if symbol in seen_symbols:
                    continue
                seen_symbols.add(symbol)
                results.append(item)
                if len(results) >= limit:
                    break
            if len(results) >= limit:
                break

        if len(results) < limit:
            for item in self._search_local_popular_stocks(cleaned_query, limit=limit):
                symbol = item.symbol
                if symbol in seen_symbols:
                    continue
                seen_symbols.add(symbol)
                results.append(item)
                if len(results) >= limit:
                    break

        return StockSearchResponse(query=cleaned_query, results=results[:limit])

    def normalize_symbol(self, symbol: str) -> str:
        cleaned = symbol.strip().upper()
        if not cleaned:
            raise StockDataError("Please enter a stock symbol, for example RELIANCE or TCS.")

        if "." in cleaned:
            return cleaned

        return f"{cleaned}.NS"

    def get_stock_summary(self, symbol: str) -> StockSummaryResponse:
        yahoo_symbol = self.normalize_symbol(symbol)
        summary = self._first_summary(yahoo_symbol)
        if summary is None or summary.current_price is None:
            raise StockDataError(
                "All market data providers failed for this stock. "
                "We tried Yahoo Finance, NSE India, and BSE India. Please try again in a few minutes."
            )

        return StockSummaryResponse(
            symbol=summary.symbol,
            company_name=summary.company_name,
            exchange=summary.exchange,
            currency=summary.currency,
            current_price=summary.current_price,
            previous_close=summary.previous_close,
            day_high=summary.day_high,
            day_low=summary.day_low,
            volume=summary.volume,
            market_cap=summary.market_cap,
            pe_ratio=summary.pe_ratio,
            sector=summary.sector,
            industry=summary.industry,
            website=summary.website,
            data_source=summary.data_source,
            beginner_summary=self._build_beginner_summary(
                current_price=summary.current_price,
                previous_close=summary.previous_close,
                pe_ratio=summary.pe_ratio,
                sector=summary.sector,
                data_source=summary.data_source,
            ),
        )

    def get_stock_history(self, symbol: str, period: str = "6mo", interval: str = "1d") -> StockHistoryResponse:
        yahoo_symbol = self.normalize_symbol(symbol)
        history = self._first_history(yahoo_symbol, period=period, interval=interval)
        if history is None or not history.prices:
            raise StockDataError(
                f"No historical price data found for '{symbol}' from any provider. "
                "Please try a different period or try again later."
            )

        return StockHistoryResponse(
            symbol=history.symbol,
            period=history.period,
            interval=history.interval,
            prices=history.prices,
            data_source=history.data_source,
        )

    def _first_summary(self, symbol: str) -> ProviderSummaryData | None:
        best: ProviderSummaryData | None = None
        for provider in self._summary_providers:
            try:
                summary = provider.get_summary(symbol)
            except Exception:
                continue
            if summary is None:
                continue
            if best is None:
                best = summary
            else:
                best = self._merge_summary(best, summary)
            if best.current_price is not None and best.company_name:
                if best.pe_ratio is not None or provider.name in {"yfinance", "yahoo_chart_api"}:
                    return best
        return best

    def _first_history(self, symbol: str, period: str, interval: str) -> ProviderHistoryData | None:
        for provider in self._history_providers:
            try:
                history = provider.get_history(symbol, period=period, interval=interval)
            except Exception:
                continue
            if history is not None and history.prices:
                return history
        return None

    def _merge_summary(self, primary: ProviderSummaryData, secondary: ProviderSummaryData) -> ProviderSummaryData:
        return ProviderSummaryData(
            symbol=primary.symbol or secondary.symbol,
            company_name=primary.company_name or secondary.company_name,
            exchange=primary.exchange or secondary.exchange,
            currency=primary.currency or secondary.currency,
            current_price=primary.current_price or secondary.current_price,
            previous_close=primary.previous_close or secondary.previous_close,
            day_high=primary.day_high or secondary.day_high,
            day_low=primary.day_low or secondary.day_low,
            volume=primary.volume or secondary.volume,
            market_cap=primary.market_cap or secondary.market_cap,
            pe_ratio=primary.pe_ratio or secondary.pe_ratio,
            sector=primary.sector or secondary.sector,
            industry=primary.industry or secondary.industry,
            website=primary.website or secondary.website,
            data_source=primary.data_source if primary.current_price else secondary.data_source,
        )

    def _load_popular_stocks(self) -> list[dict[str, str]]:
        try:
            with NSE_POPULAR_STOCKS_PATH.open(encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return []

    def _search_local_popular_stocks(self, query: str, limit: int) -> list[StockSearchResult]:
        needle = query.strip().upper()
        results: list[StockSearchResult] = []

        for stock in self._popular_stocks:
            symbol = stock["symbol"].upper()
            name = stock["name"]
            if needle in symbol or needle in name.upper():
                results.append(
                    StockSearchResult(
                        symbol=symbol,
                        name=name,
                        exchange="NSE",
                        quote_type="EQUITY",
                    )
                )
            if len(results) >= limit:
                break

        return results

    def _build_beginner_summary(
        self,
        current_price: float | None,
        previous_close: float | None,
        pe_ratio: float | None,
        sector: str | None,
        data_source: str,
    ) -> str:
        messages: list[str] = []

        if current_price is not None and previous_close:
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100
            direction = "up" if change >= 0 else "down"
            messages.append(f"The stock is {direction} about {abs(change_percent):.2f}% compared with its previous close.")

        if pe_ratio is not None:
            messages.append(
                f"Its PE ratio is {pe_ratio:.2f}. PE compares the share price with company earnings; later we will compare this with industry averages."
            )

        if sector:
            messages.append(f"The company belongs to the {sector} sector.")

        source_labels = {
            "yfinance": "Yahoo Finance via yfinance",
            "yahoo_chart_api": "Yahoo Finance chart API",
            "nse_india": "NSE India official API",
            "bse_india": "BSE India official API",
        }
        messages.append(f"Data source: {source_labels.get(data_source, data_source)}.")

        if not messages:
            return "Basic stock data is available. More beginner-friendly analysis will be added in later phases."

        return " ".join(messages)

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
