import pandas as pd


def total_invested(df: pd.DataFrame) -> float:
    if "invested" in df.columns:
        return float(df["invested"].sum())
    if {"quantity", "avg_cost"}.issubset(df.columns):
        return float((df["quantity"] * df["avg_cost"]).sum())
    return 0.0


def total_current_value(df: pd.DataFrame) -> float:
    if "current_value" in df.columns:
        return float(df["current_value"].sum())
    if {"quantity", "ltp_live"}.issubset(df.columns):
        return float((df["quantity"] * df["ltp_live"].fillna(0)).sum())
    if {"quantity", "ltp"}.issubset(df.columns):
        return float((df["quantity"] * df["ltp"]).sum())
    return total_invested(df)


def total_pnl(df: pd.DataFrame) -> float:
    return total_current_value(df) - total_invested(df)


def pnl_percent(df: pd.DataFrame) -> float:
    invested = total_invested(df)
    if invested == 0:
        return 0.0
    return (total_pnl(df) / invested) * 100
