"""Fast offline sector mapping — no API calls (avoids Yahoo rate limits)."""

STATIC_SECTOR_MAP: dict[str, str] = {
    "TCS": "IT",
    "INFY": "IT",
    "WIPRO": "IT",
    "HCLTECH": "IT",
    "TECHM": "IT",
    "LTIM": "IT",
    "MPHASIS": "IT",
    "PERSISTENT": "IT",
    "COFORGE": "IT",
    "HDFCBANK": "Financials",
    "ICICIBANK": "Financials",
    "SBIN": "Financials",
    "KOTAKBANK": "Financials",
    "AXISBANK": "Financials",
    "BAJFINANCE": "Financials",
    "BAJAJFINSV": "Financials",
    "HDFCLIFE": "Financials",
    "ICICIGI": "Financials",
    "ITC": "FMCG",
    "HINDUNILVR": "FMCG",
    "NESTLEIND": "FMCG",
    "BRITANNIA": "FMCG",
    "DABUR": "FMCG",
    "RELIANCE": "Energy",
    "ONGC": "Energy",
    "BPCL": "Energy",
    "IOC": "Energy",
    "NTPC": "Energy",
    "POWERGRID": "Energy",
    "ADANIENT": "Conglomerate",
    "ADANIPORTS": "Infrastructure",
    "TATAMOTORS": "Auto",
    "MARUTI": "Auto",
    "M&M": "Auto",
    "BAJAJ-AUTO": "Auto",
    "EICHERMOT": "Auto",
    "HEROMOTOCO": "Auto",
    "SUNPHARMA": "Pharma",
    "DRREDDY": "Pharma",
    "CIPLA": "Pharma",
    "DIVISLAB": "Pharma",
    "APOLLOHOSP": "Healthcare",
    "ASIANPAINT": "Consumer",
    "TITAN": "Consumer",
    "TATASTEEL": "Metals",
    "HINDALCO": "Metals",
    "JSWSTEEL": "Metals",
    "ULTRACEMCO": "Cement",
    "GRASIM": "Cement",
    "BHARTIARTL": "Telecom",
    "LT": "Infrastructure",
}


def map_sector(symbol: str) -> str:
    if not isinstance(symbol, str):
        return "Other"
    cleaned = symbol.upper().replace(".NS", "").replace(".BO", "").strip()
    for suffix in (" EQ", "-EQ", " BE", "-BE"):
        cleaned = cleaned.replace(suffix, "")
    return STATIC_SECTOR_MAP.get(cleaned, "Other")
