import pandas as pd


def sector_summary(df: pd.DataFrame) -> pd.DataFrame:
    sector_df = (
        df.groupby("sector", dropna=False)
        .agg(invested=("invested", "sum"), current_value=("current_value", "sum"))
        .reset_index()
    )
    sector_df["pnl"] = sector_df["current_value"] - sector_df["invested"]
    sector_df["pnl_pct"] = (sector_df["pnl"] / sector_df["invested"].replace(0, pd.NA)) * 100
    return sector_df
