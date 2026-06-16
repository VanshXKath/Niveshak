import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from frontend.utils.api_client import fetch_json

st.set_page_config(page_title="Fundamental Analysis", layout="wide")
st.title("📋 Fundamental Analysis")
st.caption("Screener.in-inspired ratio cards with AI-style strengths & weaknesses")

symbol = st.text_input("NSE Symbol", value=st.session_state.get("symbol", "RELIANCE")).strip().upper()

if st.button("Analyze Fundamentals", type="primary"):
    try:
        data = fetch_json(f"/api/fundamental/{symbol}")
        st.session_state["symbol"] = symbol
        st.subheader(data.get("company_name", symbol))
        st.write(data.get("beginner_summary"))

        cols = st.columns(3)
        for index, metric in enumerate(data.get("metrics", [])):
            with cols[index % 3]:
                st.metric(metric["name"], metric.get("value") or "N/A")
                if metric.get("interpretation"):
                    st.caption(metric["interpretation"])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Strengths**")
            for item in data.get("strengths", []):
                st.success(item)
            st.markdown("**Opportunities**")
            for item in data.get("opportunities", []):
                st.info(item)
        with c2:
            st.markdown("**Weaknesses**")
            for item in data.get("weaknesses", []):
                st.warning(item)
            st.markdown("**Risks**")
            for item in data.get("risks", []):
                st.error(item)
    except Exception as exc:
        st.error(str(exc))
