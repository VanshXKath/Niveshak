def generate_insights(df, sector_df) -> list[str]:
    insights: list[str] = []
    total_value = sector_df["current_value"].sum()
    if total_value <= 0:
        return ["Upload a valid broker holdings file to see insights."]

    top_sector = sector_df.sort_values("current_value", ascending=False).iloc[0]
    if top_sector["current_value"] / total_value > 0.4:
        insights.append(f"High exposure to {top_sector['sector']} sector (over 40%).")

    for _, row in sector_df[sector_df["pnl"] < 0].iterrows():
        insights.append(f"{row['sector']} sector is in loss (₹{row['pnl']:.0f}).")

    if (df["sector"] == "Other").mean() > 0.3:
        insights.append("Many stocks are in 'Other' sector — expand sector map for better breakdown.")

    if not insights:
        insights.append("Portfolio looks reasonably balanced sector-wise.")
    return insights
