from __future__ import annotations

import math
from typing import Any

import pandas as pd
import yfinance as yf

from backend.app.models.stock import (
    StockHistoryPoint,
    StockHistoryResponse,
    StockSummaryResponse,
)


class StockDataError(Exception):
    """Raised when stock data cannot be found or safely converted."""


class StockService:
    """Small service class that keeps all yfinance logic in one place."""

    def normalize_symbol(self, symbol: str) -> str:
        cleaned = symbol.strip().upper()
        if not cleaned:
            raise StockDataError("Please enter a stock symbol, for example RELIANCE or TCS.")

        if "." in cleaned:
            return cleaned

        return f"{cleaned}.NS"

    def get_stock_summary(self, symbol: str) -> StockSummaryResponse:
        yahoo_symbol = self.normalize_symbol(symbol)
        ticker = yf.Ticker(yahoo_symbol)
        info = self._get_ticker_info(ticker)
        fast_info = self._get_fast_info(ticker)

        current_price = self._safe_float(
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or self._fast_info_value(fast_info, "last_price")
        )
        previous_close = self._safe_float(info.get("previousClose") or self._fast_info_value(fast_info, "previous_close"))
        day_high = self._safe_float(info.get("dayHigh") or self._fast_info_value(fast_info, "day_high"))
        day_low = self._safe_float(info.get("dayLow") or self._fast_info_value(fast_info, "day_low"))
        pe_ratio = self._safe_float(info.get("trailingPE"))

        if not info and current_price is None:
            raise StockDataError(
                "The market data provider is not returning data right now. "
                "This can happen because free data sources sometimes rate-limit requests. "
                "Please try again after a few minutes."
            )

        return StockSummaryResponse(
            symbol=yahoo_symbol,
            company_name=info.get("longName") or info.get("shortName") or yahoo_symbol,
            exchange=info.get("exchange") or self._fast_info_value(fast_info, "exchange"),
            currency=info.get("currency") or self._fast_info_value(fast_info, "currency"),
            current_price=current_price,
            previous_close=previous_close,
            day_high=day_high,
            day_low=day_low,
            volume=self._safe_int(info.get("volume") or self._fast_info_value(fast_info, "last_volume")),
            market_cap=self._safe_int(info.get("marketCap") or self._fast_info_value(fast_info, "market_cap")),
            pe_ratio=pe_ratio,
            sector=info.get("sector"),
            industry=info.get("industry"),
            website=info.get("website"),
            beginner_summary=self._build_beginner_summary(
                current_price=current_price,
                previous_close=previous_close,
                pe_ratio=pe_ratio,
                sector=info.get("sector"),
            ),
        )

    def get_stock_history(self, symbol: str, period: str = "6mo", interval: str = "1d") -> StockHistoryResponse:
        yahoo_symbol = self.normalize_symbol(symbol)
        ticker = yf.Ticker(yahoo_symbol)

        try:
            history = ticker.history(period=period, interval=interval)
        except Exception as exc:
            raise StockDataError(
                "Historical price data is temporarily unavailable from the market data provider. "
                "Please try again after a few minutes."
            ) from exc

        if history.empty:
            raise StockDataError(f"No historical price data found for '{symbol}'.")

        history_table = history.reset_index()
        date_column = "Date" if "Date" in history_table.columns else "Datetime"

        prices = [
            StockHistoryPoint(
                date=row[date_column].strftime("%Y-%m-%d"),
                open=self._safe_float(row.get("Open")),
                high=self._safe_float(row.get("High")),
                low=self._safe_float(row.get("Low")),
                close=self._safe_float(row.get("Close")),
                volume=self._safe_int(row.get("Volume")),
            )
            for _, row in history_table.iterrows()
        ]

        return StockHistoryResponse(
            symbol=yahoo_symbol,
            period=period,
            interval=interval,
            prices=prices,
        )

    def _build_beginner_summary(
        self,
        current_price: float | None,
        previous_close: float | None,
        pe_ratio: float | None,
        sector: str | None,
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

        if not messages:
            return "Basic stock data is available. More beginner-friendly analysis will be added in later phases."

        return " ".join(messages)

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
