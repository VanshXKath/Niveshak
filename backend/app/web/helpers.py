from __future__ import annotations

import plotly.graph_objects as go

from backend.app.models.stock import StockHistoryResponse, StockSummaryResponse


def format_inr(value: float | int | None) -> str:
    if value is None:
        return "—"
    return f"₹{float(value):,.2f}"


def format_large_inr(value: int | float | None) -> str:
    if value is None:
        return "—"
    number = float(value)
    if number >= 1e12:
        return f"₹{number / 1e12:.2f} L Cr"
    if number >= 1e7:
        return f"₹{number / 1e7:.2f} Cr"
    return format_inr(number)


def sentiment_class(label: str) -> str:
    mapping = {"positive": "badge-green", "negative": "badge-red", "neutral": "badge-yellow"}
    return mapping.get((label or "").lower(), "badge-blue")


def candlestick_chart_html(history: StockHistoryResponse, title: str) -> str:
    dates = [point.date for point in history.prices]
    figure = go.Figure(
        data=[
            go.Candlestick(
                x=dates,
                open=[point.open for point in history.prices],
                high=[point.high for point in history.prices],
                low=[point.low for point in history.prices],
                close=[point.close for point in history.prices],
                increasing_line_color="#00d09c",
                decreasing_line_color="#ff6b6b",
            )
        ]
    )
    figure.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="#121a24",
        plot_bgcolor="#121a24",
        height=420,
        xaxis_rangeslider_visible=False,
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return figure.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})


def bar_chart_html(labels: list[str], values: list[float], title: str) -> str:
    figure = go.Figure(data=[go.Bar(x=labels, y=values, marker_color="#00d09c")])
    figure.update_layout(
        title=title,
        template="plotly_dark",
        paper_bgcolor="#121a24",
        plot_bgcolor="#121a24",
        height=380,
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return figure.to_html(full_html=False, include_plotlyjs="cdn", config={"displayModeBar": False})
