from __future__ import annotations

import os
from typing import Any

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")


st.set_page_config(
    page_title="Indian Stock Market AI Screener",
    layout="wide",
)


def fetch_json(endpoint: str) -> dict[str, Any]:
    url = f"{BACKEND_API_URL}{endpoint}"
    response = requests.get(url, timeout=20)
    if response.status_code != 200:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(detail)
    return response.json()


def format_inr(value: float | int | None) -> str:
    if value is None:
        return "Not available"
    return f"INR {value:,.2f}"


def format_large_number(value: int | None) -> str:
    if value is None:
        return "Not available"

    lakh_crore = 1_00_000_00_00_000
    crore = 1_00_00_000

    if value >= lakh_crore:
        return f"INR {value / lakh_crore:.2f} L Cr"
    if value >= crore:
        return f"INR {value / crore:.2f} Cr"
    return f"INR {value:,}"


def build_price_chart(history: dict[str, Any], company_name: str) -> go.Figure:
    prices = pd.DataFrame(history["prices"])
    prices["date"] = pd.to_datetime(prices["date"])

    figure = go.Figure()
    figure.add_trace(
        go.Candlestick(
            x=prices["date"],
            open=prices["open"],
            high=prices["high"],
            low=prices["low"],
            close=prices["close"],
            name="Price",
        )
    )
    figure.update_layout(
        title=f"{company_name} price chart",
        xaxis_title="Date",
        yaxis_title="Price",
        height=520,
        template="plotly_white",
        xaxis_rangeslider_visible=False,
        margin=dict(l=20, r=20, t=60, b=20),
    )
    return figure


st.title("Indian Stock Market AI Screener")
st.caption("Phase 1: search an NSE stock, fetch market data, and view a beginner-friendly dashboard.")

with st.sidebar:
    st.header("Search")
    symbol = st.text_input("NSE stock symbol", value="RELIANCE", help="Try RELIANCE, TCS, INFY, HDFCBANK, SBIN")
    period = st.selectbox("Chart period", options=["1mo", "3mo", "6mo", "1y", "5y"], index=2)
    search_clicked = st.button("Analyze stock", type="primary", use_container_width=True)

    st.divider()
    st.subheader("Beginner note")
    st.write(
        "For Indian NSE stocks, Yahoo Finance usually adds `.NS`. "
        "This app does that automatically, so typing `TCS` becomes `TCS.NS`."
    )


if not symbol:
    st.info("Enter a stock symbol from NSE to begin.")
    st.stop()

if search_clicked or symbol:
    try:
        summary = fetch_json(f"/api/stocks/{symbol}/summary")
        history = fetch_json(f"/api/stocks/{symbol}/history?period={period}&interval=1d")
    except requests.exceptions.ConnectionError:
        st.error(
            "The Streamlit app cannot reach the FastAPI backend. "
            "Start the backend first with: uvicorn backend.app.main:app --reload"
        )
        st.stop()
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    st.subheader(summary["company_name"])
    st.write(summary["beginner_summary"])

    col1, col2 = st.columns(2)
    col1.metric("Current price", format_inr(summary["current_price"]))
    col2.metric("Previous close", format_inr(summary["previous_close"]))

    col3, col4 = st.columns(2)
    col3.metric("Day high", format_inr(summary["day_high"]))
    col4.metric("Day low", format_inr(summary["day_low"]))

    col5, col6 = st.columns(2)
    col5.metric("Volume", f"{summary['volume']:,}" if summary["volume"] else "Not available")
    col6.metric("Market cap", format_large_number(summary["market_cap"]))

    col7, col8 = st.columns(2)
    col7.metric("PE ratio", summary["pe_ratio"] if summary["pe_ratio"] else "Not available")
    col8.metric("Currency", summary["currency"] or "Not available")

    st.plotly_chart(build_price_chart(history, summary["company_name"]), use_container_width=True)

    with st.expander("Company details"):
        st.write(f"Symbol used by backend: `{summary['symbol']}`")
        st.write(f"Exchange: {summary['exchange'] or 'Not available'}")
        st.write(f"Sector: {summary['sector'] or 'Not available'}")
        st.write(f"Industry: {summary['industry'] or 'Not available'}")
        if summary["website"]:
            st.link_button("Company website", summary["website"])
