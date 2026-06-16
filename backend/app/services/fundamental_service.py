from __future__ import annotations

import math
from typing import Any

import yfinance as yf

from backend.app.models.fundamental import FundamentalAnalysisResponse, FundamentalMetric
from backend.app.services.stock_service import StockDataError, StockService


class FundamentalService:
    def __init__(self) -> None:
        self._stock_service = StockService()

    def analyze(self, symbol: str) -> FundamentalAnalysisResponse:
        yahoo_symbol = self._stock_service.normalize_symbol(symbol)
        ticker = yf.Ticker(yahoo_symbol)
        info = self._safe_info(ticker)
        summary = self._stock_service.get_stock_summary(symbol)

        metrics = [
            self._metric("Market Cap", self._format_large(info.get("marketCap"))),
            self._metric("PE Ratio", self._fmt(info.get("trailingPE")), "Lower PE can mean cheaper vs earnings — compare with sector."),
            self._metric("PB Ratio", self._fmt(info.get("priceToBook")), "Price to book value — useful for banks and asset-heavy firms."),
            self._metric("ROE", self._pct(info.get("returnOnEquity")), "Return on equity — higher often means efficient use of shareholder money."),
            self._metric("ROCE", self._pct(info.get("returnOnAssets")), "Return on assets — profitability from total assets."),
            self._metric("Debt to Equity", self._fmt(info.get("debtToEquity")), "High debt increases risk in downturns."),
            self._metric("Revenue Growth", self._pct(info.get("revenueGrowth")), "Top-line growth shows demand for products/services."),
            self._metric("Earnings Growth", self._pct(info.get("earningsGrowth")), "Profit growth — key for long-term wealth creation."),
            self._metric("Profit Margin", self._pct(info.get("profitMargins")), "How much profit is kept from each rupee of sales."),
            self._metric("Free Cash Flow", self._format_large(info.get("freeCashflow")), "Cash after expenses — fuels dividends and expansion."),
            self._metric("Dividend Yield", self._pct(info.get("dividendYield")), "Income return from dividends."),
        ]

        strengths, weaknesses, risks, opportunities = self._generate_insights(info, metrics)
        beginner = (
            f"Fundamental snapshot for {summary.company_name}, inspired by screener.in-style ratio cards. "
            f"Found {len([m for m in metrics if m.value])} usable metrics. "
            "Compare ratios with sector peers before investing."
        )

        return FundamentalAnalysisResponse(
            symbol=yahoo_symbol,
            company_name=summary.company_name,
            metrics=metrics,
            strengths=strengths,
            weaknesses=weaknesses,
            risks=risks,
            opportunities=opportunities,
            beginner_summary=beginner,
        )

    def _generate_insights(
        self, info: dict[str, Any], metrics: list[FundamentalMetric]
    ) -> tuple[list[str], list[str], list[str], list[str]]:
        strengths: list[str] = []
        weaknesses: list[str] = []
        risks: list[str] = []
        opportunities: list[str] = []

        roe = info.get("returnOnEquity")
        if roe and roe > 0.15:
            strengths.append("ROE above 15% — company may be using capital efficiently.")
        elif roe and roe < 0.08:
            weaknesses.append("Low ROE — profitability on equity capital is weak.")

        debt = info.get("debtToEquity")
        if debt and debt > 100:
            risks.append("High debt-to-equity — interest costs can hurt in rising rate cycles.")
        elif debt is not None and debt < 30:
            strengths.append("Relatively low debt — balance sheet may be conservative.")

        rev_g = info.get("revenueGrowth")
        if rev_g and rev_g > 0.1:
            opportunities.append("Double-digit revenue growth — business may be gaining market share.")
        elif rev_g and rev_g < 0:
            weaknesses.append("Revenue declined — demand or pricing pressure may exist.")

        pe = info.get("trailingPE")
        if pe and pe > 40:
            risks.append("High PE — market expects strong future growth; disappointment can hurt price.")
        elif pe and 10 < pe < 25:
            strengths.append("Moderate PE — valuation may not be extreme vs earnings.")

        margin = info.get("profitMargins")
        if margin and margin > 0.15:
            strengths.append("Healthy profit margins — strong pricing power or cost control.")

        if not strengths:
            strengths.append("Review full ratio table and annual report for company-specific strengths.")
        if not weaknesses:
            weaknesses.append("No major red flags from available data — still read latest results.")
        if not risks:
            risks.append("Macro risks (rates, inflation, regulation) affect all Indian stocks.")
        if not opportunities:
            opportunities.append("Sector tailwinds and India consumption growth may support long-term investors.")

        return strengths, weaknesses, risks, opportunities

    def _safe_info(self, ticker: yf.Ticker) -> dict[str, Any]:
        try:
            return ticker.info or {}
        except Exception:
            return {}

    def _metric(self, name: str, value: str | None, interpretation: str | None = None) -> FundamentalMetric:
        return FundamentalMetric(name=name, value=value, interpretation=interpretation)

    def _fmt(self, value: Any) -> str | None:
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        if math.isnan(number) or math.isinf(number):
            return None
        return f"{number:.2f}"

    def _pct(self, value: Any) -> str | None:
        formatted = self._fmt(value)
        if formatted is None:
            return None
        return f"{float(formatted) * 100:.2f}%"

    def _format_large(self, value: Any) -> str | None:
        if value is None:
            return None
        try:
            number = float(value)
        except (TypeError, ValueError):
            return None
        crore = 1e7
        if abs(number) >= 1e12:
            return f"INR {number / 1e12:.2f} L Cr"
        if abs(number) >= crore:
            return f"INR {number / crore:.2f} Cr"
        return f"INR {number:,.0f}"
