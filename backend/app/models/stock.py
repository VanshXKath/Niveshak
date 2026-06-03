from pydantic import BaseModel, Field


class StockSummaryResponse(BaseModel):
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
    beginner_summary: str


class StockHistoryPoint(BaseModel):
    date: str
    open: float | None = Field(default=None)
    high: float | None = Field(default=None)
    low: float | None = Field(default=None)
    close: float | None = Field(default=None)
    volume: int | None = Field(default=None)


class StockHistoryResponse(BaseModel):
    symbol: str
    period: str
    interval: str
    prices: list[StockHistoryPoint]

