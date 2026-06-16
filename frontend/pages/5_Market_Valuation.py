import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from frontend.utils.api_client import fetch_json

st.set_page_config(page_title="Market Valuation", layout="wide")
st.title("🌡️ Market Valuation")
st.caption("NIFTY PE thermometer — inspired by Screener.in market pages")

if st.button("Load Market Valuation", type="primary") or st.session_state.get("market_loaded"):
    st.session_state["market_loaded"] = True
    try:
        data = fetch_json("/api/market/valuation")
        c1, c2, c3 = st.columns(3)
        c1.metric("Index", data.get("index_name"))
        c2.metric("Current PE", data.get("current_pe") or "N/A")
        c3.metric("Status", data.get("valuation_status"))
        st.info(data.get("explanation"))
        st.write(data.get("beginner_summary"))
    except Exception as exc:
        st.error(str(exc))
