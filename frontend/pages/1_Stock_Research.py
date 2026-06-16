import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from frontend.utils.api_client import fetch_json
from frontend.utils.formatters import format_inr, format_large_number

st.set_page_config(page_title="Stock Research", layout="wide")
st.title("📊 Stock Research")

symbol = st.text_input("NSE Symbol", value=st.session_state.get("symbol", "RELIANCE")).strip().upper()
period = st.selectbox("Chart period", ["1mo", "3mo", "6mo", "1y", "5y"], index=2)
chart_type = st.selectbox("Chart", ["Candlestick", "Line"])

if st.button("Analyze", type="primary"):
    try:
        summary = fetch_json(f"/api/stocks/{symbol}/summary")
        history = fetch_json(f"/api/stocks/{symbol}/history?period={period}&interval=1d")
        st.session_state["symbol"] = symbol

        st.subheader(summary["company_name"])
        st.caption(f"Source: {summary.get('data_source', 'n/a')}")
        st.write(summary.get("beginner_summary", ""))

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Price", format_inr(summary.get("current_price")))
        m2.metric("Prev Close", format_inr(summary.get("previous_close")))
        m3.metric("PE", summary.get("pe_ratio") or "N/A")
        m4.metric("Market Cap", format_large_number(summary.get("market_cap")))

        prices = pd.DataFrame(history["prices"])
        prices["date"] = pd.to_datetime(prices["date"])
        fig = go.Figure()
        if chart_type == "Candlestick":
            fig.add_trace(go.Candlestick(x=prices["date"], open=prices["open"], high=prices["high"], low=prices["low"], close=prices["close"]))
        else:
            fig.add_trace(go.Scatter(x=prices["date"], y=prices["close"], mode="lines"))
        fig.update_layout(height=500, template="plotly_dark", xaxis_rangeslider_visible=False)
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("Company details"):
            st.write(f"Symbol: `{summary.get('symbol')}`")
            st.write(f"Sector: {summary.get('sector') or 'N/A'}")
            st.write(f"Industry: {summary.get('industry') or 'N/A'}")
            if summary.get("website"):
                st.link_button("Website", summary["website"])
    except Exception as exc:
        st.error(str(exc))
