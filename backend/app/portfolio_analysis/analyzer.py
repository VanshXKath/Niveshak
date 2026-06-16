from __future__ import annotations

import pandas as pd

from backend.app.portfolio_analysis.cleaner import clean_holdings
from backend.app.portfolio_analysis.file_reader import read_holdings_file
from backend.app.portfolio_analysis.insights import generate_insights
from backend.app.portfolio_analysis.live_price import fetch_live_prices
from backend.app.portfolio_analysis.metrics import pnl_percent, total_current_value, total_invested, total_pnl
from backend.app.portfolio_analysis.sector_analysis import sector_summary
from backend.app.portfolio_analysis.sector_mapping import map_sector
from backend.app.web.helpers import bar_chart_html


def _apply_prices_from_file(df: pd.DataFrame) -> pd.DataFrame:
    """Use broker file columns first — instant, no Yahoo API."""
    result = df.copy()

    if "ltp" in result.columns:
        result["ltp_live"] = pd.to_numeric(result["ltp"], errors="coerce")
    else:
        result["ltp_live"] = pd.NA

    if "current_value" in result.columns and "quantity" in result.columns:
        qty = pd.to_numeric(result["quantity"], errors="coerce").replace(0, pd.NA)
        derived_ltp = pd.to_numeric(result["current_value"], errors="coerce") / qty
        result["ltp_live"] = result["ltp_live"].fillna(derived_ltp)

    if "avg_cost" in result.columns:
        result["ltp_live"] = result["ltp_live"].fillna(pd.to_numeric(result["avg_cost"], errors="coerce"))

    result["ltp_live"] = result["ltp_live"].fillna(0)
    return result


def _fill_missing_live_prices(df: pd.DataFrame) -> pd.DataFrame:
    """Only fetch live prices for rows still missing LTP (capped)."""
    missing_mask = df["ltp_live"].isna() | (df["ltp_live"] <= 0)
    if not missing_mask.any():
        return df

    symbols_to_fetch = df.loc[missing_mask, "symbol"].dropna().unique().tolist()
    if not symbols_to_fetch:
        return df

    live_map = fetch_live_prices(symbols_to_fetch)
    result = df.copy()
    for raw_symbol, price in live_map.items():
        if price is None:
            continue
        symbol_mask = result["symbol"] == raw_symbol
        result.loc[symbol_mask & missing_mask, "ltp_live"] = price

    result["ltp_live"] = result["ltp_live"].fillna(result.get("avg_cost", 0)).fillna(0)
    return result


def analyze_broker_file(file_bytes: bytes, filename: str, live_prices: bool = False) -> dict:
    raw_df = read_holdings_file(file_bytes, filename)
    clean_df = clean_holdings(raw_df)

    if "invested" not in clean_df.columns and {"quantity", "avg_cost"}.issubset(clean_df.columns):
        clean_df["invested"] = clean_df["quantity"] * clean_df["avg_cost"]

    clean_df = _apply_prices_from_file(clean_df)

    if live_prices:
        clean_df = _fill_missing_live_prices(clean_df)

    if "current_value" not in clean_df.columns or clean_df["current_value"].isna().all():
        clean_df["current_value"] = clean_df["quantity"] * clean_df["ltp_live"].fillna(0)
    else:
        file_values = pd.to_numeric(clean_df["current_value"], errors="coerce")
        computed = clean_df["quantity"] * clean_df["ltp_live"].fillna(0)
        clean_df["current_value"] = file_values.fillna(computed)

    clean_df["pnl"] = clean_df["current_value"] - clean_df["invested"]
    clean_df["pnl_pct"] = (clean_df["pnl"] / clean_df["invested"].replace(0, pd.NA)) * 100
    clean_df["sector"] = clean_df["symbol"].astype(str).apply(map_sector)

    sector_df = sector_summary(clean_df)
    insights = generate_insights(clean_df, sector_df)

    sector_chart = bar_chart_html(
        sector_df["sector"].tolist(),
        sector_df["current_value"].tolist(),
        "Sector allocation (current value)",
    )

    top_movers = clean_df.reindex(clean_df["pnl"].abs().sort_values(ascending=False).index).head(7)
    pnl_chart = bar_chart_html(
        top_movers["symbol"].astype(str).tolist(),
        top_movers["pnl"].tolist(),
        "Top P&L drivers",
    )

    holdings = clean_df.to_dict(orient="records")
    sectors = sector_df.to_dict(orient="records")

    return {
        "filename": filename,
        "total_invested": round(total_invested(clean_df), 2),
        "total_current_value": round(total_current_value(clean_df), 2),
        "total_pnl": round(total_pnl(clean_df), 2),
        "pnl_percent": round(pnl_percent(clean_df), 2),
        "holdings": holdings,
        "sectors": sectors,
        "insights": insights,
        "sector_chart_html": sector_chart,
        "pnl_chart_html": pnl_chart,
        "row_count": len(clean_df),
        "used_file_prices": not live_prices,
    }
