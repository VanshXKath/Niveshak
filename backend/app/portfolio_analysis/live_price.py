from __future__ import annotations

import re

import requests

from backend.app.services.providers.yahoo_chart_provider import DEFAULT_HEADERS, YAHOO_CHART_URL

MAX_LIVE_SYMBOLS = 12
REQUEST_TIMEOUT = 4


def _normalize_symbol(raw_symbol: str) -> str | None:
    if not isinstance(raw_symbol, str):
        return None
    symbol = raw_symbol.upper().strip()
    for word in [" LIMITED", " LTD", " LTD.", " LIMITED.", " PRIVATE", " PVT", " CO", " COMPANY"]:
        symbol = symbol.replace(word, "")
    symbol = re.sub(r"[^A-Z0-9\-]", "", symbol)
    return symbol or None


def _fetch_price(nse_symbol: str) -> float | None:
    try:
        response = requests.get(
            YAHOO_CHART_URL.format(symbol=f"{nse_symbol}.NS"),
            params={"range": "5d", "interval": "1d"},
            headers=DEFAULT_HEADERS,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        results = response.json().get("chart", {}).get("result") or []
        if not results:
            return None
        price = results[0].get("meta", {}).get("regularMarketPrice")
        return float(price) if price is not None else None
    except Exception:
        return None


def fetch_live_prices(symbols: list[str]) -> dict[str, float | None]:
    """Fetch live prices for a capped list — only used when broker file has no LTP."""
    price_map: dict[str, float | None] = {}

    for raw_symbol in symbols[:MAX_LIVE_SYMBOLS]:
        nse_symbol = _normalize_symbol(raw_symbol)
        if not nse_symbol:
            price_map[raw_symbol] = None
            continue
        price_map[raw_symbol] = _fetch_price(nse_symbol)

    return price_map
