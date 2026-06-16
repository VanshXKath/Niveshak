import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import pandas as pd
import streamlit as st

from frontend.utils.api_client import delete_request, fetch_json, post_json
from frontend.utils.formatters import format_inr

st.set_page_config(page_title="Portfolio", layout="wide")
st.title("💼 Portfolio Analysis")
st.caption("Groww portfolio-style holdings with diversification score")

with st.form("add_holding"):
    c1, c2, c3 = st.columns(3)
    symbol = c1.text_input("Symbol", value="TCS")
    qty = c2.number_input("Quantity", min_value=0.01, value=10.0)
    avg = c3.number_input("Avg buy price", min_value=0.01, value=3500.0)
    if st.form_submit_button("Add holding"):
        try:
            post_json("/api/portfolio/holdings", {"symbol": symbol, "quantity": qty, "avg_price": avg})
            st.success("Holding added")
        except Exception as exc:
            st.error(str(exc))

if st.button("Analyze Portfolio", type="primary"):
    try:
        data = fetch_json("/api/portfolio/analysis")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Invested", format_inr(data.get("total_invested")))
        c2.metric("Current", format_inr(data.get("total_current_value")))
        c3.metric("P&L", format_inr(data.get("total_pnl")))
        c4.metric("Risk", data.get("risk_score"))

        st.metric("Diversification Score", f"{data.get('diversification_score')}/100")
        st.write(data.get("beginner_summary"))

        holdings = data.get("holdings", [])
        if holdings:
            st.dataframe(pd.DataFrame(holdings), use_container_width=True)
            for holding in holdings:
                if st.button(f"Remove {holding['symbol']}", key=f"rm_{holding['id']}"):
                    delete_request(f"/api/portfolio/holdings/{holding['id']}")
                    st.rerun()

        if data.get("sector_exposure"):
            st.subheader("Sector Exposure")
            st.json(data["sector_exposure"])

        for rec in data.get("recommendations", []):
            st.info(rec)
    except Exception as exc:
        st.error(str(exc))
