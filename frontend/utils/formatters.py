def format_inr(value: float | int | None) -> str:
    if value is None:
        return "N/A"
    return f"₹{value:,.2f}"


def format_large_number(value: int | float | None) -> str:
    if value is None:
        return "N/A"
    crore = 1e7
    if abs(value) >= 1e12:
        return f"₹{value / 1e12:.2f} L Cr"
    if abs(value) >= crore:
        return f"₹{value / crore:.2f} Cr"
    return f"₹{value:,.0f}"


def sentiment_color(label: str) -> str:
    mapping = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}
    return mapping.get(label.lower(), "⚪")
