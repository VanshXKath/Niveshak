from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol

from backend.app.models.stock import StockHistoryPoint, StockSearchResult


@dataclass
class ProviderSummaryData:
    symbol: str
    company_name: str
    exchange: str | None = None
    currency: str | None = None
    current_price: float | None = None
    previous_close: float | None = None
    day_high: float | None = None
    day_low: float | None = None
    volume: int | None = None
    market_cap: int | None = None
    pe_ratio: float | None = None
    sector: str | None = None
    industry: str | None = None
    website: str | None = None
    data_source: str = "unknown"


@dataclass
class ProviderHistoryData:
    symbol: str
    period: str
    interval: str
    prices: list[StockHistoryPoint] = field(default_factory=list)
    data_source: str = "unknown"


class StockDataProvider(Protocol):
    name: str

    def get_summary(self, symbol: str) -> ProviderSummaryData | None:
        ...

    def get_history(self, symbol: str, period: str, interval: str) -> ProviderHistoryData | None:
        ...

    def search(self, query: str, limit: int) -> list[StockSearchResult]:
        ...
