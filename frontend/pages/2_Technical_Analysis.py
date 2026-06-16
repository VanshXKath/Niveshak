import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from frontend.utils.api_client import fetch_json

st.set_page_config(page_title="Technical Analysis", layout="wide")
st.title("📉 Technical Analysis")
st.caption("StockEdge-style indicator dashboard with plain-English explanations")

symbol = st.text_input("NSE Symbol", value=st.session_state.get("symbol", "RELIANCE")).strip().upper()
period = st.selectbox("Lookback", ["3mo", "6mo", "1y"], index=1)

if st.button("Run Technical Scan", type="primary"):
    try:
        data = fetch_json(f"/api/technical/{symbol}?period={period}")
        st.session_state["symbol"] = symbol
        st.subheader(f"{data['symbol']} — {data['trend']}")
        st.write(data.get("trend_explanation"))
        c1, c2 = st.columns(2)
        c1.metric("Support", f"₹{data.get('support_level', 0):,.2f}")
        c2.metric("Resistance", f"₹{data.get('resistance_level', 0):,.2f}")
        st.write(data.get("beginner_summary"))

        for indicator in data.get("indicators", []):
            with st.expander(f"{indicator['name']} — {indicator['signal'].upper()}"):
                st.write(f"Value: **{indicator.get('value')}**")
                st.write(indicator.get("explanation"))
    except Exception as exc:
        st.error(str(exc))
