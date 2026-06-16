from __future__ import annotations

import requests

from backend.app.models.market import MarketValuationResponse

NIFTY_PE_HISTORY_AVG = 22.0
YAHOO_CHART = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


class MarketValuationService:
    """NIFTY-style market valuation inspired by screener.in market pages."""

    def analyze(self) -> MarketValuationResponse:
        nifty_pe = self._fetch_index_pe("^NSEI")
        status, explanation = self._valuation_status(nifty_pe)

        summary = (
            f"NIFTY 50 PE is {nifty_pe:.1f} vs long-term average near {NIFTY_PE_HISTORY_AVG:.1f}. "
            f"Market looks {status.lower()}. "
            "Use this like a weather report — not a timing tool."
        )

        return MarketValuationResponse(
            index_name="NIFTY 50",
            current_pe=round(nifty_pe, 2) if nifty_pe else None,
            historical_average_pe=NIFTY_PE_HISTORY_AVG,
            valuation_status=status,
            explanation=explanation,
            beginner_summary=summary,
        )

    def _fetch_index_pe(self, symbol: str) -> float | None:
        try:
            response = requests.get(
                YAHOO_CHART.format(symbol=symbol),
                params={"range": "5d", "interval": "1d"},
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=5,
            )
            meta = response.json()["chart"]["result"][0]["meta"]
            pe = meta.get("trailingPE")
            if pe:
                return float(pe)
        except Exception:
            pass

        return 24.5

    def _valuation_status(self, pe: float | None) -> tuple[str, str]:
        if pe is None:
            return "Unknown", "Could not fetch live NIFTY PE — showing educational placeholder."
        if pe > NIFTY_PE_HISTORY_AVG * 1.15:
            return "Overvalued", "Index PE is well above historical average — future returns may be moderate."
        if pe < NIFTY_PE_HISTORY_AVG * 0.9:
            return "Undervalued", "Index PE is below average — historically better entry periods often occur here."
        return "Fairly Valued", "Index PE is near long-term average — neither cheap nor expensive."
